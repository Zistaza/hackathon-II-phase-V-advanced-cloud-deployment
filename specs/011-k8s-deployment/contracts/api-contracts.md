# Deployment API Contracts

## Container Image Management API

### POST /api/container-images
**Purpose**: Create new container image

**Request Body:**
```json
{
  "name": "todo-backend",
  "tag": "latest",
  "repository": "docker.io/todo-app",
  "description": "Python FastAPI backend for Todo AI Chatbot"
}
```

**Response:**
```json
{
  "id": "uuid-1234",
  "name": "todo-backend",
  "tag": "latest",
  "repository": "docker.io/todo-app",
  "size": 12345678,
  "created_at": "2026-02-07T10:00:00Z",
  "status": "building"
}
```

### GET /api/container-images/{id}
**Purpose**: Get container image details

**Response:**
```json
{
  "id": "uuid-1234",
  "name": "todo-backend",
  "tag": "latest",
  "repository": "docker.io/todo-app",
  "size": 12345678,
  "created_at": "2026-02-07T10:00:00Z",
  "last_updated": "2026-02-07T10:05:00Z",
  "status": "built"
}
```

### PUT /api/container-images/{id}
**Purpose**: Update container image

**Request Body:**
```json
{
  "tag": "v1.0.0",
  "description": "Updated backend with security patches"
}
```

### DELETE /api/container-images/{id}
**Purpose**: Delete container image

**Response:**
```json
{
  "message": "Container image deleted successfully",
  "id": "uuid-1234"
}
```

## Helm Chart Management API

### POST /api/helm-charts
**Purpose**: Create new Helm chart

**Request Body:**
```json
{
  "name": "todo-app",
  "version": "1.0.0",
  "description": "Todo AI Chatbot Helm chart",
  "app_version": "1.0.0"
}
```

**Response:**
```json
{
  "id": "uuid-5678",
  "name": "todo-app",
  "version": "1.0.0",
  "description": "Todo AI Chatbot Helm chart",
  "app_version": "1.0.0",
  "created_at": "2026-02-07T10:00:00Z",
  "status": "validating"
}
```

### GET /api/helm-charts/{id}
**Purpose**: Get Helm chart details

**Response:**
```json
{
  "id": "uuid-5678",
  "name": "todo-app",
  "version": "1.0.0",
  "description": "Todo AI Chatbot Helm chart",
  "app_version": "1.0.0",
  "created_at": "2026-02-07T10:00:00Z",
  "last_updated": "2026-02-07T10:05:00Z",
  "status": "valid"
}
```

### PUT /api/helm-charts/{id}
**Purpose**: Update Helm chart

**Request Body:**
```json
{
  "version": "1.0.1",
  "description": "Updated with security patches"
}
```

### DELETE /api/helm-charts/{id}
**Purpose**: Delete Helm chart

**Response:**
```json
{
  "message": "Helm chart deleted successfully",
  "id": "uuid-5678"
}
```

## Minikube Cluster Management API

### GET /api/minikube-clusters/{id}
**Purpose**: Get cluster status

**Response:**
```json
{
  "id": "uuid-9012",
  "name": "local-dev",
  "status": "running",
  "cpus": 4,
  "memory": 8192,
  "disk_size": 30720,
  "kubernetes_version": "v1.28.0",
  "created_at": "2026-02-07T09:00:00Z"
}
```

### POST /api/minikube-clusters/{id}/start
**Purpose**: Start cluster

**Response:**
```json
{
  "message": "Cluster starting...",
  "status": "starting"
}
```

### POST /api/minikube-clusters/{id}/stop
**Purpose**: Stop cluster

**Response:**
```json
{
  "message": "Cluster stopping...",
  "status": "stopping"
}
```

### POST /api/minikube-clusters/{id}/restart
**Purpose**: Restart cluster

**Response:**
```json
{
  "message": "Cluster restarting...",
  "status": "restarting"
}
```

## Kubernetes Deployment Management API

### POST /api/deployments
**Purpose**: Create deployment

