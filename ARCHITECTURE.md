# Phase-V System Architecture

Comprehensive architecture documentation for the Phase-V application.

## Overview

Phase-V is an event-driven todo application built with microservices architecture, leveraging Dapr (Distributed Application Runtime) for building blocks and Kubernetes for orchestration.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Web Client  │  │ Mobile Client│  │  API Clients │          │
│  │   (React)    │  │   (Future)   │  │   (CLI/SDK)  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┴─────────────────┘                   │
│                           │                                     │
│                  ┌────────▼────────┐                           │
│                  │   HTTPS/TLS     │                           │
│                  └────────┬────────┘                           │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                    Kubernetes Cluster                            │
│                                                                  │
│         ┌─────────────────▼─────────────────┐                   │
│         │     Traefik Ingress Controller    │                   │
│         │  - TLS Termination                │                   │
│         │  - Path-based Routing             │                   │
│         │  - Rate Limiting                  │                   │
│         └─────────────────┬─────────────────┘                   │
│                           │                                     │
│  ┌────────────────────────┼────────────────────────────────┐   │
│  │                    Application Layer                     │   │
│  │                                                           │   │
│  │  ┌──────────────┐                                        │   │
│  │  │   Frontend   │  React SPA                            │   │
│  │  │   (Static)   │                                        │   │
│  │  └──────────────┘                                        │   │
│  │                                                           │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │              Backend Services                        │ │   │
│  │  │                                                       │ │   │
│  │  │  ┌───────────┐ ┌───────────┐ ┌───────────┐          │ │   │
│  │  │  │  Backend  │ │  Events   │ │ Reminders │          │ │   │
│  │  │  │   API     │ │ Processor │ │ Scheduler │          │ │   │
│  │  │  │ :8000     │ │ :8001     │ │ :8002     │          │ │   │
│  │  │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘          │ │   │
│  │  │        │             │             │                 │ │   │
│  │  │  ┌─────┴─────┐ ┌─────┴─────┐       │                 │ │   │
│  │  │  │  Notify   │ │ WebSocket │       │                 │ │   │
│  │  │  │  Service  │ │  Service  │       │                 │ │   │
│  │  │  │  :8003    │ │  :8004    │       │                 │ │   │
│  │  │  └─────┬─────┘ └─────┬─────┘       │                 │ │   │
│  │  │        │             │             │                 │ │   │
│  │  │        └─────────────┴─────────────┘                 │ │   │
│  │  │                  │                                    │ │   │
│  │  │        ┌─────────▼─────────┐                         │ │   │
│  │  │        │  Dapr Sidecars    │                         │ │   │
│  │  │        │  (daprd)          │                         │ │   │
│  │  │        └─────────┬─────────┘                         │ │   │
│  │  └──────────────────┼───────────────────────────────────┘ │   │
│  └─────────────────────┼─────────────────────────────────────┘   │
│                        │                                          │
│         ┌──────────────┼──────────────┐                          │
│         │              │              │                          │
│         ▼              ▼              ▼                          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                   │
│  │  Dapr      │ │  Dapr      │ │  Dapr      │                   │
│  │  Pub/Sub   │ │  State     │ │  Secrets   │                   │
│  │  Component │ │  Component │ │  Component │                   │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘                   │
└────────┼──────────────┼──────────────┼──────────────────────────┘
         │              │              │
         │              │              │
         ▼              ▼              ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Redpanda Cloud │ │ Neon PostgreSQL│ │   Kubernetes   │
