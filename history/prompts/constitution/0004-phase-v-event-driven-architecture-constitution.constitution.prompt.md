---
id: 0004
title: Phase V Event-Driven Architecture Constitution
stage: constitution
date: 2026-02-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: emizee
command: /sp.constitution
labels: ["constitution", "phase-v", "event-driven", "dapr", "kafka", "cloud-deployment"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .specify/templates/plan-template.md
  - .specify/templates/spec-template.md
  - .specify/templates/tasks-template.md
  - README.md
tests:
  - none
---

## Prompt

```text
Project: Phase-V Todo AI Chatbot — Advanced Cloud Deployment

Core principles:

Event-driven architecture: All services communicate via events (Kafka/Redpanda) rather than direct API calls, ensuring decoupling and scalability.

Distributed reliability: Implement Dapr for Pub/Sub, State, Bindings (cron/jobs), Service Invocation, and Secrets Management for all services.

Security & Auth: All user actions and service-to-service communication must be authenticated and authorized (JWT/API keys/RBAC). Secrets must never be in code.

Performance & scalability: Efficient, indexed queries; asynchronous event handling; minimal blocking; reproducible deployments.

Reproducibility: All tasks, events, and Dapr/K8s configurations are versioned and traceable.

Cloud portability: All deployments must be compatible with Minikube (local) and production-grade Kubernetes clusters (AKS/GKE/OKE).

Key standards:

Advanced Features Implementation:

Recurring Tasks: Emit task.completed events, consume to auto-create next task.

Due Dates & Reminders: Schedule via Dapr Jobs API, publish to reminders topic.

Intermediate Features: Priorities, Tags, Search, Filter, Sort (only indexed queries).

Kafka Topics:

task-events: All task CRUD and completion events (for Recurring Task & Audit Service).

reminders: Reminder triggers for Notification Service.

task-updates: Real-time client sync via WebSocket Service.

Dapr Integration:

Pub/Sub: Abstract Kafka, Redpanda, or alternate component.

State: Use Postgres or Neon DB for conversation & task caching.

Jobs API: Scheduled reminder triggers with exact timing.

Secrets: Store API keys, DB credentials, and cloud secrets securely.

Service Invocation: Frontend → Backend with built-in retries and mTLS.

Deployment Standards:

Local (Minikube): Deploy all services, Dapr, Kafka/Redpanda Docker container.

Cloud (AKS/GKE/OKE): Deploy all services via Helm, full Dapr components, Kafka via Redpanda Cloud or Strimzi operator.

CI/CD & Observability:

GitHub Actions pipelines for build, test, deploy.

Monitoring with Prometheus/Grafana, logging via Loki/OpenSearch.

Automated alerts for failures, rollback strategies implemented.

Validation & Error Prevention:

All agent operations must validate input, event schema, user authorization, and task rules before execution.

Ensure idempotent event handling.

Enforce strict type checking, schema validation, and exception handling.

Documentation & Audit:

Maintain architecture diagrams for review.

Log all events, reminders, and service invocations for audit purposes.

Constraints:

Must implement all advanced and intermediate features listed above.

Deployment should first be tested locally (Minikube), then production-ready cloud deployment.

Kafka events must be idempotent and schema-compliant.

All Dapr components must be properly configured (Pub/Sub, State, Jobs, Secrets, Service Invocation).

CI/CD pipelines must fully automate build, test, deployment, and monitoring setup.

Cloud deployments must adhere to free-tier limits for Azure, Google Cloud, and Oracle (unless otherwise permitted).

Success criteria:

Fully functional Todo AI Chatbot with all Phase-V features implemented.

Event-driven architecture fully operational (task-events, reminders, task-updates).

Dapr sidecars configured and operational on all environments.

Services deployed successfully on Minikube and cloud clusters (AKS/GKE/OKE).

Reminders and recurring tasks fire correctly without errors.

Monitoring and logging dashboards are active and reporting accurately.

No unhandled exceptions, schema violations, or security breaches.

Passes internal review: agentic workflow followed strictly with reproducible results.
```

## Response snapshot

Updated project constitution from Phase IV (v3.0.0) to Phase V (v4.0.0) with comprehensive event-driven architecture principles.

**Constitution Changes:**
- Version bump: 3.0.0 → 4.0.0 (MAJOR - backward incompatible governance changes)
- Added Event-Driven Architecture principle (Kafka/Redpanda for all service communication)
- Added Distributed Reliability principle (Dapr for Pub/Sub, State, Jobs, Secrets, Service Invocation)
- Added Advanced Features section (Recurring Tasks, Due Dates & Reminders, Priorities, Tags, Search/Filter/Sort)
- Added Kafka Topics standards (task-events, reminders, task-updates with schemas)
- Added Dapr Integration Standards (Pub/Sub, State Store, Jobs API, Secrets, Service Invocation)
- Added CI/CD & Observability Standards (GitHub Actions, Prometheus/Grafana, Loki/OpenSearch)
- Added Validation & Error Prevention Standards (idempotent event handling, schema validation)
- Updated Technology Standards to include Kafka/Redpanda, Dapr, Prometheus, Grafana, Loki/OpenSearch
- Updated MCP Tooling Standards to include event publishing requirements
- Added Event Schema Standards (LOCKED) with mandatory fields

**Template Updates:**
- Updated `.specify/templates/plan-template.md` Constitution Check section with Phase V compliance gates
- Updated `.specify/templates/spec-template.md` with Event-Driven Requirements and Dapr Integration Requirements sections
- Updated `.specify/templates/tasks-template.md` Phase 2 Foundational tasks with event-driven infrastructure setup

**Documentation Updates:**
- Updated `README.md` from Phase IV to Phase V with complete overview, requirements, technology stack, Kafka topics, event schemas, Dapr components, and success criteria

**Sync Impact Report:**
All dependent templates and documentation updated successfully. No follow-up TODOs. Constitution is ready for Phase V implementation.

## Outcome

- ✅ Impact: Constitution successfully amended to v4.0.0 with comprehensive Phase V event-driven architecture principles; all dependent templates and documentation synchronized
- 🧪 Tests: N/A (documentation work)
- 📁 Files: 5 files modified (.specify/memory/constitution.md, 3 templates, README.md)
- 🔁 Next prompts: Begin Phase V feature specifications using /sp.specify for recurring tasks, reminders, priorities, tags, search/filter/sort features
- 🧠 Reflection: Major version bump justified due to fundamental architectural shift from containerization-focused (Phase IV) to event-driven architecture with Dapr integration (Phase V); all governance standards updated to enforce idempotent event handling, schema validation, and multi-environment deployment

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (constitution amendment)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate constitution compliance by running /sp.specify for first Phase V feature (recurring tasks) and ensuring all new constitution checks are enforced
