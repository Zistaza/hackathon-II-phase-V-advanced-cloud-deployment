# Research & Technical Decisions: Phase-V Advanced Features

**Feature**: 012-phasev-advanced-features
**Date**: 2026-02-12
**Purpose**: Resolve technical unknowns and document design decisions before implementation

## Research Areas

### 1. Recurring Task Generation Strategy

**Decision**: Event-driven recurrence using task.completed events

**Rationale**:
- Decouples recurrence logic from task completion logic
- Enables horizontal scaling of recurrence processor
- Supports idempotent processing via event_id deduplication
- Allows retry logic without affecting user-facing operations

**Implementation Approach**:
- Recurring Task Service subscribes to task-events topic
- Filters for task.completed events where recurrence_pattern != "none"
- Calculates next due date based on pattern (daily: +1 day, weekly: +7 days, monthly: +1 month)
- Creates new task instance via add_task MCP tool with same title, description, priority, tags
- Stores processed event_ids in Dapr State Store with 7-day TTL for idempotency

**Alternatives Considered**:
- Synchronous generation during complete_task: Rejected due to increased latency and coupling
- Cron-based polling: Rejected due to inefficiency and potential for missed tasks
- Database triggers: Rejected due to violation of event-driven architecture principle

**Edge Cases Handled**:
- Past due dates: Generate next valid future instance, skip backfill
- Deleted recurring tasks: Check task existence before generation
- Updated recurrence patterns: Only affect future instances, not current
- Duplicate events: Use event_id deduplication to prevent multiple instances

---

### 2. Reminder Scheduling Architecture

**Decision**: Dapr Jobs API with one-time scheduled jobs

**Rationale**:
- Dapr Jobs API provides exact timing guarantees
- Jobs persist across service restarts
- Built-in job cancellation support
- Cloud-portable (works on Minikube and AKS/GKE/OKE)

**Implementation Approach**:
- When task with reminder is created/updated: Schedule Dapr job with name `reminder-{task_id}-{timestamp}`
- Job payload includes: task_id, user_id, task_title, due_date, reminder_message
- Job executes at scheduled time, publishes reminder-triggered event to reminders topic
- Notification Service consumes reminders topic and delivers notification
- When task completed/deleted: Cancel job using job name

**Alternatives Considered**:
- Cron-based polling: Rejected due to lack of exact timing and inefficiency
- In-memory scheduler: Rejected due to loss of state on restart
- Database-based scheduler: Rejected due to complexity and polling overhead
- Kafka scheduled messages: Rejected due to lack of native support in Kafka

**Edge Cases Handled**:
- Reminder time in past: Reject with validation error
- Job scheduling failure: Retry with exponential backoff, log for monitoring
- Duplicate job creation: Use unique job name to prevent duplicates
- Job execution failure: Dapr retries automatically, dead-letter queue for persistent failures

---

### 3. Priority, Tag, and Search Indexing Strategy

**Decision**: PostgreSQL with composite indexes and full-text search

**Rationale**:
- Neon PostgreSQL already in use, no additional infrastructure
- Native full-text search with tsvector and GIN indexes
- Composite indexes support multi-column filtering
- JSONB support for tags array with GIN indexing

**Implementation Approach**:
- Priority: ENUM type (low, medium, high, urgent) with B-tree index
- Tags: JSONB array with GIN index for containment queries (@> operator)
- Search: tsvector column combining title and description with GIN index
- Composite index on (user_id, status, priority) for common filter combinations
- Composite index on (user_id, due_date) for date-based filtering

**SQL Schema Additions**:
```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN tags JSONB DEFAULT '[]';
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(20) DEFAULT 'none';
ALTER TABLE tasks ADD COLUMN reminder_time VARCHAR(50);
ALTER TABLE tasks ADD COLUMN search_vector tsvector;

CREATE INDEX idx_tasks_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector);
CREATE INDEX idx_tasks_due_date ON tasks(user_id, due_date);
CREATE INDEX idx_tasks_status_priority ON tasks(user_id, status, priority);

-- Trigger to maintain search_vector
CREATE TRIGGER tasks_search_vector_update BEFORE INSERT OR UPDATE
ON tasks FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);
```

**Alternatives Considered**:
- Elasticsearch: Rejected due to additional infrastructure complexity
- Separate tags table: Rejected due to join overhead and complexity
- VARCHAR array for tags: Rejected due to inferior indexing compared to JSONB

**Query Performance Targets**:
- Priority filter: <100ms for 10,000 tasks
- Tag filter: <200ms for 10,000 tasks
- Full-text search: <500ms for 10,000 tasks
- Combined filters + sort: <1000ms for 10,000 tasks

