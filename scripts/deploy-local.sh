#!/bin/bash
# Deploy Phase-V to local Minikube cluster
# Usage: ./scripts/deploy-local.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$PROJECT_ROOT/k8s"
NAMESPACE="todo-app"

echo "=== Phase-V Local Deployment (Minikube) ==="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: No Kubernetes cluster found. Start Minikube first:"
    echo "  ./scripts/setup-minikube.sh"
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

# Apply Dapr components first
echo "Applying Dapr components..."
kubectl apply -f "$K8S_DIR/local/dapr-components/" || true

# Wait for Dapr components to be ready
echo "Waiting for Dapr components to be ready..."
sleep 5

# Apply base resources
echo "Applying base Kubernetes resources..."
kubectl apply -f "$K8S_DIR/base/"

# Apply local overlays
echo "Applying local environment overlays..."
kubectl apply -f "$K8S_DIR/local/"

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
echo "Access the app: http://todo-app.local"
echo "(Make sure to add $(minikube ip) todo-app.local to /etc/hosts)"
echo ""
echo "Next step: Run ./scripts/validate-deployment.sh to verify everything is working"
echo ""
