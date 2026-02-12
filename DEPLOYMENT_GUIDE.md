# Phase-V Deployment Guide

**Feature**: 012-phasev-advanced-features
**Date**: 2026-02-12
**Target**: Kubernetes (Minikube local, AKS/GKE/OKE production)

---

## Prerequisites

### Required Software
- Docker Desktop or Docker Engine
- Kubernetes cluster (Minikube for local, AKS/GKE/OKE for production)
- Dapr CLI v1.12+ (`dapr --version`)
- kubectl (`kubectl version`)
- Helm 3+ (`helm version`)
- Python 3.11+ (`python --version`)
- Node.js 18+ (`node --version`)
- PostgreSQL client (`psql --version`)

### Required Services
- Neon PostgreSQL database (or local PostgreSQL)
- Kafka/Redpanda cluster (or local Kafka via Docker)

---

## Step 1: Database Setup

### 1.1 Configure Database Connection

Create `.env` file in `backend/` directory:

```bash
DATABASE_URL=postgresql://user:password@host:5432/todo_chatbot
JWT_SECRET=your-secret-key-here
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
```

### 1.2 Run Database Migration

```bash
cd backend

# Install Alembic if not already installed
pip install alembic

# Run migration
alembic upgrade head

# Verify migration
psql $DATABASE_URL -c "\d tasks"
psql $DATABASE_URL -c "\di"  # Check indexes
```

**Expected Output:**
- New columns: priority, tags, due_date, recurrence_pattern, reminder_time, search_vector
- New indexes: idx_tasks_priority, idx_tasks_tags, idx_tasks_search, idx_tasks_due_date, idx_tasks_status_priority

### 1.3 Verify Migration Rollback

```bash
# Test rollback
alembic downgrade -1

# Re-apply
alembic upgrade head
```

---

## Step 2: Local Development Setup (Minikube)

### 2.1 Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
kubectl cluster-info
```

### 2.2 Install Dapr on Kubernetes

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr installation
dapr status -k

# Expected output: dapr-operator, dapr-sidecar-injector, dapr-sentry, dapr-placement-server
```

### 2.3 Deploy Kafka

```bash
# Add Bitnami Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka
helm install kafka bitnami/kafka \
  --set persistence.enabled=false \
  --set zookeeper.persistence.enabled=false \
  --set replicaCount=1

# Wait for Kafka to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka --timeout=300s

# Verify Kafka is running
kubectl get pods -l app.kubernetes.io/name=kafka
```

### 2.4 Create Kafka Topics

```bash
# Get Kafka pod name
KAFKA_POD=$(kubectl get pods -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

# Create topics
kubectl exec -it $KAFKA_POD -- kafka-topics.sh \
  --create --topic task-events \
  --bootstrap-server localhost:9092 \
  --partitions 3 --replication-factor 1

kubectl exec -it $KAFKA_POD -- kafka-topics.sh \
  --create --topic reminders \
  --bootstrap-server localhost:9092 \
  --partitions 3 --replication-factor 1

kubectl exec -it $KAFKA_POD -- kafka-topics.sh \
  --create --topic task-updates \
  --bootstrap-server localhost:9092 \
  --partitions 3 --replication-factor 1

# Verify topics created
kubectl exec -it $KAFKA_POD -- kafka-topics.sh \
  --list --bootstrap-server localhost:9092
```

### 2.5 Deploy Dapr Components

```bash
# Apply Dapr components
kubectl apply -f infrastructure/dapr/components/

# Verify components
dapr components -k

# Expected: kafka-pubsub, statestore, jobs-api, kubernetes-secrets
```

---

## Step 3: Deploy Backend Services

### 3.1 Build Docker Images

```bash
# Build backend API image
cd backend
docker build -t todo-api:latest .

# Build recurring task service image
docker build -t recurring-task-service:latest -f Dockerfile.recurring .

# Build notification service image
docker build -t notification-service:latest -f Dockerfile.notification .

# Load images into Minikube
minikube image load todo-api:latest
minikube image load recurring-task-service:latest
minikube image load notification-service:latest
```

### 3.2 Deploy Services

```bash
# Deploy backend API
kubectl apply -f infrastructure/k8s/todo-api-deployment.yaml

# Deploy recurring task service
kubectl apply -f infrastructure/k8s/recurring-task-service-deployment.yaml

# Deploy notification service
kubectl apply -f infrastructure/k8s/notification-service-deployment.yaml

# Verify deployments
kubectl get deployments
kubectl get pods
```

### 3.3 Verify Dapr Sidecars

```bash
# Check that Dapr sidecars are injected
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# Expected: Each pod should have 2 containers (app + daprd)
```

---

## Step 4: Deploy Frontend

