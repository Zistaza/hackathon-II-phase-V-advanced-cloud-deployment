#!/bin/bash
# Setup Dapr on Kubernetes cluster for Phase-V
# Usage: ./scripts/setup-dapr.sh

set -e

echo "=== Phase-V Dapr Setup ==="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: No Kubernetes cluster found. Start Minikube first:"
    echo "  ./scripts/setup-minikube.sh"
    exit 1
fi

echo "✓ Kubernetes cluster detected"

# Check if dapr CLI is installed
if ! command -v dapr &> /dev/null; then
    echo "Dapr CLI not found. Installing Dapr CLI..."
    # Install Dapr CLI
    if command -v brew &> /dev/null; then
        brew install dapr/tap/dapr-cli
    elif command -v apt-get &> /dev/null; then
        wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
    else
        echo "Please install Dapr CLI: https://docs.dapr.io/getting-started/install-dapr-cli/"
        exit 1
    fi
fi

echo "✓ Dapr CLI installed (version: $(dapr version))"

# Check if Dapr is already installed on the cluster
if dapr status -k 2>/dev/null | grep -q "running"; then
    echo "✓ Dapr is already running on the cluster"
    dapr status -k
else
    echo "Installing Dapr on Kubernetes..."
    dapr init -k --wait
    
    echo ""
    echo "Waiting for Dapr components to be ready..."
    sleep 10
    
    # Wait for Dapr pods to be running
    kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=120s || true
    kubectl wait --for=condition=ready pod -l app=dapr-sentry -n dapr-system --timeout=120s || true
    kubectl wait --for=condition=ready pod -l app=dapr-sidecar-injector -n dapr-system --timeout=120s || true
fi

echo ""
echo "=== Dapr Setup Complete ==="
echo "Verify installation:"
echo "  dapr status -k"
echo ""
echo "Expected output:"
echo "  NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS"
echo "  dapr-sidecar-injector  dapr-system  True     Running  1"
echo "  dapr-sentry            dapr-system  True     Running  1"
echo "  dapr-operator          dapr-system  True     Running  1"
echo "  dapr-placement         dapr-system  True     Running  1"
echo ""
echo "Next steps:"
echo "  1. Deploy Redis: ./scripts/deploy-redis.sh"
echo "  2. Create secrets: ./scripts/create-local-secrets.sh"
echo "  3. Deploy app: ./scripts/deploy-local.sh"
echo ""