---

### 4. Event Schema Design

**Decision**: Standardized event envelope with typed payloads

**Event Envelope Schema**:
```json
{
  "event_id": "uuid-v4",
  "event_type": "task.created | task.updated | task.completed | task.deleted | reminder.triggered",
  "user_id": "string",
  "timestamp": "ISO 8601",
  "payload": {
    // Event-specific data
  }
}
```

**Event-Specific Payloads**:

**task.created**:
```json
{
  "task_id": "uuid",
  "title": "string",
  "description": "string",
  "status": "incomplete",
  "priority": "low | medium | high | urgent",
  "tags": ["string"],
  "due_date": "ISO 8601 | null",
  "recurrence_pattern": "none | daily | weekly | monthly",
  "reminder_time": "string | null"
}
```

**task.updated**:
```json
{
  "task_id": "uuid",
  "updated_fields": {
    // Only changed fields included
    "title": "string",
    "priority": "urgent",
    "tags": ["new", "tags"]
  }
}
```

**task.completed**:
```json
{
  "task_id": "uuid",
  "completion_timestamp": "ISO 8601",
  "recurrence_pattern": "none | daily | weekly | monthly"
}
```

**task.deleted**:
```json
{
  "task_id": "uuid"
}
```

**reminder.triggered**:
```json
{
  "reminder_id": "uuid",
  "task_id": "uuid",
  "task_title": "string",
  "due_date": "ISO 8601",
  "reminder_message": "string"
}
```

**Validation Strategy**:
- Pydantic models for all event types
- Schema validation at publish time (reject invalid events)
- Schema validation at consume time (log and dead-letter invalid events)
- Version field for schema evolution (future-proofing)

---

### 5. MCP Tool Extensions

**Decision**: Extend existing MCP tools with optional parameters

**add_task Extension**:
```python
{
  "name": "add_task",
  "parameters": {
    "title": "string (required)",
    "description": "string (optional)",
    "priority": "low | medium | high | urgent (optional, default: medium)",
    "tags": ["string"] (optional, default: []),
    "due_date": "ISO 8601 (optional)",
    "recurrence_pattern": "none | daily | weekly | monthly (optional, default: none)",
    "reminder_time": "1h | 1d | 1w (optional, relative to due_date)"
  }
}
```

**update_task Extension**:
```python
{
  "name": "update_task",
  "parameters": {
    "task_id": "uuid (required)",
    "title": "string (optional)",
    "description": "string (optional)",
    "priority": "low | medium | high | urgent (optional)",
    "tags": ["string"] (optional)",
    "due_date": "ISO 8601 (optional)",
    "recurrence_pattern": "none | daily | weekly | monthly (optional)",
    "reminder_time": "1h | 1d | 1w (optional)"
  }
}
```

**list_tasks Extension**:
```python
{
  "name": "list_tasks",
  "parameters": {
    "status": "complete | incomplete (optional)",
    "priority": "low | medium | high | urgent (optional)",
    "tags": ["string"] (optional, AND logic)",
    "due_date_filter": "overdue | today | this_week | this_month (optional)",
    "search": "string (optional, full-text search)",
    "sort_by": "created_at | due_date | priority | status (optional, default: created_at)",
    "sort_order": "asc | desc (optional, default: desc)"
  }
}
```

**Backward Compatibility**:
- All new parameters are optional
- Existing tool calls continue to work without modification
- Default values maintain current behavior

---

### 6. Frontend ChatKit Integration

**Decision**: Minimal UI changes, leverage ChatKit's message rendering

**Implementation Approach**:
- Display task metadata (priority, tags, due date) in message content
- Use ChatKit's built-in message formatting for structured data
- Subscribe to task-updates topic via WebSocket for real-time sync
- Update task list in UI when task-updated events received
- No custom UI components beyond ChatKit widget

**Real-Time Sync Flow**:
1. Frontend establishes WebSocket connection to backend
2. Backend subscribes to task-updates topic for authenticated user
3. When task event received, backend pushes to WebSocket
4. Frontend updates task list in ChatKit message history
5. User sees changes within 2 seconds without refresh

**Alternatives Considered**:
- Polling: Rejected due to inefficiency and latency
- Server-Sent Events: Rejected due to lack of bidirectional communication
- Custom React components: Rejected due to scope constraint (no UI redesign)

---

### 7. Idempotency Strategy

**Decision**: Event ID deduplication with Dapr State Store

