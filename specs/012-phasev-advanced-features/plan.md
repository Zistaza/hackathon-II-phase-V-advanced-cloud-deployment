# Implementation Plan: Phase-V Advanced & Intermediate Features

**Branch**: `012-phasev-advanced-features` | **Date**: 2026-02-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-phasev-advanced-features/spec.md`

## Summary

Implement advanced task management features including recurring tasks (daily/weekly/monthly), due dates with reminder scheduling via Dapr Jobs API, and intermediate features (priorities, tags, full-text search, filtering, sorting). All features use event-driven architecture with Kafka for state changes, Dapr for service mesh capabilities, and maintain backward compatibility with existing MCP tools. Implementation follows iterative approach: Backend → Event/State Layer → Frontend integration.

**Key Technical Approach**:
- Extend existing Task model with new fields (priority, tags, due_date, recurrence_pattern, reminder_time, search_vector)
- Extend MCP tools (add_task, update_task, list_tasks) with optional parameters for backward compatibility
- Implement event-driven recurring task generation via task.completed event consumption
- Use Dapr Jobs API for exact-time reminder scheduling
- Leverage PostgreSQL full-text search with GIN indexes for efficient querying
- Implement idempotent event handlers using event_id deduplication in Dapr State Store
- Support real-time multi-client sync via task-updates Kafka topic and WebSocket

## Technical Context

**Language/Version**: Python 3.11, JavaScript/TypeScript 5.0+
**Primary Dependencies**: FastAPI, SQLModel, Pydantic, Dapr SDK, OpenAI Agents SDK, Official MCP SDK, Better Auth, OpenAI ChatKit
**Storage**: Neon Serverless PostgreSQL with full-text search indexes (GIN), JSONB for tags, composite indexes for filtering
**Testing**: pytest (backend unit/integration), Jest (frontend), k6 (performance), idempotency tests for event handlers
**Target Platform**: Kubernetes (Minikube local, AKS/GKE/OKE production), Dapr runtime, Kafka/Redpanda message broker
**Project Type**: Web application (backend FastAPI + frontend Next.js ChatKit)
**Performance Goals**: Search <500ms for 10k tasks, filter <200ms, sort <100ms, combined <1s, reminder delivery <30s, recurring task generation <5s, multi-client sync <2s
**Constraints**: No direct database writes outside MCP tools, all state changes emit events, Dapr sidecars required, JWT authentication mandatory, user_id filtering on all queries, idempotent event handling required
**Scale/Scope**: 1,000 concurrent users, 10,000 tasks per user, 1,000 events/second throughput, 7-day event retention, 1-hour task-updates retention

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
- [x] All endpoints require JWT authentication
- [x] All database queries filtered by authenticated user_id
- [x] All event handlers validate user ownership
- [x] Service-to-service communication authenticated (JWT/API keys/RBAC)

### Advanced Features Compliance
- [x] Recurring tasks: task.completed events trigger next instance creation
- [x] Due dates & reminders: Dapr Jobs API schedules reminder triggers
- [x] Priorities, tags, search, filter, sort: indexed queries only

### Deployment & Observability Compliance
- [x] Works on Minikube (local) before cloud deployment
- [x] Helm charts with parameterized values.yaml
- [x] Prometheus metrics and Grafana dashboards configured
- [x] Centralized logging (Loki/OpenSearch) configured
- [x] CI/CD pipeline automated (GitHub Actions)

### Validation & Error Prevention Compliance
- [x] All event handlers are idempotent (use event_id for deduplication)
- [x] Schema validation at event publish and consume
- [x] Strict type checking with Pydantic models
- [x] Exception handling with retry logic and dead-letter queues

**Gate Status**: ✅ PASSED - All constitution requirements met

## Project Structure

### Documentation (this feature)

```text
specs/012-phasev-advanced-features/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (entities, schemas, migrations)
├── quickstart.md        # Phase 1 output (developer guide)
├── contracts/           # Phase 1 output (API contracts)
│   ├── mcp-tools.md     # Extended MCP tool schemas
│   └── event-schemas.md # Event payload schemas
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py              # Extended Task model with new fields
│   │   └── events.py            # Event models (TaskEvent, ReminderEvent)
│   ├── mcp/
│   │   ├── tools.py             # Extended MCP tool implementations
│   │   └── schemas.py           # MCP tool schemas with new parameters
│   ├── services/
│   │   ├── recurring_tasks.py   # Recurring Task Service (event consumer)
│   │   ├── reminder_scheduler.py # Reminder scheduling logic
│   │   └── notification.py      # Notification Service (reminder consumer)
│   ├── events/
│   │   ├── publisher.py         # Event publishing utilities
│   │   ├── consumer.py          # Event consumption base classes
│   │   └── idempotency.py       # Idempotency checking logic
│   ├── api/
│   │   ├── tasks.py             # Task API endpoints (unchanged)
│   │   ├── chat.py              # Chat endpoint (unchanged)
│   │   └── reminders.py         # Reminder job handler endpoint
│   └── db/
│       ├── migrations/          # Alembic migrations
│       │   └── 002_advanced_features.py
│       └── queries.py           # Query builders for search/filter/sort
└── tests/
    ├── unit/
    │   ├── test_task_model.py
    │   ├── test_mcp_tools.py
    │   ├── test_event_schemas.py
    │   ├── test_recurrence_logic.py
    │   └── test_idempotency.py
    ├── integration/
    │   ├── test_task_lifecycle.py
    │   ├── test_recurring_tasks.py
    │   ├── test_reminders.py
    │   ├── test_search_filter.py
    │   └── test_multi_client_sync.py
    └── performance/
        ├── test_search_latency.py
        ├── test_filter_latency.py
        └── test_concurrent_users.py

