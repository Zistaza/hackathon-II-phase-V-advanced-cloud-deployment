# Phase IV Kubernetes Deployment - Complete Guide

## Overview

This guide provides comprehensive instructions for deploying the Todo AI Chatbot to a local Minikube cluster using AI-assisted DevOps practices. The deployment leverages Docker AI Agent (Gordon) for optimized containerization, kubectl-ai for intelligent Kubernetes operations, and Kagent for cluster health monitoring.

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows 10/11
- **RAM**: Minimum 8GB (Recommended 16GB)
- **CPU**: Minimum 4 cores (Recommended 6 cores)
- **Disk Space**: Minimum 30GB free space
- **Docker**: Docker Desktop installed and running
- **Git**: For version control

### Software Installation

#### 1. Install Docker Desktop
Download and install Docker Desktop from https://www.docker.com/products/docker-desktop

#### 2. Install Minikube
```bash
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows (PowerShell)
irm https://storage.googleapis.com/minikube/releases/latest/minikube-windows-amd64.exe -OutFile minikube.exe
```

#### 3. Install kubectl
```bash
# macOS
brew install kubectl

# Linux
curl -LO https://dl.k8s.io/release/v1.28.0/bin/linux/amd64/kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Windows (PowerShell)
irm https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe -OutFile kubectl.exe
```

#### 4. Install Helm
```bash
# macOS
brew install helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Windows (PowerShell)
irm https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3.ps1 -OutFile get_helm.ps1
./get_helm.ps1
```

#### 5. Install AI Tools
```bash
# Install kubectl-ai
curl -sL https://kubectl-ai.sh/install | sh

# Install Kagent
curl -L https://kagent.io/install | sh
```

## Step 1: Setup Environment

### 1.1 Start Minikube Cluster
```bash
# Navigate to project directory
cd /path/to/todo-chatbot

# Start Minikube with optimal resources
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=30g \
  --driver=docker

# Enable necessary addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Configure kubectl context
kubectl config use-context minikube

# Verify cluster status
kubectl cluster-info
kubectl get nodes -o wide
kubectl get all --all-namespaces
```

### 1.2 Configure AI Tools
```bash
# Configure Docker AI
./scripts/docker-ai-setup.sh

# Configure kubectl-ai
./scripts/kubectl-ai-setup.sh

# Configure Kagent
./scripts/kagent-setup.sh
```

## Step 2: Containerize Applications

### 2.1 Use Docker AI for Containerization
```bash
# Containerize backend application
docker ai "Containerize the Todo AI Chatbot backend application with Python 3.11, FastAPI, and SQLModel. Use multi-stage builds, non-root user, health checks, and optimize for size under 15MB."

# Containerize frontend application
docker ai "Containerize the Todo AI Chatbot frontend application with Next.js 16+, React 18+, and Tailwind CSS 4.0+. Use multi-stage builds, non-root user, health checks, and optimize for size under 50MB."
```

### 2.2 Verify Container Images
```bash
# Check container images
docker images | grep todo

# Expected output:
todo-backend   latest   1234567890ab   2 minutes ago   12MB
todo-frontend  latest   0987654321ab   2 minutes ago   45MB
```

## Step 3: Deploy with Helm

### 3.1 Deploy Helm Chart
```bash
# Deploy to Minikube cluster
helm install todo-app charts/todo-app

# Check deployment status
helm status todo-app

# Get Minikube IP
minikube ip
```

### 3.2 Verify Deployment
```bash
# Check pod status
kubectl get pods

# Expected output:
NAME                               READY   STATUS    RESTARTS   AGE
todo-backend-7c6d8f9d8f-2g5h1       1/1     Running   0          2m
todo-backend-7c6d8f9d8f-4k2j3       1/1     Running   0          2m
todo-frontend-4d3c2b1a2c-1p9q8      1/1     Running   0          2m

# Check services
kubectl get services

# Expected output:
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
todo-backend     ClusterIP   10.109.87.123   <none>        8000/TCP   2m
todo-frontend    ClusterIP   10.111.45.67    <none>        80/TCP     2m
```