**Implementation Approach**:
- Store processed event_ids in Dapr State Store with key pattern: `processed-event:{event_id}`
- Set TTL to 7 days (sufficient for retry windows)
- Before processing event, check if event_id exists in state store
- If exists, skip processing and log duplicate
- If not exists, process event and store event_id

**Code Pattern**:
```python
async def handle_task_completed(event: TaskCompletedEvent):
    event_key = f"processed-event:{event.event_id}"

    # Check if already processed
    existing = await dapr_client.get_state(store_name="statestore", key=event_key)
    if existing:
        logger.info(f"Duplicate event {event.event_id}, skipping")
        return

    # Process event
    if event.recurrence_pattern != "none":
        await generate_next_task_instance(event)

    # Mark as processed
    await dapr_client.save_state(
        store_name="statestore",
        key=event_key,
        value="processed",
        state_metadata={"ttlInSeconds": "604800"}  # 7 days
    )
```

**Alternatives Considered**:
- Database-based deduplication: Rejected due to additional query overhead
- In-memory cache: Rejected due to loss of state on restart
- Kafka consumer offsets only: Rejected due to at-least-once delivery semantics

---

### 8. Testing Strategy

**Unit Tests**:
- MCP tool parameter validation
- Event schema validation
- Recurrence date calculation logic
- Search query construction
- Filter/sort query construction

**Integration Tests**:
- End-to-end task creation with priority, tags, due date
- Recurring task generation on completion
- Reminder scheduling and triggering
- Search with various keywords
- Filter combinations (status + priority + tags)
- Sort by different fields
- Multi-client sync via WebSocket

**Performance Tests**:
- Search latency with 10,000 tasks
- Filter latency with 10,000 tasks
- Concurrent task operations (1,000 users)
- Event processing throughput
- Reminder delivery latency

**Idempotency Tests**:
- Duplicate event handling
- Concurrent event processing
- Event replay scenarios

**Edge Case Tests**:
- Past due dates
- Invalid priority values
- Empty search queries
- Non-existent tags
- Reminder scheduling failures
- Job cancellation

---

## Technology Stack Summary

**Backend**: Python 3.11 + FastAPI + SQLModel + Pydantic
**Database**: Neon Serverless PostgreSQL with full-text search indexes
**Message Broker**: Kafka (via Dapr Pub/Sub component)
**Service Mesh**: Dapr (Pub/Sub, State Store, Jobs API, Secrets)
**Frontend**: OpenAI ChatKit (existing)
**AI Framework**: OpenAI Agents SDK (existing)
**MCP Server**: Official MCP SDK (existing)
**Authentication**: Better Auth with JWT (existing)
**Orchestration**: Kubernetes (Minikube local, AKS/GKE/OKE production)
**Monitoring**: Prometheus + Grafana
**Logging**: Loki or OpenSearch
**CI/CD**: GitHub Actions

---

## Performance Targets

- Task creation with all fields: <200ms
- Search query: <500ms for 10,000 tasks
- Filter query: <200ms for 10,000 tasks
- Sort query: <100ms for 10,000 tasks
- Combined filter + sort: <1000ms for 10,000 tasks
- Reminder delivery: <30 seconds from scheduled time
- Recurring task generation: <5 seconds from completion
- Multi-client sync: <2 seconds from state change
- Event processing throughput: >1000 events/second
- Concurrent users: 1,000 without degradation

---

## Risk Mitigation

**Risk**: Dapr Jobs API reliability
**Mitigation**: Implement retry logic, monitoring, fallback to polling if needed

**Risk**: Event duplication
**Mitigation**: Enforce idempotency with event_id deduplication

**Risk**: Search performance degradation
**Mitigation**: Ensure indexes, pagination, query optimization

**Risk**: Multi-client sync latency
**Mitigation**: Optimize event propagation, implement optimistic UI updates

**Risk**: Recurring task generation failures
**Mitigation**: Retry logic, dead-letter queue, monitoring alerts

**Risk**: Time zone confusion
**Mitigation**: Document UTC-only, consider future time zone support

---

## Dependencies

- Existing MCP tools infrastructure (add_task, update_task, complete_task, list_tasks, delete_task)
- Dapr runtime with Pub/Sub, State Store, Jobs API, Secrets components
- Kafka cluster (task-events, reminders, task-updates topics)
- Notification Service (consumes reminders topic)
- Database migration tooling (Alembic or equivalent)
- JWT authentication system
- Frontend ChatKit integration

---

## Open Questions

None - all technical decisions resolved with reasonable defaults and industry best practices.