### 4.1 Build Frontend Image

```bash
cd frontend

# Build production image
docker build -t todo-frontend:latest .

# Load into Minikube
minikube image load todo-frontend:latest
```

### 4.2 Deploy Frontend

```bash
# Deploy frontend
kubectl apply -f infrastructure/k8s/frontend-deployment.yaml

# Expose frontend service
kubectl expose deployment todo-frontend --type=NodePort --port=3000

# Get frontend URL
minikube service todo-frontend --url
```

---

## Step 5: Verification & Testing

### 5.1 Health Checks

```bash
# Check backend API health
kubectl port-forward svc/todo-api 8000:8000
curl http://localhost:8000/health

# Check recurring task service health
kubectl port-forward svc/recurring-task-service 8002:8002
curl http://localhost:8002/health

# Check notification service health
kubectl port-forward svc/notification-service 8001:8001
curl http://localhost:8001/health

# Check WebSocket health
curl http://localhost:8000/ws/health
```

### 5.2 Test Task Creation with Reminders

```bash
# Get JWT token (replace with actual auth flow)
TOKEN="your-jwt-token"

# Create task with due date and reminder
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task with Reminder",
    "description": "This task has a reminder",
    "priority": "high",
    "tags": ["test", "reminder"],
    "due_date": "2026-02-13T10:00:00Z",
    "reminder_time": "1h"
  }'

# Verify reminder job created
# Check Dapr logs for job scheduling
kubectl logs -l app=todo-api -c daprd | grep "job"
```

### 5.3 Test Recurring Tasks

```bash
# Create recurring task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Standup",
    "description": "Team standup meeting",
    "priority": "medium",
    "due_date": "2026-02-13T09:00:00Z",
    "recurrence_pattern": "daily"
  }'

# Complete the task
TASK_ID="<task-id-from-response>"
curl -X POST http://localhost:8000/api/tasks/$TASK_ID/complete \
  -H "Authorization: Bearer $TOKEN"

# Check recurring task service logs for next instance creation
kubectl logs -l app=recurring-task-service | grep "Generated next recurring task"
```

### 5.4 Test Search & Filtering

```bash
# Search tasks
curl "http://localhost:8000/api/tasks?search=standup" \
  -H "Authorization: Bearer $TOKEN"

# Filter by priority
curl "http://localhost:8000/api/tasks?priority=high" \
  -H "Authorization: Bearer $TOKEN"

# Filter by tags
curl "http://localhost:8000/api/tasks?tags=test,reminder" \
  -H "Authorization: Bearer $TOKEN"

# Combined filter + sort
curl "http://localhost:8000/api/tasks?priority=high&status=incomplete&sort_by=due_date&sort_order=asc" \
  -H "Authorization: Bearer $TOKEN"
```

### 5.5 Test Multi-Client Sync

1. Open frontend in two browser tabs
2. Authenticate in both tabs
3. Create a task in tab 1
4. Verify task appears in tab 2 within 2 seconds
5. Update task priority in tab 2
6. Verify update appears in tab 1 within 2 seconds

---

## Step 6: Monitoring & Observability

### 6.1 Deploy Prometheus

```bash
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack

# Access Prometheus UI
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
# Open http://localhost:9090
```

### 6.2 Deploy Grafana

```bash
# Grafana is included in kube-prometheus-stack
# Get Grafana password
kubectl get secret prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Access Grafana UI
kubectl port-forward svc/prometheus-grafana 3000:80
# Open http://localhost:3000 (username: admin)
```

### 6.3 Import Dashboards

```bash
# Import pre-built dashboards from infrastructure/monitoring/grafana/dashboards/
# - task-operations.json
# - event-processing.json
# - reminders.json
```

---

## Step 7: Production Deployment (AKS/GKE/OKE)

### 7.1 Create Cloud Cluster

**Azure (AKS):**
```bash
az aks create \
  --resource-group todo-chatbot-rg \
  --name todo-chatbot-cluster \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

az aks get-credentials --resource-group todo-chatbot-rg --name todo-chatbot-cluster
```

**Google Cloud (GKE):**
```bash
gcloud container clusters create todo-chatbot-cluster \
  --num-nodes=3 \
  --zone=us-central1-a

gcloud container clusters get-credentials todo-chatbot-cluster --zone=us-central1-a
```

**Oracle Cloud (OKE):**
```bash
oci ce cluster create \
  --compartment-id <compartment-id> \
  --name todo-chatbot-cluster \
  --kubernetes-version v1.28.0 \
  --node-shape VM.Standard.E4.Flex
```

### 7.2 Configure Production Secrets

