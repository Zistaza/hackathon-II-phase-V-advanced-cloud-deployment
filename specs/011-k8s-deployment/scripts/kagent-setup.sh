#!/bin/bash

# Kagent Setup Script
# Configures Kagent for cluster health monitoring and analysis

set -e

echo "🤖 Setting up Kagent for cluster health monitoring..."

# Check if kubectl is installed
if ! command -v kubectl &&; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if Kagent is available
if ! command -v kagent &&; then
    echo "❌ Kagent is not installed. Installing Kagent..."
    curl -L https://kagent.io/install | sh
fi

# Verify Kagent installation
echo "🧪 Verifying Kagent installation..."
kagent --version

# Configure Kagent settings
echo "🔧 Configuring Kagent settings..."
kagent config set \
    --provider=openai \
    --model=gpt-4 \
    --api-key=&quot;${OPENAI_API_KEY}&quot; \
    --cluster=minikube \
    --analysis-frequency=daily \
    --alert-thresholds=&quot;cpu:70,memory:80,disk:90&quot;

# Show current configuration
echo "📋 Current Kagent configuration:"
kagent config show

# Test Kagent functionality
echo "🧪 Testing Kagent functionality..."
kagent analyze cluster --health --dry-run

# Create Kagent configuration directory
echo "📁 Creating Kagent configuration directory..."
mkdir -p .kagent

# Create sample Kagent configuration
echo "📝 Creating sample Kagent configuration..."
cat > .kagent/config.yaml << 'EOF'
# Kagent Configuration for Todo AI Chatbot

provider:
  name: openai
  model: gpt-4
  api_key: &quot;${OPENAI_API_KEY}&quot;

cluster:
  name: minikube
  context: minikube
  namespace: default

analysis:
  frequency: daily
  dry_run: false
  verbose: true

thresholds:
  cpu: 70
  memory: 80
  disk: 90
  network: 1000

alerts:
  enabled: true
  email: admin@example.com
  slack: #k8s-alerts

resources:
  # Resource optimization settings
  backend:
    cpu_request: 100m
    cpu_limit: 500m
    memory_request: 256Mi
    memory_limit: 512Mi
    replicas: 2

  frontend:
    cpu_request: 50m
    cpu_limit: 200m
    memory_request: 128Mi
    memory_limit: 256Mi
    replicas: 1

health_checks:
  interval: 30s
  timeout: 3s
  retries: 3
  start_period: 5s
EOF

# Validate configuration
echo "✅ Validating Kagent configuration..."
kagent config validate .kagent/config.yaml

# Create Kagent aliases
echo "⚡ Creating Kagent aliases..."
echo 'alias kagent-analyze="kagent analyze --cluster"' >> ~/.bashrc
echo 'alias kagent-optimize="kagent optimize --resources"' >> ~/.bashrc
echo 'alias kagent-alerts="kagent alerts --status"' >> ~/.bashrc
echo 'alias kagent-health="kagent health --summary"' >> ~/.bashrc

echo "✅ Kagent setup completed successfully!"
echo "📋 Available commands:"
echo "- kagent-analyze: Analyze cluster health"
echo "- kagent-optimize: Optimize resources"
echo "- kagent-alerts: Check alerts status"
echo "- kagent-health: Get health summary"
echo ""
echo "📁 Configuration saved to: .kagent/config.yaml"
echo "🤖 Ready for cluster health monitoring!"