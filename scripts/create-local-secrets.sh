#!/bin/bash
# Create Kubernetes secrets for local Phase-V deployment
# Usage: ./scripts/create-local-secrets.sh

set -e

NAMESPACE="todo-app"

echo "=== Phase-V Local Secrets Creation ==="

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

# Load environment variables from .env.example if it exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env.example"

if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from $ENV_FILE"
    export $(grep -v '^#' "$ENV_FILE" | xargs) || true
fi

# Create PostgreSQL secret (using Neon connection string)
echo "Creating PostgreSQL secret..."
POSTGRES_CONNECTION_STRING="${POSTGRES_CONNECTION_STRING:-postgresql://user:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require}"
kubectl create secret generic neon-secret \
  --from-literal=connectionString="$POSTGRES_CONNECTION_STRING" \
  --namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create JWT secret
echo "Creating JWT secret..."
JWT_SECRET="${JWT_SECRET:-your-super-secret-jwt-key-change-in-production}"
kubectl create secret generic jwt-secret \
  --from-literal=secret="$JWT_SECRET" \
  --namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create Redis secret
echo "Creating Redis secret..."
REDIS_PASSWORD="${REDIS_PASSWORD:-redis-password}"
kubectl create secret generic redis-secret \
  --from-literal=password="$REDIS_PASSWORD" \
  --namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create Dapr Redis secret (for state store)
echo "Creating Dapr Redis secret..."
kubectl create secret generic dapr-redis-secret \
  --from-literal=password="$REDIS_PASSWORD" \
  --namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "=== Secrets Creation Complete ==="
echo "Verify secrets:"
echo "  kubectl get secrets -n $NAMESPACE"
echo ""
echo "Expected output:"
echo "  NAME               TYPE     DATA   AGE"
echo "  neon-secret        Opaque   1      10s"
echo "  jwt-secret         Opaque   1      10s"
echo "  redis-secret       Opaque   1      10s"
echo "  dapr-redis-secret  Opaque   1      10s"
echo ""
echo "Next steps:"
echo "  1. Deploy Dapr components: kubectl apply -f k8s/local/dapr-components/"
echo "  2. Deploy app: ./scripts/deploy-local.sh"
echo ""
