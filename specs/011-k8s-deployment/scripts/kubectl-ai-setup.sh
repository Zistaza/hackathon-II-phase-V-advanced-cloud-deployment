#!/bin/bash

# kubectl-ai Setup Script
# Configures kubectl-ai for AI-assisted Kubernetes operations

set -e

echo "🤖 Setting up kubectl-ai for AI-assisted Kubernetes operations..."

# Check if kubectl is installed
if ! command -v kubectl &&; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if kubectl-ai is available
if ! command -v kubectl-ai &&; then
    echo "❌ kubectl-ai is not installed. Installing kubectl-ai..."
    curl -sL https://kubectl-ai.sh/install | sh
fi

# Verify kubectl-ai installation
echo "🧪 Verifying kubectl-ai installation..."
kubectl-ai --version

# Configure kubectl-ai settings
echo "🔧 Configuring kubectl-ai settings..."
kubectl-ai config set \
    --provider=openai \
    --model=gpt-4 \
    --api-key=&quot;${OPENAI_API_KEY}&quot; \
    --context=minikube \
    --auto-approve=false

# Show current configuration
echo "📋 Current kubectl-ai configuration:"
kubectl-ai config show

# Test kubectl-ai functionality
echo "🧪 Testing kubectl-ai functionality..."
kubectl-ai &quot;help&quot;

# Create kubectl-ai configuration directory
echo "📁 Creating kubectl-ai configuration directory..."
mkdir -p .kubectl-ai

# Create sample kubectl-ai configuration
echo "📝 Creating sample kubectl-ai configuration..."
cat > .kubectl-ai/config.yaml << 'EOF'
# kubectl-ai Configuration for Todo AI Chatbot

provider:
  name: openai
  model: gpt-4
  api_key: &quot;${OPENAI_API_KEY}&quot;

context:
  name: minikube
  cluster: minikube
  namespace: default

auto_approve: false

commands:
  # Custom AI commands for Todo AI Chatbot
  deploy:
    description: Deploy application using AI assistance
    template: &quot;deploy the {resource} using helm chart {chart}&quot;

  scale:
    description: Scale deployment using AI assistance
    template: &quot;scale the {resource} to {replicas} replicas&quot;

  debug:
    description: Debug Kubernetes resources using AI assistance
    template: &quot;debug the {resource} and provide solutions&quot;
EOF

# Validate configuration
echo "✅ Validating kubectl-ai configuration..."
kubectl-ai config validate .kubectl-ai/config.yaml

# Create kubectl-ai aliases
echo "⚡ Creating kubectl-ai aliases..."
echo 'alias k-ai="kubectl-ai"' >> ~/.bashrc
echo 'alias k-ai-deploy="kubectl-ai &quot;deploy&quot;"' >> ~/.bashrc
echo 'alias k-ai-scale="kubectl-ai &quot;scale&quot;"' >> ~/.bashrc
echo 'alias k-ai-debug="kubectl-ai &quot;debug&quot;"' >> ~/.bashrc

echo "✅ kubectl-ai setup completed successfully!"
echo "📋 Available commands:"
echo "- kubectl-ai: Main kubectl-ai command"
echo "- k-ai-deploy: Deploy using AI assistance"
echo "- k-ai-scale: Scale using AI assistance"
echo "- k-ai-debug: Debug using AI assistance"
echo ""
echo "📁 Configuration saved to: .kubectl-ai/config.yaml"
echo "🤖 Ready for AI-assisted Kubernetes operations!"