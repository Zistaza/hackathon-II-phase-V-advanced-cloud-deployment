# Quickstart Deployment Guide: Phase-V Infrastructure

**Feature**: 013-phasev-infra-deployment
**Date**: 2026-02-14
**Version**: 1.0.0

## Overview

This guide provides step-by-step instructions for deploying the Todo application to both local (Minikube) and cloud (Oracle Cloud Always Free) environments.

---

## Prerequisites

### Required Tools

```bash
# Verify tool versions
kubectl version --client
dapr version
helm version
minikube version
docker version
```

**Minimum Versions**:
- kubectl: 1.25+
- Dapr CLI: 1.12+
- Helm: 3.0+
- Minikube: 1.30+
- Docker: 20.10+

### Install Missing Tools

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

---

## Part A: Local Deployment (Minikube)

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker \
  --kubernetes-version=v1.28.0

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

### Step 2: Install Dapr on Minikube

```bash
# Initialize Dapr
dapr init --kubernetes --wait

# Verify Dapr installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
# dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m   2024-02-14 10:30:00
# dapr-sentry            dapr-system  True     Running  1         1.12.0   1m   2024-02-14 10:30:00
# dapr-operator          dapr-system  True     Running  1         1.12.0   1m   2024-02-14 10:30:00
# dapr-placement         dapr-system  True     Running  1         1.12.0   1m   2024-02-14 10:30:00
```

### Step 3: Deploy Redis (Local Pub/Sub)

```bash
# Add Bitnami Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Create namespace
kubectl create namespace todo-app

# Install Redis
helm install redis bitnami/redis \
  --namespace todo-app \
  --set auth.password=redis-password \
  --set master.persistence.enabled=false \
  --set replica.replicaCount=0

# Verify Redis is running
kubectl get pods -n todo-app -l app.kubernetes.io/name=redis
```

### Step 4: Create Secrets

```bash
# Create PostgreSQL secret (using Neon connection string)
kubectl create secret generic neon-secret \
  --from-literal=connectionString="postgresql://user:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require" \
  --namespace todo-app

# Create JWT secret
kubectl create secret generic jwt-secret \
  --from-literal=secret="your-jwt-secret-key-here" \
  --namespace todo-app

# Create Redis secret
kubectl create secret generic redis-secret \
  --from-literal=password="redis-password" \
  --namespace todo-app

# Verify secrets
kubectl get secrets -n todo-app
```

### Step 5: Deploy Dapr Components (Local)

```bash
# Apply Dapr components for local environment
kubectl apply -f k8s/local/dapr-components/

# Verify components
dapr components -k -n todo-app

# Expected output:
# NAME                 TYPE                 VERSION  SCOPES
# pubsub               pubsub.redis         v1       backend, event-processor, ...
# statestore           state.postgresql     v1       event-processor, reminder-scheduler
# reminder-cron        bindings.cron        v1       reminder-scheduler
# kubernetes-secrets   secretstores.kubernetes v1    backend, event-processor, ...
```

### Step 6: Deploy Application Services

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/base/

# Verify deployments
kubectl get deployments -n todo-app

# Expected output:
# NAME                   READY   UP-TO-DATE   AVAILABLE   AGE
# frontend               2/2     2            2           1m
# backend                2/2     2            2           1m
# event-processor        2/2     2            2           1m
# reminder-scheduler     1/1     1            1           1m
# notification-service   1/1     1            1           1m
# websocket-service      2/2     2            2           1m

# Verify Dapr sidecars are injected
kubectl get pods -n todo-app

# Each pod should have 2/2 containers (app + dapr sidecar)
```

### Step 7: Configure Ingress

```bash
# Apply local ingress configuration
kubectl apply -f k8s/local/ingress.yaml

# Get Minikube IP
minikube ip

# Add to /etc/hosts
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts

# Verify ingress
kubectl get ingress -n todo-app
```

### Step 8: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Check Dapr components
dapr components -k -n todo-app

# Test application
curl http://todo-app.local/api/health

# Expected output: {"status":"healthy"}

# Access application in browser
open http://todo-app.local
```

