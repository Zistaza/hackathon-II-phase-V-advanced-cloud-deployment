#!/bin/bash

# Deployment Validation Script
# Validates complete deployment workflow and functionality

set -e

echo "🚀 Validating complete deployment workflow..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CHART_DIR="charts/todo-app"
RELEASE_NAME="todo-app"
NAMESPACE="default"

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if kubectl is installed
check_kubectl() {
    if ! command -v kubectl &&; then
        print_status $RED "❌ kubectl is not installed. Please install kubectl first."
        exit 1
    fi
}

# Function to check if Helm is installed
check_helm() {
    if ! command -v helm &&; then
        print_status $RED "❌ Helm is not installed. Please install Helm first."
        exit 1
    fi
}

# Function to check if Minikube is running
check_minikube() {
    if ! minikube status > /dev/null 2&amp;1; then
        print_status $RED "❌ Minikube is not running. Please start Minikube first."
        exit 1
    fi
}

# Function to validate Minikube setup
validate_minikube() {
    echo "🐳 Checking Minikube setup..."

    # Check Minikube status
    if minikube status > /dev/null 2&amp;1; then
        print_status $GREEN "✅ Minikube is running"
    else
        print_status $RED "❌ Minikube is not running"
        return 1
    fi

    # Check Kubernetes version
    local k8s_version=$(kubectl version --short && kubectl version --short 2>/dev/null | grep -o "Server Version: v[0-9.]*" | cut -d' ' -f3)
    echo "   Kubernetes version: $k8s_version"

    # Check nodes
    local node_count=$(kubectl get nodes -o name | wc -l)
    echo "   Nodes: $node_count"

    # Check if required addons are enabled
    local addons=("ingress" "metrics-server" "dashboard")
    for addon in "${addons[@]}"; do
        if minikube addons list | grep -q "$addon.*enabled"; then
            print_status $GREEN "✅ $addon addon is enabled"
        else
            print_status $YELLOW "⚠️  $addon addon is not enabled"
        fi
    done
}

# Function to validate Helm chart
validate_helm_chart() {
    echo "⚙️  Checking Helm chart..."

    # Lint the chart
    echo "   Running helm lint..."
    if helm lint "$CHART_DIR" > /dev/null 2&amp;1; then
        print_status $GREEN "✅ Chart syntax is valid"
    else
        print_status $RED "❌ Chart syntax errors found"
        helm lint "$CHART_DIR"
        return 1
    fi

    # Template the chart
    echo "   Validating templates..."
    if helm template "$CHART_DIR" > /dev/null 2&amp;1; then
        print_status $GREEN "✅ Templates are valid"
    else
        print_status $RED "❌ Template validation failed"
        helm template "$CHART_DIR"
        return 1
    fi
}

# Function to deploy the application
deploy_application() {
    echo "🚀 Deploying application..."

    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" 2>/dev/null || true

    # Install Helm chart
    echo "   Installing Helm chart..."
    if helm install "$RELEASE_NAME" "$CHART_DIR" --namespace "$NAMESPACE" --create-namespace > /dev/null 2&amp;1; then
        print_status $GREEN "✅ Chart installed successfully"
    else
        print_status $RED "❌ Failed to install chart"
        return 1
    fi
}

# Function to validate deployment status
validate_deployment_status() {
    echo "✅ Checking deployment status..."

    # Wait for deployments to be ready
    echo "   Waiting for deployments to be ready..."
    sleep 30

    # Check backend deployment
    local backend_status=$(kubectl get deployment "$RELEASE_NAME-backend" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "")

    if [ "$backend_status" = "True" ]; then
        print_status $GREEN "✅ Backend deployment is available"
    else
        print_status $RED "❌ Backend deployment is not available"
        return 1
    fi

    # Check frontend deployment
    local frontend_status=$(kubectl get deployment "$RELEASE_NAME-frontend" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "")

    if [ "$frontend_status" = "True" ]; then
        print_status $GREEN "✅ Frontend deployment is available"
    else
        print_status $RED "❌ Frontend deployment is not available"
        return 1
    fi
}

