#!/bin/bash
# Deploy Redis for local Dapr Pub/Sub
# Usage: ./scripts/deploy-redis.sh

set -e

echo "=== Phase-V Redis Deployment ==="

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: No Kubernetes cluster found. Start Minikube first:"
    echo "  ./scripts/setup-minikube.sh"
    exit 1
fi

echo "✓ Kubernetes cluster detected"

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "Error: Helm not found. Please install Helm:"
    echo "  curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash"
    exit 1
fi

echo "✓ Helm CLI installed (version: $(helm version --short))"

# Create namespace if it doesn't exist
NAMESPACE="todo-app"
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "Creating namespace: $NAMESPACE"
    kubectl create namespace "$NAMESPACE"
else
    echo "✓ Namespace $NAMESPACE exists"
fi

# Add Bitnami Helm repository if not already added
if ! helm repo list | grep -q "bitnami"; then
    echo "Adding Bitnami Helm repository..."
    helm repo add bitnami https://charts.bitnami.com/bitnami
fi

# Update Helm repositories
echo "Updating Helm repositories..."
helm repo update

# Check if Redis is already deployed
if helm list -n "$NAMESPACE" | grep -q "redis"; then
    echo "✓ Redis is already deployed"
    helm list -n "$NAMESPACE" | grep redis
else
    echo "Deploying Redis for local Pub/Sub..."
    
    # Install Redis with configuration optimized for local development
    helm install redis bitnami/redis \
      --namespace "$NAMESPACE" \
      --set auth.password=redis-password \
      --set master.persistence.enabled=false \
      --set master.resources.requests.cpu=100m \
      --set master.resources.requests.memory=256Mi \
      --set master.resources.limits.cpu=200m \
      --set master.resources.limits.memory=512Mi \
      --set replica.replicaCount=0 \
      --wait \
      --timeout 5m
fi

echo ""
echo "Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis -n "$NAMESPACE" --timeout=120s || true

echo ""
echo "=== Redis Deployment Complete ==="
echo "Verify Redis:"
echo "  kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=redis"
echo ""
echo "Expected output:"
echo "  NAME    READY   STATUS    RESTARTS   AGE"
echo "  redis-0 1/1     Running   0          1m"
echo ""
echo "Next steps:"
echo "  1. Create secrets: ./scripts/create-local-secrets.sh"
echo "  2. Deploy Dapr components: kubectl apply -f k8s/local/dapr-components/"
echo "  3. Deploy app: ./scripts/deploy-local.sh"
echo ""