│ (Kafka-compatible)│ (Serverless)   │ │    Secrets     │
│                │ │                │ │                │
│ - task.events  │ │ - Task state   │ │ - DB URL       │
│ - reminder.    │ │ - Idempotency  │ │ - JWT Secret   │
│ - notification │ │ - Recurrence   │ │ - API Keys     │
└────────────────┘ └────────────────┘ └────────────────┘
```

## Service Architecture

### Backend API Service

**Port:** 8000
**Replicas:** 2
**Purpose:** Main REST API for task operations

```
┌─────────────────────────────────────────┐
│           Backend API                    │
├─────────────────────────────────────────┤
│  /api/tasks          - CRUD operations  │
│  /api/tasks/{id}     - Task details     │
│  /api/tasks/{id}/complete - Complete    │
│  /api/reminders      - Reminder mgmt    │
│  /api/search         - Full-text search │
│  /health             - Health check     │
│  /metrics            - Prometheus       │
└─────────────────────────────────────────┘
```

**Key Features:**
- JWT authentication
- Task CRUD operations
- Priority management
- Tag management
- Search and filtering
- Event publishing via Dapr

### Event Processor Service

**Port:** 8001
**Replicas:** 2
**Purpose:** Consume and process events from Kafka

```
┌─────────────────────────────────────────┐
│         Event Processor                  │
├─────────────────────────────────────────┤
│  Subscriptions:                          │
│  - task.events (task.created)           │
│  - task.events (task.updated)           │
│  - task.events (task.completed)         │
│  - task.events (task.deleted)           │
│                                          │
│  Handlers:                               │
│  - TaskEventConsumer                    │
│  - AuditConsumer                        │
│  - RecurringTaskConsumer                │
└─────────────────────────────────────────┘
```

**Key Features:**
- Idempotent event processing
- Dead letter queue handling
- Retry with exponential backoff
- Audit logging
- Recurring task generation

### Reminder Scheduler Service

**Port:** 8002
**Replicas:** 1
**Purpose:** Schedule and trigger reminders

```
┌─────────────────────────────────────────┐
│       Reminder Scheduler                 │
├─────────────────────────────────────────┤
│  Dapr Cron Binding:                      │
│  - Triggers every minute                │
│                                          │
│  Functions:                              │
│  - Check due reminders                  │
│  - Publish reminder.due events          │
│  - Schedule future reminders            │
│  - Handle recurring patterns            │
└─────────────────────────────────────────┘
```

**Key Features:**
- Cron-based scheduling
- Reminder due detection
- Recurring pattern support (daily, weekly, monthly)
- Time zone handling

### Notification Service

**Port:** 8003
**Replicas:** 1
**Purpose:** Send notifications via various channels

```
┌─────────────────────────────────────────┐
│       Notification Service               │
├─────────────────────────────────────────┤
│  Subscriptions:                          │
│  - reminder.events (reminder.due)       │
│  - notification.events                  │
│                                          │
│  Channels:                               │
│  - In-app notifications                 │
│  - Email (future)                       │
│  - Push notifications (future)          │
└─────────────────────────────────────────┘
```

### WebSocket Service

**Port:** 8004
**Replicas:** 2
**Purpose:** Real-time multi-client synchronization

```
┌─────────────────────────────────────────┐
│        WebSocket Service                 │
├─────────────────────────────────────────┤
│  /ws/{user_id}  - WebSocket endpoint    │
│                                          │
│  Messages:                               │
│  - task.created                         │
│  - task.updated                         │
│  - task.deleted                         │
│  - task.sync                            │
└─────────────────────────────────────────┘
```

**Key Features:**
- User-specific connections
- Real-time task synchronization
- Connection state management
- Automatic reconnection support

## Data Flow

### Task Creation Flow

```
1. Client → Backend API: POST /api/tasks
2. Backend API → Database: Save task
3. Backend API → Dapr Pub/Sub: Publish task.created event
4. Dapr Pub/Sub → Event Processor: Deliver event
5. Event Processor → State Store: Record idempotency key
6. Event Processor → Business Logic: Process event
7. Event Processor → Audit Log: Record event
8. Backend API → Client: Return task created response
9. Backend API → WebSocket: Broadcast update
```

### Reminder Flow

```
1. Client → Backend API: Create task with reminder
2. Backend API → Database: Save task + reminder
3. Backend API → Dapr Pub/Sub: Publish reminder.scheduled
4. Dapr Cron Binding → Reminder Scheduler: Trigger every minute
5. Reminder Scheduler → Database: Check due reminders
6. Reminder Scheduler → Dapr Pub/Sub: Publish reminder.due
7. Notification Service: Receive and process
8. Notification Service → Client: Send notification
```

### Recurring Task Flow

```
1. Client → Backend API: Create recurring task
2. Backend API → Database: Save task + recurrence
3. Backend API → Dapr Pub/Sub: Publish task.recurrence.created
4. Event Processor: Store recurrence config
5. Reminder Scheduler: Check recurrence triggers
6. Event Processor → Backend API: Create new instance
7. Event Processor → Dapr Pub/Sub: Publish task.created (new instance)
8. Update recurrence state for next trigger
```

## Dapr Building Blocks

### Pub/Sub

**Component:** Redis (local) / Redpanda (cloud)
**Topics:**
- `task.events` - Task lifecycle events
- `reminder.events` - Reminder events
- `recurrence.events` - Recurring task events
- `notification.events` - Notification events

**Configuration:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.redis  # or pubsub.kafka
  metadata:
  - name: redisHost
    value: redis.todo-app.svc.cluster.local:6379
```

### State Store

**Component:** PostgreSQL
**Keys:**
- `task:{id}` - Task state
- `event-processor:processed-event:{id}` - Idempotency
- `recurrence:{id}` - Recurrence config
- `audit:task:{event_id}` - Audit log

**Configuration:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  metadata:
  - name: connectionString
    secretKeyRef:
      name: neon-secret
      key: connectionString
```

### Bindings

**Component:** Cron
**Purpose:** Trigger reminder scheduler

**Configuration:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  metadata:
  - name: schedule
    value: "@every 1m"
```

### Service Invocation

**Purpose:** Service-to-service communication
**Features:**
- Automatic retries
- Load balancing
- Distributed tracing

**Example:**
```python
# Invoke notification service from backend
response = dapr.invoke_method(
    app_id="phase-v-notification-service",
    method="/api/notifications",
    data={"user_id": "123", "message": "Reminder!"}
)
```

