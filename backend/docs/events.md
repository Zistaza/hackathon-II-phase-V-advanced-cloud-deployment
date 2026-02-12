# Event Schema Documentation - Phase-V Advanced Features

**Version**: 1.0.0
**Event System**: Kafka via Dapr Pub/Sub
**Serialization**: JSON

---

## Event Envelope

All events follow a standardized envelope format:

```json
{
  "event_id": "uuid-v4 (unique identifier for idempotency)",
  "event_type": "string (event type identifier)",
  "user_id": "string (owner of the resource)",
  "timestamp": "ISO 8601 datetime (event creation time in UTC)",
  "payload": {
    // Event-specific data
  }
}
```

---

## Event Types

### 1. task.created

**Topic**: `task-events`, `task-updates`

**Description**: Published when a new task is created.

**Payload Schema**:
```json
{
  "task_id": "uuid",
  "title": "string",
  "description": "string | null",
  "status": "incomplete | complete",
  "priority": "low | medium | high | urgent",
  "tags": ["string"],
  "due_date": "ISO 8601 datetime | null",
  "recurrence_pattern": "none | daily | weekly | monthly",
  "reminder_time": "string | null"
}
```

**Example**:
```json
{
  "event_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "event_type": "task.created",
  "user_id": "user123",
  "timestamp": "2026-02-12T10:00:00Z",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project proposal",
    "description": "Write and submit Q1 project proposal",
    "status": "incomplete",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2026-02-15T11:00:00Z",
    "recurrence_pattern": "none",
    "reminder_time": "1h"
  }
}
```

**Consumers**:
- WebSocket Service (broadcasts to connected clients)

---

### 2. task.updated

**Topic**: `task-events`, `task-updates`

**Description**: Published when a task is updated.

**Payload Schema**:
```json
{
  "task_id": "uuid",
  "updated_fields": {
    // Only fields that were changed
    "field_name": "new_value"
  }
}
```

**Example**:
```json
{
  "event_id": "8d0e7780-8536-51ef-a55c-f18gd2g01bf8",
  "event_type": "task.updated",
  "user_id": "user123",
  "timestamp": "2026-02-12T11:00:00Z",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "updated_fields": {
      "priority": "urgent",
      "tags": ["work", "urgent", "client"]
    }
  }
}
```

**Consumers**:
- WebSocket Service (broadcasts to connected clients)

---

### 3. task.completed

**Topic**: `task-events`, `task-updates`

**Description**: Published when a task is marked as complete.

**Payload Schema**:
```json
{
  "task_id": "uuid",
  "completion_timestamp": "ISO 8601 datetime",
  "recurrence_pattern": "none | daily | weekly | monthly",
  "original_task": {
    // Full task data (only if recurrence_pattern != "none")
    "title": "string",
    "description": "string | null",
    "priority": "string",
    "tags": ["string"],
    "due_date": "ISO 8601 datetime | null"
  }
}
```

**Example**:
```json
{
  "event_id": "9e1f8891-9647-62fg-b66d-g29he3h12cg9",
  "event_type": "task.completed",
  "user_id": "user123",
  "timestamp": "2026-02-12T12:00:00Z",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "completion_timestamp": "2026-02-12T12:00:00Z",
    "recurrence_pattern": "weekly",
    "original_task": {
      "title": "Team standup",
      "description": "Weekly team standup meeting",
      "priority": "medium",
      "tags": ["work", "meeting"],
      "due_date": "2026-02-12T09:00:00Z"
    }
  }
}
```

**Consumers**:
- Recurring Task Service (generates next instance if recurrence_pattern != "none")
- WebSocket Service (broadcasts to connected clients)

---

### 4. task.deleted

**Topic**: `task-events`, `task-updates`

**Description**: Published when a task is deleted.

**Payload Schema**:
```json
{
  "task_id": "uuid"
}
```

