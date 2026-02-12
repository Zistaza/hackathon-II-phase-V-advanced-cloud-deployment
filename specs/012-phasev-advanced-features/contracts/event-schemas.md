# Event Schema Contracts: Phase-V Advanced Features

**Version**: 2.0.0
**Date**: 2026-02-12
**Feature**: 012-phasev-advanced-features

## Overview

This document defines the event schemas for Phase-V advanced features. All events follow the standardized envelope format with typed payloads.

---

## Event Envelope (Standard)

All events MUST conform to this envelope structure:

```json
{
  "event_id": "uuid-v4",
  "event_type": "string (enum)",
  "user_id": "string",
  "timestamp": "ISO 8601 datetime",
  "payload": {
    // Event-specific data
  }
}
```

**Envelope Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_id | UUID | Yes | Unique event identifier for idempotency |
| event_type | String (Enum) | Yes | Type of event (see Event Types below) |
| user_id | String | Yes | Owner of the resource |
| timestamp | ISO 8601 | Yes | Event creation timestamp (UTC) |
| payload | Object | Yes | Event-specific data (see schemas below) |

---

## Event Types

### task.created

**Topic**: task-events, task-updates
**Description**: Published when a new task is created
**Consumers**: Audit Service, WebSocket Service (for multi-client sync)

**Payload Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Created task ID"
    },
    "title": {
      "type": "string",
      "description": "Task title"
    },
    "description": {
      "type": "string",
      "description": "Task description (nullable)"
    },
    "status": {
      "type": "string",
      "enum": ["incomplete"],
      "description": "Initial status (always incomplete)"
    },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high", "urgent"],
      "description": "Task priority"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Task tags"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "Task due date (nullable)"
    },
    "recurrence_pattern": {
      "type": "string",
      "enum": ["none", "daily", "weekly", "monthly"],
      "description": "Recurrence pattern"
    },
    "reminder_time": {
      "type": "string",
      "description": "Reminder time (nullable)"
    }
  },
  "required": ["task_id", "title", "status", "priority", "tags", "recurrence_pattern"]
}
```

**Example**:
```json
{
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "event_type": "task.created",
  "user_id": "user123",
  "timestamp": "2026-02-12T10:00:00Z",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project proposal",
    "description": "Write and submit the Q1 project proposal",
    "status": "incomplete",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2026-02-15T11:00:00Z",
    "recurrence_pattern": "none",
    "reminder_time": "1h"
  }
}
```

---

### task.updated

**Topic**: task-events, task-updates
**Description**: Published when a task is updated
**Consumers**: Audit Service, WebSocket Service (for multi-client sync)

**Payload Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Updated task ID"
    },
    "updated_fields": {
      "type": "object",
      "description": "Object containing only the fields that were updated",
      "additionalProperties": true
    }
  },
  "required": ["task_id", "updated_fields"]
}
```

**Example**:
```json
{
  "event_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "event_type": "task.updated",
  "user_id": "user123",
  "timestamp": "2026-02-12T11:00:00Z",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "updated_fields": {
      "priority": "urgent",
      "tags": ["work", "urgent", "client"],
      "due_date": "2026-02-14T11:00:00Z"
    }
  }
}
```

---

### task.completed

**Topic**: task-events, task-updates
**Description**: Published when a task is marked as complete
**Consumers**: Recurring Task Service, Audit Service, WebSocket Service

**Payload Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Completed task ID"
    },
    "completion_timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When the task was completed"
    },
    "recurrence_pattern": {
      "type": "string",
      "enum": ["none", "daily", "weekly", "monthly"],
      "description": "Recurrence pattern (for recurring task generation)"
    },
    "original_task": {
      "type": "object",
      "description": "Original task data (for recurring task generation)",
      "properties": {
        "title": {
          "type": "string"
        },
        "description": {
          "type": "string"
        },
        "priority": {
          "type": "string"
        },
        "tags": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "due_date": {
          "type": "string",
          "format": "date-time"
        }
      }
    }
  },
  "required": ["task_id", "completion_timestamp", "recurrence_pattern"]
}
```

**Example**:
```json
{
  "event_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "event_type": "task.completed",
  "user_id": "user123",
  "timestamp": "2026-02-12T12:00:00Z",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "completion_timestamp": "2026-02-12T12:00:00Z",
    "recurrence_pattern": "weekly",
    "original_task": {
      "title": "Weekly team meeting",
      "description": "Attend the weekly team sync",
      "priority": "medium",
      "tags": ["work", "meeting"],
      "due_date": "2026-02-12T14:00:00Z"
    }
  }
}
```

---

### task.deleted

**Topic**: task-events, task-updates
**Description**: Published when a task is deleted
**Consumers**: Audit Service, WebSocket Service (for multi-client sync)

**Payload Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Deleted task ID"
    }
  },
  "required": ["task_id"]
}
```