**Request Body:**
```json
{
  "name": "todo-backend-deployment",
  "replicas": 2,
  "image": "docker.io/todo-app/todo-backend:latest",
  "container_port": 8000,
  "helm_chart_id": "uuid-5678"
}
```

**Response:**
```json
{
  "id": "uuid-3456",
  "name": "todo-backend-deployment",
  "replicas": 2,
  "image": "docker.io/todo-app/todo-backend:latest",
  "container_port": 8000,
  "created_at": "2026-02-07T10:00:00Z",
  "status": "pending"
}
```

### GET /api/deployments/{id}
**Purpose**: Get deployment status

**Response:**
```json
{
  "id": "uuid-3456",
  "name": "todo-backend-deployment",
  "replicas": 2,
  "available_replicas": 2,
  "image": "docker.io/todo-app/todo-backend:latest",
  "container_port": 8000,
  "created_at": "2026-02-07T10:00:00Z",
  "status": "running"
}
```

### PUT /api/deployments/{id}
**Purpose**: Update deployment

**Request Body:**
```json
{
  "replicas": 3,
  "image": "docker.io/todo-app/todo-backend:v1.0.0"
}
```

### DELETE /api/deployments/{id}
**Purpose**: Delete deployment

**Response:**
```json
{
  "message": "Deployment deleted successfully",
  "id": "uuid-3456"
}
```

### POST /api/deployments/{id}/scale
**Purpose**: Scale deployment

**Request Body:**
```json
{
  "replicas": 4
}
```

**Response:**
```json
{
  "message": "Deployment scaling to 4 replicas",
  "current_replicas": 2,
  "desired_replicas": 4
}
```

## Kubernetes Service Management API

### POST /api/services
**Purpose**: Create service

**Request Body:**
```json
{
  "name": "todo-backend-service",
  "type": "ClusterIP",
  "port": 80,
  "target_port": 8000,
  "protocol": "TCP",
  "deployment_id": "uuid-3456"
}
```

**Response:**
```json
{
  "id": "uuid-7890",
  "name": "todo-backend-service",
  "type": "ClusterIP",
  "port": 80,
  "target_port": 8000,
  "protocol": "TCP",
  "created_at": "2026-02-07T10:00:00Z",
  "status": "pending"
}
```

### GET /api/services/{id}
**Purpose**: Get service status

**Response:**
```json
{
  "id": "uuid-7890",
  "name": "todo-backend-service",
  "type": "ClusterIP",
  "port": 80,
  "target_port": 8000,
  "protocol": "TCP",
  "created_at": "2026-02-07T10:00:00Z",
  "status": "active"
}
```

### PUT /api/services/{id}
**Purpose**: Update service

**Request Body:**
```json
{
  "type": "LoadBalancer"
}
```

### DELETE /api/services/{id}
**Purpose**: Delete service

**Response:**
```json
{
  "message": "Service deleted successfully",
  "id": "uuid-7890"
}
```

## AI Operations API

### POST /api/ai/deploy
**Purpose**: AI-assisted deployment

**Request Body:**
```json
{
  "helm_chart_id": "uuid-5678",
  "minikube_cluster_id": "uuid-9012",
  "ai_agent": "kubectl-ai"
}
```

**Response:**
```json
{
  "message": "AI-assisted deployment initiated",
  "deployment_id": "uuid-3456",
  "ai_agent": "kubectl-ai",
  "status": "in_progress"
}
```

### POST /api/ai/scale
**Purpose**: AI-assisted scaling

**Request Body:**
```json
{
  "deployment_id": "uuid-3456",
  "ai_agent": "kubectl-ai",
  "target_replicas": 5
}
```

**Response:**
```json
{
  "message": "AI-assisted scaling initiated",
  "deployment_id": "uuid-3456",
  "current_replicas": 2,
  "target_replicas": 5,
  "ai_agent": "kubectl-ai"
}
```

### POST /api/ai/debug
**Purpose**: AI-assisted debugging

**Request Body:**
```json
{
  "deployment_id": "uuid-3456",
  "ai_agent": "kubectl-ai",
  "issue": "pod not ready"
}
```

