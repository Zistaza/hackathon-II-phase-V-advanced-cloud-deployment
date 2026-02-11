#!/bin/bash

# Docker AI Setup Script
# Configures Docker AI Agent (Gordon) for optimized containerization

set -e

echo "🤖 Setting up Docker AI Agent (Gordon) for containerization..."

# Check if Docker is installed
if ! command -v docker &&; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

# Check if Docker AI is available
if ! docker ai > /dev/null 2>&amp;1; then
    echo "❌ Docker AI is not available. Please ensure Docker Desktop is running with AI features enabled."
    exit 1
fi

# Configure Docker AI settings
echo "🔧 Configuring Docker AI settings..."
docker ai config set \
    --builder=gordon \
    --optimize=true \
    --security=true \
    --healthchecks=true

# Show current configuration
echo "📋 Current Docker AI configuration:"
docker ai config show

# Test Docker AI functionality
echo "🧪 Testing Docker AI functionality..."
docker ai --version
docker ai config validate

# Create Docker AI configuration directory
echo "📁 Creating Docker AI configuration directory..."
mkdir -p .docker-ai

# Create sample Docker AI configuration
echo "📝 Creating sample Docker AI configuration..."
cat > .docker-ai/config.yaml << 'EOF'
# Docker AI Configuration for Todo AI Chatbot

gordon:
  # Build optimization settings
  optimize:
    multi-stage: true
    non-root-user: true
    security-hardening: true
    health-checks: true

  # Image size optimization
  size:
    backend-target: 15MB
    frontend-target: 50MB

  # Security settings
  security:
    scan-images: true
    vulnerability-check: true
    non-root-enforcement: true

  # Health check settings
  health:
    interval: 30s
    timeout: 3s
    retries: 3
    start-period: 5s
EOF

# Validate configuration
echo "✅ Validating Docker AI configuration..."
docker ai config validate .docker-ai/config.yaml

# Create Docker AI aliases
echo "⚡ Creating Docker AI aliases..."
echo 'alias docker-ai-build="docker ai build --builder=gordon --optimize=true --security=true"' >> ~/.bashrc
echo 'alias docker-ai-show="docker ai show --all"' >> ~/.bashrc
echo 'alias docker-ai-config="docker ai config --edit"' >> ~/.bashrc

echo "✅ Docker AI Agent setup completed successfully!"
echo "📋 Available commands:"
echo "- docker-ai-build: Build with Gordon optimization"
echo "- docker-ai-show: Show Docker AI information"
echo "- docker-ai-config: Edit Docker AI configuration"
echo ""
echo "📁 Configuration saved to: .docker-ai/config.yaml"
echo "🤖 Ready to containerize applications with Docker AI!"