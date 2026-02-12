# Phase V: Advanced Cloud Deployment with Event-Driven Architecture

## Overview
Phase V extends the **Phase III Todo Chatbot** with advanced features and event-driven architecture, deploying to both **local Kubernetes (Minikube)** and **production cloud clusters (AKS/GKE/OKE)**.
This includes implementing recurring tasks, reminders, priorities, tags, search/filter/sort, Kafka event streaming, Dapr integration, and full CI/CD with observability.

## Objective
- Implement advanced task management features (recurring tasks, due dates, reminders, priorities, tags, search/filter/sort)
- Build event-driven architecture using Kafka/Redpanda for service communication
- Integrate Dapr for Pub/Sub, State Management, Jobs API, Secrets, and Service Invocation
- Deploy to Minikube (local) and at least one cloud cluster (AKS/GKE/OKE)
- Implement full CI/CD pipelines with GitHub Actions
- Configure monitoring (Prometheus/Grafana) and logging (Loki/OpenSearch)
- Follow the **Agentic Dev Stack workflow**: Write spec → Generate plan → Break into tasks → Implement via Claude Code

## Requirements

### Advanced Features
- **Recurring Tasks**: Auto-create next task instance on completion via task.completed events
- **Due Dates & Reminders**: Schedule reminders via Dapr Jobs API, publish to reminders topic
- **Priorities**: Support low, medium, high, urgent priority levels with indexed queries
- **Tags**: Multiple tags per task with efficient filtering
- **Search**: Full-text search on task title and description
- **Filter**: By status, priority, tags, due date
- **Sort**: By creation date, due date, priority, completion status

### Event-Driven Architecture
- **Kafka Topics**: task-events, reminders, task-updates
- **Event Schemas**: event_id, event_type, user_id, timestamp, payload
- **Idempotent Handlers**: Use event_id for deduplication
- **No Direct API Calls**: Services communicate via events or Dapr Service Invocation

### Dapr Integration
- **Pub/Sub**: Abstract Kafka/Redpanda message broker
- **State Store**: Postgres/Neon DB for conversation and task caching
- **Jobs API**: Reminder scheduling with exact timing
- **Secrets**: Secure storage for API keys, DB credentials, cloud secrets
- **Service Invocation**: Frontend → Backend with mTLS and retries

### Deployment & Operations
- **Local**: Minikube with Dapr sidecars, Kafka/Redpanda container
- **Cloud**: AKS/GKE/OKE with Helm charts, production Dapr components
- **CI/CD**: GitHub Actions for build, test, deploy, rollback
- **Monitoring**: Prometheus metrics, Grafana dashboards
- **Logging**: Centralized logging with correlation IDs

## Technology Stack
| Component              | Technology / Tool                                    |
|------------------------|-----------------------------------------------------|
| Frontend               | OpenAI ChatKit, Next.js 16+, React 18+              |
| Backend                | Python FastAPI, OpenAI Agents SDK                   |
| MCP Server             | Official MCP SDK                                    |
| ORM                    | SQLModel                                            |
| Database               | Neon Serverless PostgreSQL                          |
| Authentication         | Better Auth with JWT                                |
| Message Broker         | Kafka or Redpanda                                   |
| Service Mesh           | Dapr (Pub/Sub, State, Jobs, Secrets, Invocation)   |
| Orchestration          | Kubernetes (Minikube local, AKS/GKE/OKE production) |
| Package Manager        | Helm Charts                                         |
| Monitoring             | Prometheus + Grafana                                |
| Logging                | Loki or OpenSearch                                  |
| CI/CD                  | GitHub Actions                                      |

## Kafka Topics & Event Schemas

### task-events
All task CRUD operations and completion events
```json
{
  "event_id": "uuid",
  "event_type": "task.created|task.updated|task.completed|task.deleted",
  "user_id": "string",
  "timestamp": "ISO 8601",
  "payload": { "task_id": "string", "..." }
}
```

### reminders
Reminder triggers for notification service
```json
{
  "event_id": "uuid",
  "event_type": "reminder.trigger",
  "user_id": "string",
  "timestamp": "ISO 8601",
  "payload": { "reminder_id": "string", "task_id": "string", "due_date": "ISO 8601" }
}
```

### task-updates
Real-time task state changes for client sync
```json
{
  "event_id": "uuid",
  "event_type": "task.state_changed",
  "user_id": "string",
  "timestamp": "ISO 8601",
  "payload": { "task_id": "string", "changes": {...} }
}
```

## Dapr Components Configuration

### Pub/Sub Component (pubsub.yaml)
Configure Kafka/Redpanda for event streaming with at-least-once delivery semantics.

### State Store Component (statestore.yaml)
Configure Postgres/Neon DB for conversation history and task caching with appropriate consistency guarantees.

### Jobs API Component (jobs.yaml)
Configure reminder scheduling with cron expressions or one-time schedules, ensuring job persistence across restarts.

### Secrets Component (secrets.yaml)
Configure Kubernetes Secrets or cloud-native secret stores for API keys, DB credentials, and cloud secrets.

## Success Criteria

- ✅ All advanced features implemented (recurring tasks, reminders, priorities, tags, search/filter/sort)
- ✅ Event-driven architecture operational (task-events, reminders, task-updates topics)
- ✅ Dapr sidecars configured on all environments (Minikube, AKS/GKE/OKE)
- ✅ Services deployed successfully on Minikube and at least one cloud cluster
- ✅ Reminders fire correctly via Dapr Jobs API
- ✅ Recurring tasks auto-create next instance on completion
- ✅ Monitoring dashboards active (Prometheus/Grafana)
- ✅ Centralized logging operational (Loki/OpenSearch)
- ✅ CI/CD pipelines automated (GitHub Actions)
- ✅ All event handlers idempotent with event_id deduplication
- ✅ No unhandled exceptions, schema violations, or security breaches
- ✅ Deployment is demo-ready and judge-verifiable

## Getting Started

See the constitution at `.specify/memory/constitution.md` for complete Phase V principles and standards.

Follow the Agentic Dev Stack workflow:
1. Write feature specification using `/sp.specify`
2. Generate implementation plan using `/sp.plan`
3. Break into tasks using `/sp.tasks`
4. Implement via Claude Code agents

## Architecture

Phase V builds on Phase III (Todo AI Chatbot) and Phase IV (Kubernetes Deployment) by adding:
- Event-driven service communication via Kafka/Redpanda
- Dapr integration for Pub/Sub, State, Jobs, Secrets, Service Invocation
- Advanced task management features (recurring, reminders, priorities, tags, search)
- Full CI/CD with observability (monitoring, logging, alerting)
- Cloud portability (Minikube → AKS/GKE/OKE)
