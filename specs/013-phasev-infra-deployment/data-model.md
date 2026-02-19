# Data Model & Event Schemas: Phase-V Infrastructure

**Feature**: 013-phasev-infra-deployment
**Date**: 2026-02-14
**Status**: Complete

## Overview

This document defines all event schemas, entities, and data structures for the event-driven architecture. All events follow a standardized schema with idempotency guarantees.

---

## Core Event Schema

All events MUST conform to this base schema:

```yaml
BaseEvent:
  event_id: UUID          # Unique identifier for idempotency (required)
  event_type: string      # Event type identifier (required)
  user_id: string         # Owner of the resource (required)
  timestamp: ISO 8601     # Event creation time in UTC (required)
  payload: object         # Event-specific data (required)
  metadata:               # Optional metadata
    source: string        # Service that published the event
    correlation_id: UUID  # For tracing related events
    version: string       # Schema version (e.g., "1.0.0")
```

**Validation Rules**:
- `event_id` MUST be a valid UUID v4
- `event_type` MUST match pattern: `^[a-z]+\.[a-z]+$` (e.g., "task.created")
- `user_id` MUST be a non-empty string
- `timestamp` MUST be ISO 8601 format with timezone (e.g., "2026-02-14T10:30:00Z")
- `payload` MUST be a valid JSON object

---

## Event Types

### 1. Task Lifecycle Events

#### 1.1 task.created

Published when a new task is created.

```yaml
TaskCreatedEvent:
  event_id: UUID
  event_type: "task.created"
  user_id: string
  timestamp: ISO 8601
  payload:
    task_id: UUID
    title: string (max 255 chars)
    description: string (optional, max 5000 chars)
    priority: enum ["low", "medium", "high", "urgent"]
    tags: array<string> (optional, max 10 tags, each max 50 chars)
    due_date: ISO 8601 (optional)
    recurrence_rule: string (optional, cron-like format)
    reminder_time: ISO 8601 (optional)
  metadata:
    source: "backend-api"
    correlation_id: UUID
    version: "1.0.0"
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task.created",
  "user_id": "user_123",
  "timestamp": "2026-02-14T10:30:00Z",
  "payload": {
    "task_id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase V",
    "priority": "high",
    "tags": ["documentation", "phase-v"],
    "due_date": "2026-02-20T17:00:00Z",
    "recurrence_rule": null,
    "reminder_time": "2026-02-20T09:00:00Z"
  },
  "metadata": {
    "source": "backend-api",
    "correlation_id": "770e8400-e29b-41d4-a716-446655440002",
    "version": "1.0.0"
  }
}
```

#### 1.2 task.updated

Published when a task is modified.

```yaml
TaskUpdatedEvent:
  event_id: UUID
  event_type: "task.updated"
  user_id: string
  timestamp: ISO 8601
  payload:
    task_id: UUID
    changes:
      title: string (optional)
      description: string (optional)
      priority: enum ["low", "medium", "high", "urgent"] (optional)
      tags: array<string> (optional)
      due_date: ISO 8601 (optional)
      recurrence_rule: string (optional)
      reminder_time: ISO 8601 (optional)
    previous_values:
      # Same structure as changes, contains old values
  metadata:
    source: "backend-api"
    correlation_id: UUID
    version: "1.0.0"
```

**Example**:
```json
{
  "event_id": "880e8400-e29b-41d4-a716-446655440003",
  "event_type": "task.updated",
  "user_id": "user_123",
  "timestamp": "2026-02-14T11:00:00Z",
  "payload": {
    "task_id": "660e8400-e29b-41d4-a716-446655440001",
    "changes": {
      "priority": "urgent",
      "due_date": "2026-02-18T17:00:00Z"
    },
    "previous_values": {
      "priority": "high",
      "due_date": "2026-02-20T17:00:00Z"
    }
  },
  "metadata": {
    "source": "backend-api",
    "correlation_id": "990e8400-e29b-41d4-a716-446655440004",
    "version": "1.0.0"
  }
}
```

#### 1.3 task.completed

