# Tasks: Phase-V Infrastructure, Deployment & Cloud Architecture

**Input**: Design documents from `/specs/013-phasev-infra-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- **Infrastructure**: `k8s/`, `helm/`, `.github/workflows/`
- **Scripts**: `scripts/`
- **Monitoring**: `monitoring/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure

- [x] T001 Create infrastructure directory structure (k8s/base/, k8s/local/, k8s/cloud/, helm/, scripts/, monitoring/)
- [x] T002 [P] Create backend event processing directory structure (backend/src/events/, backend/src/dapr/, backend/src/services/)
- [x] T003 [P] Install backend dependencies (dapr-sdk, kafka-python, prometheus-client) in backend/requirements.txt
- [x] T004 [P] Create deployment scripts directory and base scripts (scripts/deploy-local.sh, scripts/deploy-cloud.sh, scripts/setup-dapr.sh)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Event Schema Foundation

- [x] T005 [P] Create base event schema with Pydantic models in backend/src/events/schemas.py (BaseEvent, EventMetadata)
- [x] T006 [P] Create TaskEvent schemas in backend/src/events/schemas.py (TaskCreatedEvent, TaskUpdatedEvent, TaskCompletedEvent, TaskDeletedEvent)
- [x] T007 [P] Create ReminderEvent schemas in backend/src/events/schemas.py (ReminderScheduledEvent, ReminderDueEvent, ReminderCancelledEvent)
- [x] T008 [P] Create TaskRecurrenceEvent schema in backend/src/events/schemas.py
- [x] T009 [P] Create TaskUpdateEvent schema for WebSocket in backend/src/events/schemas.py

### Dapr Component Configuration

- [x] T010 [P] Create Dapr Pub/Sub component for local (Redis) in k8s/local/dapr-components/pubsub.yaml
- [x] T011 [P] Create Dapr Pub/Sub component for cloud (Redpanda) in k8s/cloud/dapr-components/pubsub.yaml
- [x] T012 [P] Create Dapr State Store component (PostgreSQL) in k8s/local/dapr-components/statestore.yaml and k8s/cloud/dapr-components/statestore.yaml
- [x] T013 [P] Create Dapr Bindings component (cron) in k8s/local/dapr-components/bindings.yaml and k8s/cloud/dapr-components/bindings.yaml
- [x] T014 [P] Create Dapr Secrets component (Kubernetes Secrets) in k8s/local/dapr-components/secrets.yaml and k8s/cloud/dapr-components/secrets.yaml
- [x] T015 [P] Create Dapr Configuration with tracing and metrics in k8s/local/dapr-components/config.yaml and k8s/cloud/dapr-components/config.yaml
- [x] T016 [P] Create Dapr Subscription configurations for all topics in k8s/base/dapr-subscriptions.yaml
- [x] T017 [P] Create Dapr Resiliency policy with retry and circuit breaker in k8s/base/dapr-resiliency.yaml

### Kubernetes Base Resources

- [x] T018 Create namespace definition in k8s/base/namespace.yaml
- [x] T019 [P] Create backend deployment with Dapr annotations in k8s/base/backend-deployment.yaml
- [x] T020 [P] Create event-processor deployment with Dapr annotations in k8s/base/event-processor-deployment.yaml
- [x] T021 [P] Create reminder-scheduler deployment with Dapr annotations in k8s/base/reminder-scheduler-deployment.yaml
- [x] T022 [P] Create notification-service deployment with Dapr annotations in k8s/base/notification-service-deployment.yaml
- [x] T023 [P] Create websocket-service deployment with Dapr annotations in k8s/base/websocket-service-deployment.yaml
- [x] T024 [P] Create frontend deployment in k8s/base/frontend-deployment.yaml
- [x] T025 [P] Create ClusterIP services for all deployments in k8s/base/services.yaml
- [x] T026 [P] Create ConfigMap for application configuration in k8s/base/configmap.yaml
- [x] T027 [P] Create HorizontalPodAutoscaler for backend and event-processor in k8s/base/hpa.yaml
- [x] T028 [P] Create ResourceQuota for Oracle Cloud Always Free limits in k8s/base/resourcequota.yaml
- [x] T029 [P] Create NetworkPolicy for backend security in k8s/base/networkpolicy.yaml
- [x] T030 [P] Create PodDisruptionBudget for high availability in k8s/base/pdb.yaml

### Ingress Configuration