### Step 9: Deploy Monitoring Stack (Optional)

```bash
# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace todo-app \
  --set server.persistentVolume.enabled=false \
  --set alertmanager.enabled=false

# Install Grafana
helm install grafana grafana/grafana \
  --namespace todo-app \
  --set persistence.enabled=false \
  --set adminPassword=admin

# Get Grafana password
kubectl get secret --namespace todo-app grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward Grafana
kubectl port-forward -n todo-app svc/grafana 3000:80

# Access Grafana at http://localhost:3000
```

### Step 10: Test Event Flow

```bash
# Port forward backend service
kubectl port-forward -n todo-app svc/backend 8000:8000

# Create a test task (publishes task.created event)
curl -X POST http://localhost:8000/api/user_123/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Test task",
    "description": "Testing event flow",
    "priority": "high",
    "due_date": "2026-02-20T17:00:00Z",
    "reminder_time": "2026-02-20T09:00:00Z"
  }'

# Check event processor logs
kubectl logs -n todo-app -l app=event-processor -c event-processor --tail=50

# Check reminder scheduler logs
kubectl logs -n todo-app -l app=reminder-scheduler -c reminder-scheduler --tail=50

# Verify event was processed (check Dapr state store)
kubectl exec -n todo-app -it $(kubectl get pod -n todo-app -l app=event-processor -o jsonpath='{.items[0].metadata.name}') -c event-processor -- \
  curl http://localhost:3500/v1.0/state/statestore/event-processor:processed-event:EVENT_ID
```

---

## Part B: Cloud Deployment (Oracle Cloud Always Free)

### Prerequisites

- Oracle Cloud account (Always Free tier)
- OCI CLI installed and configured
- kubectl configured for Oracle Cloud

### Step 1: Provision Oracle Cloud Compute Instances

```bash
# Create 2 compute instances (Always Free tier)
# Instance 1: k3s server (2 OCPUs, 12GB RAM)
# Instance 2: k3s agent (2 OCPUs, 12GB RAM)

# Via OCI Console:
# 1. Navigate to Compute > Instances
# 2. Create Instance
# 3. Select "Always Free Eligible" shape (VM.Standard.E2.1.Micro or VM.Standard.A1.Flex)
# 4. Choose Ubuntu 22.04 image
# 5. Configure networking (allow ports 22, 80, 443, 6443)
# 6. Add SSH key
# 7. Create instance
# 8. Repeat for second instance
```

### Step 2: Install k3s on Oracle Cloud

```bash
# SSH into first instance (k3s server)
ssh ubuntu@<instance-1-public-ip>

# Install k3s server
curl -sfL https://get.k3s.io | sh -s - server \
  --write-kubeconfig-mode 644 \
  --disable traefik \
  --node-external-ip <instance-1-public-ip>

# Get k3s token for agent
sudo cat /var/lib/rancher/k3s/server/node-token

# SSH into second instance (k3s agent)
ssh ubuntu@<instance-2-public-ip>

# Install k3s agent
curl -sfL https://get.k3s.io | K3S_URL=https://<instance-1-private-ip>:6443 \
  K3S_TOKEN=<token-from-server> sh -

# Back on server, verify nodes
kubectl get nodes

# Expected output:
# NAME        STATUS   ROLES                  AGE   VERSION
# instance-1  Ready    control-plane,master   2m    v1.28.5+k3s1
# instance-2  Ready    <none>                 1m    v1.28.5+k3s1
```

### Step 3: Copy kubeconfig to Local Machine

```bash
# On k3s server
sudo cat /etc/rancher/k3s/k3s.yaml

# On local machine
mkdir -p ~/.kube
# Copy k3s.yaml content to ~/.kube/config
# Replace 127.0.0.1 with <instance-1-public-ip>

# Verify connection
kubectl get nodes
```

### Step 4: Install Dapr on Oracle Cloud Cluster

