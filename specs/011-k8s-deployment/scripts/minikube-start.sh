#!/bin/bash

# Minikube Setup Script
# Sets up Minikube cluster with optimal resources for Todo AI Chatbot deployment

set -e

echo "🚀 Setting up Minikube cluster for Todo AI Chatbot deployment..."

# Check if Minikube is installed
if ! command -v minikube &&; then
    echo "❌ Minikube is not installed. Please install Minikube first."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&amp;1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Stop existing Minikube if running
echo "📦 Stopping any existing Minikube cluster..."
minikube stop 2> /dev/null || true

# Start Minikube with optimal resources
echo "🚀 Starting Minikube with optimal resources..."
minikube start \
    --cpus=4 \
    --memory=8192 \
    --disk-size=30g \
    --driver=docker \
    --kubernetes-version=v1.28.0

# Enable necessary addons
echo "🔧 Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Configure kubectl context
echo "🔍 Configuring kubectl context..."
kubectl config use-context minikube

# Verify cluster status
echo "🔍 Verifying cluster status..."
kubectl cluster-info
kubectl get nodes -o wide
kubectl get all --all-namespaces

# Show Minikube IP
echo "🌐 Minikube IP: $(minikube ip)"

# Show dashboard URL
echo "📊 Dashboard URL: $(minikube dashboard --url)"

echo "✅ Minikube cluster setup completed successfully!"
echo "📋 Next steps:"
echo "1. Containerize your applications using Docker AI"
echo "2. Deploy using Helm charts"
echo "3. Access your application at http://$(minikube ip)"