Published when a task is marked as completed.

```yaml
TaskCompletedEvent:
  event_id: UUID
  event_type: "task.completed"
  user_id: string
  timestamp: ISO 8601
  payload:
    task_id: UUID
    completed_at: ISO 8601
    recurrence_rule: string (optional, if task is recurring)
  metadata:
    source: "backend-api"
    correlation_id: UUID
    version: "1.0.0"
```

**Example**:
```json
{
  "event_id": "aa0e8400-e29b-41d4-a716-446655440005",
  "event_type": "task.completed",
  "user_id": "user_123",
  "timestamp": "2026-02-14T12:00:00Z",
  "payload": {
    "task_id": "660e8400-e29b-41d4-a716-446655440001",
    "completed_at": "2026-02-14T12:00:00Z",
    "recurrence_rule": null
  },
  "metadata": {
    "source": "backend-api",
    "correlation_id": "bb0e8400-e29b-41d4-a716-446655440006",
    "version": "1.0.0"
  }
}
```

#### 1.4 task.deleted

Published when a task is deleted.

```yaml
TaskDeletedEvent:
  event_id: UUID
  event_type: "task.deleted"
  user_id: string
  timestamp: ISO 8601
  payload:
    task_id: UUID
    deleted_at: ISO 8601
  metadata:
    source: "backend-api"
    correlation_id: UUID
    version: "1.0.0"
```

**Example**:
```json
{
  "event_id": "cc0e8400-e29b-41d4-a716-446655440007",
  "event_type": "task.deleted",
  "user_id": "user_123",
  "timestamp": "2026-02-14T13:00:00Z",
  "payload": {
    "task_id": "660e8400-e29b-41d4-a716-446655440001",
    "deleted_at": "2026-02-14T13:00:00Z"
  },
  "metadata": {
    "source": "backend-api",
    "correlation_id": "dd0e8400-e29b-41d4-a716-446655440008",
    "version": "1.0.0"
  }
}
```

### 2. Reminder Events

#### 2.1 reminder.scheduled

Published when a reminder is scheduled for a task.

```yaml
ReminderScheduledEvent:
  event_id: UUID
  event_type: "reminder.scheduled"
  user_id: string
  timestamp: ISO 8601
  payload:
    reminder_id: UUID
    task_id: UUID
    reminder_time: ISO 8601
    job_id: string (Dapr Jobs API job identifier)
  metadata:
    source: "reminder-scheduler"
    correlation_id: UUID
    version: "1.0.0"
```

#### 2.2 reminder.due

Published when a scheduled reminder time arrives.

```yaml
ReminderDueEvent:
  event_id: UUID
  event_type: "reminder.due"
  user_id: string
  timestamp: ISO 8601
  payload:
    reminder_id: UUID
    task_id: UUID
    task_title: string
    reminder_time: ISO 8601
  metadata:
    source: "reminder-scheduler"
    correlation_id: UUID
    version: "1.0.0"
```

**Example**:
```json
{
  "event_id": "ee0e8400-e29b-41d4-a716-446655440009",
  "event_type": "reminder.due",
  "user_id": "user_123",
  "timestamp": "2026-02-20T09:00:00Z",
  "payload": {
    "reminder_id": "ff0e8400-e29b-41d4-a716-446655440010",
    "task_id": "660e8400-e29b-41d4-a716-446655440001",
    "task_title": "Complete project documentation",
    "reminder_time": "2026-02-20T09:00:00Z"
  },
  "metadata": {
    "source": "reminder-scheduler",
    "correlation_id": "000e8400-e29b-41d4-a716-446655440011",
    "version": "1.0.0"
  }
}
```

#### 2.3 reminder.cancelled

Published when a reminder is cancelled (task completed or deleted).

```yaml
ReminderCancelledEvent:
  event_id: UUID
  event_type: "reminder.cancelled"
  user_id: string
  timestamp: ISO 8601
  payload:
    reminder_id: UUID
    task_id: UUID
    reason: enum ["task_completed", "task_deleted", "manual_cancellation"]
    job_id: string (Dapr Jobs API job identifier)
  metadata:
    source: "reminder-scheduler"
    correlation_id: UUID
    version: "1.0.0"
```