- [x] T031 [P] Create local ingress (HTTP) for Minikube in k8s/local/ingress.yaml
- [x] T032 [P] Create cloud ingress (HTTPS with TLS) for Oracle Cloud in k8s/cloud/ingress.yaml

### Base Event Infrastructure

- [x] T033 Create idempotent event handler base class in backend/src/events/handlers.py
- [x] T034 [P] Implement Dapr Pub/Sub publisher in backend/src/dapr/pubsub.py
- [x] T035 [P] Implement Dapr State Store client in backend/src/dapr/state.py
- [x] T036 [P] Implement Dapr Bindings client in backend/src/dapr/bindings.py
- [x] T037 [P] Implement Dapr Secrets client in backend/src/dapr/secrets.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Event-Driven Architecture Implementation (Priority: P1) 🎯 MVP

**Goal**: Implement Kafka-based event-driven architecture with producers and consumers for task operations, reminders, and recurring tasks

**Independent Test**: Publish task events to Kafka topics and verify consumers process them correctly with idempotency guarantees

### Implementation for User Story 1

- [x] T038 [P] [US1] Implement event publisher for task.created in backend/src/events/publishers.py
- [x] T039 [P] [US1] Implement event publisher for task.updated in backend/src/events/publishers.py
- [x] T040 [P] [US1] Implement event publisher for task.completed in backend/src/events/publishers.py
- [x] T041 [P] [US1] Implement event publisher for task.deleted in backend/src/events/publishers.py
- [x] T042 [P] [US1] Integrate event publishing into existing task API endpoints in backend/src/api/tasks.py
- [x] T043 [P] [US1] Create RecurringTaskConsumer service in backend/src/services/event_processor.py
- [x] T044 [P] [US1] Create AuditConsumer service in backend/src/services/event_processor.py
- [x] T045 [US1] Implement idempotency check using Dapr State Store in backend/src/events/handlers.py
- [x] T046 [US1] Implement retry logic with exponential backoff in backend/src/events/handlers.py
- [x] T047 [US1] Implement dead-letter queue routing in backend/src/events/handlers.py
- [x] T048 [US1] Add event publishing to task creation endpoint in backend/src/api/tasks.py
- [x] T049 [US1] Add event publishing to task update endpoint in backend/src/api/tasks.py
- [x] T050 [US1] Add event publishing to task completion endpoint in backend/src/api/tasks.py
- [x] T051 [US1] Add event publishing to task deletion endpoint in backend/src/api/tasks.py
- [x] T052 [US1] Implement recurring task creation logic in RecurringTaskConsumer
- [x] T053 [US1] Add Prometheus metrics for event publishing in backend/src/events/publishers.py
- [x] T054 [US1] Add Prometheus metrics for event consumption in backend/src/events/consumers.py

**Checkpoint**: Event-driven architecture functional - events published and consumed with idempotency

---

## Phase 4: User Story 2 - Local Minikube Deployment (Priority: P1)

**Goal**: Deploy entire system on Minikube for local testing before cloud deployment

**Independent Test**: Run deployment scripts on fresh Minikube cluster and verify all services accessible via ingress

### Implementation for User Story 2

- [x] T055 [P] [US2] Create Minikube setup script in scripts/setup-minikube.sh
- [x] T056 [P] [US2] Create Dapr installation script for Minikube in scripts/setup-dapr.sh
- [x] T057 [P] [US2] Create Redis deployment script for local Pub/Sub in scripts/deploy-redis.sh
- [x] T058 [US2] Create local deployment script in scripts/deploy-local.sh
- [x] T059 [US2] Create Kubernetes secrets creation script for local in scripts/create-local-secrets.sh
- [x] T060 [US2] Create deployment validation script in scripts/validate-deployment.sh
- [x] T061 [P] [US2] Create Kustomization file for local environment in k8s/local/kustomization.yaml
- [x] T062 [US2] Test Minikube deployment end-to-end following quickstart.md
- [x] T063 [US2] Verify all pods running with Dapr sidecars (2/2 containers)
- [x] T064 [US2] Verify ingress accessible at http://todo-app.local
- [x] T065 [US2] Verify event flow: create task → event published → consumer processes
- [x] T066 [US2] Document troubleshooting steps in quickstart.md

**Checkpoint**: Local deployment functional - all services running on Minikube

---

## Phase 5: User Story 3 - Dapr Integration (Priority: P1)

**Goal**: Integrate Dapr building blocks for Pub/Sub, state management, secrets, and service invocation

**Independent Test**: Verify each Dapr building block works correctly in isolation

### Implementation for User Story 3

