#!/bin/bash
# Deploy Phase-V to Oracle Cloud (k3s)
# Usage: ./scripts/deploy-cloud.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$PROJECT_ROOT/k8s"
NAMESPACE="todo-app"

echo "=== Phase-V Cloud Deployment (Oracle Cloud) ==="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: No Kubernetes cluster found. Configure kubectl for your cloud cluster first."
    echo "Export your kubeconfig: export KUBECONFIG=~/.kube/config"
    exit 1
fi

echo "✓ Kubernetes cluster detected"

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "Creating namespace: $NAMESPACE"
    kubectl create namespace "$NAMESPACE"
else
    echo "✓ Namespace $NAMESPACE exists"
fi

# Check if Dapr is installed
if ! command -v dapr &> /dev/null || ! dapr status -k 2>/dev/null | grep -q "running"; then
    echo "⚠️  Dapr is not installed. Installing Dapr..."
    dapr init -k --wait
fi

# Apply Dapr components for cloud
echo "Applying Dapr cloud components..."
kubectl apply -f "$K8S_DIR/cloud/dapr-components/"

# Wait for Dapr components
echo "Waiting for Dapr components to be ready..."
sleep 5

# Apply base resources
echo "Applying base Kubernetes resources..."
kubectl apply -f "$K8S_DIR/base/"

# Apply cloud overlays
echo "Applying cloud environment overlays..."
kubectl apply -f "$K8S_DIR/cloud/"

echo ""
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment --all -n "$NAMESPACE" --timeout=300s || true

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Verify deployment:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl get deployments -n $NAMESPACE"
echo "  kubectl get ingress -n $NAMESPACE"
echo ""
echo "Check pod status:"
echo "  kubectl get pods -n $NAMESPACE -w"
echo ""
echo "Access the app:"
echo "  https://todo-app.example.com (configure your domain)"
echo ""
echo "Next steps:"
echo "  1. Run ./scripts/create-cloud-secrets.sh to create secrets"
echo "  2. Run ./scripts/validate-deployment.sh to verify deployment"
echo "  3. Configure DNS for your domain"
echo ""