```bash
# Initialize Dapr
dapr init --kubernetes --wait

# Verify Dapr installation
dapr status -k
```

### Step 5: Install Traefik Ingress Controller

```bash
# Install Traefik
helm repo add traefik https://traefik.github.io/charts
helm repo update

helm install traefik traefik/traefik \
  --namespace kube-system \
  --set ports.web.exposedPort=80 \
  --set ports.websecure.exposedPort=443

# Verify Traefik is running
kubectl get pods -n kube-system -l app.kubernetes.io/name=traefik
```

### Step 6: Configure External Pub/Sub (Redpanda Cloud)

```bash
# Sign up for Redpanda Cloud free tier
# https://redpanda.com/try-redpanda

# Create cluster and get connection details
# - Bootstrap servers: seed-12345.redpanda.cloud:9092
# - SASL username: your-username
# - SASL password: your-password

# Create Kubernetes secret
kubectl create secret generic redpanda-secret \
  --from-literal=username="your-username" \
  --from-literal=password="your-password" \
  --namespace todo-app
```

### Step 7: Create Cloud Secrets

```bash
# Create namespace
kubectl create namespace todo-app

# Create Neon PostgreSQL secret
kubectl create secret generic neon-secret \
  --from-literal=connectionString="postgresql://user:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require" \
  --namespace todo-app

# Create JWT secret
kubectl create secret generic jwt-secret \
  --from-literal=secret="your-jwt-secret-key-here" \
  --namespace todo-app

# Verify secrets
kubectl get secrets -n todo-app
```

### Step 8: Deploy Dapr Components (Cloud)

```bash
# Apply Dapr components for cloud environment
kubectl apply -f k8s/cloud/dapr-components/

# Verify components
dapr components -k -n todo-app

# Expected output should show Kafka (Redpanda) instead of Redis
```

### Step 9: Deploy Application Services

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/base/

# Verify deployments
kubectl get deployments -n todo-app
kubectl get pods -n todo-app

# Monitor pod startup
kubectl get pods -n todo-app -w
```

### Step 10: Configure DNS and SSL/TLS

```bash
# Get Traefik LoadBalancer IP
kubectl get svc -n kube-system traefik

# Configure DNS A record
# Point todo-app.example.com to LoadBalancer IP

# Install cert-manager for Let's Encrypt
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: traefik
EOF

# Apply cloud ingress with TLS
kubectl apply -f k8s/cloud/ingress.yaml

# Verify certificate is issued
kubectl get certificate -n todo-app
```

### Step 11: Verify Cloud Deployment

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Check resource usage
kubectl top nodes
kubectl top pods -n todo-app

# Test application
curl https://todo-app.example.com/api/health

# Access application in browser
open https://todo-app.example.com
```

### Step 12: Deploy Monitoring Stack

```bash
# Install Prometheus with resource limits
helm install prometheus prometheus-community/prometheus \
  --namespace todo-app \
  --set server.persistentVolume.enabled=false \
  --set server.resources.requests.cpu=100m \
  --set server.resources.requests.memory=256Mi \
  --set server.resources.limits.cpu=200m \
  --set server.resources.limits.memory=512Mi \
  --set alertmanager.enabled=false

# Install Grafana with resource limits
helm install grafana grafana/grafana \
  --namespace todo-app \
  --set persistence.enabled=false \
  --set resources.requests.cpu=50m \
  --set resources.requests.memory=128Mi \
  --set resources.limits.cpu=100m \
  --set resources.limits.memory=256Mi \
  --set adminPassword=admin

# Configure Grafana dashboards
# Import dashboards from monitoring/grafana/dashboards/
```

---

## Troubleshooting

### Issue: Minikube fails to start

```bash
# Check if Docker is running
docker ps

# Check available resources
free -h
df -h

# Delete and recreate Minikube cluster
minikube delete
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Use different driver if Docker fails
minikube start --driver=kvm2  # On Linux with KVM
minikube start --driver=virtualbox  # With VirtualBox
```

### Issue: Pods stuck in Pending state

