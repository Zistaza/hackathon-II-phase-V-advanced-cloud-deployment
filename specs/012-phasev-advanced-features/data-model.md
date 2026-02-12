# Data Model: Phase-V Advanced Features

**Feature**: 012-phasev-advanced-features
**Date**: 2026-02-12
**Purpose**: Define data entities, relationships, and validation rules

## Core Entities

### Task (Extended)

**Description**: Represents a user's todo item with advanced features (priorities, tags, due dates, recurrence, reminders)

**Storage**: Neon PostgreSQL via SQLModel ORM

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| task_id | UUID | PRIMARY KEY, NOT NULL | Unique task identifier |
| user_id | String | NOT NULL, INDEXED | Owner of the task (from JWT) |
| title | String | NOT NULL, MAX 200 chars | Task title |
| description | String | NULLABLE, MAX 2000 chars | Task description |
| status | Enum | NOT NULL, DEFAULT 'incomplete' | Task status: complete, incomplete |
| priority | Enum | NOT NULL, DEFAULT 'medium' | Priority: low, medium, high, urgent |
| tags | JSONB Array | NOT NULL, DEFAULT [] | Array of tag strings |
| due_date | Timestamp | NULLABLE, WITH TIME ZONE | Task due date (UTC) |
| recurrence_pattern | Enum | NOT NULL, DEFAULT 'none' | Recurrence: none, daily, weekly, monthly |
| reminder_time | String | NULLABLE, MAX 50 chars | Relative reminder time (e.g., "1h", "1d") |
| search_vector | tsvector | GENERATED, INDEXED | Full-text search vector (title + description) |
| created_at | Timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | Timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |
| completed_at | Timestamp | NULLABLE | Completion timestamp |

**Indexes**:
- PRIMARY KEY: task_id
- INDEX: (user_id, status, priority) - Common filter combination
- INDEX: (user_id, due_date) - Date-based filtering
- GIN INDEX: tags - Tag containment queries
- GIN INDEX: search_vector - Full-text search
- INDEX: (user_id, created_at) - Default sorting

**Validation Rules**:
- title: Required, 1-200 characters
- description: Optional, max 2000 characters
- status: Must be 'complete' or 'incomplete'
- priority: Must be 'low', 'medium', 'high', or 'urgent'
- tags: Array of strings, each tag max 50 characters, max 20 tags per task
- due_date: Must be ISO 8601 format, cannot be in the past (for new tasks)
- recurrence_pattern: Must be 'none', 'daily', 'weekly', or 'monthly'
- reminder_time: Must match pattern: \d+[hdw] (e.g., "1h", "2d", "1w")
- user_id: Must match authenticated user from JWT

