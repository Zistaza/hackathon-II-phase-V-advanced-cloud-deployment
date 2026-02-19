#!/bin/bash
# Install Traefik ingress controller on k3s cluster
# Usage: ./scripts/install-traefik.sh

set -e

echo "=== Phase-V Traefik Installation ==="

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

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    print_error "No Kubernetes cluster found"
    print_info "Make sure k3s is installed and kubeconfig is set up"
    exit 1
fi

print_info "Kubernetes cluster detected"

# Check if Traefik is already installed
if kubectl get deployment traefik -n kube-system &> /dev/null; then
    print_warning "Traefik is already installed"
    kubectl get deployment traefik -n kube-system
    read -p "Do you want to reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping Traefik installation"
        exit 0
    fi
    
    # Uninstall existing Traefik
    print_info "Uninstalling existing Traefik..."
    helm uninstall traefik -n kube-system || true
    sleep 5
fi

# Add Traefik Helm repository
print_info "Adding Traefik Helm repository..."
helm repo add traefik https://traefik.github.io/charts 2>/dev/null || true
helm repo update

# Create values file for Traefik configuration
VALUES_FILE=$(mktemp)
cat > "$VALUES_FILE" <<EOF
deployment:
  enabled: true
  replicas: 2
  imageTag: v3.0.0
  
ports:
  web:
    exposedPort: 80
    port: 8000
    redirectTo:
      port: websecure
      priority: 10
  websecure:
    exposedPort: 443
    port: 8443
    tls:
      enabled: true
      
providers:
  kubernetesCRD:
    enabled: true
    allowCrossNamespace: true
    allowExternalNameServices: true
  kubernetesIngress:
    enabled: true
    allowExternalNameServices: true
    publishedService:
      enabled: true

logs:
  general:
    level: INFO
  access:
    enabled: true

metrics:
  prometheus:
    entryPoint: metrics
    addEntryPointsLabels: true
    addServicesLabels: true

globalArguments:
  - "--global.checknewversion=false"
  - "--global.sendanonymoususage=false"

additionalArguments:
  - "--serversTransport.insecureSkipVerify=true"
  - "--api.dashboard=true"
  - "--ping=true"

resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"

tolerations:
  - key: "node-role.kubernetes.io/master"
    operator: "Equal"
    value: ""
    effect: "NoSchedule"
  - key: "node-role.kubernetes.io/control-plane"
    operator: "Equal"
    value: ""
    effect: "NoSchedule"

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchLabels:
            app.kubernetes.io/name: traefik
        topologyKey: kubernetes.io/hostname
EOF

print_info "Installing Traefik ingress controller..."

# Install Traefik with Helm
helm install traefik traefik/traefik \
  --namespace kube-system \
  --version 28.0.0 \
  --values "$VALUES_FILE" \
  --wait \
  --timeout 5m

# Clean up temp file
rm -f "$VALUES_FILE"

print_info "Waiting for Traefik to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=traefik -n kube-system --timeout=120s

# Get Traefik service info
print_info ""
print_info "=== Traefik Installation Complete ==="
print_info ""
print_info "Traefik Service:"
kubectl get svc traefik -n kube-system

# Get external IP (if available)
EXTERNAL_IP=$(kubectl get svc traefik -n kube-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")

if [ -n "$EXTERNAL_IP" ]; then
    print_info ""
    print_info "External IP: $EXTERNAL_IP"
    print_info ""
    print_info "Update your DNS records:"
    print_info "  A record: todo-app.example.com -> $EXTERNAL_IP"
    print_info ""
else
    print_info ""
    print_warning "No external IP assigned yet (may take a few minutes)"
    print_info "Check with: kubectl get svc traefik -n kube-system -w"
    print_info ""
    print_info "For Oracle Cloud, use the node's public IP:"
    print_info "  kubectl get nodes -o wide"
    print_info ""
fi

# Verify Traefik dashboard
print_info "Traefik Dashboard (port-forward):"
print_info "  kubectl port-forward -n kube-system svc/traefik 9000:9000"
print_info "  Then open: http://localhost:9000/dashboard/"
print_info ""

# Show next steps
print_info "=== Next Steps ==="
print_info "  1. Install cert-manager: ./scripts/install-cert-manager.sh"
print_info "  2. Create ClusterIssuer for Let's Encrypt"
print_info "  3. Deploy application: ./scripts/deploy-cloud.sh"
print_info ""