- [x] T067 [P] [US3] Implement Dapr Pub/Sub event publishing in backend/src/dapr/pubsub.py
- [x] T068 [P] [US3] Implement Dapr Pub/Sub event subscription handlers in backend/src/events/consumers.py
- [x] T069 [P] [US3] Implement Dapr State Store save/get/delete operations in backend/src/dapr/state.py
- [x] T070 [P] [US3] Implement Dapr Secrets retrieval in backend/src/dapr/secrets.py
- [x] T071 [P] [US3] Implement Dapr Service Invocation client in backend/src/dapr/invocation.py
- [x] T072 [US3] Integrate Dapr Pub/Sub into event publishers (replace direct Kafka calls)
- [x] T073 [US3] Integrate Dapr State Store into idempotency checks
- [x] T074 [US3] Integrate Dapr Secrets into database connection and JWT secret loading
- [x] T075 [US3] Add Dapr health check endpoints in backend/src/api/health.py
- [x] T076 [US3] Configure Dapr sidecar resource limits in deployment manifests
- [x] T077 [US3] Test Dapr Pub/Sub: publish event via Dapr, verify consumption
- [x] T078 [US3] Test Dapr State Store: save state, restart pod, verify retrieval
- [x] T079 [US3] Test Dapr Bindings: verify cron triggers at scheduled time
- [x] T080 [US3] Test Dapr Secrets: verify secrets retrieved without hardcoding
- [x] T081 [US3] Test Dapr Service Invocation: verify service-to-service calls with retries

**Checkpoint**: Dapr integration complete - all building blocks functional

---

## Phase 6: User Story 4 - Oracle Cloud Deployment (Priority: P2)

**Goal**: Deploy system to Oracle Cloud Always Free tier with public HTTPS endpoint

**Independent Test**: Deploy to Oracle Cloud and verify public endpoint accessible with all features working

### Implementation for User Story 4

- [x] T082 [P] [US4] Create Oracle Cloud provisioning documentation in docs/oracle-cloud-setup.md
- [x] T083 [P] [US4] Create k3s installation script for Oracle Compute in scripts/install-k3s.sh
- [x] T084 [P] [US4] Create Traefik ingress controller installation script in scripts/install-traefik.sh
- [x] T085 [P] [US4] Create cert-manager installation script for SSL/TLS in scripts/install-cert-manager.sh
- [x] T086 [US4] Create cloud deployment script in scripts/deploy-cloud.sh
- [x] T087 [US4] Create Kubernetes secrets creation script for cloud in scripts/create-cloud-secrets.sh
- [x] T088 [US4] Create Redpanda Cloud connection configuration in k8s/cloud/dapr-components/pubsub.yaml
- [x] T089 [P] [US4] Create Kustomization file for cloud environment in k8s/cloud/kustomization.yaml
- [x] T090 [P] [US4] Create ClusterIssuer for Let's Encrypt in k8s/cloud/cert-manager-issuer.yaml
- [x] T091 [US4] Test k3s cluster provisioning on Oracle Compute instances
- [x] T092 [US4] Test Dapr installation on Oracle Cloud cluster
- [x] T093 [US4] Test Redpanda Cloud connection from Oracle Cloud
- [x] T094 [US4] Test SSL certificate issuance via Let's Encrypt
- [x] T095 [US4] Verify public HTTPS endpoint accessible
- [x] T096 [US4] Verify resource usage within Always Free limits (2 OCPU, 12GB RAM)
- [x] T097 [US4] Document cloud deployment procedure in quickstart.md

**Checkpoint**: Cloud deployment functional - application accessible via HTTPS

---

## Phase 7: User Story 5 - CI/CD Pipeline (Priority: P2)

**Goal**: Automate build, test, and deployment workflows with GitHub Actions

**Independent Test**: Push code changes and verify pipeline automatically builds, tests, and deploys

### Implementation for User Story 5

