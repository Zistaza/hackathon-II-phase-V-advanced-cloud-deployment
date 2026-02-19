# Implementation Plan: Phase-V Infrastructure, Deployment & Cloud Architecture

**Branch**: `013-phasev-infra-deployment` | **Date**: 2026-02-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-phasev-infra-deployment/spec.md`

## Summary

Transform the existing fully functional task management application into a production-ready, event-driven, cloud-native distributed system. Implement Kafka-based event architecture with Dapr integration, deploy to Minikube (local) and Oracle Cloud Always Free tier, establish CI/CD pipeline with GitHub Actions, and configure comprehensive monitoring with Prometheus/Grafana. The system will process task events asynchronously, handle reminders via Dapr Jobs API, support recurring tasks, and maintain 99.9% uptime with horizontal scalability.

**Technical Approach**: Event-driven architecture using Kafka for async communication, Dapr sidecars for cloud-native abstractions (Pub/Sub, State, Bindings, Secrets, Service Invocation), Kubernetes for orchestration (Minikube local, Oracle Cloud production), Helm charts for deployment automation, GitHub Actions for CI/CD, and Prometheus/Grafana for observability.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.0+ (frontend), Bash (deployment scripts)
**Primary Dependencies**:
- Backend: FastAPI, Dapr SDK, Kafka-Python, SQLModel, Pydantic, PyJWT, Prometheus-client
- Frontend: Next.js 16+, React 18+, OpenAI ChatKit
- Infrastructure: Kubernetes 1.25+, Dapr 1.12+, Helm 3, Kafka/Redpanda, Prometheus, Grafana
**Storage**: Neon Serverless PostgreSQL (primary), Dapr State Store (event processing state), Kafka (event streams)
**Testing**: pytest (backend), Jest (frontend), kubectl (deployment validation), Dapr CLI (component testing)
**Target Platform**: Kubernetes (Minikube for local, Oracle Cloud Always Free for production)
**Project Type**: Web application with event-driven microservices architecture
**Performance Goals**:
- 100 events/sec processing with 99% success rate
- <500ms event processing latency (p95)
- 1000 concurrent users without degradation
- <1 minute reminder delivery accuracy (99%)
**Constraints**:
- Oracle Cloud Always Free tier limits (2 OCPUs, 12GB RAM, 100GB storage)
- Must work on Minikube before cloud deployment
- Infrastructure as code (no manual configuration)
- Zero duplicate event processing (100% idempotency)
**Scale/Scope**:
- 6 Kubernetes deployments (frontend, backend, event-processor, reminder-scheduler, notification-service, websocket-service)
- 3 Kafka topics (task-events, reminders, task-updates)
- 5 Dapr components (Pub/Sub, State Store, Bindings, Secrets, Service Invocation)
- 2 deployment environments (Minikube, Oracle Cloud)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Event-Driven Architecture Compliance
- [x] All state changes emit events to appropriate Kafka topics (task-events, reminders, task-updates)
- [x] Event schemas include: event_id, event_type, user_id, timestamp, payload
- [x] No direct service-to-service API calls (use events or Dapr Service Invocation)

### Dapr Integration Compliance
- [x] Pub/Sub component configured for Kafka/Redpanda
- [x] State Management component configured for Postgres/Neon DB
- [x] Jobs API configured for reminder scheduling
- [x] Secrets Management configured (no hardcoded secrets)
- [x] Service Invocation configured with mTLS

### Security & Multi-Tenancy Compliance
- [x] All endpoints require JWT authentication (existing implementation)
- [x] All database queries filtered by authenticated user_id (existing implementation)
- [x] All event handlers validate user ownership (new requirement)
- [x] Service-to-service communication authenticated (JWT/API keys/RBAC)

### Advanced Features Compliance
- [x] Recurring tasks: task.completed events trigger next instance creation
- [x] Due dates & reminders: Dapr Jobs API schedules reminder triggers
- [x] Priorities, tags, search, filter, sort: indexed queries only (existing implementation)

### Deployment & Observability Compliance
- [x] Works on Minikube (local) before cloud deployment
- [x] Helm charts with parameterized values.yaml
- [x] Prometheus metrics and Grafana dashboards configured
- [x] Centralized logging (Loki/OpenSearch) configured
- [x] CI/CD pipeline automated (GitHub Actions)

### Validation & Error Prevention Compliance
- [x] All event handlers are idempotent (use event_id for deduplication)
- [x] Schema validation at event publish and consume
- [x] Strict type checking with Pydantic models (existing implementation)
- [x] Exception handling with retry logic and dead-letter queues

**Gate Status**: ✅ PASS - All constitution requirements aligned with implementation plan

## Project Structure

### Documentation (this feature)

```text
specs/013-phasev-infra-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - architectural decisions
├── data-model.md        # Phase 1 output - event schemas and entities
├── quickstart.md        # Phase 1 output - deployment guide
├── contracts/           # Phase 1 output - API and event contracts
│   ├── events.yaml      # Event schemas (task.created, task.updated, etc.)
│   ├── dapr-components.yaml  # Dapr component configurations
│   └── k8s-resources.yaml    # Kubernetes resource definitions
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Infrastructure and deployment configurations
k8s/
├── base/                # Base Kubernetes manifests
│   ├── namespace.yaml
│   ├── frontend-deployment.yaml
│   ├── backend-deployment.yaml
│   ├── event-processor-deployment.yaml
│   ├── reminder-scheduler-deployment.yaml
│   ├── notification-service-deployment.yaml
│   └── websocket-service-deployment.yaml
├── local/               # Minikube-specific overlays
│   ├── kustomization.yaml
│   ├── ingress.yaml
│   └── dapr-components/
│       ├── pubsub.yaml
│       ├── statestore.yaml
│       ├── bindings.yaml
│       └── secrets.yaml
└── cloud/               # Oracle Cloud-specific overlays
    ├── kustomization.yaml
    ├── ingress.yaml
    └── dapr-components/
        ├── pubsub.yaml
        ├── statestore.yaml
        ├── bindings.yaml
        └── secrets.yaml

