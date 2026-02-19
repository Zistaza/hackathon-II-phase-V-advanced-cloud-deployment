#!/bin/bash
# Install k3s cluster on Oracle Cloud Compute instances
# Usage: Run on server node, then run agent script on worker nodes
# Prerequisites: Oracle Linux 8 or Ubuntu 22.04 with SSH access

set -e

echo "=== Phase-V k3s Installation ==="

# Configuration
K3S_VERSION="v1.28.5+k3s1"
SERVER_NODE_IP="${SERVER_NODE_IP:-}"
AGENT_NODE_IP="${AGENT_NODE_IP:-}"
CLUSTER_CIDR="${CLUSTER_CIDR:-10.42.0.0/16}"
SERVICE_CIDR="${SERVICE_CIDR:-10.43.0.0/16}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root or with sudo"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
else
    print_error "Cannot detect operating system"
    exit 1
fi

print_info "Detected OS: $OS"

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        apt-get update
        apt-get install -y curl wget socat conntrack ebtables ethtool
    elif command -v yum &> /dev/null; then
        # Oracle Linux/CentOS/RHEL
        yum install -y curl wget socat conntrack-tools ebtables ethtool
    else
        print_error "Unsupported package manager"
        exit 1
    fi
    
    print_info "Dependencies installed"
}

# Check if k3s is already installed
if command -v k3s &> /dev/null; then
    print_warning "k3s is already installed"
    read -p "Do you want to reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping k3s installation"
        exit 0
    fi
    
    # Uninstall existing k3s
    print_info "Uninstalling existing k3s..."
    /usr/local/bin/k3s-uninstall.sh || true
fi

# Install k3s server
install_k3s_server() {
    print_info "Installing k3s server..."
    
    # Get server's private IP
    if [ -z "$SERVER_NODE_IP" ]; then
        # Try to auto-detect private IP
        SERVER_NODE_IP=$(hostname -I | awk '{print $1}')
        print_warning "Auto-detected server IP: $SERVER_NODE_IP"
        print_info "Set SERVER_NODE_IP environment variable to override"
    fi
    
    # Install k3s server
    curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="$K3S_VERSION" sh -s - server \
        --write-kubeconfig-mode 644 \
        --disable traefik \
        --disable servicelb \
        --disable local-storage \
        --node-external-ip "$SERVER_NODE_IP" \
        --cluster-cidr "$CLUSTER_CIDR" \
        --service-cidr "$SERVICE_CIDR" \
        --kubelet-arg "node-ip=$SERVER_NODE_IP"
    
    print_info "k3s server installed successfully"
    
    # Copy kubeconfig to user's home
    mkdir -p /home/$SUDO_USER/.kube
    cp /etc/rancher/k3s/k3s.yaml /home/$SUDO_USER/.kube/config
    chown $SUDO_USER:$SUDO_USER /home/$SUDO_USER/.kube/config
    
    # Get node token for agents
    NODE_TOKEN=$(cat /var/lib/rancher/k3s/server/node-token)
    
    print_info ""
    print_info "=== k3s Server Installation Complete ==="
    print_info "Kubeconfig: /home/$SUDO_USER/.kube/config"
    print_info "Node Token: $NODE_TOKEN"
    print_info ""
    print_info "To connect agent nodes, run on each agent:"
    print_info "  curl -sfL https://get.k3s.io | K3S_URL=https://${SERVER_NODE_IP}:6443 K3S_TOKEN=${NODE_TOKEN} sh -"
    print_info ""
    
    # Verify cluster
    print_info "Verifying cluster..."
    sleep 5
    kubectl cluster-info
    kubectl get nodes
}

# Install k3s agent
install_k3s_agent() {
    if [ -z "$SERVER_NODE_IP" ]; then
        print_error "SERVER_NODE_IP environment variable is required for agent installation"
        print_info "Usage: SERVER_NODE_IP=<server-ip> $0 agent"
        exit 1
    fi
    
    if [ -z "$K3S_TOKEN" ]; then
        print_error "K3S_TOKEN environment variable is required for agent installation"
        print_info "Get the token from the server node: cat /var/lib/rancher/k3s/server/node-token"
        exit 1
    fi
    
    print_info "Installing k3s agent..."
    print_info "Connecting to server: $SERVER_NODE_IP"
    
    # Install k3s agent
    curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="$K3S_VERSION" sh -s - agent \
        --server "https://${SERVER_NODE_IP}:6443" \
        --token "$K3S_TOKEN" \
        --node-ip "$AGENT_NODE_IP"
    
    print_info "k3s agent installed successfully"
}

# Show usage
show_usage() {
    echo "Usage: $0 [server|agent]"
    echo ""
    echo "Commands:"
    echo "  server  Install k3s server (default)"
    echo "  agent   Install k3s agent node"
    echo ""
    echo "Environment Variables:"
    echo "  SERVER_NODE_IP   Server node IP address (required for agent)"
    echo "  AGENT_NODE_IP    Agent node IP address (optional, auto-detected)"
    echo "  K3S_TOKEN        k3s node token (required for agent)"
    echo ""
    echo "Examples:"
    echo "  # Install k3s server"
    echo "  sudo $0 server"
    echo ""
    echo "  # Install k3s agent"
    echo "  SERVER_NODE_IP=10.0.0.2 K3S_TOKEN=<token> sudo $0 agent"
}

# Main
case "${1:-server}" in
    server)
        install_dependencies
        install_k3s_server
        ;;
    agent)
        install_dependencies
        install_k3s_agent
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac

print_info ""
print_info "=== Installation Complete ==="
print_info "Next steps:"
print_info "  1. Install Traefik: ./scripts/install-traefik.sh"
print_info "  2. Install cert-manager: ./scripts/install-cert-manager.sh"
print_info "  3. Install Dapr: dapr init -k --wait"
print_info "  4. Deploy application: ./scripts/deploy-cloud.sh"
print_info ""
