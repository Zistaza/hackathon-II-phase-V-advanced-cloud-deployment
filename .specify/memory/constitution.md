<!-- SYNC IMPACT REPORT:
Version change: 3.0.0 -> 4.0.0
Modified principles: Phase IV – Local Kubernetes Deployment → Phase V – Advanced Cloud Deployment with Event-Driven Architecture
Added sections: Event-Driven Architecture, Distributed Reliability (Dapr), Advanced Features (Recurring Tasks, Due Dates & Reminders, Priorities, Tags, Search/Filter/Sort), Kafka Topics, Dapr Integration Standards, CI/CD & Observability, Validation & Error Prevention, Cloud Portability
Removed sections: Phase IV containerization-only focus, Docker AI (Gordon) as primary tool, kubectl-ai/Kagent as primary operations tools
Templates requiring updates: ✅ updated - .specify/templates/plan-template.md (constitution check section), ✅ updated - .specify/templates/spec-template.md (requirements alignment), ✅ updated - .specify/templates/tasks-template.md (task categorization for event-driven features)
Follow-up TODOs: None
-->

# Phase V – Advanced Cloud Deployment with Event-Driven Architecture Constitution

## Core Principles

### Event-Driven Architecture
All services communicate via events (Kafka/Redpanda) rather than direct API calls; this ensures decoupling, scalability, and resilience; every significant state change must emit an event to the appropriate topic

### Distributed Reliability
Implement Dapr for Pub/Sub, State Management, Bindings (cron/jobs), Service Invocation, and Secrets Management across all services; Dapr sidecars must be configured and operational in all deployment environments

### Security by Default (NON-NEGOTIABLE)
Every request is authenticated and authorized via JWT; backend must reject unauthenticated requests with HTTP 401; all database queries must be filtered by authenticated user ID; all service-to-service communication must be authenticated (JWT/API keys/RBAC); secrets must NEVER be in code

### Multi-Tenant Isolation
Users can only access and modify their own data; user ID in the URL must match the user ID in the JWT; cross-user data access is strictly forbidden; all event handlers must validate user ownership before processing

### Performance & Scalability
Efficient, indexed queries only; asynchronous event handling; minimal blocking operations; reproducible deployments; horizontal scalability must be maintained

### Reproducibility
All tasks, events, and Dapr/K8s configurations are versioned and traceable; deployment must be repeatable from clean state; all infrastructure as code

### Cloud Portability
All deployments must be compatible with Minikube (local development) and production-grade Kubernetes clusters (AKS/GKE/OKE); no cloud-specific dependencies that prevent migration

### Spec-Driven Development
All implementation must originate from written specifications; every feature starts with a clear spec document that defines requirements, acceptance criteria, and test cases before any code is written

### Separation of Concerns
UI, agent logic, MCP tooling, event handling, and persistence responsibilities are isolated; each layer has clear boundaries and interfaces without cross-contamination of concerns

### Agentic-first Design
AI agent reasoning drives all task operations; the system must be designed around the OpenAI Agents SDK and its decision-making capabilities; all user interactions flow through the AI agent

### Statelessness
No server-side memory between requests; all state must be persisted in the database or Dapr State Store; the backend must be horizontally scalable and restart-safe with full conversation context reconstruction from database

### Tool-based Interaction
AI must interact with the application exclusively via MCP (Model Context Protocol) tools; no direct API calls from agents; all operations must occur through the defined MCP tool interface

### Deterministic APIs
Backend behavior must be predictable, validated, and testable; the single chat endpoint must follow the defined contract with appropriate response handling

### Cloud-Native Design
Stateless backend, serverless-friendly database usage; event-driven asynchronous workflows; minimal viable implementations avoiding premature optimization

## Advanced Features Implementation

### Recurring Tasks
Emit `task.completed` events when tasks are marked complete; consume these events to auto-create the next task instance based on recurrence rules (daily, weekly, monthly); recurrence logic must be idempotent

### Due Dates & Reminders
Schedule reminders via Dapr Jobs API with exact timing; publish reminder triggers to the `reminders` topic; Notification Service consumes and delivers reminders; reminders must be cancellable if task is completed or deleted

