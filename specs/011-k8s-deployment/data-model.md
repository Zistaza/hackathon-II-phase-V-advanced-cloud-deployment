# Data Model: Phase IV Kubernetes Deployment

## Key Entities

### Container Images
**Purpose**: Docker images for frontend and backend applications that encapsulate the existing Phase III Todo AI Chatbot functionality

**Fields**:
- **id**: UUID (Primary Key)
- **name**: String (e.g., "todo-backend", "todo-frontend")
- **tag**: String (e.g., "latest", "v1.0.0")
- **repository**: String (Docker registry URL)
- **size**: Integer (bytes)
- **created_at**: Timestamp
- **last_updated**: Timestamp
- **status**: Enum ("building", "built", "failed")

**Relationships**:
- Belongs to: Application (frontend/backend)

### Helm Chart
**Purpose**: Packaged Kubernetes deployment configuration that defines the application's services, deployments, and configurations

**Fields**:
- **id**: UUID (Primary Key)
- **name**: String (e.g., "todo-app")
- **version**: String (e.g., "1.0.0")
- **description**: String
- **app_version**: String
- **created_at**: Timestamp
- **last_updated**: Timestamp
- **status**: Enum ("validating", "valid", "invalid")

**Relationships**:
- Contains: Deployment templates
- Contains: Service templates
- Contains: Configuration templates

### Minikube Cluster
**Purpose**: Local Kubernetes environment where the Todo AI Chatbot will be deployed and demonstrated

**Fields**:
- **id**: UUID (Primary Key)
- **name**: String (e.g., "local-dev")
- **status**: Enum ("running", "stopped", "error")
- **cpus**: Integer (allocated CPU cores)
- **memory**: Integer (allocated memory in MB)
- **disk_size**: Integer (allocated disk space in MB)
- **kubernetes_version**: String
- **created_at**: Timestamp

**Relationships**:
- Hosts: Kubernetes Deployments
- Hosts: Kubernetes Services

### Kubernetes Deployment
**Purpose**: Kubernetes deployment resources for frontend and backend applications

**Fields**:
- **id**: UUID (Primary Key)
- **name**: String (e.g., "todo-backend-deployment")
- **replicas**: Integer (desired replica count)
- **image**: String (container image reference)
- **container_port**: Integer (exposed port)
- **created_at**: Timestamp
- **last_updated**: Timestamp
- **status**: Enum ("pending", "running", "failed", "updating")

**Relationships**:
- Part of: Helm Chart
- Uses: Container Image
- Associated with: Minikube Cluster

### Kubernetes Service
**Purpose**: Kubernetes service resources for exposing frontend and backend applications

**Fields**:
- **id**: UUID (Primary Key)
- **name**: String (e.g., "todo-backend-service")
- **type**: Enum ("ClusterIP", "NodePort", "LoadBalancer")
- **port**: Integer (service port)
- **target_port**: Integer (container port)
- **protocol**: Enum ("TCP", "UDP")
- **created_at**: Timestamp
- **status**: Enum ("pending", "active", "failed")

**Relationships**:
- Part of: Helm Chart
- Exposes: Kubernetes Deployment
- Associated with: Minikube Cluster

## Validation Rules

### Container Images
- **name**: Must follow Docker naming conventions
- **tag**: Must be valid semantic version or "latest"
- **size**: Must be reasonable for application type
- **status**: Must reflect actual build state

### Helm Chart
- **name**: Must be unique within namespace
- **version**: Must follow semantic versioning
- **status**: Must be "valid" for deployment

### Minikube Cluster
- **cpus**: Must be within host machine capabilities
- **memory**: Must be within host machine capabilities
- **status**: Must be "running" for deployment operations

### Kubernetes Deployments
- **replicas**: Must be positive integer
- **image**: Must reference existing container image
- **status**: Must reflect actual deployment state

### Kubernetes Services
- **type**: Must be valid service type
- **port**: Must be within valid port range
- **target_port**: Must match container port

## State Transitions

### Container Images
- **building** → **built**: When image build completes successfully
- **building** → **failed**: When image build fails
- **built** → **failed**: When image verification fails