```bash
# Create Kubernetes secrets
kubectl create secret generic postgres-secrets \
  --from-literal=connectionString="$DATABASE_URL"

kubectl create secret generic jwt-secrets \
  --from-literal=secret="$JWT_SECRET"

kubectl create secret generic kafka-secrets \
  --from-literal=brokers="$KAFKA_BROKERS" \
  --from-literal=username="$KAFKA_USERNAME" \
  --from-literal=password="$KAFKA_PASSWORD"
```

### 7.3 Deploy with Helm

```bash
# Update Helm values for production
helm install todo-app ./infrastructure/helm/todo-app \
  --set environment=production \
  --set replicaCount=3 \
  --set image.tag=v1.0.0 \
  --set ingress.enabled=true \
  --set ingress.host=todo.example.com

# Verify deployment
helm status todo-app
kubectl get pods -l app.kubernetes.io/name=todo-app
```

---

## Troubleshooting

### Issue: Dapr Sidecar Not Injecting

**Solution:**
```bash
# Check Dapr sidecar injector
kubectl get pods -n dapr-system

# Verify namespace has Dapr enabled
kubectl get namespace default -o yaml | grep dapr

# Enable Dapr for namespace
kubectl annotate namespace default dapr.io/enabled=true
```

### Issue: Kafka Connection Failed

**Solution:**
```bash
# Check Kafka service
kubectl get svc kafka

# Test Kafka connectivity from pod
kubectl run kafka-test --rm -it --image=bitnami/kafka:latest -- bash
kafka-topics.sh --list --bootstrap-server kafka:9092
```

### Issue: Events Not Publishing

**Solution:**
```bash
# Check Dapr Pub/Sub component
dapr components -k | grep kafka-pubsub

# Check application logs
kubectl logs -l app=todo-api -c todo-api

# Check Dapr sidecar logs
kubectl logs -l app=todo-api -c daprd
```

### Issue: Reminders Not Triggering

**Solution:**
```bash
# Check Dapr Jobs API component
dapr components -k | grep jobs-api

# List scheduled jobs
# (Dapr Jobs API doesn't have a list command yet, check logs)
kubectl logs -l app=todo-api -c daprd | grep "job"

# Verify reminder endpoint is accessible
kubectl port-forward svc/todo-api 8000:8000
curl http://localhost:8000/api/reminders/health
```

---

## Performance Tuning

### Database Optimization

```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM tasks
WHERE user_id = 'user123'
AND search_vector @@ plainto_tsquery('test');

-- Vacuum and analyze
VACUUM ANALYZE tasks;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE tablename = 'tasks';
```

### Kafka Optimization

```bash
# Increase partitions for higher throughput
kubectl exec -it $KAFKA_POD -- kafka-topics.sh \
  --alter --topic task-events \
  --partitions 6 \
  --bootstrap-server localhost:9092
```

### Dapr Optimization

Update Dapr configuration in `infrastructure/dapr/config.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: daprConfig
spec:
  tracing:
    samplingRate: "1"
  metric:
    enabled: true
  mtls:
    enabled: true
```

---

## Rollback Procedure

### Rollback Application

```bash
# Rollback to previous Helm release
helm rollback todo-app

# Verify rollback
helm history todo-app
```

### Rollback Database

```bash
# Rollback migration
cd backend
alembic downgrade -1

# Verify rollback
psql $DATABASE_URL -c "\d tasks"
```

---

## Maintenance

### Backup Database

```bash
# Backup PostgreSQL database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore from backup
psql $DATABASE_URL < backup_20260212.sql
```

### Clean Up Old Events

```bash
# Dapr State Store automatically cleans up expired events (7-day TTL)
# No manual cleanup required

# Check state store size
psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_total_relation_size('dapr_state'));"
```

### Update Services

```bash
# Update backend API
kubectl set image deployment/todo-api todo-api=todo-api:v1.1.0

# Verify rolling update
kubectl rollout status deployment/todo-api
```

---

## Security Checklist

- [ ] JWT secrets stored in Kubernetes Secrets
- [ ] Database credentials stored in Kubernetes Secrets
- [ ] Kafka credentials stored in Kubernetes Secrets
- [ ] TLS enabled for all external endpoints
- [ ] Dapr mTLS enabled for service-to-service communication
- [ ] Network policies configured to restrict pod-to-pod traffic
- [ ] RBAC configured for Kubernetes service accounts
- [ ] Container images scanned for vulnerabilities
- [ ] Secrets rotation policy implemented

---

## Support & Documentation

- **Architecture Diagrams**: `docs/architecture/`
- **API Documentation**: `docs/api/`
- **Event Schemas**: `specs/012-phasev-advanced-features/contracts/`
- **Troubleshooting Guide**: This document
- **GitHub Issues**: https://github.com/your-org/todo-chatbot/issues