**Example**:
```json
{
  "event_id": "0f2g9902-0758-73gh-c77e-h30if4i23dh0",
  "event_type": "task.deleted",
  "user_id": "user123",
  "timestamp": "2026-02-12T13:00:00Z",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Consumers**:
- WebSocket Service (broadcasts to connected clients)

---

### 5. reminder.scheduled

**Topic**: `task-events`

**Description**: Published when a reminder is scheduled via Dapr Jobs API.

**Payload Schema**:
```json
{
  "reminder_id": "uuid",
  "task_id": "uuid",
  "scheduled_time": "ISO 8601 datetime",
  "job_id": "string (Dapr job identifier)"
}
```

**Example**:
```json
{
  "event_id": "1g3h0013-1869-84hi-d88f-i41jg5j34ei1",
  "event_type": "reminder.scheduled",
  "user_id": "user123",
  "timestamp": "2026-02-12T10:00:00Z",
  "payload": {
    "reminder_id": "2h4i1124-2970-95ij-e99g-j52kh6k45fj2",
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "scheduled_time": "2026-02-15T10:00:00Z",
    "job_id": "reminder-550e8400-e29b-41d4-a716-446655440000-1707998400"
  }
}
```

**Consumers**:
- None (informational event for audit trail)

---

### 6. reminder.triggered

**Topic**: `reminders`

**Description**: Published when a scheduled reminder time arrives.

**Payload Schema**:
```json
{
  "reminder_id": "uuid",
  "task_id": "uuid",
  "task_title": "string",
  "due_date": "ISO 8601 datetime",
  "reminder_message": "string"
}
```

**Example**:
```json
{
  "event_id": "3i5j2235-3081-06jk-f00h-k63li7l56gk3",
  "event_type": "reminder.triggered",
  "user_id": "user123",
  "timestamp": "2026-02-15T10:00:00Z",
  "payload": {
    "reminder_id": "2h4i1124-2970-95ij-e99g-j52kh6k45fj2",
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_title": "Complete project proposal",
    "due_date": "2026-02-15T11:00:00Z",
    "reminder_message": "Task 'Complete project proposal' is due in 1 hour"
  }
}
```

**Consumers**:
- Notification Service (delivers notification to user)

---

## Kafka Topics

### task-events

**Purpose**: Task lifecycle events for event-driven processing

**Partitions**: 3

**Retention**: 7 days

**Consumers**:
- Recurring Task Service (processes task.completed events)

**Events**:
- task.created
- task.updated
- task.completed
- task.deleted
- reminder.scheduled

---

### task-updates

**Purpose**: Real-time task updates for multi-client synchronization

**Partitions**: 3

**Retention**: 1 hour (short retention for real-time sync only)

**Consumers**:
- WebSocket Service (broadcasts to connected clients)

**Events**:
- task.created
- task.updated
- task.completed
- task.deleted

---

### reminders

**Purpose**: Reminder notifications

**Partitions**: 3

**Retention**: 7 days

**Consumers**:
- Notification Service (delivers reminders to users)

**Events**:
- reminder.triggered

---

## Idempotency

All event consumers implement idempotency using `event_id` deduplication:

1. Before processing an event, check if `event_id` exists in Dapr State Store
2. If exists, skip processing (duplicate event)
3. If not exists, process event and store `event_id` with 7-day TTL

**State Store Key Pattern**: `processed-event:{event_id}`

**TTL**: 604800 seconds (7 days)

---

## Event Validation

All events are validated using Pydantic models:

**At Publish Time**:
- Event envelope structure validated
- Payload schema validated against event type
- Invalid events rejected with error

**At Consume Time**:
- Event envelope structure validated
- Payload schema validated against event type
- Invalid events logged and sent to dead-letter queue

---

## Error Handling

### Dead Letter Queue (DLQ)

Events that fail processing after retries are sent to DLQ:

**DLQ Topic Pattern**: `{original-topic}-dlq`

**DLQ Topics**:
- `task-events-dlq`
- `reminders-dlq`
- `task-updates-dlq`

**DLQ Message Format**:
```json
{
  "original_event": { /* original event data */ },
  "error": "Error message",
  "error_type": "ValidationError | ProcessingError | TimeoutError",
  "retry_count": 3,
  "timestamp": "ISO 8601 datetime"
}
```

### Retry Policy

- **Max Retries**: 3
- **Backoff**: Exponential (1s, 2s, 4s)
- **Timeout**: 30 seconds per attempt

---

## Monitoring

### Metrics

All event operations expose Prometheus metrics:

- `events_published_total{event_type, topic}`: Total events published
- `events_consumed_total{event_type, consumer}`: Total events consumed
- `event_processing_duration_seconds{event_type, consumer}`: Processing duration
- `event_processing_errors_total{event_type, consumer, error_type}`: Processing errors
- `consumer_lag_messages{consumer, topic}`: Consumer lag
- `dlq_messages_total{topic, reason}`: DLQ messages

### Logging

All event operations are logged with structured logging:

```json
{
  "timestamp": "2026-02-12T10:00:00Z",
  "level": "INFO",
  "event_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "event_type": "task.created",
  "user_id": "user123",
  "operation": "publish | consume",
  "topic": "task-events",
  "consumer": "recurring-task-service",
  "duration_ms": 45,
  "status": "success | error"
}
```

---

## Schema Evolution

### Versioning Strategy

Events support backward-compatible schema evolution:

1. **Adding Fields**: New optional fields can be added to payload
2. **Deprecating Fields**: Old fields marked as deprecated but not removed
3. **Breaking Changes**: Require new event type (e.g., `task.created.v2`)

### Version Field

Future events may include version field:

```json
{
  "event_id": "uuid",
  "event_type": "task.created",
  "version": "1.0",
  "user_id": "string",
  "timestamp": "ISO 8601",
  "payload": {}
}
```

---

## Security

### Event Authorization

- All events include `user_id` for ownership tracking
- Consumers validate user ownership before processing
- Cross-user event access prevented

### Event Encryption

- Events transmitted over TLS
- Sensitive data in payload can be encrypted
- Encryption keys managed via Dapr Secrets

---

## Testing

### Event Publishing Test

```python
from backend.src.events.publisher import publish_task_event
from backend.src.models.events import TaskEvent, EventType, TaskCreatedPayload

event = TaskEvent(
    event_type=EventType.TASK_CREATED,
    user_id="test-user",
    payload=TaskCreatedPayload(
        task_id="test-task-id",
        title="Test Task",
        # ... other fields
    )
)

await publish_task_event(event)
```

### Event Consumption Test

```python
from backend.src.events.consumer import BaseEventConsumer

class TestConsumer(BaseEventConsumer):
    async def process_event(self, event):
        # Test event processing logic
        pass

consumer = TestConsumer()
await consumer.handle_event(test_event)
```

---

## References

- [Dapr Pub/Sub Documentation](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Event-Driven Architecture Patterns](https://martinfowler.com/articles/201701-event-driven.html)