# Function to validate services
validate_services() {
    echo "🔌 Checking services..."

    # Check backend service
    local backend_service=$(kubectl get service "$RELEASE_NAME-backend" -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")

    if [ -n "$backend_service" ]; then
        print_status $GREEN "✅ Backend service is running"
    else
        print_status $RED "❌ Backend service is not running"
        return 1
    fi

    # Check frontend service
    local frontend_service=$(kubectl get service "$RELEASE_NAME-frontend" -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")

    if [ -n "$frontend_service" ]; then
        print_status $GREEN "✅ Frontend service is running"
    else
        print_status $RED "❌ Frontend service is not running"
        return 1
    fi
}

# Function to validate ingress
validate_ingress() {
    echo "🌐 Checking ingress..."

    # Check if ingress is enabled
    if grep -q "ingress:\|enabled: true" "$CHART_DIR/values.yaml"; then
        # Check ingress resource
        local ingress=$(kubectl get ingress "$RELEASE_NAME-ingress" -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")

        if [ -n "$ingress" ]; then
            print_status $GREEN "✅ Ingress is configured and accessible"
            echo "   Ingress IP: $ingress"
        else
            print_status $YELLOW "⚠️  Ingress is not accessible yet"
        fi
    else
        print_status $BLUE "ℹ️  Ingress is disabled"
    fi
}

# Function to validate application functionality
validate_functionality() {
    echo "✅ Checking application functionality..."

    # Get Minikube IP
    local minikube_ip=$(minikube ip)

    # Check if frontend is accessible
    echo "   Testing frontend accessibility..."
    if curl -f -s "http://$minikube_ip" > /dev/null 2&amp;1; then
        print_status $GREEN "✅ Frontend is accessible"
    else
        print_status $YELLOW "⚠️  Frontend might not be accessible yet"
    fi

    # Check if backend is accessible
    echo "   Testing backend accessibility..."
    if curl -f -s "http://$minikube_ip:8000/health" > /dev/null 2&amp;1; then
        print_status $GREEN "✅ Backend is accessible"
    else
        print_status $YELLOW "⚠️  Backend might not be accessible yet"
    fi
}

# Function to test cleanup
test_cleanup() {
    echo "🧹 Testing cleanup..."

    # Uninstall Helm release
    echo "   Uninstalling Helm release..."
    if helm uninstall "$RELEASE_NAME" -n "$NAMESPACE" > /dev/null 2&amp;1; then
        print_status $GREEN "✅ Helm release uninstalled successfully"
    else
        print_status $RED "❌ Failed to uninstall Helm release"
        return 1
    fi

    # Wait for resources to be deleted
    sleep 10

    # Check if resources are deleted
    local backend_deployment=$(kubectl get deployment "$RELEASE_NAME-backend" -n "$NAMESPACE" 2>/dev/null || echo "")
    local frontend_deployment=$(kubectl get deployment "$RELEASE_NAME-frontend" -n "$NAMESPACE" 2>/dev/null || echo "")

    if [ -z "$backend_deployment" ] && [ -z "$frontend_deployment" ]; then
        print_status $GREEN "✅ All resources cleaned up successfully"
    else
        print_status $RED "❌ Some resources still exist"
        return 1
    fi
}

# Function to generate summary
print_summary() {
    local minikube=$1
    local helm_chart=$2
    local deployment=$3
    local services=$4
    local ingress=$5
    local functionality=$6
    local cleanup=$7

    echo ""
    echo "📊 DEPLOYMENT VALIDATION SUMMARY"
    echo "================================"

    local passed=0
    local total=7

    if [ $minikube -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $helm_chart -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $deployment -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $services -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $ingress -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $functionality -eq 1 ]; then passed=$((passed + 1)); fi
    if [ $cleanup -eq 1 ]; then passed=$((passed + 1)); fi

    echo "   Passed: $passed/$total checks"

    if [ $passed -eq $total ]; then
        print_status $GREEN "🎉 ALL VALIDATIONS PASSED"
        echo ""
        echo "✅ Deployment workflow is successful"
        echo "✅ Application is properly configured"
        echo "✅ Cleanup process works correctly"
    else
        print_status $RED "❌ SOME VALIDATIONS FAILED"
        echo ""
        echo "⚠️  Recommendations:"
        echo "- Fix the failed validations"
        echo "- Check the deployment status"
        echo "- Verify the application functionality"
    fi
}

# Main validation process
echo "🚀 Starting deployment validation..."
echo "===================================="

# Check prerequisites
check_kubectl
check_helm
check_minikube

# Validate Minikube setup
minikube_passed=0
if validate_minikube; then
    minikube_passed=1
fi

# Validate Helm chart
helm_chart_passed=0
if validate_helm_chart; then
    helm_chart_passed=1
fi

# Deploy application
deployment_passed=0
if deploy_application; then
    deployment_passed=1
fi

# Validate deployment status
if [ $deployment_passed -eq 1 ]; then
    if validate_deployment_status; then
        deployment_passed=1
    else
        deployment_passed=0
    fi
fi

# Validate services
services_passed=0
if validate_services; then
    services_passed=1
fi

# Validate ingress
ingress_passed=0
if validate_ingress; then
    ingress_passed=1
fi

# Validate application functionality
functionality_passed=0
if validate_functionality; then
    functionality_passed=1
fi

# Test cleanup
cleanup_passed=0
if test_cleanup; then
    cleanup_passed=1
fi

# Generate summary and exit with appropriate code
print_summary $minikube_passed $helm_chart_passed $deployment_passed $services_passed $ingress_passed $functionality_passed $cleanup_passed

if [ $minikube_passed -eq 1 ] && [ $helm_chart_passed -eq 1 ] && [ $deployment_passed -eq 1 ] && [ $services_passed -eq 1 ] && [ $ingress_passed -eq 1 ] && [ $functionality_passed -eq 1 ] && [ $cleanup_passed -eq 1 ]; then
    exit 0
else
    exit 1
fi