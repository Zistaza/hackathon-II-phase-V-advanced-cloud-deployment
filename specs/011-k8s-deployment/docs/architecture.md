# Kubernetes Deployment Architecture

## System Overview

This document describes the architecture of the Todo AI Chatbot deployment on Kubernetes, including the components, data flow, and integration points.

## Architecture Components

### 1. Frontend Service

**Technology:** Next.js 16+ (App Router) + React 18+ + Tailwind CSS 4.0+
**Container:** `todo-frontend:latest`
**Replicas:** 1
**Resources:**
- CPU: 50m request, 200m limit
- Memory: 128Mi request, 256Mi limit
**Service Type:** ClusterIP
**Port:** 80

### 2. Backend Service

**Technology:** Python 3.11 + FastAPI + SQLModel + Neon PostgreSQL
**Container:** `todo-backend:latest`
**Replicas:** 2
**Resources:**
- CPU: 100m request, 500m limit
- Memory: 256Mi request, 512Mi limit
**Service Type:** ClusterIP
**Port:** 8000

### 3. Database Service

**Technology:** Neon Serverless PostgreSQL
**Connection:** External service (not deployed in cluster)
**Access:** Environment variables and connection strings

### 4. Ingress Controller

**Technology:** NGINX Ingress Controller
**Purpose:** External access to frontend service
**Configuration:** TLS termination and routing rules

## Data Flow

### User Request Flow

```
Internet → Ingress Controller → Frontend Service → Backend Service → Database
   ↓               ↓                ↓                ↓
Browser         NGINX         Next.js        FastAPI        Neon PostgreSQL
```

### Authentication Flow

```
User Login → Frontend → Backend → Better Auth → JWT Token → Frontend
    ↓              ↓              ↓              ↓              ↓
Browser      Next.js      FastAPI      Auth Service    Token         React State
```

## Container Architecture

### Frontend Container

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Security configuration
USER nginx
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Backend Container

```dockerfile
FROM python:3.11-slim as builder
RUN apt-get update && apt-get install -y gcc g++ \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt
COPY . .

FROM python:3.11-slim as production
WORKDIR /app
RUN apt-get update && apt-get install -y libpq5 \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Kubernetes Resources

### Deployments

#### Frontend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  labels:
    app: todo-frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
      - name: frontend
        image: todo-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "50m"
            memory: "128Mi"
          limits:
            cpu: "200m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Backend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app: todo-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "100m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: database-url
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

### Services

#### Frontend Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: todo-frontend
```

#### Backend Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
  selector:
    app: todo-backend
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: todo.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-frontend
            port:
              number: 80
```

## AI-Assisted Operations

### Docker AI Integration

**Container Optimization:**
- Multi-stage builds for size reduction
- Non-root user implementation
- Security hardening configurations
- Health check automation

**Image Management:**
- Automated vulnerability scanning
- Size optimization recommendations
- Build validation and testing
- Registry integration

### kubectl-ai Integration

**Deployment Operations:**
- Intelligent deployment commands
- Automated scaling recommendations
- AI-powered debugging
- Resource optimization suggestions

**Command Examples:**
```bash
# Deploy using AI assistance
kubectl-ai &quot;deploy the todo-app using helm chart&quot;

# Scale using AI recommendations
kubectl-ai &quot;scale the todo-backend to optimal replicas&quot;

# Debug using AI assistance
kubectl-ai &quot;debug the todo-backend deployment and provide solutions&quot;
```

### Kagent Integration

**Cluster Health Monitoring:**
- Real-time cluster analysis
- Resource utilization insights
- Performance bottleneck detection
- Health trend analysis

**Analysis Capabilities:**
```bash
# Analyze cluster health
kagent analyze cluster --health

# Get resource optimization recommendations
kagent optimize resources --cluster

# Analyze specific deployment
kagent analyze deployment todo-backend --insights
```

## Security Architecture

### Container Security
- **Non-root Users:** All containers run as non-root users
- **Image Scanning:** Regular vulnerability scanning
- **Security Contexts:** Pod security contexts and policies
- **Network Policies:** Network segmentation and isolation

### Application Security
- **JWT Authentication:** Secure token-based authentication
- **Data Isolation:** User-specific data isolation
- **Input Validation:** Request validation and sanitization
- **Rate Limiting:** API rate limiting and protection

### Network Security
- **Service Mesh:** Optional service mesh for advanced routing
- **TLS Encryption:** Data encryption in transit
- **Network Policies:** Pod-to-pod communication control
- **Ingress Security:** SSL/TLS termination and routing

## Performance Optimization

### Resource Management
- **CPU Limits:** Appropriate CPU limits and requests
- **Memory Management:** Memory limits and garbage collection
- **Replica Configuration:** Optimal replica counts
- **Resource Quotas:** Namespace resource quotas

### Scaling Strategies
- **Horizontal Pod Autoscaler:** Automatic scaling based on metrics
- **Cluster Autoscaler:** Node scaling for resource optimization
- **AI-Powered Scaling:** Intelligent scaling recommendations
- **Load Balancing:** Service load balancing and distribution

### Monitoring and Optimization
- **Metrics Collection:** Comprehensive metrics collection
- **Performance Analysis:** AI-powered performance insights
- **Resource Optimization:** Continuous resource optimization
- **Capacity Planning:** Predictive capacity planning

## Disaster Recovery

### Backup Strategies
- **Database Backups:** Regular database backups
- **Configuration Backups:** Helm chart and configuration backups
- **State Management:** Stateless application design
- **Recovery Procedures:** Automated recovery procedures

### High Availability
- **Multi-replica Deployments:** Multiple pod replicas
- **Load Balancing:** Service load balancing
- **Health Checks:** Pod health monitoring
- **Auto-healing:** Self-healing capabilities

## Monitoring and Observability

### Metrics and Logging
- **Prometheus Integration:** Metrics collection and storage
- **Grafana Dashboards:** Visualization and alerting
- **Structured Logging:** JSON-formatted application logs
- **Log Aggregation:** Centralized log collection

### Alerting and Notification
- **Health Alerts:** Pod and service health alerts
- **Performance Alerts:** Performance degradation alerts
- **Security Alerts:** Security-related alerts
- **Resource Alerts:** Resource utilization alerts

## Compliance and Governance

### Audit Trails
- **Deployment History:** Complete deployment history
- **Configuration Changes:** Configuration change tracking
- **Access Logs:** Access and authentication logs
- **Compliance Reports:** Automated compliance reporting

### Policy Enforcement
- **Security Policies:** Security policy enforcement
- **Resource Policies:** Resource allocation policies
- **Network Policies:** Network communication policies
- **Data Policies:** Data handling and protection policies