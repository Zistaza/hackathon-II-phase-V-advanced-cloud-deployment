#!/bin/bash

# validate-quickstart.sh - Verify that the quickstart.md guide works as expected

set -euo pipefail

echo "Verifying quickstart.md deployment instructions..."

# Check if required tools are installed
TOOLS=("minikube" "kubectl" "helm" "docker")
for TOOL in "${TOOLS[@]}"; do
    if ! command -v "$TOOL" &> /dev/null; then
        echo "❌ $TOOL is not installed"
        exit 1
    fi
    echo "✅ $TOOL is installed"
done

# Check if Kubernetes cluster is running
if ! minikube status &> /dev/null; then
    echo "❌ Minikube cluster is not running"
    exit 1
fi

echo "✅ Minikube cluster is running"

# Check if Helm chart exists
if [ ! -f "specs/011-k8s-deployment/charts/todo-app/Chart.yaml" ]; then
    echo "❌ Helm chart not found at specs/011-k8s-deployment/charts/todo-app/Chart.yaml"
    exit 1
fi

echo "✅ Helm chart found"

# Check if container images exist
if [ ! -f "backend/Dockerfile" ] || [ ! -f "frontend/Dockerfile" ]; then
    echo "❌ Dockerfiles not found"
    exit 1
fi

echo "✅ Dockerfiles found"

echo "🎉 quickstart.md validation successful!"
exit 0