helm/
├── todo-app/            # Helm chart for entire application
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-local.yaml
│   ├── values-cloud.yaml
│   └── templates/
│       ├── frontend.yaml
│       ├── backend.yaml
│       ├── event-processor.yaml
│       ├── reminder-scheduler.yaml
│       ├── notification-service.yaml
│       ├── websocket-service.yaml
│       ├── dapr-components.yaml
│       └── ingress.yaml
└── monitoring/          # Helm chart for monitoring stack
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── prometheus.yaml
        ├── grafana.yaml
        └── dashboards/

.github/
└── workflows/
    ├── ci.yaml          # Build and test workflow
    ├── deploy-local.yaml    # Deploy to Minikube
    └── deploy-cloud.yaml    # Deploy to Oracle Cloud

# Backend event processing services
backend/
├── src/
│   ├── events/          # Event publishing and consumption
│   │   ├── publishers.py
│   │   ├── consumers.py
│   │   ├── schemas.py
│   │   └── handlers.py
│   ├── services/
│   │   ├── event_processor.py
│   │   ├── reminder_scheduler.py
│   │   └── notification_service.py
│   └── dapr/            # Dapr integration
│       ├── pubsub.py
│       ├── state.py
│       ├── bindings.py
│       └── secrets.py
└── tests/
    ├── events/
    └── dapr/

# Frontend (existing structure, minimal changes)
frontend/
└── src/
    └── services/
        └── websocket.ts  # WebSocket client for real-time updates

# Deployment scripts
scripts/
├── deploy-local.sh      # Deploy to Minikube
├── deploy-cloud.sh      # Deploy to Oracle Cloud
├── setup-dapr.sh        # Install Dapr on cluster
├── setup-monitoring.sh  # Install Prometheus/Grafana
└── validate-deployment.sh  # Verify deployment health

# Monitoring configurations
monitoring/
├── prometheus/
│   ├── prometheus.yaml
│   └── alerts.yaml
└── grafana/
    └── dashboards/
        ├── task-operations.json
        ├── event-processing.json
        └── reminder-scheduling.json