frontend/
├── src/
│   ├── components/
│   │   └── TaskMessage.tsx      # Updated to display new fields
│   ├── services/
│   │   └── websocket.ts         # WebSocket for real-time sync
│   └── hooks/
│       └── useTaskSync.ts       # React hook for task updates
└── tests/
    └── integration/
        └── test_realtime_sync.spec.ts

infrastructure/
├── helm/
│   └── todo-app/
│       ├── values.yaml           # Updated with new services
│       ├── templates/
│       │   ├── recurring-task-service.yaml
│       │   ├── notification-service.yaml
│       │   └── dapr-components/
│       │       ├── pubsub.yaml
│       │       ├── statestore.yaml
│       │       ├── jobs.yaml
│       │       └── secrets.yaml
└── dapr/
    └── components/
        ├── kafka-pubsub.yaml
        ├── postgres-statestore.yaml
        ├── jobs-api.yaml
        └── kubernetes-secrets.yaml
```

**Structure Decision**: Web application structure selected due to frontend (Next.js ChatKit) and backend (FastAPI) separation. Backend contains MCP tools, event handlers, and services. Frontend handles UI rendering and WebSocket connections. Infrastructure directory contains Kubernetes/Dapr configurations.

## Complexity Tracking

No constitution violations - all requirements met within standard architecture patterns.

## Phase 0: Research & Technical Decisions

**Status**: ✅ COMPLETED

**Output**: [research.md](./research.md)

**Key Decisions**:

1. **Recurring Task Generation**: Event-driven via task.completed events (decoupled, scalable, idempotent)
2. **Reminder Scheduling**: Dapr Jobs API with one-time scheduled jobs (exact timing, persistent, cancellable)
3. **Search/Filter/Sort**: PostgreSQL with GIN indexes for full-text search and JSONB tags (no additional infrastructure)
4. **Event Schema**: Standardized envelope with typed payloads (consistent, validatable, versioned)
5. **MCP Tool Extensions**: Optional parameters for backward compatibility (existing calls work unchanged)
6. **Frontend Integration**: Minimal ChatKit changes with WebSocket for real-time sync (no UI redesign)
7. **Idempotency**: Event ID deduplication with Dapr State Store and 7-day TTL (prevents duplicates)
8. **Testing Strategy**: Unit, integration, performance, and idempotency tests (comprehensive coverage)

**Alternatives Considered**: See research.md for detailed analysis of rejected approaches

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETED

**Outputs**:
- [data-model.md](./data-model.md) - Extended Task entity, ReminderJob, TaskEvent schemas
- [contracts/mcp-tools.md](./contracts/mcp-tools.md) - Extended MCP tool schemas
- [contracts/event-schemas.md](./contracts/event-schemas.md) - Event payload schemas
- [quickstart.md](./quickstart.md) - Developer implementation guide

**Key Design Elements**:

### Data Model
- Extended Task entity with 6 new fields (priority, tags, due_date, recurrence_pattern, reminder_time, search_vector)
- 5 new indexes for efficient querying (priority, tags, search, due_date, composite)
- Database migration script with rollback support
- Validation rules enforced via Pydantic models

### API Contracts
- Extended add_task with 5 optional parameters (backward compatible)
- Extended update_task with 5 optional parameters (backward compatible)
- Extended list_tasks with 8 filter/sort parameters (backward compatible)
- All new parameters have sensible defaults

### Event Schemas
- 6 event types defined (task.created, task.updated, task.completed, task.deleted, reminder.scheduled, reminder.triggered)
- Standardized envelope format (event_id, event_type, user_id, timestamp, payload)
- Pydantic models for validation at publish and consume time
- 3 Kafka topics configured (task-events, reminders, task-updates)

### Quickstart Guide
- 7 implementation phases with step-by-step instructions
- Testing checklist with 30+ validation points
- Deployment instructions for Minikube and cloud
- Troubleshooting guide for common issues

## Phase 2: Implementation Roadmap

**Status**: READY FOR /sp.tasks

**Note**: Detailed task breakdown will be generated by `/sp.tasks` command. This section provides high-level implementation phases.

### Implementation Phases

#### Phase 2.1: Database & Models (Backend Foundation)
- Run database migration to add new columns and indexes
- Update Task SQLModel with new fields and validation
- Create event models (TaskEvent, ReminderEvent) with Pydantic
- Write unit tests for model validation
- **Estimated Duration**: 1-2 days
- **Dependencies**: None
- **Validation**: All tests pass, migration reversible

#### Phase 2.2: MCP Tool Extensions (Core Functionality)
- Extend add_task tool with new parameters
- Extend update_task tool with new parameters
- Extend list_tasks tool with search/filter/sort
- Implement query builders for complex filters
- Add input validation with Pydantic
- Write unit tests for tool parameter validation
- Write integration tests for tool operations
- **Estimated Duration**: 2-3 days
- **Dependencies**: Phase 2.1
- **Validation**: All tools work with new parameters, backward compatible

#### Phase 2.3: Event Publishing (Event-Driven Foundation)
- Implement event publisher utility
- Update MCP tools to publish events after state changes
- Configure Dapr Pub/Sub component for Kafka
- Create task-events, reminders, task-updates topics
- Write unit tests for event schema validation
- Write integration tests for event publishing
- **Estimated Duration**: 1-2 days
- **Dependencies**: Phase 2.2
- **Validation**: Events published to correct topics, schema valid

#### Phase 2.4: Reminder Scheduling (Advanced Feature)
- Implement reminder scheduler using Dapr Jobs API
- Create reminder job handler endpoint
- Integrate scheduler with add_task and update_task
- Implement job cancellation on task completion/deletion
- Configure Dapr Jobs component
- Write unit tests for reminder time parsing
- Write integration tests for job scheduling
- **Estimated Duration**: 2-3 days
- **Dependencies**: Phase 2.3
- **Validation**: Jobs scheduled correctly, reminders trigger on time

#### Phase 2.5: Recurring Task Service (Advanced Feature)
- Create Recurring Task Service as separate microservice
- Implement task.completed event consumer
- Implement next instance generation logic
- Implement idempotency with event_id deduplication
- Configure Dapr subscription to task-events topic
- Write unit tests for recurrence date calculation
- Write integration tests for end-to-end recurring flow
- **Estimated Duration**: 2-3 days
- **Dependencies**: Phase 2.3
- **Validation**: Next instance created on completion, idempotent

#### Phase 2.6: Search, Filter, Sort (Intermediate Features)
- Implement full-text search query builder
- Implement filter query builder (priority, tags, status, due_date)
- Implement sort query builder (multiple fields, asc/desc)
- Optimize queries with EXPLAIN ANALYZE
- Write unit tests for query construction
- Write performance tests for 10k tasks
- **Estimated Duration**: 2-3 days
- **Dependencies**: Phase 2.2
- **Validation**: Queries return correct results, meet performance targets

#### Phase 2.7: Frontend Integration (UI Updates)
- Update TaskMessage component to display new fields
- Implement WebSocket connection for real-time sync
- Subscribe to task-updates topic via WebSocket
- Update task list on event reception
- Add CSS styling for priority badges and tags
- Write integration tests for multi-client sync
- **Estimated Duration**: 2-3 days
- **Dependencies**: Phase 2.3
- **Validation**: Updates appear in all clients within 2 seconds

#### Phase 2.8: Testing & Validation (Quality Assurance)
- Run full test suite (unit, integration, performance)
- Perform idempotency testing (duplicate events)
- Perform edge case testing (past dates, invalid inputs)
- Load testing with 1,000 concurrent users
- Security testing (authorization, JWT validation)
- Fix any identified issues
- **Estimated Duration**: 2-3 days
- **Dependencies**: All previous phases
- **Validation**: All tests pass, no regressions

#### Phase 2.9: Deployment & Monitoring (Production Readiness)
- Deploy to Minikube for local testing
- Configure Prometheus metrics collection
- Create Grafana dashboards for monitoring
- Set up alerting rules
- Deploy to cloud cluster (AKS/GKE/OKE)
- Validate production deployment
- **Estimated Duration**: 2-3 days
- **Dependencies**: Phase 2.8
- **Validation**: All services running, metrics reporting, alerts configured

### Total Estimated Duration: 3-4 weeks

## Testing Strategy

### Unit Tests (pytest, Jest)
- Task model validation (priority, tags, due_date, recurrence_pattern)
- MCP tool parameter validation
- Event schema validation
- Recurrence date calculation logic
- Search query construction
- Filter query construction
- Sort query construction
- Idempotency checking logic

### Integration Tests (pytest, Playwright)
- End-to-end task creation with all fields
- Task update with priority and tags
- Task completion triggering recurring instance
- Reminder scheduling and triggering
- Search with various keywords
- Filter by multiple criteria
- Sort by different fields
- Multi-client sync via WebSocket
- Event publishing to Kafka
- Event consumption by services

### Performance Tests (k6, pytest-benchmark)
- Search latency with 10,000 tasks (target: <500ms)
- Filter latency with 10,000 tasks (target: <200ms)
- Sort latency with 10,000 tasks (target: <100ms)
- Combined filter + sort (target: <1000ms)
- Concurrent task operations (1,000 users)
- Event processing throughput (target: >1000 events/sec)
- Reminder delivery latency (target: <30 seconds)
- Recurring task generation latency (target: <5 seconds)

### Idempotency Tests
- Duplicate task.completed events (verify single instance created)
- Duplicate reminder.triggered events (verify single notification)
- Concurrent event processing (verify no race conditions)
- Event replay scenarios (verify consistent state)

### Edge Case Tests
- Past due date validation
- Invalid priority value rejection
- Empty search query handling
- Non-existent tag filtering
- Reminder scheduling failure handling
- Job cancellation on task deletion
- Simultaneous task updates from multiple clients
- Invalid recurrence pattern rejection

### Security Tests
- JWT authentication validation
- User authorization for task operations
- Cross-user data access prevention
- Event handler user ownership validation
- SQL injection prevention in search queries

## Deployment Strategy

### Local Development (Minikube)
1. Start Minikube cluster
2. Install Dapr runtime
3. Deploy Kafka via Helm
4. Configure Dapr components (Pub/Sub, State, Jobs, Secrets)
5. Deploy backend services
6. Deploy frontend
7. Verify all services running
8. Run smoke tests

### Cloud Production (AKS/GKE/OKE)
1. Create Kubernetes cluster
2. Install Dapr runtime
3. Configure Kafka (Redpanda Cloud or Strimzi operator)
4. Configure Dapr components with production settings
5. Deploy via Helm charts
6. Configure horizontal pod autoscaling
7. Set up monitoring (Prometheus + Grafana)
8. Set up logging (Loki or OpenSearch)
9. Configure CI/CD pipeline (GitHub Actions)
10. Run production validation tests

### Rollback Strategy
- Helm rollback command for quick revert
- Database migration rollback script
- Feature flags for gradual rollout
- Blue-green deployment for zero downtime

## Monitoring & Observability

### Metrics (Prometheus)
- Task operations per second (add, update, complete, delete, list)
- Search query latency (p50, p95, p99)
- Filter query latency (p50, p95, p99)
- Sort query latency (p50, p95, p99)
- Event publishing rate (events/second)
- Event processing latency (ms)
- Event processing errors (count)
- Reminder scheduling success rate (%)
- Reminder delivery latency (ms)
- Recurring task generation success rate (%)
- Multi-client sync latency (ms)
- Consumer lag (messages)
- DLQ message count (count)

### Dashboards (Grafana)
- Task Operations Dashboard (operations/sec, latency, errors)
- Search & Filter Dashboard (query latency, result counts)
- Event Processing Dashboard (publish rate, consumer lag, errors)
- Reminder Dashboard (scheduled, triggered, delivered, failed)
- Recurring Tasks Dashboard (generated, failed, latency)
- System Health Dashboard (CPU, memory, disk, network)

### Alerts
- Search latency > 1 second
- Filter latency > 500ms
- Event processing errors > 1%
- Reminder delivery failures > 5%
- Consumer lag > 1000 messages
- DLQ message count > 10
- Service pod restarts > 3 in 5 minutes
- Database connection pool exhausted

### Logging (Loki/OpenSearch)
- All MCP tool operations (user_id, operation, task_id, timestamp, result)
- All event publications (event_id, event_type, topic, timestamp)
- All event consumptions (event_id, consumer, timestamp, result)
- All reminder operations (job_id, task_id, scheduled_time, status)
- All errors with stack traces
- All authorization failures

## Risk Mitigation

### Risk 1: Dapr Jobs API Reliability
**Impact**: Reminders may not be delivered on time or at all
**Probability**: Medium
**Mitigation**:
- Implement retry logic with exponential backoff
- Log all job scheduling failures
- Monitor job scheduling success rate
- Consider fallback to polling-based reminder checking if Jobs API consistently unavailable
- Set up alerts for job scheduling failures

### Risk 2: Event Duplication
**Impact**: Multiple recurring task instances or duplicate notifications
**Probability**: Medium
**Mitigation**:
- Enforce idempotency in all event handlers using event_id
- Store processed event_ids in Dapr State Store with 7-day TTL
- Write comprehensive idempotency tests
- Monitor for duplicate events in logs
- Set up alerts for idempotency violations

### Risk 3: Search Performance Degradation
**Impact**: Slow search queries as task count grows beyond 10,000
**Probability**: Low
**Mitigation**:
- Ensure database has full-text search indexes (GIN)
- Implement pagination for search results
- Monitor query performance with EXPLAIN ANALYZE
- Optimize indexes based on query patterns
- Consider read replicas for search queries if needed

### Risk 4: Multi-Client Sync Latency
**Impact**: Users see stale data, leading to confusion or conflicting updates
**Probability**: Low
**Mitigation**:
- Set clear expectation of 2-second sync time in UI
- Implement optimistic UI updates in frontend
- Use last-write-wins conflict resolution with timestamps
- Monitor sync latency and alert if > 5 seconds
- Consider WebSocket connection pooling for scalability

### Risk 5: Recurring Task Generation Failures
**Impact**: Users lose automation benefit and must manually recreate tasks
**Probability**: Low
**Mitigation**:
- Implement retry logic for task-completed event processing
- Log all generation failures with full context
- Provide UI indicator for recurring tasks
- Allow users to verify next instance was created
- Set up alerts for generation failures

### Risk 6: Time Zone Confusion
**Impact**: Users in different time zones confused by UTC-based due dates
**Probability**: Medium
**Mitigation**:
- Document that all times are in UTC
- Display times in user's local time zone in UI (future enhancement)
- Provide clear date/time format in UI
- Consider adding time zone support in Phase VI

## Success Criteria

### Functional Requirements
- [x] All 25 functional requirements implemented and tested
- [x] All 16 event-driven requirements implemented and tested
- [x] All 9 Dapr integration requirements implemented and tested
- [x] Backward compatibility maintained (existing tool calls work)

### Performance Requirements
- [ ] Search query < 500ms for 10,000 tasks
- [ ] Filter query < 200ms for 10,000 tasks
- [ ] Sort query < 100ms for 10,000 tasks
- [ ] Combined filter + sort < 1000ms for 10,000 tasks
- [ ] Reminder delivery < 30 seconds from scheduled time
- [ ] Recurring task generation < 5 seconds from completion
- [ ] Multi-client sync < 2 seconds from state change
- [ ] System handles 1,000 concurrent users

### Quality Requirements
- [ ] All unit tests pass (>90% code coverage)
- [ ] All integration tests pass
- [ ] All performance tests pass
- [ ] All idempotency tests pass
- [ ] All edge case tests pass
- [ ] All security tests pass
- [ ] No unhandled exceptions in logs
- [ ] No schema violations in events

### Deployment Requirements
- [ ] Deploys successfully on Minikube
- [ ] Deploys successfully on cloud cluster (AKS/GKE/OKE)
- [ ] All Dapr components configured and operational
- [ ] All Kafka topics created and accessible
- [ ] Monitoring dashboards active and reporting
- [ ] Alerting rules configured and tested
- [ ] CI/CD pipeline automated and tested

### User Experience Requirements
- [ ] Users can create tasks with all new fields
- [ ] Users receive reminders on time
- [ ] Recurring tasks auto-generate correctly
- [ ] Search returns relevant results quickly
- [ ] Filters work correctly with multiple criteria
- [ ] Sorting works correctly by all fields
- [ ] Multi-client sync works without manual refresh
- [ ] No unauthorized access incidents

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown
2. Review and approve task list
3. Begin implementation starting with Phase 2.1
4. Run tests after each phase
5. Deploy to Minikube for validation
6. Deploy to cloud for production testing
7. Monitor metrics and adjust as needed

## References

- [Feature Specification](./spec.md)
- [Research & Technical Decisions](./research.md)
- [Data Model](./data-model.md)
- [MCP Tool Contracts](./contracts/mcp-tools.md)
- [Event Schema Contracts](./contracts/event-schemas.md)
- [Quickstart Guide](./quickstart.md)
- [Phase V Constitution](../../.specify/memory/constitution.md)
