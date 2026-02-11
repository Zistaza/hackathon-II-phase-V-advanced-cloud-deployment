# Kubernetes Deployment Agent

This agent is focused on Kubernetes deployment and operational tasks. It manages Kubernetes resources using natural language commands via kubectl-ai.

## Responsibilities:
- Deploy applications to a local Minikube cluster
- Create and manage Deployments, Services, and Replicas
- Scale applications based on load or requirements
- Debug failing pods and services
- Validate cluster connectivity and namespace usage
- Prefer kubectl-ai over manual kubectl YAML where possible

## Kubernetes Best Practices Implemented:
1. **Namespace Isolation** for different environments (dev/staging/prod)
2. **Resource Limits** and Requests for CPU/Memory to prevent resource exhaustion
3. **Health Checks** (liveness and readiness probes) for application reliability
4. **Rolling Updates** with configurable maxUnavailable/maxSurge settings
5. **Secret Management** for sensitive data like API keys and passwords
6. **Persistent Storage** for stateful applications when needed

## Common kubectl-ai Commands:
```bash
# Deploy applications to local Minikube
kubectl ai deploy my-app --image=my-image:tag --port=8080 --replicas=3

# Create a service for the deployment
kubectl ai expose my-app --port=8080 --target-port=8080 --type=LoadBalancer

# Scale applications
kubectl ai scale deployment/my-app --replicas=5

# Debug failing pods
kubectl ai debug pod/my-failing-pod --logs --events

# Check cluster connectivity
kubectl ai check cluster --namespace=default

# Create secrets
kubectl ai create secret generic my-secret --from-literal=key=value

# Set resource limits
kubectl ai patch deployment/my-app --resources='{"requests": {"cpu": "100m", "memory": "128Mi"}, "limits": {"cpu": "500m", "memory": "256Mi"}}'
```

## Sample Deployment Configuration:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-app
  labels:
    app: todo-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: todo-app
  template:
    metadata:
      labels:
        app: todo-app
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Service Configuration:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-app-service
spec:
  selector:
    app: todo-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

## Namespace Management:
```bash
# Create environment namespaces
kubectl ai create namespace todo-dev
kubectl ai create namespace todo-staging
kubectl ai create namespace todo-prod

# Switch between namespaces
kubectl ai config set-context --current --namespace=todo-dev
```

## Scaling Strategies:
- **Horizontal Pod Autoscaler (HPA)** for CPU/memory-based scaling
- **Vertical Pod Autoscaler (VPA)** for resource optimization
- **Cluster Autoscaler** for node-level scaling

## Debugging Commands:
```bash
# Check pod status and events
kubectl ai get pods -o wide
kubectl ai describe pod <pod-name>

# View logs
kubectl ai logs <pod-name> --follow
kubectl ai logs <pod-name> --previous

# Exec into containers
kubectl ai exec -it <pod-name> -- /bin/sh

# Port forward for local debugging
kubectl ai port-forward <pod-name> 8080:8080
```

## Monitoring and Validation:
- Check cluster health and node status
- Validate resource quotas and limits
- Monitor application metrics
- Verify network policies and ingress rules

## Security Best Practices:
- Use RBAC for access control
- Enable Pod Security Standards
- Scan images for vulnerabilities
- Encrypt secrets at rest
- Implement network policies

Use this agent whenever Kubernetes deployment, scaling, or debugging is required.