#!/bin/bash
# Install cert-manager for SSL/TLS certificate management
# Usage: ./scripts/install-cert-manager.sh

set -e

echo "=== Phase-V cert-manager Installation ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CERT_MANAGER_VERSION="v1.14.0"

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

# Check if cert-manager is already installed
if kubectl get namespace cert-manager &> /dev/null; then
    print_warning "cert-manager is already installed"
    kubectl get pods -n cert-manager
    read -p "Do you want to reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping cert-manager installation"
        exit 0
    fi
    
    # Uninstall existing cert-manager
    print_info "Uninstalling existing cert-manager..."
    kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/${CERT_MANAGER_VERSION}/cert-manager.yaml --ignore-not-found || true
    sleep 5
fi

# Install cert-manager with kubectl
print_info "Installing cert-manager ${CERT_MANAGER_VERSION}..."

# Create namespace
kubectl create namespace cert-manager --dry-run=client -o yaml | kubectl apply -f -

# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/${CERT_MANAGER_VERSION}/cert-manager.yaml

print_info "Waiting for cert-manager to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s

# Verify installation
print_info ""
print_info "=== cert-manager Installation Complete ==="
print_info ""
print_info "cert-manager pods:"
kubectl get pods -n cert-manager

# Create ClusterIssuer for Let's Encrypt
print_info ""
print_info "Creating Let's Encrypt ClusterIssuer..."

ISSUER_FILE=$(mktemp)
cat > "$ISSUER_FILE" <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
  namespace: cert-manager
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: ${LETSENCRYPT_EMAIL:-admin@example.com}
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    solvers:
    - http01:
        ingress:
          class: traefik
          podTemplate:
            spec:
              nodeSelector:
                "kubernetes.io/os": linux
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
  namespace: cert-manager
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: ${LETSENCRYPT_EMAIL:-admin@example.com}
    privateKeySecretRef:
      name: letsencrypt-staging-account-key
    solvers:
    - http01:
        ingress:
          class: traefik
          podTemplate:
            spec:
              nodeSelector:
                "kubernetes.io/os": linux
EOF

kubectl apply -f "$ISSUER_FILE"
rm -f "$ISSUER_FILE"

print_info ""
print_info "=== ClusterIssuers Created ==="
print_info ""
kubectl get clusterissuers.cert-manager.io

# Show usage instructions
print_info ""
print_info "=== Usage Instructions ==="
print_info ""
print_info "To use Let's Encrypt in your Ingress, add these annotations:"
print_info ""
print_info "  metadata:"
print_info "    annotations:"
print_info "      cert-manager.io/cluster-issuer: letsencrypt-prod"
print_info "  spec:"
print_info "    tls:"
print_info "    - hosts:"
print_info "      - your-domain.example.com"
print_info "      secretName: your-domain-tls"
print_info ""
print_info "Or create a Certificate resource:"
print_info ""
print_info "  apiVersion: cert-manager.io/v1"
print_info "  kind: Certificate"
print_info "  metadata:"
print_info "    name: your-domain-cert"
print_info "    namespace: todo-app"
print_info "  spec:"
print_info "    secretName: your-domain-tls"
print_info "    issuerRef:"
print_info "      name: letsencrypt-prod"
print_info "      kind: ClusterIssuer"
print_info "    dnsNames:"
print_info "    - your-domain.example.com"
print_info ""

# Show next steps
print_info "=== Next Steps ==="
print_info "  1. Set your email: export LETSENCRYPT_EMAIL=your-email@example.com"
print_info "  2. Re-run this script to update ClusterIssuers with your email"
print_info "  3. Create Certificate resources for your domains"
print_info "  4. Deploy application: ./scripts/deploy-cloud.sh"
print_info ""

# Verify cert-manager is working
print_info "=== Verification ==="
print_info "Test cert-manager webhook:"
kubectl api-resources | grep cert-manager.io || print_warning "cert-manager API not found"
print_info ""
print_info "Check cert-manager logs:"
print_info "  kubectl logs -n cert-manager -l app.kubernetes.io/name=cert-manager --tail=20"
print_info ""