- [x] T098 [P] [US5] Create CI workflow for build and test in .github/workflows/ci.yaml
- [x] T099 [P] [US5] Create Docker build workflow for backend in .github/workflows/docker-backend.yaml
- [x] T100 [P] [US5] Create Docker build workflow for frontend in .github/workflows/docker-frontend.yaml
- [x] T101 [P] [US5] Create Docker build workflow for event-processor in .github/workflows/docker-event-processor.yaml
- [x] T102 [P] [US5] Create Docker build workflow for reminder-scheduler in .github/workflows/docker-reminder-scheduler.yaml
- [x] T103 [P] [US5] Create Docker build workflow for notification-service in .github/workflows/docker-notification-service.yaml
- [x] T104 [P] [US5] Create Docker build workflow for websocket-service in .github/workflows/docker-websocket-service.yaml
- [x] T105 [US5] Create deployment workflow for Minikube in .github/workflows/deploy-local.yaml
- [x] T106 [US5] Create deployment workflow for Oracle Cloud in .github/workflows/deploy-cloud.yaml
- [x] T107 [US5] Configure GitHub Secrets for kubeconfig, registry credentials, and cloud secrets
- [x] T108 [US5] Implement rollback mechanism in deployment workflows
- [x] T109 [US5] Add deployment health checks in workflows
- [x] T110 [US5] Test CI workflow: push code, verify build and test
- [x] T111 [US5] Test Docker build: verify images pushed to registry
- [x] T112 [US5] Test deployment workflow: verify cluster updated
- [x] T113 [US5] Test rollback: trigger failure, verify previous version restored

**Checkpoint**: CI/CD pipeline functional - automated deployment working

---

## Phase 8: User Story 6 - Monitoring & Observability (Priority: P2)

**Goal**: Configure comprehensive monitoring with Prometheus and Grafana for production observability

**Independent Test**: Generate load and verify metrics appear in Prometheus and dashboards display correctly in Grafana

### Implementation for User Story 6

- [x] T114 [P] [US6] Create Prometheus configuration in monitoring/prometheus/prometheus.yaml
- [x] T115 [P] [US6] Create Prometheus alerting rules in monitoring/prometheus/alerts.yaml
- [x] T116 [P] [US6] Create Grafana dashboard for task operations in monitoring/grafana/dashboards/task-operations.json
- [x] T117 [P] [US6] Create Grafana dashboard for event processing in monitoring/grafana/dashboards/event-processing.json
- [x] T118 [P] [US6] Create Grafana dashboard for reminder scheduling in monitoring/grafana/dashboards/reminder-scheduling.json
- [x] T119 [P] [US6] Create Grafana dashboard for system health in monitoring/grafana/dashboards/system-health.json
- [x] T120 [US6] Create monitoring stack installation script in scripts/setup-monitoring.sh
- [x] T121 [US6] Add Prometheus metrics to backend API in backend/src/api/metrics.py
- [x] T122 [US6] Add Prometheus metrics to event processor in backend/src/services/event_processor.py
- [x] T123 [US6] Add Prometheus metrics to reminder scheduler in backend/src/services/reminder_scheduler.py
- [x] T124 [US6] Configure Prometheus scrape configs for all services
- [x] T125 [US6] Configure Grafana data source for Prometheus
- [x] T126 [US6] Test Prometheus metrics scraping from all services
- [x] T127 [US6] Test Grafana dashboards display real-time data
- [x] T128 [US6] Test alerting rules trigger under simulated failure
- [x] T129 [US6] Document monitoring setup in quickstart.md

**Checkpoint**: Monitoring functional - full observability into system health

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [x] T130 [P] Create comprehensive README.md with architecture overview
- [x] T131 [P] Create DEPLOYMENT.md with detailed deployment instructions
- [x] T132 [P] Create TROUBLESHOOTING.md with common issues and solutions
- [x] T133 [P] Create ARCHITECTURE.md with system architecture diagrams
- [x] T134 [P] Update quickstart.md with final validation checklist
- [x] T135 [P] Add code comments and docstrings to event handlers
- [x] T136 [P] Add code comments and docstrings to Dapr clients
- [x] T137 Validate all deployment scripts work on fresh environments
- [x] T138 Run end-to-end validation following quickstart.md
- [x] T139 Verify resource usage within Oracle Cloud Always Free limits
- [x] T140 Create demo video or screenshots for documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Event-Driven Architecture): Can start after Foundational
  - US2 (Local Deployment): Can start after Foundational, benefits from US1 completion
  - US3 (Dapr Integration): Can start after Foundational, integrates with US1
  - US4 (Cloud Deployment): Depends on US2 and US3 completion
  - US5 (CI/CD): Depends on US2 and US4 completion
  - US6 (Monitoring): Can start after Foundational, integrates with all stories
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Event-Driven Architecture)**: Independent - can start after Foundational
- **US2 (Local Deployment)**: Independent - can start after Foundational (benefits from US1 for testing)
- **US3 (Dapr Integration)**: Independent - can start after Foundational (integrates with US1)
- **US4 (Cloud Deployment)**: Depends on US2 (local validation) and US3 (Dapr working)
- **US5 (CI/CD)**: Depends on US2 (local) and US4 (cloud) deployment working
- **US6 (Monitoring)**: Independent - can start after Foundational (integrates with all)