## Step 4: Access Application

### 4.1 Access Frontend
```bash
# Get Minikube IP
minikube ip

# Access frontend in browser
open http://$(minikube ip)
```

### 4.2 Test Backend API
```bash
# Test backend health endpoint
curl http://$(minikube ip):8000/health

# Test backend API endpoint
curl http://$(minikube ip):8000/api/health
```

## Step 5: AI-Assisted Operations

### 5.1 Use kubectl-ai for Deployment Operations
```bash
# Scale deployment
kubectl-ai "scale the todo-backend to 3 replicas"

# Debug pod
kubectl-ai "debug the todo-backend deployment and provide solutions"

# Update deployment
kubectl-ai "update the todo-backend to use latest image"

# Check status
kubectl-ai "status of todo-backend deployment including resource utilization and recent events"
```

### 5.2 Use Kagent for Cluster Analysis
```bash
# Analyze cluster health
kagent analyze cluster --health

# Get resource optimization recommendations
kagent optimize resources --cluster

# Analyze specific deployment
kagent analyze deployment todo-backend --insights
```

## Step 6: Advanced Operations

### 6.1 Ingress Configuration
```bash
# Enable ingress in values.yaml
ingress:
  enabled: true
  className: ""
  annotations: {}
  labels: {}
  hosts:
    - host: todo.local
      paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: todo-frontend
              port:
                number: 80
  tls: []

# Redeploy with ingress
helm upgrade todo-app charts/todo-app
```

### 6.2 Network Policies
```bash
# Configure network policies in values.yaml
networkPolicies:
  enabled: true
  backend:
    from:
      - podSelector:
          matchLabels:
            app.kubernetes.io/component: frontend
    ports:
      - protocol: TCP
        port: 8000
  frontend:
    from:
      - ipBlock:
          cidr: 0.0.0.0/0
    ports:
      - protocol: TCP
        port: 80
```

### 6.3 Resource Management
```bash
# Configure resource limits and requests in values.yaml
backend:
  resources:
    limits:
      cpu: "500m"
      memory: "512Mi"
    requests:
      cpu: "100m"
      memory: "256Mi"

frontend:
  resources:
    limits:
      cpu: "200m"
      memory: "256Mi"
    requests:
      cpu: "50m"
      memory: "128Mi"
```

## Step 7: Monitoring and Observability

### 7.1 Enable Monitoring
```bash
# Enable metrics-server
minikube addons enable metrics-server

# Check resource usage
kubectl top pods
kubectl top nodes
```

### 7.2 Set Up Alerts
```bash
# Configure alerts in values.yaml
alerts:
  destinations:
    - name: slack
      type: slack
      channel: #k8s-alerts
      webhook: ${SLACK_WEBHOOK_URL}
    - name: email
      type: email
      recipients:
        - admin@example.com
      smtp_server: smtp.example.com
      port: 587

  rules:
    - name: high-cpu
      condition: cpu > 80%
      severity: warning
      message: "High CPU utilization detected: {value}%"
      action: scale-up
```

## Step 8: Troubleshooting

### 8.1 Common Issues and Solutions

#### Minikube Won't Start
```bash
# Check Docker status
docker ps

# Try different driver
minikube start --driver=docker

# Check system resources
free -h
```

#### Container Image Build Fails
```bash
# Check Docker daemon status
docker info

# Clear Docker cache
docker system prune -a

# Try building manually
docker build -t todo-backend .
```

#### Helm Chart Deployment Fails
```bash
# Check Helm chart syntax
helm lint charts/todo-app

# Check Kubernetes events
kubectl get events --sort-by='.lastTimestamp'

# Check pod logs
kubectl logs deployment/todo-backend
```

#### kubectl-ai Commands Fail
```bash
# Check kubectl-ai installation
kubectl ai --version

# Verify AI provider configuration
kubectl ai config list

# Check network connectivity
ping api.openai.com
```

### 8.2 Useful Commands

