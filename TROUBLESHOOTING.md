# Phase-V Troubleshooting Guide

Common issues and solutions for Phase-V deployment and operation.

## Table of Contents

- [Cluster Issues](#cluster-issues)
- [Dapr Issues](#dapr-issues)
- [Deployment Issues](#deployment-issues)
- [Application Issues](#application-issues)
- [Network Issues](#network-issues)
- [Database Issues](#database-issues)
- [Event Processing Issues](#event-processing-issues)
- [Monitoring Issues](#monitoring-issues)

---

## Cluster Issues

### Minikube Fails to Start

**Symptoms:**
```
😿  minikube start errors out: exit status 1
```

**Solutions:**

1. Check Docker is running:
```bash
docker ps
systemctl status docker
```

2. Check available resources:
```bash
free -h
df -h
```

3. Delete and recreate:
```bash
minikube delete
minikube start --cpus=4 --memory=8192
```

4. Try different driver:
```bash
minikube start --driver=kvm2
# or
minikube start --driver=virtualbox
```

### k3s Agent Cannot Connect to Server

**Symptoms:**
```
Failed to connect to proxy
```

**Solutions:**

1. Verify server IP is correct (use private IP)
2. Check firewall rules allow port 6443
3. Verify token is correct:
```bash
# On server
cat /var/lib/rancher/k3s/server/node-token

# On agent, reinstall with correct token
curl -sfL https://get.k3s.io | K3S_URL=https://<server-ip>:6443 K3S_TOKEN=<token> sh -
```

4. Check security group allows internal traffic

---

## Dapr Issues

### Dapr Sidecar Not Injecting

**Symptoms:**
- Pods show 1/1 containers instead of 2/2
- Dapr annotations present but no sidecar

**Solutions:**

1. Check Dapr installation:
```bash
dapr status -k
```

2. Check pod annotations:
```bash
kubectl get pod <pod-name> -n todo-app -o yaml | grep dapr.io
```

3. Check Dapr sidecar injector logs:
```bash
kubectl logs -n dapr-system -l app=dapr-sidecar-injector --tail=50
```

4. Restart deployment:
```bash
kubectl rollout restart deployment/<deployment-name> -n todo-app
```

5. Reinstall Dapr:
```bash
dapr uninstall -k
dapr init -k --wait
```

### Dapr Components Not Ready

**Symptoms:**
```
dapr components -k shows components not ready
```

**Solutions:**

1. Check component configuration:
```bash
kubectl get component pubsub -n todo-app -o yaml
```

2. Check Dapr logs:
```bash
kubectl logs <pod-name> -n todo-app -c daprd --tail=100
```

3. Verify secrets exist:
```bash
kubectl get secrets -n todo-app
```

4. Reapply components:
```bash
kubectl apply -f k8s/local/dapr-components/
# or
kubectl apply -f k8s/cloud/dapr-components/
```

### Dapr Pub/Sub Not Working

**Symptoms:**
- Events not being published
- Subscription errors in logs

**Solutions:**

1. Check Redis is running:
```bash
kubectl get pods -n todo-app -l app.kubernetes.io/name=redis
```

2. Test Redis connection:
```bash
kubectl exec -n todo-app redis-0 -- redis-cli ping
```

3. Check Dapr subscription:
```bash
kubectl get subscriptions -n todo-app
```

4. Test event publishing:
```bash
kubectl exec -n todo-app -it <backend-pod> -c backend -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_id":"test-123","event_type":"task.created"}'
```

---

## Deployment Issues

### Pods Stuck in Pending State

**Symptoms:**
```
kubectl get pods shows Pending status
```

**Solutions:**

1. Check pod events:
```bash
kubectl describe pod <pod-name> -n todo-app
```

2. Check resource quota:
```bash
kubectl get resourcequota -n todo-app
kubectl top nodes
```

3. Check image pull errors:
```bash
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

4. For insufficient resources:
```bash
# Scale down replicas
kubectl scale deployment <deployment-name> --replicas=1 -n todo-app

# Or increase cluster resources
minikube stop
minikube start --cpus=6 --memory=16384
```

### Pods in CrashLoopBackOff

**Symptoms:**
```
kubectl get pods shows CrashLoopBackOff
```

**Solutions:**

1. Check pod logs:
```bash
kubectl logs <pod-name> -n todo-app -c <container-name>
kubectl logs <pod-name> -n todo-app -c daprd
```

2. Check environment variables:
```bash
kubectl exec -n todo-app <pod-name> -- env
```

3. Check secrets are accessible:
```bash
kubectl get secret neon-secret -n todo-app -o yaml
kubectl get secret jwt-secret -n todo-app -o yaml
```

4. Check database connectivity:
```bash
kubectl exec -n todo-app -it <pod-name> -c backend -- \
  python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

### Rollout Status Timeout

**Symptoms:**
```
error: timed out waiting for the condition
```

**Solutions:**

1. Check deployment status:
```bash
kubectl rollout status deployment/<deployment-name> -n todo-app --timeout=60s
```

2. Check replica status:
```bash
kubectl get deployment <deployment-name> -n todo-app
```

3. Check pod logs for errors:
```bash
kubectl logs -n todo-app -l app=<deployment-name> --tail=100
```

4. Cancel rollout and investigate:
```bash
kubectl rollout undo deployment/<deployment-name> -n todo-app
```

---

## Application Issues

### Health Endpoint Returns Error

**Symptoms:**
```bash
curl http://todo-app.local/api/health
# Returns 500 or connection refused
```

**Solutions:**

1. Check backend pod status:
```bash
kubectl get pods -n todo-app -l app=phase-v-backend
```

2. Check backend logs:
```bash
kubectl logs -n todo-app -l app=phase-v-backend --tail=100
```

3. Port forward and test directly:
```bash
kubectl port-forward -n todo-app svc/phase-v-backend 8000:8000
curl http://localhost:8000/health
```

4. Check environment variables:
```bash
kubectl exec -n todo-app -it <backend-pod> -c backend -- \
  env | grep -E "DATABASE|JWT|REDIS"
```

### JWT Authentication Fails

**Symptoms:**
```
401 Unauthorized
Invalid token
```

**Solutions:**

1. Verify JWT secret is set:
```bash
kubectl get secret jwt-secret -n todo-app -o jsonpath='{.data.secret}' | base64 -d
```

2. Check token expiration:
```python
import jwt
decoded = jwt.decode(token, options={"verify_exp": False})
print(decoded)
```

3. Regenerate token with correct secret:
```bash
# Update secret
kubectl create secret generic jwt-secret \
  --from-literal=secret="new-secret" \
  -n todo-app \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart backend
kubectl rollout restart deployment/phase-v-backend -n todo-app
```

### WebSocket Connection Fails

**Symptoms:**
```
WebSocket connection failed
```

**Solutions:**

1. Check websocket service:
```bash
kubectl get svc phase-v-websocket-service -n todo-app
```

2. Check websocket pod logs:
```bash
kubectl logs -n todo-app -l app=phase-v-websocket-service --tail=50
```

3. Verify ingress WebSocket configuration:
```bash
kubectl get ingress todo-app-ingress -n todo-app -o yaml
```

4. Test WebSocket connection:
```bash
wscat -c ws://todo-app.local/ws/test-user
```

---

## Network Issues

### Ingress Not Accessible

**Symptoms:**
```
curl: (7) Failed to connect to todo-app.local
```

**Solutions:**

1. Check ingress controller:
```bash
kubectl get pods -n ingress-nginx
# or for k3s
kubectl get pods -n kube-system -l app.kubernetes.io/name=traefik
```

2. Check ingress resource:
```bash
kubectl get ingress -n todo-app
```

3. Verify /etc/hosts entry:
```bash
grep todo-app.local /etc/hosts
# Should show: <minikube-ip> todo-app.local
```

4. Get correct IP:
```bash
minikube ip
# or for cloud
kubectl get svc traefik -n kube-system
```

5. Update /etc/hosts:
```bash
echo "<ip> todo-app.local" | sudo tee -a /etc/hosts
```

### SSL Certificate Not Issued

**Symptoms:**
```
kubectl get certificates shows NotReady
Browser shows SSL error
```

**Solutions:**

1. Check certificate status:
```bash
kubectl describe certificate todo-app-tls -n todo-app
```

2. Check cert-manager logs:
```bash
kubectl logs -n cert-manager -l app.kubernetes.io/name=cert-manager --tail=100
```

3. Verify DNS is pointing correctly:
```bash
nslookup todo-app.example.com
dig todo-app.example.com
```

4. Check ClusterIssuer:
```bash
kubectl get clusterissuer letsencrypt-prod -o yaml
```

5. Manually trigger certificate:
```bash
kubectl delete certificate todo-app-tls -n todo-app
kubectl apply -f k8s/cloud/ingress.yaml
```

---

## Database Issues

### Database Connection Fails

**Symptoms:**
```
psycopg2.OperationalError: connection refused
```

**Solutions:**

1. Check connection string:
```bash
kubectl get secret neon-secret -n todo-app -o jsonpath='{.data.connectionString}' | base64 -d
```

2. Test database connection:
```bash
kubectl exec -n todo-app -it <backend-pod> -c backend -- \
  python -c "import psycopg2; conn = psycopg2.connect('$DATABASE_URL'); print('Connected!')"
```

3. Check Neon project:
- Verify project is active
- Check connection string format
- Ensure IP is allowed (Neon allows all by default)

4. Update secret:
```bash
kubectl create secret generic neon-secret \
  --from-literal=connectionString="postgresql://..." \
  -n todo-app \
  --dry-run=client -o yaml | kubectl apply -f -
```

---

## Event Processing Issues

### Events Not Being Consumed

**Symptoms:**
- Events published but not processed
- Consumer logs show no activity

**Solutions:**

1. Check Dapr subscription:
```bash
kubectl get subscriptions -n todo-app
```

2. Check consumer logs:
```bash
kubectl logs -n todo-app -l app=event-processor --tail=100
```

3. Verify topic names match:
```bash
# Check publisher topic
kubectl exec -n todo-app -it <backend-pod> -c backend -- \
  grep -r "task.events" src/

# Check subscription topic
kubectl get subscriptions -n todo-app -o yaml
```

4. Check idempotency state:
```bash
kubectl exec -n todo-app -it <event-processor-pod> -c event-processor -- \
  curl http://localhost:3500/v1.0/state/statestore/event-processor:processed-event:<event-id>
```

### High Consumer Lag

**Symptoms:**
```
consumer_lag_messages metric shows high values
```

**Solutions:**

1. Check consumer throughput:
```bash
kubectl logs -n todo-app -l app=event-processor --tail=1000 | grep "Processing"
```

2. Scale consumer replicas:
```bash
kubectl scale deployment phase-v-event-processor --replicas=3 -n todo-app
```

3. Check for processing errors:
```bash
kubectl logs -n todo-app -l app=event-processor | grep -i error
```

4. Monitor lag metric:
```bash
# In Prometheus
consumer_lag_messages{consumer="event-processor"}
```

---

## Monitoring Issues

### Prometheus Not Scraping Metrics

**Symptoms:**
- No metrics in Prometheus
- Targets show DOWN

**Solutions:**

1. Check Prometheus targets:
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090/targets
```

2. Check service annotations:
```bash
kubectl get svc -n todo-app -o yaml | grep prometheus
```

3. Check pod annotations:
```bash
kubectl get pods -n todo-app -o yaml | grep prometheus.io/scrape
```

4. Verify scrape config:
```bash
kubectl get configmap prometheus-config -n monitoring -o yaml
```

### Grafana Dashboards Not Showing Data

**Symptoms:**
- Dashboards show "No data"
- Panels are empty

**Solutions:**

1. Verify Prometheus datasource:
```bash
kubectl get configmap grafana-datasources -n monitoring -o yaml
```

2. Check dashboard ConfigMap:
```bash
kubectl get configmap grafana-dashboards -n monitoring
```

3. Restart Grafana:
```bash
kubectl rollout restart deployment grafana -n monitoring
```

4. Verify Prometheus queries:
```
# In Grafana Explore, test queries:
up{namespace="todo-app"}
rate(task_operations_total[5m])
```

### Alerts Not Firing

**Symptoms:**
- Conditions met but no alerts

**Solutions:**

1. Check alerting rules:
```bash
kubectl get prometheusrule -n monitoring
```

2. Verify rules in Prometheus:
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090/rules
```

3. Test alert expression:
```
# In Prometheus, test expression:
sum(rate(task_operations_total{status="error"}[5m])) / sum(rate(task_operations_total[5m]))
```

4. Check Alertmanager (if configured):
```bash
kubectl get pods -n monitoring -l app=alertmanager
```

---

## Script Issues

### Deployment Script Fails

**Symptoms:**
```
./scripts/deploy-local.sh fails with error
```

**Solutions:**

1. Run with debugging:
```bash
bash -x ./scripts/deploy-local.sh
```

2. Check prerequisites:
```bash
kubectl cluster-info
helm version
dapr version
```

3. Check script permissions:
```bash
chmod +x ./scripts/*.sh
```

4. Run steps manually:
```bash
# Follow script steps one by one
kubectl apply -f k8s/local/dapr-components/
kubectl apply -f k8s/base/
kubectl apply -f k8s/local/
```

---

## Resource Issues

### High CPU/Memory Usage

**Symptoms:**
```
kubectl top shows high resource usage
Pods being OOMKilled
```

**Solutions:**

1. Check resource usage:
```bash
kubectl top nodes
kubectl top pods -n todo-app
```

2. Adjust resource limits:
```bash
kubectl edit deployment <deployment-name> -n todo-app
# Update resources section
```

3. Scale down replicas:
```bash
kubectl scale deployment <deployment-name> --replicas=1 -n todo-app
```

4. For Oracle Cloud, verify within Always Free limits:
- Total: 2 OCPU, 12GB RAM
- Adjust deployments accordingly

---

## Getting Help

If issues persist:

1. Check logs:
```bash
kubectl logs -n todo-app <pod-name> --tail=200
```

2. Describe resources:
```bash
kubectl describe pod <pod-name> -n todo-app
kubectl describe deployment <deployment-name> -n todo-app
```

3. Check events:
```bash
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

4. Create an issue on GitHub with:
- Error messages
- Relevant logs
- Steps to reproduce

---

**Last Updated:** 2026-02-19
**Version:** 1.0.0
