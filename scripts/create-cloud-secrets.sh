#!/bin/bash
# Create Kubernetes secrets for cloud Phase-V deployment
# Usage: ./scripts/create-cloud-secrets.sh

set -e

NAMESPACE="todo-app"

echo "=== Phase-V Cloud Secrets Creation ==="

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
    exit 1
fi

print_info "Kubernetes cluster detected"

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_info "Creating namespace: $NAMESPACE"
    kubectl create namespace "$NAMESPACE"
else
    print_info "✓ Namespace $NAMESPACE exists"
fi

# Load environment variables from .env if it exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    print_info "Loading environment variables from $ENV_FILE"
    export $(grep -v '^#' "$ENV_FILE" | xargs) || true
fi

# Create PostgreSQL secret (Neon)
print_info "Creating PostgreSQL secret..."
POSTGRES_CONNECTION_STRING="${POSTGRES_CONNECTION_STRING:-${DATABASE_URL:-postgresql://user:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require}}"
kubectl create secret generic neon-secret \
  --from-literal=connectionString="$POSTGRES_CONNECTION_STRING" \
  --namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create JWT secret
print_info "Creating JWT secret..."
JWT_SECRET="${JWT_SECRET:-$(openssl rand -base64 32)}"
kubectl create secret generic jwt-secret \
  --from-literal=secret="$JWT_SECRET" \
  --namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create Redpanda Cloud secret
print_info "Creating Redpanda Cloud secret..."
REDPANDA_USERNAME="${REDPANDA_USERNAME:-}"
REDPANDA_PASSWORD="${REDPANDA_PASSWORD:-}"

if [ -z "$REDPANDA_USERNAME" ] || [ -z "$REDPANDA_PASSWORD" ]; then
    print_warning "Redpanda credentials not set. Using placeholder values."
    print_warning "Update with: kubectl edit secret redpanda-secret -n $NAMESPACE"
    REDPANDA_USERNAME="redpanda-username"
    REDPANDA_PASSWORD="redpanda-password"
fi

kubectl create secret generic redpanda-secret \
  --from-literal=username="$REDPANDA_USERNAME" \
  --from-literal=password="$REDPANDA_PASSWORD" \
  --namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create Dapr Redis secret (for state store if using Redis)
print_info "Creating Dapr Redis secret..."
REDIS_PASSWORD="${REDIS_PASSWORD:-$(openssl rand -base64 16)}"
kubectl create secret generic dapr-redis-secret \
  --from-literal=password="$REDIS_PASSWORD" \
  --namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create OpenAI secret (optional)
if [ -n "$OPENAI_API_KEY" ]; then
    print_info "Creating OpenAI API key secret..."
    kubectl create secret generic openai-secret \
      --from-literal=api-key="$OPENAI_API_KEY" \
      --namespace "$NAMESPACE" \
      --dry-run=client -o yaml | kubectl apply -f -
else
    print_warning "OPENAI_API_KEY not set. Skipping OpenAI secret creation."
fi

print_info ""
print_info "=== Secrets Creation Complete ==="
print_info ""
print_info "Verify secrets:"
print_info "  kubectl get secrets -n $NAMESPACE"
print_info ""
print_info "Expected secrets:"
print_info "  NAME               TYPE     DATA   AGE"
print_info "  neon-secret        Opaque   1      10s"
print_info "  jwt-secret         Opaque   1      10s"
print_info "  redpanda-secret    Opaque   2      10s"
print_info "  dapr-redis-secret  Opaque   1      10s"
print_info ""
print_info "Next steps:"
print_info "  1. Deploy Dapr components: kubectl apply -f k8s/cloud/dapr-components/"
print_info "  2. Deploy app: ./scripts/deploy-cloud.sh"
print_info "  3. Verify secrets are accessible: kubectl exec -n $NAMESPACE <pod> -- env | grep -E 'DATABASE|JWT|REDPANDA'"
print_info ""

# Show warning about sensitive data
print_warning "IMPORTANT: Review and update secrets with actual values!"
print_warning "  kubectl edit secret neon-secret -n $NAMESPACE"
print_warning "  kubectl edit secret jwt-secret -n $NAMESPACE"
print_warning "  kubectl edit secret redpanda-secret -n $NAMESPACE"
print_info ""