### 3. Recurring Task Events

#### 3.1 task.recurrence

Published when a recurring task needs to create the next instance.

```yaml
TaskRecurrenceEvent:
  event_id: UUID
  event_type: "task.recurrence"
  user_id: string
  timestamp: ISO 8601
  payload:
    parent_task_id: UUID
    recurrence_rule: string (cron-like format)
    next_due_date: ISO 8601
    template:
      title: string
      description: string
      priority: enum ["low", "medium", "high", "urgent"]
      tags: array<string>
  metadata:
    source: "event-processor"
    correlation_id: UUID
    version: "1.0.0"
```

**Example**:
```json
{
  "event_id": "110e8400-e29b-41d4-a716-446655440012",
  "event_type": "task.recurrence",
  "user_id": "user_123",
  "timestamp": "2026-02-14T12:00:00Z",
  "payload": {
    "parent_task_id": "660e8400-e29b-41d4-a716-446655440001",
    "recurrence_rule": "0 9 * * 1",
    "next_due_date": "2026-02-17T09:00:00Z",
    "template": {
      "title": "Weekly team standup",
      "description": "Recurring weekly meeting",
      "priority": "medium",
      "tags": ["meeting", "recurring"]
    }
  },
  "metadata": {
    "source": "event-processor",
    "correlation_id": "220e8400-e29b-41d4-a716-446655440013",
    "version": "1.0.0"
  }
}
```

### 4. Real-Time Update Events

#### 4.1 task.update

Published for real-time WebSocket updates to clients.

```yaml
TaskUpdateEvent:
  event_id: UUID
  event_type: "task.update"
  user_id: string
  timestamp: ISO 8601
  payload:
    task_id: UUID
    update_type: enum ["created", "updated", "completed", "deleted"]
    changes: object (same as task.updated changes)
  metadata:
    source: "websocket-service"
    correlation_id: UUID
    version: "1.0.0"
```

---

## Kafka Topics

### Topic: task-events

**Purpose**: All task lifecycle events (created, updated, completed, deleted)

**Configuration**:
- Partitions: 3 (partitioned by user_id for ordering guarantees)
- Replication Factor: 1 (Redpanda Cloud default)
- Retention: 7 days
- Cleanup Policy: delete

**Consumers**:
- Event Processor (recurring tasks)
- Audit Service (logging)
- WebSocket Service (real-time updates)

**Schema**:
```yaml
key: user_id (string)
value: TaskCreatedEvent | TaskUpdatedEvent | TaskCompletedEvent | TaskDeletedEvent
```

### Topic: reminders

**Purpose**: Reminder scheduling and delivery events

**Configuration**:
- Partitions: 3 (partitioned by user_id)
- Replication Factor: 1
- Retention: 7 days
- Cleanup Policy: delete

**Consumers**:
- Notification Service (send reminders)

**Schema**:
```yaml
key: user_id (string)
value: ReminderScheduledEvent | ReminderDueEvent | ReminderCancelledEvent
```

### Topic: task-updates

**Purpose**: Real-time task state changes for WebSocket clients

**Configuration**:
- Partitions: 3 (partitioned by user_id)
- Replication Factor: 1
- Retention: 1 hour (short retention for real-time updates)
- Cleanup Policy: delete

**Consumers**:
- WebSocket Service (broadcast to connected clients)

**Schema**:
```yaml
key: user_id (string)
value: TaskUpdateEvent
```

---

## Dapr State Store Schema

### State Key Format

```
{component_name}:{entity_type}:{entity_id}
```

**Examples**:
- `event-processor:processed-event:550e8400-e29b-41d4-a716-446655440000`
- `reminder-scheduler:scheduled-job:ff0e8400-e29b-41d4-a716-446655440010`

### State Entities

#### 1. Processed Event (for idempotency)