```bash
# Check pod events
kubectl describe pod <pod-name> -n todo-app

# Common causes:
# 1. Insufficient resources
kubectl top nodes
kubectl get resourcequota -n todo-app

# 2. Image pull errors
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# 3. Dapr sidecar injection issues
kubectl logs <pod-name> -n todo-app -c daprd

# 4. Check if namespace exists
kubectl get namespace todo-app

# Fix: Delete and redeploy
kubectl delete pod <pod-name> -n todo-app
kubectl rollout restart deployment/<deployment-name> -n todo-app
```

### Issue: Dapr sidecar not injecting

```bash
# Verify Dapr is installed
dapr status -k

# Check pod annotations
kubectl get pod <pod-name> -n todo-app -o yaml | grep dapr.io

# Verify namespace has Dapr enabled
kubectl get namespace todo-app -o yaml | grep dapr

# Check Dapr sidecar injector logs
kubectl logs -n dapr-system -l app=dapr-sidecar-injector --tail=50

# Restart deployment
kubectl rollout restart deployment/<deployment-name> -n todo-app

# Reinstall Dapr if needed
dapr uninstall -k
dapr init -k --wait
```

### Issue: Redis not connecting

```bash
# Check Redis pod status
kubectl get pods -n todo-app -l app.kubernetes.io/name=redis

# Check Redis logs
kubectl logs -n todo-app redis-0

# Test Redis connection
kubectl exec -n todo-app redis-0 -- redis-cli ping

# Verify Redis secret
kubectl get secret redis-secret -n todo-app -o jsonpath='{.data.password}' | base64 -d

# Restart Redis
helm upgrade redis bitnami/redis --namespace todo-app --reuse-values
```

### Issue: Events not flowing through Pub/Sub

```bash
# Check Dapr Pub/Sub component
kubectl get component pubsub -n todo-app -o yaml

# For local (Redis):
kubectl logs <backend-pod> -n todo-app -c daprd | grep pubsub

# For cloud (Redpanda):
kubectl logs <backend-pod> -n todo-app -c daprd | grep kafka

# Check Dapr subscriptions
kubectl get subscriptions -n todo-app

# Test event publishing
kubectl exec -n todo-app -it <backend-pod> -c backend -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_id":"test-123","event_type":"task.created","user_id":"user_123","timestamp":"2026-02-14T10:30:00Z","payload":{"task_id":"task-456","title":"Test","priority":"high"}}'

# Check event processor logs
kubectl logs -n todo-app -l app=event-processor --tail=50
```

### Issue: Ingress not accessible

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl get ingress -n todo-app

# Verify /etc/hosts entry
grep todo-app.local /etc/hosts

# Get Minikube IP
minikube ip

# Add to /etc/hosts if missing
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts

# Test with curl
curl -v http://todo-app.local/api/health

# Check ingress logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx --tail=50
```

### Issue: Database connection failures

```bash
# Check secrets
kubectl get secret neon-secret -n todo-app -o jsonpath='{.data.connectionString}' | base64 -d

# Test database connection
kubectl exec -n todo-app -it <backend-pod> -c backend -- \
  psql "$CONNECTION_STRING" -c "SELECT 1"

# Verify PostgreSQL component
kubectl get component statestore -n todo-app -o yaml

# Check Dapr state store logs
kubectl logs <backend-pod> -n todo-app -c daprd | grep state
```

### Issue: High resource usage

```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n todo-app

# Identify resource-intensive pods
kubectl describe pod <pod-name> -n todo-app | grep -A 5 "Limits"

# Adjust resource limits
kubectl edit deployment <deployment-name> -n todo-app

# Scale down replicas if needed
kubectl scale deployment <deployment-name> --replicas=1 -n todo-app

# For Minikube, increase resources
minikube stop
minikube start --cpus=6 --memory=16384
```

### Issue: SSL certificate not issued (Cloud)

```bash
# Check certificate status
kubectl describe certificate todo-app-tls -n todo-app

# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager

# Verify DNS is pointing to correct IP
nslookup todo-app.example.com
dig todo-app.example.com

# Check ClusterIssuer
kubectl get clusterissuer letsencrypt-prod -o yaml

# Manually trigger certificate issuance
kubectl delete certificate todo-app-tls -n todo-app
kubectl apply -f k8s/cloud/ingress.yaml

# Check Traefik logs
kubectl logs -n kube-system -l app.kubernetes.io/name=traefik --tail=50
```

### Issue: Deployment script failures

```bash
# Run scripts with debugging
bash -x ./scripts/setup-minikube.sh
bash -x ./scripts/deploy-local.sh
bash -x ./scripts/validate-deployment.sh

# Check script prerequisites
./scripts/setup-minikube.sh --help

# Verify kubectl context
kubectl config current-context
kubectl cluster-info

# Check for running processes
ps aux | grep minikube
ps aux | grep docker
```

### Issue: Health endpoint not responding

```bash
# Check backend pod status
kubectl get pods -n todo-app -l app=phase-v-backend

# Check backend logs
kubectl logs -n todo-app -l app=phase-v-backend --tail=100

# Port forward and test directly
kubectl port-forward -n todo-app svc/backend 8000:8000 &
curl http://localhost:8000/api/health

# Check if backend is listening
kubectl exec -n todo-app -it <backend-pod> -c backend -- netstat -tlnp

# Verify environment variables
kubectl exec -n todo-app -it <backend-pod> -c backend -- env | grep -E "DATABASE|REDIS|JWT"
```

### Issue: WebSocket connection failures

```bash
# Check websocket service
kubectl get svc phase-v-websocket-service -n todo-app

# Check websocket pod logs
kubectl logs -n todo-app -l app=phase-v-websocket-service --tail=50

# Test WebSocket connection
wscat -c ws://todo-app.local/ws/test-user

# Check ingress WebSocket configuration
kubectl get ingress todo-app-ingress -n todo-app -o yaml
```

---

## Validation Checklist

### Local Deployment (Minikube)

- [ ] Minikube cluster running with sufficient resources
- [ ] Dapr installed and all components healthy
- [ ] Redis running for Pub/Sub
- [ ] All 6 application pods running (2/2 containers each)
- [ ] Ingress accessible at http://todo-app.local
- [ ] Task creation publishes events successfully
- [ ] Event processor consumes events
- [ ] Reminder scheduler schedules reminders
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards displaying data

### Cloud Deployment (Oracle Cloud)

- [ ] k3s cluster running on 2 compute instances
- [ ] Dapr installed and all components healthy
- [ ] Redpanda Cloud connected for Pub/Sub
- [ ] All 6 application pods running within resource limits
- [ ] Ingress accessible at https://todo-app.example.com
- [ ] SSL certificate issued and valid
- [ ] Task creation publishes events to Redpanda
- [ ] Event processor consumes events
- [ ] Reminder scheduler schedules reminders
- [ ] Resource usage within Always Free limits (2 OCPU, 12GB RAM)
- [ ] Prometheus and Grafana running with resource limits
- [ ] No pods in CrashLoopBackOff or Pending state

---

## Cleanup

### Local Cleanup (Minikube)

```bash
# Delete application
kubectl delete namespace todo-app

# Delete Dapr
dapr uninstall --kubernetes

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

### Cloud Cleanup (Oracle Cloud)

```bash
# Delete application
kubectl delete namespace todo-app

# Delete Dapr
dapr uninstall --kubernetes

# Delete cert-manager
kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Terminate compute instances via OCI Console
```

---

## Next Steps

1. ✅ Local deployment complete → Test all features
2. ✅ Cloud deployment complete → Configure CI/CD pipeline
3. ⏭️ Run `/sp.tasks` to generate implementation tasks
4. ⏭️ Begin implementation with Phase 2.1 (Event-Driven Architecture)

**Deployment Time**:
- Local (Minikube): ~15 minutes
- Cloud (Oracle): ~30 minutes

**Status**: Quickstart guide complete and ready for deployment