### Intermediate Features
Priorities: Support priority levels (low, medium, high, urgent) with indexed queries; Tags: Support multiple tags per task with efficient filtering; Search: Full-text search on task title and description; Filter: By status, priority, tags, due date; Sort: By creation date, due date, priority, completion status

## Kafka Topics

### task-events
All task CRUD operations and completion events; consumed by Recurring Task Service and Audit Service; schema must include: event_type, task_id, user_id, timestamp, payload

### reminders
Reminder triggers published by Reminder Scheduler; consumed by Notification Service; schema must include: reminder_id, task_id, user_id, due_date, timestamp

### task-updates
Real-time task state changes for client synchronization; consumed by WebSocket Service for live updates; schema must include: update_type, task_id, user_id, changes, timestamp

## Dapr Integration Standards

### Pub/Sub Component
Abstract Kafka, Redpanda, or alternate message broker; configure topic subscriptions declaratively; ensure at-least-once delivery semantics; implement idempotent event handlers

### State Management Component
Use Postgres or Neon DB for conversation history and task caching; configure state store with appropriate consistency guarantees; support TTL for ephemeral state

### Jobs API (Bindings)
Schedule reminder triggers with exact timing (cron expressions or one-time schedules); ensure job persistence across restarts; support job cancellation

### Secrets Management
Store API keys, database credentials, and cloud secrets securely; never commit secrets to version control; use Kubernetes Secrets or cloud-native secret stores; rotate secrets regularly

### Service Invocation
Frontend → Backend communication with built-in retries and mTLS; service-to-service calls with automatic load balancing; circuit breaker patterns for resilience

## Deployment Standards

### Local Development (Minikube)
Deploy all services with Dapr sidecars; run Kafka/Redpanda as Docker container or Helm chart; configure all Dapr components (Pub/Sub, State, Jobs, Secrets); validate full event flow locally

### Cloud Production (AKS/GKE/OKE)
Deploy all services via Helm charts; configure production-grade Dapr components; use Kafka via Redpanda Cloud or Strimzi operator; implement proper resource limits and requests; configure horizontal pod autoscaling

### Infrastructure as Code
All Kubernetes manifests versioned in Git; Helm charts with parameterized values.yaml; Dapr component configurations versioned; deployment scripts automated and documented

## CI/CD & Observability Standards

### GitHub Actions Pipelines
Automated build, test, and deploy workflows; run tests on every pull request; deploy to staging on merge to main; deploy to production on release tags; automated rollback on failure

### Monitoring
Prometheus for metrics collection (request rates, error rates, latency, event processing lag); Grafana dashboards for visualization; alerts for critical thresholds; Dapr metrics integration

### Logging
Centralized logging via Loki or OpenSearch; structured JSON logs with correlation IDs; log all events, reminders, and service invocations; retention policies configured

### Alerting
Automated alerts for service failures, event processing delays, high error rates; on-call rotation configured; runbooks for common incidents

## Validation & Error Prevention Standards

### Input Validation
All agent operations must validate input before processing; enforce schema validation on all events; validate user authorization before any data access; validate task rules (due dates, recurrence patterns)

### Idempotent Event Handling
All event consumers must be idempotent; use event IDs to detect duplicates; store processed event IDs in state store; handle out-of-order events gracefully

### Type Safety & Schema Validation
Enforce strict type checking in all code; validate event schemas at publish and consume time; use Pydantic models for all data structures; reject invalid data early

### Exception Handling
Catch and log all exceptions; return appropriate error responses; implement retry logic with exponential backoff; dead-letter queues for failed events

## Documentation & Audit Standards

### Architecture Diagrams
Maintain up-to-date architecture diagrams showing service boundaries, event flows, and Dapr components; document all Kafka topics and their schemas; diagram deployment topology

### Event Audit Trail
Log all events with full context (user_id, timestamp, event_type, payload); maintain audit log for compliance; support event replay for debugging; retention policies documented

### Service Documentation
Document all API endpoints with OpenAPI/Swagger; document all MCP tools with schemas; document all event schemas; maintain runbooks for operations

