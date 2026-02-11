# Kubernetes Deployment Scripts

## Setup Scripts

### Minikube Setup
```bash
minikube-start.sh```
- Starts Minikube cluster with optimal resources
- Enables necessary addons (ingress, metrics-server)
- Configures kubectl context

### Docker AI Setup
```bash
docker-ai-setup.sh```
- Configures Docker AI Agent (Gordon)
- Sets up Docker AI environment variables
- Validates Docker AI installation

### kubectl-ai Setup
```bash
kubectl-ai-setup.sh```
- Installs and configures kubectl-ai
- Sets up AI provider configuration
- Validates kubectl-ai installation

### Kagent Setup
```bash
kagent-setup.sh```
- Installs and configures Kagent
- Sets up Kagent analysis tools
- Validates Kagent installation

## Deployment Scripts

### Containerization
```bash
containerize-backend.sh```
- Uses Docker AI to containerize backend application
- Generates optimized Dockerfile
- Builds and tags container image

```bash
containerize-frontend.sh```
- Uses Docker AI to containerize frontend application
- Generates optimized Dockerfile
- Builds and tags container image

### Helm Deployment
```bash
deploy-helm.sh```
- Installs Helm chart using kubectl-ai
- Validates deployment status
- Monitors rollout progress

```bash
validate-deployment.sh```
- Validates deployment health and functionality
- Checks pod status and readiness
- Verifies service accessibility

## Management Scripts

### Cluster Management
```bash
cluster-status.sh```
- Shows cluster resource utilization
- Displays pod and service status
- Provides health insights

```bash
cluster-logs.sh```
- Collects logs from all pods
- Aggregates logs for analysis
- Provides log filtering capabilities

### Cleanup
```bash
cleanup.sh```
- Removes Helm releases
- Deletes pods and services
- Cleans up temporary files

## AI Operations Scripts

### kubectl-ai Integration
```bash
ai-scale.sh```
- Uses kubectl-ai for intelligent scaling
- Provides scaling recommendations
- Validates scaling operations

```bash
ai-debug.sh```
- Uses kubectl-ai for debugging
- Identifies issues and provides solutions
- Automates troubleshooting

### Kagent Analysis
```bash
kagent-analysis.sh```
- Runs Kagent cluster analysis
- Provides health insights and recommendations
- Generates optimization reports

## Configuration Files

### Environment Configuration
```bash
config/minikube-config.yaml```
- Minikube cluster configuration
- Resource allocation settings
- Addon enablement

```bash
config/docker-ai-config.yaml```
- Docker AI Agent configuration
- Build optimization settings
- Security configurations

```bash
config/kubectl-ai-config.yaml```
- kubectl-ai configuration
- AI provider settings
- Command customization

## Usage Examples

### Complete Deployment Workflow
```bash
# Setup environment
./scripts/setup.sh

# Containerize applications
./scripts/containerize-backend.sh
./scripts/containerize-frontend.sh

# Deploy to cluster
./scripts/deploy-helm.sh

# Validate deployment
./scripts/validate-deployment.sh

# Monitor and manage
./scripts/cluster-status.sh
./scripts/ai-scale.sh
./scripts/kagent-analysis.sh
```

### Individual Operations
```bash
# Start Minikube
./scripts/minikube-start.sh

# Build backend container
./scripts/containerize-backend.sh

# Scale deployment
./scripts/ai-scale.sh

# Analyze cluster
./scripts/kagent-analysis.sh
```

## Dependencies

- Docker Desktop
- Minikube
- kubectl
- Helm 3
- Docker AI Agent (Gordon)
- kubectl-ai
- Kagent

## Requirements

- Node.js 18+ for frontend
- Python 3.11+ for backend
- Git for version control
- Internet connection for AI operations

## Security Considerations

- All containers run as non-root users
- Image scanning and vulnerability management
- RBAC and network policies configured
- Secrets management through environment variables