### Helm Chart
- **validating** → **valid**: When chart passes validation
- **validating** → **invalid**: When chart validation fails
- **valid** → **invalid**: When chart becomes invalid due to changes

### Minikube Cluster
- **stopped** → **running**: When cluster starts successfully
- **running** → **error**: When cluster encounters critical issues
- **error** → **running**: When cluster recovers from error state

### Kubernetes Deployments
- **pending** → **running**: When deployment becomes ready
- **pending** → **failed**: When deployment fails to become ready
- **running** → **updating**: When deployment is being updated
- **updating** → **running**: When deployment update completes
- **updating** → **failed**: When deployment update fails

### Kubernetes Services
- **pending** → **active**: When service becomes ready
- **pending** → **failed**: When service fails to become ready

## API Contracts

### Container Image Management
- **POST /api/container-images** - Create new container image
- **GET /api/container-images/{id}** - Get container image details
- **PUT /api/container-images/{id}** - Update container image
- **DELETE /api/container-images/{id}** - Delete container image

### Helm Chart Management
- **POST /api/helm-charts** - Create new Helm chart
- **GET /api/helm-charts/{id}** - Get Helm chart details
- **PUT /api/helm-charts/{id}** - Update Helm chart
- **DELETE /api/helm-charts/{id}** - Delete Helm chart

### Minikube Cluster Management
- **GET /api/minikube-clusters/{id}** - Get cluster status
- **POST /api/minikube-clusters/{id}/start** - Start cluster
- **POST /api/minikube-clusters/{id}/stop** - Stop cluster
- **POST /api/minikube-clusters/{id}/restart** - Restart cluster

### Kubernetes Deployment Management
- **POST /api/deployments** - Create deployment
- **GET /api/deployments/{id}** - Get deployment status
- **PUT /api/deployments/{id}** - Update deployment
- **DELETE /api/deployments/{id}** - Delete deployment
- **POST /api/deployments/{id}/scale** - Scale deployment

### Kubernetes Service Management
- **POST /api/services** - Create service
- **GET /api/services/{id}** - Get service status
- **PUT /api/services/{id}** - Update service
- **DELETE /api/services/{id}** - Delete service

## Integration Points

### With Docker AI (Gordon)
- **Image Building**: Docker AI generates optimized Dockerfiles
- **Image Optimization**: AI recommendations for image size reduction
- **Build Validation**: AI validation of build processes

### With kubectl-ai
- **Deployment Operations**: AI-assisted Kubernetes commands
- **Scaling Operations**: Intelligent scaling recommendations
- **Debugging Operations**: AI-powered troubleshooting

### With Kagent
- **Cluster Health**: AI analysis of cluster state
- **Resource Optimization**: AI recommendations for resource allocation
- **Performance Monitoring**: AI-powered performance insights

## Security Considerations

### Container Security
- **Non-root Users**: All containers run as non-root users
- **Image Scanning**: Regular security scanning of container images
- **Vulnerability Management**: Tracking and addressing security vulnerabilities

### Kubernetes Security
- **RBAC**: Proper role-based access control
- **Network Policies**: Network segmentation and security
- **Pod Security**: Pod security policies and contexts

### Data Protection
- **Secrets Management**: Secure handling of sensitive data
- **Encryption**: Data encryption at rest and in transit
- **Access Control**: Proper authentication and authorization

## Performance Considerations

### Container Performance
- **Resource Limits**: Appropriate CPU and memory limits
- **Health Checks**: Regular health check endpoints
- **Readiness Probes**: Proper readiness probe configurations

### Kubernetes Performance
- **Resource Requests**: Appropriate resource requests
- **Pod Affinity**: Optimal pod placement
- **Service Mesh**: Optional service mesh for advanced routing

## Monitoring and Observability

### Metrics Collection
- **Container Metrics**: CPU, memory, disk, network usage
- **Application Metrics**: Custom application metrics
- **Business Metrics**: Business-relevant metrics

### Logging
- **Structured Logging**: JSON-formatted logs
- **Log Aggregation**: Centralized log collection
- **Log Retention**: Appropriate log retention policies

### Alerting
- **Health Alerts**: Pod and service health alerts
- **Performance Alerts**: Performance degradation alerts
- **Security Alerts**: Security-related alerts