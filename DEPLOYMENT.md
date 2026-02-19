# Phase-V Deployment Guide

Comprehensive deployment instructions for Phase-V application.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Deployment (Minikube)](#local-deployment-minikube)
- [Cloud Deployment (Oracle Cloud)](#cloud-deployment-oracle-cloud)
- [Post-Deployment](#post-deployment)
- [Verification](#verification)
- [Rollback](#rollback)

---

## Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 20.10+ | Container runtime |
| kubectl | 1.25+ | Kubernetes CLI |
| Helm | 3.0+ | Package manager |
| Minikube | 1.30+ | Local Kubernetes |
| Dapr CLI | 1.12+ | Dapr management |

### Installation Commands

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

---

## Local Deployment (Minikube)

### Step 1: Start Minikube

```bash
./scripts/setup-minikube.sh
```

**Manual alternative:**
```bash
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker \
  --kubernetes-version=v1.28.0
```

### Step 2: Install Dapr

```bash
./scripts/setup-dapr.sh
```

**Verify Dapr:**
```bash
dapr status -k
# All components should show "Running"
```

### Step 3: Deploy Redis

```bash
./scripts/deploy-redis.sh
```

**Verify Redis:**
```bash
kubectl get pods -n todo-app -l app.kubernetes.io/name=redis
# Should show: redis-0 1/1 Running
```

### Step 4: Create Secrets

```bash
./scripts/create-local-secrets.sh
```

**Verify secrets:**
```bash
kubectl get secrets -n todo-app
# Should show: neon-secret, jwt-secret, redis-secret, dapr-redis-secret
```

### Step 5: Deploy Application

```bash
./scripts/deploy-local.sh
```

**Wait for deployment:**
```bash
kubectl wait --for=condition=available deployment --all -n todo-app --timeout=300s
```

### Step 6: Configure Ingress

```bash
# Add to /etc/hosts
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts
```

### Step 7: Validate Deployment

```bash
./scripts/validate-deployment.sh
```

**Access application:**
```
http://todo-app.local
```

---

## Cloud Deployment (Oracle Cloud)

### Prerequisites

- Oracle Cloud account (Always Free tier)
- OCI CLI configured
- Domain name for HTTPS
- Redpanda Cloud account (free tier)
- Neon PostgreSQL account (free tier)

### Step 1: Provision Oracle Cloud

Follow [docs/oracle-cloud-setup.md](docs/oracle-cloud-setup.md) to:
1. Create VCN and subnet
2. Create 2 compute instances (VM.Standard.E2.1.Micro)
3. Configure security lists
4. Generate SSH keys

### Step 2: Install k3s

**On server node:**
```bash
SERVER_NODE_IP=<server-private-ip> sudo ./scripts/install-k3s.sh server
```

**On agent node:**
```bash
SERVER_NODE_IP=<server-private-ip> K3S_TOKEN=<token-from-server> sudo ./scripts/install-k3s.sh agent
```

**Verify cluster:**
```bash
kubectl get nodes
# Should show 2 nodes: server (control-plane) and agent (worker)
```

### Step 3: Install Traefik

```bash
./scripts/install-traefik.sh
```

**Verify Traefik:**
```bash
kubectl get svc traefik -n kube-system
# Note the external IP
```

### Step 4: Install cert-manager

```bash
export LETSENCRYPT_EMAIL=your-email@example.com
./scripts/install-cert-manager.sh
```

**Verify cert-manager:**
```bash
kubectl get pods -n cert-manager
# Should show: cert-manager, cert-manager-cainjector, cert-manager-webhook
```

### Step 5: Install Dapr

```bash
dapr init -k --wait
dapr status -k
```

### Step 6: Create Secrets

```bash
# Database
export DATABASE_URL="postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/db"

# Redpanda
export REDPANDA_USERNAME="your-username"
export REDPANDA_PASSWORD="your-password"

# Deploy secrets
./scripts/create-cloud-secrets.sh
```

### Step 7: Update Configuration

Edit `k8s/cloud/dapr-components/pubsub.yaml`:
```yaml
- name: brokers
  value: "xxxxx.redpanda.cloud:9092"  # Your Redpanda bootstrap servers
```

Edit `k8s/cloud/cert-manager-issuer.yaml`:
```yaml
email: your-email@example.com  # Your email for Let's Encrypt
```

Edit `k8s/cloud/ingress.yaml`:
```yaml
spec:
  tls:
  - hosts:
    - todo-app.example.com  # Your domain
```

### Step 8: Deploy Application

```bash
./scripts/deploy-cloud.sh
```

**Wait for deployment:**
```bash
kubectl wait --for=condition=available deployment --all -n todo-app --timeout=600s
```

### Step 9: Configure DNS

Point your domain to the Traefik external IP:
```bash
kubectl get svc traefik -n kube-system
# Get the IP and create DNS A record
```

**DNS Configuration:**
```
Type: A
Name: todo-app.example.com
Value: <traefik-external-ip>
TTL: 300
```

### Step 10: Verify SSL Certificate

```bash
kubectl get certificates -n todo-app
# Should show: todo-app-tls with Ready=True
```

**Access application:**
```
https://todo-app.example.com
```

---

## Post-Deployment

### Deploy Monitoring Stack

```bash
./scripts/setup-monitoring.sh
```

**Access Grafana:**
```bash
kubectl port-forward -n monitoring svc/grafana 3000:80
# http://localhost:3000 (admin/admin)
```

**Access Prometheus:**
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# http://localhost:9090
```

### Configure Alerts

Edit alerting rules in `monitoring/prometheus/alerts.yaml` and apply:
```bash
kubectl apply -f monitoring/prometheus/alerts.yaml
```

---

## Verification

### Check Pods

```bash
kubectl get pods -n todo-app
# All pods should show 2/2 containers (app + Dapr sidecar)
```

### Check Services

```bash
kubectl get services -n todo-app
```

### Check Dapr Components

```bash
dapr components -k -n todo-app
# Should show: pubsub, statestore, bindings, secrets
```

### Check Dapr Subscriptions

```bash
kubectl get subscriptions -n todo-app
```

### Test Health Endpoint

```bash
curl https://todo-app.example.com/api/health
# Should return: {"status":"healthy"}
```

### Test Task Creation

```bash
curl -X POST https://todo-app.example.com/api/user_123/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "Test Task", "priority": "high"}'
```

### Check Event Flow

```bash
# Check event processor logs
kubectl logs -n todo-app -l app=event-processor --tail=50

# Check reminder scheduler logs
kubectl logs -n todo-app -l app=reminder-scheduler --tail=50
```

### Check Resource Usage

```bash
kubectl top nodes
kubectl top pods -n todo-app
```

---

## Rollback

### Automatic Rollback

The deployment workflow automatically rolls back on failure.

### Manual Rollback

**Via GitHub Actions:**
1. Go to Actions > Deploy - Oracle Cloud
2. Click "Run workflow"
3. Check "Rollback to previous version"
4. Click "Run workflow"

**Via kubectl:**
```bash
kubectl rollout undo deployment --all -n todo-app
kubectl rollout status deployment --all -n todo-app
```

### Rollback to Specific Version

```bash
kubectl rollout undo deployment/phase-v-backend -n todo-app --to-revision=<revision-number>
```

---

## Cleanup

### Local Cleanup

```bash
# Delete application
kubectl delete namespace todo-app

# Delete Dapr
dapr uninstall -k

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

### Cloud Cleanup

```bash
# Delete application
kubectl delete namespace todo-app

# Delete Dapr
dapr uninstall -k

# Delete cert-manager
kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml

# Terminate compute instances via OCI Console
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

---

## Next Steps

1. ✅ Verify all services are running
2. ✅ Test application functionality
3. ✅ Configure monitoring alerts
4. ✅ Set up log aggregation (optional)
5. ✅ Configure backup strategy (optional)

---

**Deployment Time:**
- Local (Minikube): ~15 minutes
- Cloud (Oracle Cloud): ~30 minutes

**Status:** Ready for production use
