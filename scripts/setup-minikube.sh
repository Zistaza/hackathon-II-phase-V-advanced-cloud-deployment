#!/bin/bash
# Setup Minikube cluster for Phase-V deployment
# Usage: ./scripts/setup-minikube.sh

set -e

echo "=== Phase-V Minikube Setup ==="

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "Error: Minikube not found. Please install Minikube first:"
    echo "  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64"
    echo "  sudo install minikube-linux-amd64 /usr/local/bin/minikube"
    exit 1
fi

echo "✓ Minikube CLI installed"

# Check if cluster already exists
if minikube status | grep -q "host: Running"; then
    echo "✓ Minikube cluster is already running"
    minikube status
    echo ""
    echo "To use existing cluster, skip to:"
    echo "  kubectl cluster-info"
    exit 0
fi

# Stop any existing cluster first
if minikube status &> /dev/null; then
    echo "Stopping existing Minikube cluster..."
    minikube stop
fi

# Start Minikube with recommended resources for Phase-V
echo "Starting Minikube cluster with recommended resources..."
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker \
  --kubernetes-version=v1.28.0 \
  --namespace=todo-app

echo ""
echo "✓ Minikube cluster started"

# Verify cluster is running
echo "Verifying cluster..."
kubectl cluster-info
kubectl get nodes

echo ""
echo "=== Minikube Setup Complete ==="
echo "Next steps:"
echo "  1. Install Dapr: ./scripts/setup-dapr.sh"
echo "  2. Deploy Redis: ./scripts/deploy-redis.sh"
echo "  3. Create secrets: ./scripts/create-local-secrets.sh"
echo "  4. Deploy app: ./scripts/deploy-local.sh"
echo ""