## Database Schema

### Tasks Table

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    tags TEXT[],
    metadata JSONB
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
```

### Reminders Table

```sql
CREATE TABLE reminders (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    user_id UUID NOT NULL,
    reminder_time TIMESTAMP NOT NULL,
    message TEXT,
    delivered BOOLEAN DEFAULT FALSE,
    delivered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reminders_user_id ON reminders(user_id);
CREATE INDEX idx_reminders_time ON reminders(reminder_time);
```

### Recurring Tasks Table

```sql
CREATE TABLE recurring_tasks (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    user_id UUID NOT NULL,
    pattern VARCHAR(20) NOT NULL, -- daily, weekly, monthly
    pattern_config JSONB,
    last_triggered_at TIMESTAMP,
    next_trigger_at TIMESTAMP,
    occurrence_count INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE
);
```

## Security Architecture

### Authentication Flow

```
1. Client → Auth Service: Login (username/password)
2. Auth Service → Database: Verify credentials
3. Auth Service → JWT: Generate token
4. Auth Service → Client: Return JWT token
5. Client → API: Request with Authorization: Bearer {token}
6. API → JWT Middleware: Validate token
7. API → Business Logic: Process request
```

### JWT Token Structure

```json
{
  "sub": "user_id",
  "iat": 1234567890,
  "exp": 1234654290,
  "roles": ["user"],
  "permissions": ["tasks:read", "tasks:write"]
}
```

### Network Security

```
┌─────────────────────────────────────────┐
│         Network Policies                 │
├─────────────────────────────────────────┤
│  - Backend: Allow from Ingress only     │
│  - Services: Allow from Backend only    │
│  - Database: Allow from Services only   │
│  - Redis: Allow from Dapr only          │
└─────────────────────────────────────────┘
```

## Monitoring Architecture

```
┌─────────────────────────────────────────┐
│          Monitoring Stack                │
├─────────────────────────────────────────┤
│                                          │
│  ┌──────────────┐  ┌──────────────┐     │
│  │  Prometheus  │  │   Grafana    │     │
│  │              │  │              │     │
│  │  - Scrape    │  │  - Dashboards│     │
│  │  - Store     │  │  - Alerts    │     │
│  │  - Query     │  │  - Query     │     │
│  └──────┬───────┘  └──────▲───────┘     │
│         │                 │              │
│         └─────────────────┘              │
│                │                         │
│         ┌──────▼───────┐                 │
│         │  /metrics    │                 │
│         │  Endpoints   │                 │
│         └──────────────┘                 │
└─────────────────────────────────────────┘
```

### Metrics Categories

1. **Business Metrics**
   - Task operations
   - Event throughput
   - Reminder delivery

2. **Performance Metrics**
   - Request latency
   - Processing duration
   - Query performance

3. **Error Metrics**
   - Error rates
   - DLQ messages
   - Consumer lag

4. **Infrastructure Metrics**
   - CPU/Memory usage
   - Pod health
   - Node health

## Deployment Architecture

### Local (Minikube)

```
┌─────────────────────────────────┐
│         Minikube Cluster         │
├─────────────────────────────────┤
│  Namespace: todo-app            │
│                                  │
│  Deployments:                   │
│  - backend (2 replicas)         │
│  - event-processor (2)          │
│  - reminder-scheduler (1)       │
│  - notification-service (1)     │
│  - websocket-service (2)        │
│  - frontend (2)                 │
│                                  │
│  Dapr Components:               │
│  - Redis (Pub/Sub)              │
│  - PostgreSQL (State)           │
│  - Cron (Bindings)              │
└─────────────────────────────────┘
```

### Cloud (Oracle Cloud)

```
┌─────────────────────────────────────────┐
│      Oracle Cloud Always Free           │
├─────────────────────────────────────────┤
│                                          │
│  ┌──────────────┐  ┌──────────────┐     │
│  │  Compute 1   │  │  Compute 2   │     │
│  │  (k3s Server)│  │  (k3s Agent) │     │
│  │  1 OCPU/6GB  │  │  1 OCPU/6GB  │     │
│  └──────────────┘  └──────────────┘     │
│                                          │
│  External Services:                      │
│  - Redpanda Cloud (Pub/Sub)             │
│  - Neon PostgreSQL (State)              │
│  - Let's Encrypt (TLS)                  │
└─────────────────────────────────────────┘
```

## Scalability

### Horizontal Scaling

- **Backend API:** 2-5 replicas based on load
- **Event Processor:** 2-10 replicas for high throughput
- **WebSocket:** 2-5 replicas for connection handling
- **Frontend:** 2-3 replicas for static content

### Vertical Scaling

- Limited by Oracle Cloud Always Free (2 OCPU, 12GB RAM total)
- Adjust resource requests/limits based on actual usage
- Monitor and optimize for cost efficiency

---

**Document Version:** 1.0.0
**Last Updated:** 2026-02-19