## Technology Standards

Frontend: OpenAI ChatKit; Backend: Python FastAPI; AI Framework: OpenAI Agents SDK; MCP Server: Official MCP SDK only; ORM: SQLModel; Database: Neon Serverless PostgreSQL; Authentication: Better Auth with JWT; Message Broker: Kafka or Redpanda; Service Mesh: Dapr; Orchestration: Kubernetes (Minikube local, AKS/GKE/OKE production); Packaging: Helm charts; Monitoring: Prometheus + Grafana; Logging: Loki or OpenSearch; CI/CD: GitHub Actions

## Development Workflow

All features must be implemented according to written specs; The system must support conversation resumption after server restarts; The chatbot must fully manage todos through natural language; All task operations performed exclusively through MCP tools; All state changes must emit events to appropriate Kafka topics; All event handlers must be idempotent and validate user ownership; Infrastructure must be deployed using Helm charts with proper Dapr configuration

## Governance

All implementation must follow the defined API contracts, MCP tool schemas, and event schemas; All infrastructure must follow the defined deployment and observability standards; All event handlers must be idempotent and validate authorization

### REST API Contract (LOCKED)

All implementations must conform to the following REST API contract:
- POST /api/{user_id}/chat — Single chat endpoint handles all AI interactions

No endpoint renaming, path restructuring, or contract deviation is allowed without a constitution amendment.

### MCP Tooling Standards (LOCKED)

All implementations must conform to the following MCP tools contract:
- add_task — Creates a new task in the database and publishes task.created event
- list_tasks — Lists all tasks for the authenticated user (filtered by user_id)
- complete_task — Marks a task as completed and publishes task.completed event
- delete_task — Deletes a task from the database and publishes task.deleted event
- update_task — Updates task properties and publishes task.updated event

No tool renaming, schema modification, or contract deviation is allowed without a constitution amendment.

### Event Schema Standards (LOCKED)

All event schemas must include:
- event_id: Unique identifier for idempotency
- event_type: Type of event (task.created, task.completed, etc.)
- user_id: Owner of the resource
- timestamp: ISO 8601 timestamp
- payload: Event-specific data

No schema changes allowed without constitution amendment and migration plan.

### Constraints

No hardcoded secrets or credentials in code; Backend must remain stateless; No direct database access from frontend; MCP tools must not contain conversational logic; All events must be schema-compliant and idempotent; All Dapr components must be properly configured; Deployment must work on Minikube first, then cloud; Cloud deployments must adhere to free-tier limits (Azure, Google Cloud, Oracle) unless otherwise permitted

## Success Criteria

- Fully functional Todo AI Chatbot with all Phase-V features implemented
- Event-driven architecture fully operational (task-events, reminders, task-updates topics)
- Dapr sidecars configured and operational on all environments (Minikube, AKS/GKE/OKE)
- Services deployed successfully on Minikube and at least one cloud cluster
- Reminders fire correctly via Dapr Jobs API without errors
- Recurring tasks auto-create next instance on completion
- Priorities, tags, search, filter, sort features fully functional
- Monitoring and logging dashboards active and reporting accurately
- CI/CD pipelines fully automated (build, test, deploy, rollback)
- No unhandled exceptions, schema violations, or security breaches
- All event handlers are idempotent and validate user ownership
- All API endpoints require valid JWT authentication
- Users can only access and modify their own tasks
- Tasks persist reliably in Neon PostgreSQL
- Conversation history is replayable after server restart
- MCP tools validate user ownership and handle errors gracefully
- Agent demonstrates correct tool usage and confirmations
- Chatbot fully manages todos through natural language
- Passes internal review: agentic workflow followed strictly with reproducible results
- Deployment is demo-ready and judge-verifiable

## Authority Hierarchy

Phase III Constitution → Phase IV Constitution → Phase V Constitution → Phase V Specifications → Phase V Plans → Phase V Tasks → Execution

Any conflict must be resolved in favor of the higher authority document.

**Version**: 4.0.0 | **Ratified**: 2026-01-24 | **Last Amended**: 2026-02-12