**State Transitions**:
```
incomplete -> complete (via complete_task)
complete -> incomplete (via update_task with status='incomplete')
```

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import ARRAY, String, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class TaskStatus(str, Enum):
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class RecurrencePattern(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    task_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.INCOMPLETE, nullable=False)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, nullable=False)
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSONB))
    due_date: datetime | None = Field(default=None)
    recurrence_pattern: RecurrencePattern = Field(default=RecurrencePattern.NONE, nullable=False)
    reminder_time: str | None = Field(default=None, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: datetime | None = Field(default=None)
```

---

### ReminderJob

**Description**: Represents a scheduled reminder job in Dapr Jobs API

**Storage**: Dapr Jobs API (persisted by Dapr runtime)

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| job_id | String | PRIMARY KEY | Unique job identifier (format: reminder-{task_id}-{timestamp}) |
| task_id | UUID | NOT NULL | Associated task ID |
| user_id | String | NOT NULL | Task owner ID |
| scheduled_time | Timestamp | NOT NULL | When to trigger reminder (UTC) |
| reminder_message | String | NOT NULL | Message to display in notification |
| task_title | String | NOT NULL | Task title (for notification) |
| due_date | Timestamp | NOT NULL | Task due date (for notification) |

**Validation Rules**:
- job_id: Must follow pattern: reminder-{uuid}-{timestamp}
- scheduled_time: Must be in the future
- user_id: Must match task owner
- All fields required

**Dapr Job Payload**:
```json
{
  "job_id": "reminder-550e8400-e29b-41d4-a716-446655440000-1707753600",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "scheduled_time": "2026-02-15T10:00:00Z",
  "reminder_message": "Task 'Complete project proposal' is due in 1 hour",
  "task_title": "Complete project proposal",
  "due_date": "2026-02-15T11:00:00Z"
}
```

---

### TaskEvent

**Description**: Represents a task lifecycle event published to Kafka

**Storage**: Kafka topics (task-events, task-updates)

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| event_id | UUID | NOT NULL, UNIQUE | Unique event identifier (for idempotency) |
| event_type | Enum | NOT NULL | Event type: task.created, task.updated, task.completed, task.deleted |
| user_id | String | NOT NULL | Task owner ID |
| timestamp | Timestamp | NOT NULL | Event timestamp (UTC) |
| payload | JSON | NOT NULL | Event-specific data |

**Event Types**:

**task.created**:
```json
{
  "event_id": "uuid",
  "event_type": "task.created",
  "user_id": "user123",
  "timestamp": "2026-02-12T10:00:00Z",
  "payload": {
    "task_id": "uuid",
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

**task.updated**:
```json
{
  "event_id": "uuid",
  "event_type": "task.updated",
  "user_id": "user123",
  "timestamp": "2026-02-12T11:00:00Z",
  "payload": {
    "task_id": "uuid",
    "updated_fields": {
      "priority": "urgent",
      "tags": ["work", "urgent", "client"]
    }
  }
}
```

**task.completed**:
```json
{
  "event_id": "uuid",
  "event_type": "task.completed",
  "user_id": "user123",
  "timestamp": "2026-02-12T12:00:00Z",
  "payload": {
    "task_id": "uuid",
    "completion_timestamp": "2026-02-12T12:00:00Z",
    "recurrence_pattern": "weekly"
  }
}
```

**task.deleted**:
```json
{
  "event_id": "uuid",
  "event_type": "task.deleted",
  "user_id": "user123",
  "timestamp": "2026-02-12T13:00:00Z",
  "payload": {
    "task_id": "uuid"
  }
}
```

**Validation Rules**:
- event_id: Must be valid UUID v4
- event_type: Must be one of the defined types
- user_id: Must be non-empty string
- timestamp: Must be ISO 8601 format
- payload: Must conform to event-specific schema

**Pydantic Models**:
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
    REMINDER_TRIGGERED = "reminder.triggered"

class TaskCreatedPayload(BaseModel):
    task_id: UUID
    title: str
    description: str | None
    status: str
    priority: str
    tags: list[str]
    due_date: datetime | None
    recurrence_pattern: str
    reminder_time: str | None

class TaskUpdatedPayload(BaseModel):
    task_id: UUID
    updated_fields: dict

class TaskCompletedPayload(BaseModel):
    task_id: UUID
    completion_timestamp: datetime
    recurrence_pattern: str

class TaskDeletedPayload(BaseModel):
    task_id: UUID

class TaskEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: TaskCreatedPayload | TaskUpdatedPayload | TaskCompletedPayload | TaskDeletedPayload
```

---

### ReminderEvent

**Description**: Represents a reminder trigger event published to reminders topic

**Storage**: Kafka reminders topic

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| event_id | UUID | NOT NULL, UNIQUE | Unique event identifier |
| event_type | String | NOT NULL, VALUE 'reminder.triggered' | Event type |
| user_id | String | NOT NULL | Task owner ID |
| timestamp | Timestamp | NOT NULL | Event timestamp (UTC) |
| payload | JSON | NOT NULL | Reminder-specific data |

**Schema**:
```json
{
  "event_id": "uuid",
  "event_type": "reminder.triggered",
  "user_id": "user123",
  "timestamp": "2026-02-15T10:00:00Z",
  "payload": {
    "reminder_id": "uuid",
    "task_id": "uuid",
    "task_title": "Complete project proposal",
    "due_date": "2026-02-15T11:00:00Z",
    "reminder_message": "Task 'Complete project proposal' is due in 1 hour"
  }
}
```

---

## Relationships

```
Task (1) ----< (0..1) ReminderJob
  - One task can have zero or one active reminder job
  - Relationship managed via task_id in ReminderJob

Task (1) ----< (0..*) TaskEvent
  - One task generates multiple events over its lifecycle
  - Relationship tracked via task_id in event payload

Task (1) ----< (0..*) ReminderEvent
  - One task can generate multiple reminder events (if rescheduled)
  - Relationship tracked via task_id in event payload
```

---

## Database Migration

**Migration Script** (Alembic):
```python
"""Add advanced features to tasks table

Revision ID: 002_advanced_features
Revises: 001_initial_schema
Create Date: 2026-02-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR

def upgrade():
    # Add new columns
    op.add_column('tasks', sa.Column('priority', sa.String(10), nullable=False, server_default='medium'))
    op.add_column('tasks', sa.Column('tags', JSONB, nullable=False, server_default='[]'))
    op.add_column('tasks', sa.Column('due_date', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(20), nullable=False, server_default='none'))
    op.add_column('tasks', sa.Column('reminder_time', sa.String(50), nullable=True))
    op.add_column('tasks', sa.Column('search_vector', TSVECTOR, nullable=True))

    # Create indexes
    op.create_index('idx_tasks_priority', 'tasks', ['user_id', 'priority'])
    op.create_index('idx_tasks_tags', 'tasks', ['tags'], postgresql_using='gin')
    op.create_index('idx_tasks_search', 'tasks', ['search_vector'], postgresql_using='gin')
    op.create_index('idx_tasks_due_date', 'tasks', ['user_id', 'due_date'])
    op.create_index('idx_tasks_status_priority', 'tasks', ['user_id', 'status', 'priority'])

    # Create trigger for search_vector
    op.execute("""
        CREATE TRIGGER tasks_search_vector_update BEFORE INSERT OR UPDATE
        ON tasks FOR EACH ROW EXECUTE FUNCTION
        tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);
    """)

    # Update existing rows
    op.execute("UPDATE tasks SET search_vector = to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, ''))")

def downgrade():
    op.drop_index('idx_tasks_status_priority', 'tasks')
    op.drop_index('idx_tasks_due_date', 'tasks')
    op.drop_index('idx_tasks_search', 'tasks')
    op.drop_index('idx_tasks_tags', 'tasks')
    op.drop_index('idx_tasks_priority', 'tasks')
    op.execute("DROP TRIGGER IF EXISTS tasks_search_vector_update ON tasks")
    op.drop_column('tasks', 'search_vector')
    op.drop_column('tasks', 'reminder_time')
    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
```

---

## Query Patterns

### Filter by Priority
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND priority = $2
ORDER BY created_at DESC;
```

### Filter by Tags (contains all)
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND tags @> $2::jsonb
ORDER BY created_at DESC;
```

### Full-Text Search
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND search_vector @@ plainto_tsquery('english', $2)
ORDER BY ts_rank(search_vector, plainto_tsquery('english', $2)) DESC;
```

### Combined Filter + Sort
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND status = $2
  AND priority = $3
  AND tags @> $4::jsonb
  AND due_date BETWEEN $5 AND $6
ORDER BY due_date ASC;
```

---

## Data Validation

**Backend Validation** (Pydantic):
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: list[str] = Field(default_factory=list, max_items=20)
    due_date: datetime | None = None
    recurrence_pattern: RecurrencePattern = RecurrencePattern.NONE
    reminder_time: str | None = Field(default=None, pattern=r'^\d+[hdw]$')

    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        for tag in v:
            if len(tag) > 50:
                raise ValueError('Tag length must be <= 50 characters')
        return v

    @validator('due_date')
    def validate_due_date(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Due date cannot be in the past')
        return v

    @validator('reminder_time')
    def validate_reminder_time(cls, v, values):
        if v and not values.get('due_date'):
            raise ValueError('Reminder requires due_date to be set')
        if v and not re.match(r'^\d+[hdw]$', v):
            raise ValueError('Reminder time must match pattern: <number><h|d|w>')
        return v
```

---

## Performance Considerations

- All queries filtered by user_id (indexed)
- Composite indexes for common filter combinations
- GIN indexes for JSONB tags and full-text search
- Search vector automatically maintained by trigger
- Pagination recommended for large result sets (>100 tasks)
- Query timeout: 5 seconds
- Connection pooling: 20 connections per service instance
