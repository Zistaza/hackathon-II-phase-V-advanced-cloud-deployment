#!/bin/bash
# Validate Phase-V deployment on Minikube
# Usage: ./scripts/validate-deployment.sh

set -e

NAMESPACE="todo-app"
ERRORS=0

echo "=== Phase-V Deployment Validation ==="
echo ""

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Error: No Kubernetes cluster found"
    exit 1
fi

echo "✓ Kubernetes cluster is running"

# Check namespace
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "✓ Namespace $NAMESPACE exists"
else
    echo "❌ Namespace $NAMESPACE does not exist"
    ERRORS=$((ERRORS + 1))
fi

# Check Dapr installation
echo ""
echo "Checking Dapr installation..."
if command -v dapr &> /dev/null && dapr status -k 2>/dev/null | grep -q "running"; then
    echo "✓ Dapr is installed and running"
    dapr status -k | head -6
else
    echo "⚠️  Dapr is not running (may not be required for local Redis setup)"
fi

# Check Redis
echo ""
echo "Checking Redis..."
REDIS_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=redis -o jsonpath='{.items[*].status.phase}' 2>/dev/null || echo "")
if [[ "$REDIS_PODS" == *"Running"* ]]; then
    echo "✓ Redis is running"
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=redis
else
    echo "⚠️  Redis is not running (required for local Pub/Sub)"
fi

# Check Dapr components
echo ""
echo "Checking Dapr components..."
DAPR_COMPONENTS=$(kubectl get components -n "$NAMESPACE" 2>/dev/null | wc -l)
if [ "$DAPR_COMPONENTS" -gt 1 ]; then
    echo "✓ Dapr components deployed ($((DAPR_COMPONENTS - 1)) found)"
    kubectl get components -n "$NAMESPACE" 2>/dev/null || true
else
    echo "⚠️  Dapr components not found"
fi

# Check deployments
echo ""
echo "Checking application deployments..."
EXPECTED_DEPLOYMENTS=("backend" "frontend" "event-processor" "reminder-scheduler" "notification-service" "websocket-service")
for deployment in "${EXPECTED_DEPLOYMENTS[@]}"; do
    if kubectl get deployment "$deployment" -n "$NAMESPACE" &> /dev/null; then
        READY=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        REPLICAS=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
        if [ "$READY" -ge 1 ] 2>/dev/null; then
            echo "✓ $deployment: $READY/$REPLICAS ready"
        else
            echo "⚠️  $deployment: $READY/$REPLICAS ready (waiting)"
        fi
    else
        echo "❌ $deployment: not found"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check pods and Dapr sidecars
echo ""
echo "Checking pods and Dapr sidecar injection..."
PODS=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)
if [ -n "$PODS" ]; then
    echo "Pod status (should show 2/2 for app + Dapr sidecar):"
    kubectl get pods -n "$NAMESPACE"
    
    # Check for sidecar injection
    SIDECAR_PODS=0
    TOTAL_PODS=0
    for pod in $PODS; do
        TOTAL_PODS=$((TOTAL_PODS + 1))
        CONTAINERS=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.status.containerStatuses[*].ready}' 2>/dev/null | wc -w || echo "0")
        if [ "$CONTAINERS" -ge 2 ]; then
            SIDECAR_PODS=$((SIDECAR_PODS + 1))
        fi
    done
    
    if [ "$SIDECAR_PODS" -eq "$TOTAL_PODS" ]; then
        echo "✓ All pods have Dapr sidecars injected ($SIDECAR_PODS/$TOTAL_PODS)"
    else
        echo "⚠️  Some pods missing Dapr sidecars ($SIDECAR_PODS/$TOTAL_PODS)"
    fi
else
    echo "❌ No pods found in namespace"
    ERRORS=$((ERRORS + 1))
fi

# Check services
echo ""
echo "Checking services..."
SERVICES=$(kubectl get services -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l || echo "0")
if [ "$SERVICES" -gt 0 ]; then
    echo "✓ Services deployed ($SERVICES found)"
    kubectl get services -n "$NAMESPACE" --no-headers | head -5
else
    echo "⚠️  No services found"
fi

# Check ingress
echo ""
echo "Checking ingress..."
if kubectl get ingress -n "$NAMESPACE" 2>/dev/null | grep -q "todo-app"; then
    echo "✓ Ingress configured"
    kubectl get ingress -n "$NAMESPACE"
    
    # Check /etc/hosts entry
    if grep -q "todo-app.local" /etc/hosts 2>/dev/null; then
        echo "✓ /etc/hosts entry exists"
    else
        echo "⚠️  /etc/hosts entry missing. Add with:"
        echo "   echo \"$(minikube ip 2>/dev/null || echo 'MINIKUBE_IP') todo-app.local\" | sudo tee -a /etc/hosts"
    fi
else
    echo "⚠️  Ingress not configured"
fi

# Test health endpoint
echo ""
echo "Testing health endpoint..."
MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "")
if [ -n "$MINIKUBE_IP" ] && grep -q "todo-app.local" /etc/hosts 2>/dev/null; then
    HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://todo-app.local/api/health" 2>/dev/null || echo "000")
    if [ "$HEALTH_RESPONSE" == "200" ]; then
        echo "✓ Health endpoint responding (HTTP $HEALTH_RESPONSE)"
    else
        echo "⚠️  Health endpoint not responding (HTTP $HEALTH_RESPONSE)"
    fi
else
    echo "⚠️  Cannot test health endpoint (Minikube IP or /etc/hosts not configured)"
fi

# Check secrets
echo ""
echo "Checking secrets..."
SECRETS=$(kubectl get secrets -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l || echo "0")
if [ "$SECRETS" -ge 3 ]; then
    echo "✓ Secrets deployed ($SECRETS found)"
    kubectl get secrets -n "$NAMESPACE" --no-headers | grep -v "default-token"
else
    echo "⚠️  Not all secrets deployed ($SECRETS found, expected 4)"
fi

# Summary
echo ""
echo "==================================="
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ Validation Complete - All checks passed!"
else
    echo "❌ Validation Complete - $ERRORS error(s) found"
fi
echo "==================================="
echo ""
echo "Next steps:"
echo "  1. Fix any issues marked with ❌"
echo "  2. Test event flow: ./scripts/test-end-to-end.py"
echo "  3. Access the app: http://todo-app.local"
echo ""

exit $ERRORS
