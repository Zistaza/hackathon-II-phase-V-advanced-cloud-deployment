#!/bin/bash
# Setup monitoring stack for Phase-V (Prometheus + Grafana)
# Usage: ./scripts/setup-monitoring.sh

set -e

echo "=== Phase-V Monitoring Stack Setup ==="

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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MONITORING_DIR="$PROJECT_ROOT/monitoring"
NAMESPACE="monitoring"

# Create namespace
print_info "Creating monitoring namespace..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Deploy Prometheus
print_info "Deploying Prometheus..."
kubectl apply -f "$MONITORING_DIR/prometheus/prometheus.yaml"
kubectl apply -f "$MONITORING_DIR/prometheus/alerts.yaml"

print_info "Waiting for Prometheus to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus -n "$NAMESPACE" --timeout=120s || true

# Deploy Grafana
print_info "Deploying Grafana..."

# Create Grafana values file
VALUES_FILE=$(mktemp)
cat > "$VALUES_FILE" <<EOF
replicas: 1

adminUser: admin
adminPassword: admin

service:
  type: ClusterIP
  port: 3000

persistence:
  enabled: false
  size: 10Gi

resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

datasources:
  datasources.yaml:
    datasources:
      - name: Prometheus
        type: prometheus
        url: http://prometheus.monitoring.svc.cluster.local:9090
        access: proxy
        isDefault: true
        editable: true

dashboardProviders:
  dashboardproviders.yaml:
    providers:
      - name: 'default'
        orgId: 1
        folder: ''
        type: file
        disableDeletion: false
        editable: true
        options:
          path: /var/lib/grafana/dashboards/default

dashboardsConfigMaps:
  default: "grafana-dashboards"

rbac:
  pspEnabled: false
EOF

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    print_error "Helm not found. Please install Helm first."
    exit 1
fi

# Add Grafana Helm repository
helm repo add grafana https://grafana.github.io/helm-charts 2>/dev/null || true
helm repo update

# Check if Grafana is already installed
if helm list -n "$NAMESPACE" | grep -q "grafana"; then
    print_warning "Grafana is already installed"
    helm list -n "$NAMESPACE" | grep grafana
    read -p "Do you want to reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping Grafana installation"
    else
        helm uninstall grafana -n "$NAMESPACE" || true
        sleep 5
        helm install grafana grafana/grafana -f "$VALUES_FILE" -n "$NAMESPACE" --wait
    fi
else
    helm install grafana grafana/grafana -f "$VALUES_FILE" -n "$NAMESPACE" --wait
fi

# Clean up temp file
rm -f "$VALUES_FILE"

# Create ConfigMap for Grafana dashboards
print_info "Creating Grafana dashboard ConfigMaps..."
kubectl create configmap grafana-dashboards \
  --from-file="$MONITORING_DIR/grafana/dashboards/" \
  --namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart Grafana to pick up dashboards
print_info "Restarting Grafana..."
kubectl rollout restart deployment grafana -n "$NAMESPACE"

# Wait for Grafana
print_info "Waiting for Grafana to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n "$NAMESPACE" --timeout=120s || true

# Print status
print_info ""
print_info "=== Monitoring Stack Setup Complete ==="
print_info ""
print_info "Prometheus:"
kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=prometheus
print_info ""
print_info "Grafana:"
kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=grafana
print_info ""
print_info "Services:"
kubectl get svc -n "$NAMESPACE"
print_info ""

# Get Grafana password
GRAFANA_PASSWORD=$(kubectl get secret grafana -n "$NAMESPACE" -o jsonpath="{.data.admin-password}" | base64 -d)

print_info "=== Access Information ==="
print_info ""
print_info "Grafana:"
print_info "  Username: admin"
print_info "  Password: $GRAFANA_PASSWORD"
print_info ""
print_info "To access Grafana locally:"
print_info "  kubectl port-forward -n $NAMESPACE svc/grafana 3000:80"
print_info "  Then open: http://localhost:3000"
print_info ""
print_info "To access Prometheus locally:"
print_info "  kubectl port-forward -n $NAMESPACE svc/prometheus 9090:9090"
print_info "  Then open: http://localhost:9090"
print_info ""

# Verify dashboards
print_info "=== Dashboard Verification ==="
print_info ""
print_info "Available dashboards:"
kubectl get configmap grafana-dashboards -n "$NAMESPACE" -o jsonpath='{.data}' | jq -r 'keys[]' || print_warning "Could not list dashboards"
print_info ""

print_info "=== Next Steps ==="
print_info "  1. Access Grafana and verify dashboards are imported"
print_info "  2. Check Prometheus targets: http://localhost:9090/targets"
print_info "  3. Verify metrics are being scraped from Phase-V services"
print_info "  4. Configure alerting rules if needed"
print_info ""