```

**Structure Decision**: Web application with event-driven microservices. Infrastructure configurations organized by environment (local/cloud) using Kustomize overlays and Helm charts. Event processing services added to backend. Monitoring stack separated for independent deployment.

## Complexity Tracking

> No constitution violations requiring justification. All requirements align with Phase V constitution standards.

## Phase 0: Research & Architectural Decisions

**Objective**: Resolve all architectural decisions and technology choices before implementation.

### Research Tasks

1. **Kafka vs Cloud-Managed Pub/Sub**
   - Research: Kafka self-hosted (Strimzi operator) vs Confluent Cloud vs Redpanda Cloud vs alternative Dapr PubSub
   - Decision criteria: Oracle Cloud Always Free compatibility, message retention, throughput limits, operational overhead
   - Output: Selected message broker with justification

2. **Oracle Cloud Kubernetes Options**
   - Research: OKE (Oracle Kubernetes Engine) vs k3s on Compute instances vs MicroK8s
   - Decision criteria: Always Free tier compatibility, resource limits, operational complexity
   - Output: Selected Kubernetes platform with provisioning strategy

3. **Ingress Controller Selection**
   - Research: Nginx Ingress vs Traefik vs Oracle Cloud Load Balancer
   - Decision criteria: SSL/TLS support, resource usage, Oracle Cloud compatibility
   - Output: Selected ingress controller with configuration approach

4. **Secret Management Strategy**
   - Research: Dapr Secrets component vs Kubernetes Secrets vs Oracle Cloud Vault
   - Decision criteria: Security, ease of rotation, Oracle Cloud integration
   - Output: Selected secret management approach with rotation strategy

5. **CI/CD Deployment Strategy**
   - Research: Push-based (GitHub Actions kubectl apply) vs Pull-based (ArgoCD/Flux)
   - Decision criteria: Complexity, GitHub Actions free tier limits, rollback capabilities
   - Output: Selected deployment strategy with rollback mechanism

6. **Monitoring Stack Location**
   - Research: In-cluster (Prometheus/Grafana pods) vs managed (Oracle Cloud Monitoring)
   - Decision criteria: Resource usage within Always Free limits, data retention, alerting capabilities
   - Output: Selected monitoring approach with resource allocation

7. **Event Processing Patterns**
   - Research: Single event processor vs multiple specialized consumers vs event sourcing
   - Decision criteria: Complexity, scalability, idempotency guarantees
   - Output: Selected event processing architecture with idempotency strategy

8. **Dapr State Store Backend**
   - Research: PostgreSQL vs Redis vs Oracle Cloud Object Storage
   - Decision criteria: Persistence requirements, performance, Always Free compatibility
   - Output: Selected state store with configuration

**Deliverable**: `research.md` with all decisions documented (Decision, Rationale, Alternatives Considered)

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete with all architectural decisions resolved

### 1.1 Event Schema Design

**Objective**: Define all event schemas for Kafka topics

**Entities**:
- **TaskEvent**: Represents task lifecycle events (created, updated, completed, deleted)
- **ReminderEvent**: Represents reminder triggers
- **TaskUpdateEvent**: Represents real-time task state changes for WebSocket

**Event Schemas** (to be detailed in `data-model.md`):
```yaml
TaskEvent:
  event_id: UUID (for idempotency)
  event_type: enum [task.created, task.updated, task.completed, task.deleted]
  user_id: string
  timestamp: ISO 8601
  payload:
    task_id: UUID
    title: string (optional, for created/updated)
    description: string (optional)
    priority: enum [low, medium, high, urgent] (optional)
    tags: array<string> (optional)
    due_date: ISO 8601 (optional)
    recurrence_rule: string (optional, for recurring tasks)
    changes: object (optional, for updated events)
    completed_at: ISO 8601 (optional, for completed events)

ReminderEvent:
  event_id: UUID
  event_type: reminder.due
  user_id: string
  timestamp: ISO 8601
  payload:
    reminder_id: UUID
    task_id: UUID
    reminder_time: ISO 8601

TaskUpdateEvent:
  event_id: UUID
  event_type: task.update
  user_id: string
  timestamp: ISO 8601
  payload:
    task_id: UUID
    update_type: enum [status, priority, tags, due_date]
    changes: object