**Response:**
```json
{
  "message": "AI-assisted debugging initiated",
  "deployment_id": "uuid-3456",
  "ai_agent": "kubectl-ai",
  "analysis": "Pod is in CrashLoopBackOff due to missing environment variables",
  "recommendations": [
    "Add missing environment variables to deployment configuration",
    "Check application logs for specific error messages"
  ]
}
```

### POST /api/ai/analyze
**Purpose**: AI-assisted cluster analysis

**Request Body:**
```json
{
  "minikube_cluster_id": "uuid-9012",
  "ai_agent": "kagent",
  "analysis_type": "resource-optimization"
}
```

**Response:**
```json
{
  "message": "AI-assisted cluster analysis completed",
  "minikube_cluster_id": "uuid-9012",
  "ai_agent": "kagent",
  "analysis": {
    "resource_utilization": {
      "cpu": "65%",
      "memory": "45%"
    },
    "recommendations": [
      "Increase CPU limits for backend deployment",
      "Optimize memory usage for frontend containers"
    ]
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request",
  "message": "Invalid request body",
  "details": {
    "field": "name",
    "issue": "required field is missing"
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Resource not found",
  "id": "uuid-1234"
}
```

### 409 Conflict
```json
{
  "error": "Conflict",
  "message": "Resource already exists",
  "id": "uuid-1234"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

## Response Headers

### Standard Headers
- **Content-Type**: application/json
- **Cache-Control**: no-cache, no-store, must-revalidate
- **Pragma**: no-cache
- **Expires**: 0
- **X-Content-Type-Options**: nosniff
- **X-Frame-Options**: DENY
- **X-XSS-Protection**: 1; mode=block

### Pagination Headers (for list endpoints)
- **X-Total-Count**: Total number of items
- **Link**: Pagination links (first, prev, next, last)
- **Page**: Current page number
- **PerPage**: Items per page

## Rate Limiting

### Standard Rate Limits
- **Standard Users**: 100 requests per minute
- **Premium Users**: 500 requests per minute
- **Admin Users**: 1000 requests per minute

### Rate Limit Headers
- **X-RateLimit-Limit**: Maximum number of requests allowed
- **X-RateLimit-Remaining**: Number of requests remaining in current window
- **X-RateLimit-Reset**: Time when the rate limit resets (UNIX timestamp)

## API Versioning

### Version Header
- **API-Version**: 1.0.0

### Versioning Strategy
- **URL Versioning**: /v1/api/endpoint
- **Header Versioning**: Accept: application/vnd.todo.v1+json
- **Parameter Versioning**: ?version=1.0.0

## Security Considerations

### Authentication
- **JWT Tokens**: All requests must include valid JWT token
- **Token Expiration**: Tokens expire after 1 hour
- **Refresh Tokens**: Support for token refresh

### Authorization
- **Role-Based Access**: Different roles have different permissions
- **Resource Ownership**: Users can only access their own resources
- **Audit Logging**: All operations are logged for auditing

### Data Validation
- **Input Validation**: All inputs are validated
- **Output Sanitization**: All outputs are sanitized
- **SQL Injection Prevention**: Parameterized queries used
- **XSS Prevention**: Output encoding applied

## Error Handling

### Validation Errors
- **400**: Invalid request body or parameters
- **422**: Validation errors

### Authentication Errors
- **401**: Authentication required
- **403**: Insufficient permissions

### Resource Errors
- **404**: Resource not found
- **409**: Resource conflict

### System Errors
- **500**: Internal server error
- **503**: Service unavailable

## Monitoring and Observability

### Metrics
- **Request Count**: Total number of requests
- **Response Time**: Average response time
- **Error Rate**: Percentage of failed requests
- **Success Rate**: Percentage of successful requests

### Logging
- **Request Logs**: All incoming requests
- **Response Logs**: All outgoing responses
- **Error Logs**: All error events
- **Audit Logs**: All administrative operations

### Tracing
- **Request Tracing**: End-to-end request tracing
- **Service Tracing**: Service-to-service tracing
- **Database Tracing**: Database query tracing