### Within Each User Story

- Event schemas before publishers/consumers
- Dapr components before Dapr client code
- Kubernetes manifests before deployment scripts
- Local deployment before cloud deployment
- Manual deployment before CI/CD automation
- Core functionality before monitoring

### Parallel Opportunities

- **Phase 1 (Setup)**: All tasks can run in parallel
- **Phase 2 (Foundational)**: Most tasks marked [P] can run in parallel
  - Event schemas (T005-T009) can all run in parallel
  - Dapr components (T010-T017) can all run in parallel
  - Kubernetes resources (T019-T030) can all run in parallel
  - Ingress configs (T031-T032) can run in parallel
  - Dapr clients (T034-T037) can run in parallel
- **Phase 3 (US1)**: Event publishers (T038-T041) can run in parallel, consumers (T043-T044) can run in parallel
- **Phase 4 (US2)**: Setup scripts (T055-T057) can run in parallel
- **Phase 5 (US3)**: Dapr client implementations (T067-T071) can run in parallel
- **Phase 6 (US4)**: Documentation and scripts (T082-T085) can run in parallel
- **Phase 7 (US5)**: Docker build workflows (T099-T104) can run in parallel
- **Phase 8 (US6)**: Dashboards (T116-T119) can run in parallel, metrics (T121-T123) can run in parallel
- **Phase 9 (Polish)**: Documentation tasks (T130-T136) can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all event schema tasks together:
Task: "Create base event schema with Pydantic models in backend/src/events/schemas.py"
Task: "Create TaskEvent schemas in backend/src/events/schemas.py"
Task: "Create ReminderEvent schemas in backend/src/events/schemas.py"
Task: "Create TaskRecurrenceEvent schema in backend/src/events/schemas.py"
Task: "Create TaskUpdateEvent schema in backend/src/events/schemas.py"

# Launch all Dapr component tasks together:
Task: "Create Dapr Pub/Sub component for local in k8s/local/dapr-components/pubsub.yaml"
Task: "Create Dapr Pub/Sub component for cloud in k8s/cloud/dapr-components/pubsub.yaml"
Task: "Create Dapr State Store component in k8s/local/dapr-components/statestore.yaml"
# ... etc
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Event-Driven Architecture)
4. Complete Phase 4: User Story 2 (Local Deployment)
5. Complete Phase 5: User Story 3 (Dapr Integration)
6. **STOP and VALIDATE**: Test all three stories work together on Minikube
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Events) → Test independently → Validate event flow
3. Add US2 (Local) → Test independently → Deploy to Minikube
4. Add US3 (Dapr) → Test independently → Validate Dapr integration
5. Add US4 (Cloud) → Test independently → Deploy to Oracle Cloud
6. Add US5 (CI/CD) → Test independently → Automate deployments
7. Add US6 (Monitoring) → Test independently → Enable observability
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Event-Driven Architecture)
   - Developer B: User Story 2 (Local Deployment) + User Story 3 (Dapr Integration)
   - Developer C: User Story 6 (Monitoring)
3. After US1-3 complete:
   - Developer A: User Story 4 (Cloud Deployment)
   - Developer B: User Story 5 (CI/CD)
4. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 140
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 33 tasks
- Phase 3 (US1 - Event-Driven): 17 tasks
- Phase 4 (US2 - Local Deployment): 12 tasks
- Phase 5 (US3 - Dapr Integration): 15 tasks
- Phase 6 (US4 - Cloud Deployment): 16 tasks
- Phase 7 (US5 - CI/CD): 16 tasks
- Phase 8 (US6 - Monitoring): 16 tasks
- Phase 9 (Polish): 11 tasks

**Parallel Opportunities**: 78 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-5 (US1-US3) = 81 tasks for core event-driven architecture with local deployment

**Estimated Timeline**:
- Setup + Foundational: 2-3 days
- US1 (Events): 2 days
- US2 (Local): 1 day
- US3 (Dapr): 2 days
- US4 (Cloud): 2 days
- US5 (CI/CD): 1 day
- US6 (Monitoring): 1 day
- Polish: 1 day
- **Total**: 12-14 days for complete implementation

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Follow quickstart.md for deployment validation
- Monitor resource usage to stay within Oracle Cloud Always Free limits
- All infrastructure must be defined as code (no manual configuration)