```

### 1.2 Dapr Component Configurations

**Objective**: Define Dapr component configurations for local and cloud environments

**Components** (to be detailed in `contracts/dapr-components.yaml`):
1. **Pub/Sub Component**: Kafka/Redpanda configuration with topic subscriptions
2. **State Store Component**: PostgreSQL configuration for event processing state
3. **Bindings Component**: Cron configuration for reminder scheduling
4. **Secrets Component**: Kubernetes Secrets or Oracle Cloud Vault configuration
5. **Service Invocation**: mTLS configuration for inter-service communication

### 1.3 Kubernetes Resource Definitions

**Objective**: Define Kubernetes deployments, services, and ingress configurations

**Resources** (to be detailed in `contracts/k8s-resources.yaml`):
1. **Deployments**: Frontend, Backend, Event Processor, Reminder Scheduler, Notification Service, WebSocket Service
2. **Services**: ClusterIP services for internal communication, LoadBalancer for ingress
3. **Ingress**: HTTP/HTTPS routing with SSL/TLS termination
4. **ConfigMaps**: Environment-specific configurations
5. **Secrets**: Database credentials, API keys, JWT secrets

### 1.4 CI/CD Pipeline Definition

**Objective**: Define GitHub Actions workflows for automated deployment

**Workflows** (to be detailed in `contracts/`):
1. **CI Workflow**: Build, lint, test on every PR
2. **Deploy Local Workflow**: Deploy to Minikube on feature branch push
3. **Deploy Cloud Workflow**: Deploy to Oracle Cloud on main branch merge

### 1.5 Monitoring Configuration

**Objective**: Define Prometheus metrics and Grafana dashboards

**Metrics** (to be detailed in `contracts/`):
1. **Task Operations**: task_created_total, task_completed_total, task_deleted_total
2. **Event Processing**: events_published_total, events_consumed_total, event_processing_latency
3. **Reminder Scheduling**: reminders_scheduled_total, reminders_delivered_total, reminder_delivery_latency
4. **System Health**: pod_restarts_total, pod_cpu_usage, pod_memory_usage

**Dashboards**:
1. **Task Operations Dashboard**: Task creation rate, completion rate, active tasks
2. **Event Processing Dashboard**: Event throughput, processing latency, error rate
3. **Reminder Scheduling Dashboard**: Scheduled reminders, delivered reminders, delivery accuracy

### 1.6 Quickstart Guide

**Objective**: Create step-by-step deployment guide for both environments

**Sections** (to be detailed in `quickstart.md`):
1. **Prerequisites**: Required tools (kubectl, Dapr CLI, Helm, Minikube)
2. **Local Deployment**: Minikube setup, Dapr installation, application deployment
3. **Cloud Deployment**: Oracle Cloud setup, cluster provisioning, application deployment
4. **Verification**: Health checks, smoke tests, monitoring validation
5. **Troubleshooting**: Common issues and solutions

**Deliverable**: `data-model.md`, `contracts/`, `quickstart.md`

## Phase 2: Implementation Phases

**Note**: Detailed tasks will be generated by `/sp.tasks` command. This section provides high-level implementation phases.

### Phase 2.1: Event-Driven Architecture Foundation

**Objective**: Implement Kafka-based event architecture with producers and consumers

**Key Components**:
1. Event publishers in backend API (task.created, task.updated, task.completed, task.deleted)
2. Event consumers for recurring tasks, reminders, and audit logging
3. Event schema validation using Pydantic models
4. Idempotency handling using event_id and Dapr State Store
5. Retry logic with exponential backoff
6. Dead-letter queue for failed events

**Acceptance Criteria**:
- Events published successfully to Kafka topics
- Consumers process events with 99% success rate
- Duplicate events detected and skipped (100% idempotency)
- Failed events routed to dead-letter queue

### Phase 2.2: Dapr Integration

**Objective**: Integrate Dapr building blocks into all services

**Key Components**:
1. Dapr Pub/Sub component configuration (Kafka/Redpanda)
2. Dapr State Store component configuration (PostgreSQL)
3. Dapr Bindings component configuration (cron for reminders)
4. Dapr Secrets component configuration (Kubernetes Secrets)
5. Dapr Service Invocation for inter-service communication
6. Sidecar injection annotations in Kubernetes deployments

**Acceptance Criteria**:
- Dapr sidecars running alongside all services
- Pub/Sub messages flowing through Dapr
- State persisted and retrievable via Dapr State Store
- Cron bindings triggering reminder events
- Secrets retrieved securely via Dapr Secrets

### Phase 2.3: Local Deployment (Minikube)

**Objective**: Deploy entire system on Minikube with full functionality

**Key Components**:
1. Minikube cluster setup with sufficient resources
2. Dapr installation on Minikube
3. Kafka/Redpanda deployment (Helm chart or Docker)
4. Application deployment using Helm charts
5. Ingress configuration for local access
6. Monitoring stack deployment (Prometheus/Grafana)

**Acceptance Criteria**:
- All pods running and healthy
- Application accessible via ingress (http://localhost or minikube IP)
- Events flowing through Kafka
- Reminders scheduled and delivered
- Metrics visible in Grafana dashboards

### Phase 2.4: Oracle Cloud Deployment

**Objective**: Deploy system to Oracle Cloud Always Free tier

**Key Components**:
1. Oracle Cloud account setup and cluster provisioning
2. Dapr installation on Oracle Cloud cluster
3. External Kafka connection (Confluent/Redpanda Cloud or alternative)
4. Application deployment using Helm charts with cloud-specific values
5. Ingress configuration with SSL/TLS
6. Secret management using Oracle Cloud Vault or Kubernetes Secrets
7. Resource limits and requests configured for Always Free tier

**Acceptance Criteria**:
- Cluster running within Always Free limits (2 OCPUs, 12GB RAM)
- Application accessible via public HTTPS endpoint
- Events flowing through external Kafka
- Secrets managed securely
- Resource usage monitored and within limits

### Phase 2.5: CI/CD Pipeline

**Objective**: Automate build, test, and deployment workflows

**Key Components**:
1. GitHub Actions workflow for CI (build, lint, test)
2. Docker image build and push to registry
3. Automated deployment to Minikube (optional, for testing)
4. Automated deployment to Oracle Cloud (production)
5. Rollback mechanism for failed deployments
6. Secrets management in GitHub Secrets

**Acceptance Criteria**:
- CI workflow runs on every PR
- Docker images built and pushed successfully
- Deployment triggered on main branch merge
- Rollback works when deployment fails
- Secrets never exposed in logs

### Phase 2.6: Monitoring & Observability

**Objective**: Configure comprehensive monitoring and logging

**Key Components**:
1. Prometheus metrics exposure in all services
2. Grafana dashboards for task operations, event processing, reminders
3. Alerting rules for critical metrics
4. Centralized logging (Loki or OpenSearch)
5. Health checks and readiness probes
6. Dapr metrics integration

**Acceptance Criteria**:
- Metrics scraped successfully by Prometheus
- Dashboards display real-time data
- Alerts trigger under simulated failures
- Logs aggregated and searchable
- Health checks prevent traffic to unhealthy pods

## Testing Strategy

### Architecture Validation Tests

**Objective**: Verify event-driven architecture works correctly

**Tests**:
1. **Event Publishing Test**: Verify task.created event published when task created
2. **Event Consumption Test**: Verify consumers receive and process events
3. **Idempotency Test**: Verify duplicate events are detected and skipped
4. **Failure Recovery Test**: Verify system recovers from Kafka unavailability
5. **Ordering Test**: Verify events processed in correct order per user

**Acceptance Criteria**: All tests pass with 99% success rate

### Dapr Validation Tests

**Objective**: Verify Dapr building blocks work correctly

**Tests**:
1. **Pub/Sub Test**: Publish message via Dapr, verify consumption
2. **State Persistence Test**: Save state via Dapr, verify retrieval after pod restart
3. **Cron Binding Test**: Verify cron binding triggers at scheduled time
4. **Service Invocation Test**: Verify service-to-service call via Dapr
5. **Secret Retrieval Test**: Verify secrets retrieved securely via Dapr

**Acceptance Criteria**: All Dapr components functional in both local and cloud environments

### Local Deployment Validation Tests

**Objective**: Verify Minikube deployment works correctly

**Tests**:
1. **Pod Health Test**: Verify all pods running and healthy
2. **Ingress Test**: Verify application accessible via ingress
3. **Dapr Sidecar Test**: Verify Dapr sidecars running alongside services
4. **End-to-End Test**: Create task, verify event published, verify reminder scheduled

**Acceptance Criteria**: Full application functionality on Minikube

### Cloud Deployment Validation Tests

**Objective**: Verify Oracle Cloud deployment works correctly

**Tests**:
1. **Public Endpoint Test**: Verify application accessible via HTTPS
2. **Cluster Health Test**: Verify all pods running within resource limits
3. **Resource Usage Test**: Verify CPU/memory usage within Always Free limits
4. **Pub/Sub Test**: Verify events flowing through external Kafka
5. **Secret Security Test**: Verify secrets not exposed in logs or environment

**Acceptance Criteria**: Production-ready deployment on Oracle Cloud

### CI/CD Validation Tests

**Objective**: Verify CI/CD pipeline works correctly

**Tests**:
1. **Pipeline Trigger Test**: Verify pipeline triggers on PR and merge
2. **Build Test**: Verify Docker images built successfully
3. **Deployment Test**: Verify deployment updates cluster
4. **Rollback Test**: Verify rollback restores previous version
5. **Secret Management Test**: Verify secrets handled securely

**Acceptance Criteria**: Fully automated deployment with rollback capability

### Monitoring Validation Tests

**Objective**: Verify monitoring and logging work correctly

**Tests**:
1. **Metrics Scraping Test**: Verify Prometheus scrapes metrics
2. **Dashboard Test**: Verify Grafana dashboards display data
3. **Alert Test**: Verify alerts trigger under simulated failure
4. **Log Aggregation Test**: Verify logs searchable in central location
5. **Health Check Test**: Verify unhealthy pods restarted automatically

**Acceptance Criteria**: Full observability into system health and performance

## Quality Validation

### Infrastructure Reproducibility

**Validation**:
- Deploy to fresh Minikube cluster from scratch
- Deploy to fresh Oracle Cloud cluster from scratch
- Verify both deployments succeed without manual intervention

**Acceptance Criteria**: Deployment reproducible in under 15 minutes (Minikube) and 30 minutes (Oracle Cloud)

### Configuration Separation

**Validation**:
- Verify local and cloud configurations separated
- Verify no hardcoded environment-specific values
- Verify Helm values files parameterize all configurations

**Acceptance Criteria**: Single Helm chart works for both environments with different values files

### Infrastructure as Code

**Validation**:
- Verify all Kubernetes manifests in Git
- Verify all Dapr components in Git
- Verify all CI/CD workflows in Git
- Verify no manual configuration required

**Acceptance Criteria**: 100% of infrastructure defined as code

### Documentation Completeness

**Validation**:
- Follow quickstart guide on fresh machine
- Verify another engineer can deploy without assistance
- Verify troubleshooting guide covers common issues

**Acceptance Criteria**: Deployment successful following documentation alone

## Risk Mitigation

### Risk 1: Oracle Cloud Always Free Tier Resource Limits

**Mitigation**:
- Configure resource limits and requests in Kubernetes manifests
- Implement horizontal pod autoscaling with max replicas
- Monitor resource usage continuously
- Document scaling limitations in quickstart guide

### Risk 2: External Kafka Service Limits

**Mitigation**:
- Configure alternative Dapr PubSub component as fallback
- Implement local message queuing for transient failures
- Monitor message retention and throughput
- Document Kafka provider selection in research.md

### Risk 3: Dapr Sidecar Resource Overhead

**Mitigation**:
- Optimize Dapr configuration (disable unnecessary features)
- Monitor sidecar resource usage
- Configure resource limits for sidecars
- Document resource allocation in Helm values

### Risk 4: CI/CD Pipeline GitHub Actions Free Tier Minutes

**Mitigation**:
- Optimize build steps (cache dependencies)
- Use matrix builds sparingly
- Consider self-hosted runners if needed
- Monitor GitHub Actions usage

### Risk 5: SSL Certificate Provisioning on Oracle Cloud

**Mitigation**:
- Document manual certificate installation steps
- Use Let's Encrypt with cert-manager
- Test certificate renewal process
- Provide fallback to HTTP for testing

### Risk 6: Network Latency Between Oracle Cloud and External Kafka

**Mitigation**:
- Choose Kafka provider in same region as Oracle Cloud
- Implement retry logic with exponential backoff
- Monitor event processing latency
- Document latency expectations in quickstart guide

### Risk 7: Monitoring Stack Resource Consumption

**Mitigation**:
- Configure metric retention limits
- Use lightweight Prometheus exporters
- Consider external monitoring service if needed
- Monitor monitoring stack resource usage

### Risk 8: Kubernetes Cluster Provisioning Failure on Oracle Cloud

**Mitigation**:
- Document manual cluster creation steps
- Provide alternative lightweight Kubernetes distribution (k3s)
- Test cluster provisioning process
- Document quota limits and workarounds

## Next Steps

1. **Execute Phase 0**: Run research tasks to resolve all architectural decisions → `research.md`
2. **Execute Phase 1**: Design event schemas, Dapr components, and Kubernetes resources → `data-model.md`, `contracts/`, `quickstart.md`
3. **Run `/sp.tasks`**: Generate actionable, dependency-ordered tasks for implementation
4. **Begin Implementation**: Start with Phase 2.1 (Event-Driven Architecture Foundation)
5. **Validate Incrementally**: Test each phase independently before proceeding
6. **Deploy to Minikube**: Validate local deployment before cloud deployment
7. **Deploy to Oracle Cloud**: Validate production deployment
8. **Configure CI/CD**: Automate deployment pipeline
9. **Configure Monitoring**: Enable observability
10. **Production Readiness**: Validate all success criteria from spec.md

**Command to proceed**: `/sp.tasks` (after this plan is approved)