```yaml
ProcessedEvent:
  key: "event-processor:processed-event:{event_id}"
  value:
    event_id: UUID
    event_type: string
    processed_at: ISO 8601
    processor: string (service name)
  ttl: 604800 (7 days in seconds)
```

#### 2. Scheduled Job (for reminder tracking)

```yaml
ScheduledJob:
  key: "reminder-scheduler:scheduled-job:{reminder_id}"
  value:
    reminder_id: UUID
    task_id: UUID
    user_id: string
    job_id: string (Dapr Jobs API identifier)
    scheduled_time: ISO 8601
    status: enum ["scheduled", "delivered", "cancelled"]
  ttl: 2592000 (30 days in seconds)
```

---

## Pydantic Models (Python)

### Base Event Model

```python
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class EventMetadata(BaseModel):
    source: str
    correlation_id: UUID4
    version: str = "1.0.0"

class BaseEvent(BaseModel):
    event_id: UUID4 = Field(..., description="Unique event identifier")
    event_type: str = Field(..., pattern=r"^[a-z]+\.[a-z]+$")
    user_id: str = Field(..., min_length=1)
    timestamp: datetime
    payload: Dict[str, Any]
    metadata: EventMetadata

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Task Event Models

```python
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskCreatedPayload(BaseModel):
    task_id: UUID4
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Priority
    tags: Optional[list[str]] = Field(None, max_items=10)
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None
    reminder_time: Optional[datetime] = None

class TaskCreatedEvent(BaseEvent):
    event_type: str = Field(default="task.created", const=True)
    payload: TaskCreatedPayload
```

---

## Event Publishing Guidelines

### 1. Event ID Generation

```python
import uuid

event_id = uuid.uuid4()
```

### 2. Timestamp Format

```python
from datetime import datetime, timezone

timestamp = datetime.now(timezone.utc)
```

### 3. Partition Key

Always use `user_id` as the partition key to ensure ordering guarantees per user.

```python
partition_key = event.user_id
```

### 4. Schema Validation

Always validate events before publishing:

```python
from pydantic import ValidationError

try:
    event = TaskCreatedEvent(**event_data)
    # Publish event
except ValidationError as e:
    # Handle validation error
    logger.error(f"Event validation failed: {e}")
```

---

## Event Consumption Guidelines

### 1. Idempotency Check

Always check if event has been processed before:

```python
async def is_event_processed(event_id: str) -> bool:
    state_key = f"event-processor:processed-event:{event_id}"
    state = await dapr_client.get_state(store_name="statestore", key=state_key)
    return state.data is not None
```

### 2. Mark Event as Processed

After successful processing, mark event as processed:

```python
async def mark_event_processed(event_id: str, event_type: str):
    state_key = f"event-processor:processed-event:{event_id}"
    state_value = {
        "event_id": event_id,
        "event_type": event_type,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "processor": "event-processor"
    }
    await dapr_client.save_state(
        store_name="statestore",
        key=state_key,
        value=state_value,
        state_metadata={"ttlInSeconds": "604800"}  # 7 days
    )
```

### 3. Error Handling

Implement retry logic with exponential backoff:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def process_event(event: BaseEvent):
    # Process event logic
    pass
```

### 4. Dead Letter Queue

Route failed events to dead-letter queue after max retries:

```python
async def send_to_dlq(event: BaseEvent, error: Exception):
    dlq_event = {
        "original_event": event.dict(),
        "error": str(error),
        "failed_at": datetime.now(timezone.utc).isoformat(),
        "retry_count": 3
    }
    await dapr_client.publish_event(
        pubsub_name="pubsub",
        topic_name="dead-letter-queue",
        data=dlq_event
    )
```

---

## Summary

This data model provides:
- ✅ Standardized event schemas with idempotency guarantees
- ✅ Clear topic design with partitioning strategy
- ✅ Pydantic models for type safety and validation
- ✅ Dapr State Store schema for event processing state
- ✅ Guidelines for event publishing and consumption
- ✅ Error handling and dead-letter queue patterns

**Next Steps**: Create contracts/ directory with YAML configurations