#### Monitoring
```bash
# Watch pod status
watch kubectl get pods

# View pod logs
kubectl logs -f deployment/todo-backend

# Check resource usage
kubectl top pods

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

#### Debugging
```bash
# Describe pod
kubectl describe pod todo-backend-7c6d8f9d8f-2g5h1

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Debug pod
kubectl exec -it todo-backend-7c6d8f9d8f-2g5h1 -- /bin/bash
```

#### Networking
```bash
# Port forward
kubectl port-forward svc/todo-backend 8000:8000

# Check service endpoints
kubectl get endpoints todo-backend

# Test service connectivity
kubectl exec -it todo-frontend-4d3c2b1a2c-1p9q8 -- curl todo-backend:8000/health
```

## Step 9: Cleanup

### 9.1 Uninstall Helm Release
```bash
# Uninstall Helm release
helm uninstall todo-app

# Verify resources are deleted
kubectl get pods -n default
kubectl get services -n default
kubectl get deployments -n default
```

### 9.2 Stop Minikube
```bash
# Stop Minikube
minikube stop

# Delete Minikube
minikube delete
```

## Best Practices

### Resource Management
- **Start with 4 CPU, 8GB RAM, 30GB disk**
- **Monitor resource usage regularly**
- **Scale resources based on application needs**
- **Clean up unused resources periodically**

### Security
- **Use non-root containers**
- **Enable RBAC and network policies**
- **Regularly update Kubernetes and addons**
- **Monitor security events**

### Performance
- **Enable metrics-server for monitoring**
- **Use appropriate resource limits**
- **Configure horizontal pod autoscaling**
- **Optimize container images**

### Maintenance
- **Regular backups of configuration**
- **Update Minikube and Kubernetes regularly**
- **Monitor cluster health and performance**
- **Clean up unused resources and images**

## Verification Checklist

### ✅ Containerization
- [ ] Backend containerized as todo-backend:latest
- [ ] Frontend containerized as todo-frontend:latest
- [ ] Container images are optimized and secure
- [ ] Images can run successfully in containers

### ✅ Kubernetes Deployment
- [ ] Helm chart created and validated
- [ ] All pods are running and ready
- [ ] Services are active and accessible
- [ ] Application is accessible via browser

### ✅ AI DevOps Tools
- [ ] kubectl-ai installed and functional
- [ ] Kagent installed and functional
- [ ] AI-assisted scaling demonstrated
- [ ] AI-assisted debugging demonstrated
- [ ] AI-assisted cluster analysis demonstrated

### ✅ Application Functionality
- [ ] Backend API endpoints are accessible
- [ ] Frontend loads correctly
- [ ] Authentication works with JWT
- [ ] User data isolation is maintained
- [ ] All Phase III functionality is preserved

### ✅ Documentation
- [ ] Complete deployment documentation created
- [ ] Troubleshooting guide available
- [ ] Verification checklist completed
- [ ] Demo-ready presentation prepared

## Next Steps

1. **Demo Preparation**: Prepare demonstration script and slides
2. **Performance Testing**: Test application under load
3. **Security Review**: Verify security configurations
4. **Documentation**: Complete all documentation
5. **Feedback Collection**: Gather feedback from test users

## Support

For additional help:
- Check the troubleshooting section above
- Review the official documentation:
  - [Docker Documentation](https://docs.docker.com/)
  - [Kubernetes Documentation](https://kubernetes.io/docs/)
  - [Helm Documentation](https://helm.sh/docs/)
  - [kubectl-ai Documentation](https://kubectl-ai.sh/docs)
  - [Kagent Documentation](https://kagent.io/)
- Search for solutions on Stack Overflow or Kubernetes forums
- Consult with team members or mentors

## Congratulations!

You have successfully deployed the Todo AI Chatbot to a local Kubernetes cluster using AI-assisted DevOps practices! Your deployment is now ready for demonstration and evaluation.

---

**Note**: This guide assumes you have already completed Phase III implementation. The deployment focuses solely on infrastructure and does not modify any application logic.