**Example**:
```json
{
  "event_id": "d4e5f6a7-b8c9-0123-def1-234567890123",
  "event_type": "task.deleted",
  "user_id": "user123",
  "timestamp": "2026-02-12T13:00:00Z",
  "payload": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

---

### reminder.scheduled

**Topic**: task-events
**Description**: Published when a reminder job is scheduled
**Consumers**: Audit Service, Monitoring Service

**Payload Schema**:
```json
{
  "type": "object",
  "properties": {
    "reminder_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique reminder identifier"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Associated task ID"
    },
    "scheduled_time": {
      "type": "string",
      "format": "date-time",
      "description": "When the reminder will trigger"
    },
    "job_id": {
      "type": "string",
      "description": "Dapr job ID"
    }
  },
  "required": ["reminder_id", "task_id", "scheduled_time", "job_id"]
}
```

**Example**:
```json
{
  "event_id": "e5f6a7b8-c9d0-1234-ef12-345678901234",
  "event_type": "reminder.scheduled",
  "user_id": "user123",
  "timestamp": "2026-02-12T10:00:00Z",
  "payload": {
    "reminder_id": "f6a7b8c9-d0e1-2345-f123-456789012345",
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "scheduled_time": "2026-02-15T10:00:00Z",
    "job_id": "reminder-550e8400-e29b-41d4-a716-446655440000-1707991200"
  }
}
```

---

### reminder.triggered

**Topic**: reminders
**Description**: Published when a reminder time arrives (triggered by Dapr Job)
**Consumers**: Notification Service

**Payload Schema**:
```json
{
  "type": "object",
  "properties": {
    "reminder_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique reminder identifier"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Associated task ID"
    },
    "task_title": {
      "type": "string",
      "description": "Task title (for notification)"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "Task due date"
    },
    "reminder_message": {
      "type": "string",
      "description": "Message to display in notification"
    }
  },
  "required": ["reminder_id", "task_id", "task_title", "due_date", "reminder_message"]
}
```

**Example**:
```json
{
  "event_id": "f6a7b8c9-d0e1-2345-f123-456789012345",
  "event_type": "reminder.triggered",
  "user_id": "user123",
  "timestamp": "2026-02-15T10:00:00Z",
  "payload": {
    "reminder_id": "f6a7b8c9-d0e1-2345-f123-456789012345",
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_title": "Complete project proposal",
    "due_date": "2026-02-15T11:00:00Z",
    "reminder_message": "Task 'Complete project proposal' is due in 1 hour"
  }
}
```

---

## Kafka Topics

### task-events

**Purpose**: All task lifecycle events (created, updated, completed, deleted, reminder.scheduled)
**Partitioning**: By user_id (ensures ordering per user)
**Retention**: 7 days
**Consumers**:
- Recurring Task Service (filters for task.completed with recurrence_pattern != "none")
- Audit Service (logs all events)
- Monitoring Service (tracks metrics)

**Configuration**:
```yaml
topic: task-events
partitions: 10
replication-factor: 3
retention.ms: 604800000  # 7 days
```

---

### reminders

**Purpose**: Reminder trigger events
**Partitioning**: By user_id
**Retention**: 1 day
**Consumers**:
- Notification Service (delivers reminders to users)

**Configuration**:
```yaml
topic: reminders
partitions: 10
replication-factor: 3
retention.ms: 86400000  # 1 day
```

---

### task-updates

**Purpose**: Real-time task state changes for multi-client sync
**Partitioning**: By user_id
**Retention**: 1 hour (short-lived, only for real-time sync)
**Consumers**:
- WebSocket Service (pushes updates to connected clients)

**Configuration**:
```yaml
topic: task-updates
partitions: 10
replication-factor: 3
retention.ms: 3600000  # 1 hour
```

---

## Idempotency

All event consumers MUST implement idempotency using event_id:

```python
async def handle_event(event: TaskEvent):
    event_key = f"processed-event:{event.event_id}"

    # Check if already processed
    existing = await dapr_client.get_state(
        store_name="statestore",
        key=event_key
    )

    if existing:
        logger.info(f"Duplicate event {event.event_id}, skipping")
        return

    # Process event
    await process_event_logic(event)

    # Mark as processed (7-day TTL)
    await dapr_client.save_state(
        store_name="statestore",
        key=event_key,
        value="processed",
        state_metadata={"ttlInSeconds": "604800"}
    )
```

---

## Schema Validation

All events MUST be validated at publish and consume time using Pydantic models:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from enum import Enum

class EventType(str, Enum):
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    REMINDER_SCHEDULED = "reminder.scheduled"
    REMINDER_TRIGGERED = "reminder.triggered"

class TaskEvent(BaseModel):
    event_id: UUID
    event_type: EventType
    user_id: str
    timestamp: datetime
    payload: dict  # Validated by event-specific payload models

# Validate before publishing
event = TaskEvent(
    event_id=uuid4(),
    event_type=EventType.TASK_CREATED,
    user_id="user123",
    timestamp=datetime.utcnow(),
    payload=task_created_payload.dict()
)

# Publish to Kafka via Dapr
await dapr_client.publish_event(
    pubsub_name="kafka-pubsub",
    topic_name="task-events",
    data=event.json()
)
```

---

## Error Handling

**Invalid Events**:
- Log error with full event details
- Send to dead-letter queue (DLQ)
- Alert monitoring system
- Do NOT retry (schema violations are permanent failures)

**Processing Failures**:
- Log error with event_id and stack trace
- Retry with exponential backoff (max 3 retries)
- After max retries, send to DLQ
- Alert monitoring system

**Dead-Letter Queue**:
```yaml
topic: task-events-dlq
partitions: 3
replication-factor: 3
retention.ms: 2592000000  # 30 days
```

---

## Monitoring

Track these metrics for all topics:
- Event publish rate (events/second)
- Event processing latency (ms)
- Event processing errors (count)
- DLQ message count (count)
- Consumer lag (messages)

Alert thresholds:
- Processing latency > 5 seconds
- Error rate > 1%
- Consumer lag > 1000 messages
- DLQ message count > 10
