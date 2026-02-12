# Quickstart Guide: Phase-V Advanced Features

**Feature**: 012-phasev-advanced-features
**Date**: 2026-02-12
**Audience**: Developers implementing Phase-V advanced features

## Overview

This guide provides step-by-step instructions for implementing Phase-V advanced features including recurring tasks, due dates & reminders, priorities, tags, search, filter, and sort capabilities.

---

## Prerequisites

- Phase-III Todo AI Chatbot fully functional
- Dapr runtime installed and configured
- Kafka/Redpanda cluster running
- Neon PostgreSQL database accessible
- Python 3.11+ with FastAPI, SQLModel, Pydantic
- OpenAI Agents SDK and MCP SDK configured
- Better Auth with JWT authentication working

---

## Implementation Phases

### Phase 1: Database Schema Migration

**Duration**: 1-2 hours

**Steps**:

1. Create migration script:
```bash
cd backend
alembic revision -m "add_advanced_features"
```

2. Add migration code (see data-model.md for full SQL):
```python
def upgrade():
    op.add_column('tasks', sa.Column('priority', sa.String(10), nullable=False, server_default='medium'))
    op.add_column('tasks', sa.Column('tags', JSONB, nullable=False, server_default='[]'))
    op.add_column('tasks', sa.Column('due_date', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(20), nullable=False, server_default='none'))
    op.add_column('tasks', sa.Column('reminder_time', sa.String(50), nullable=True))
    op.add_column('tasks', sa.Column('search_vector', TSVECTOR, nullable=True))

    # Create indexes (see data-model.md)
    # Create search trigger (see data-model.md)
```

3. Run migration:
```bash
alembic upgrade head
```

4. Verify schema:
```bash
psql $DATABASE_URL -c "\d tasks"
```

**Validation**:
- All new columns exist
- All indexes created
- Search trigger active

---

### Phase 2: Extend MCP Tools

**Duration**: 3-4 hours

**Steps**:

1. Update Task model in `backend/src/models/task.py`:
```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSONB
from enum import Enum

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
    # ... existing fields ...
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSONB))
    due_date: datetime | None = Field(default=None)
    recurrence_pattern: RecurrencePattern = Field(default=RecurrencePattern.NONE)
    reminder_time: str | None = Field(default=None)
```

2. Update MCP tool schemas in `backend/src/mcp/tools.py`:
```python
# add_task tool
{
    "name": "add_task",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
            "tags": {"type": "array", "items": {"type": "string"}},
            "due_date": {"type": "string", "format": "date-time"},
            "recurrence_pattern": {"type": "string", "enum": ["none", "daily", "weekly", "monthly"]},
            "reminder_time": {"type": "string", "pattern": "^\\d+[hdw]$"}
        },
        "required": ["title"]
    }
}
```

3. Update tool implementations to handle new fields

4. Add validation logic:
```python
from pydantic import BaseModel, validator

class TaskCreate(BaseModel):
    title: str
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: list[str] = []
    due_date: datetime | None = None
    recurrence_pattern: RecurrencePattern = RecurrencePattern.NONE
    reminder_time: str | None = None

    @validator('due_date')
    def validate_due_date(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Due date cannot be in the past')
        return v
```

**Validation**:
- Test add_task with all new parameters
- Test update_task with new parameters
- Test list_tasks without parameters (backward compatibility)

---

### Phase 3: Implement Search & Filter

**Duration**: 2-3 hours

**Steps**:

1. Update list_tasks implementation in `backend/src/mcp/tools.py`:
```python
async def list_tasks(
    user_id: str,
    status: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_date_filter: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 50,
    offset: int = 0
):
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if tags:
        query = query.where(Task.tags.contains(tags))
    if search:
        query = query.where(Task.search_vector.match(search))
    if due_date_filter:
        # Apply date range filter
        pass

    # Apply sorting
    if sort_order == "asc":
        query = query.order_by(getattr(Task, sort_by).asc())
    else:
        query = query.order_by(getattr(Task, sort_by).desc())

    # Apply pagination
    query = query.limit(limit).offset(offset)

    results = await session.execute(query)
    return results.scalars().all()
```

2. Add full-text search support:
```python
from sqlalchemy import func

# Full-text search
if search:
    query = query.where(
        func.to_tsvector('english', Task.title + ' ' + Task.description).match(search)
    )
```

**Validation**:
- Test search with various keywords
- Test filter by priority
- Test filter by tags
- Test combined filters
- Test sorting by different fields
- Verify query performance (<1s for 10k tasks)

---

### Phase 4: Implement Event Publishing

**Duration**: 2-3 hours

**Steps**:

1. Create event models in `backend/src/events/models.py`:
```python
from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"

class TaskEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: dict
```

2. Create event publisher in `backend/src/events/publisher.py`:
```python
from dapr.clients import DaprClient

async def publish_task_event(event: TaskEvent):
    async with DaprClient() as client:
        await client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="task-events",
            data=event.json()
        )

        # Also publish to task-updates for multi-client sync
        await client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="task-updates",
            data=event.json()
        )
```

3. Update MCP tool implementations to publish events:
```python
async def add_task_impl(...):
    # Create task
    task = Task(...)
    session.add(task)
    await session.commit()

    # Publish event
    event = TaskEvent(
        event_type=EventType.TASK_CREATED,
        user_id=user_id,
        payload=task.dict()
    )
    await publish_task_event(event)

    return task
```

**Validation**:
- Verify events published to Kafka
- Check event format matches schema
- Verify both task-events and task-updates topics receive events

---

### Phase 5: Implement Reminder Scheduling

**Duration**: 3-4 hours

**Steps**:

1. Create reminder scheduler in `backend/src/reminders/scheduler.py`:
```python
from dapr.clients import DaprClient
from datetime import datetime, timedelta

async def schedule_reminder(task: Task):
    if not task.due_date or not task.reminder_time:
        return

    # Parse reminder_time (e.g., "1h", "2d")
    amount = int(task.reminder_time[:-1])
    unit = task.reminder_time[-1]

    if unit == 'h':
        delta = timedelta(hours=amount)
    elif unit == 'd':
        delta = timedelta(days=amount)
    elif unit == 'w':
        delta = timedelta(weeks=amount)

    scheduled_time = task.due_date - delta

    # Schedule Dapr job
    job_id = f"reminder-{task.task_id}-{int(scheduled_time.timestamp())}"

    async with DaprClient() as client:
        await client.create_job(
            job_name=job_id,
            schedule=scheduled_time.isoformat(),
            data={
                "task_id": str(task.task_id),
                "user_id": task.user_id,
                "task_title": task.title,
                "due_date": task.due_date.isoformat(),
                "reminder_message": f"Task '{task.title}' is due in {task.reminder_time}"
            }
        )
```

2. Create reminder job handler in `backend/src/reminders/handler.py`:
```python
@app.post("/api/reminders/trigger")
async def handle_reminder_trigger(job_data: dict):
    # Publish reminder.triggered event
    event = TaskEvent(
        event_type=EventType.REMINDER_TRIGGERED,
        user_id=job_data["user_id"],
        payload=job_data
    )

    await publish_event(
        pubsub_name="kafka-pubsub",
        topic_name="reminders",
        data=event.json()
    )
```

3. Update add_task and update_task to schedule reminders:
```python
async def add_task_impl(...):
    task = Task(...)
    session.add(task)
    await session.commit()

    # Schedule reminder
    await schedule_reminder(task)

    # Publish event
    await publish_task_event(...)
```

**Validation**:
- Create task with reminder
- Verify Dapr job created
- Wait for reminder time
- Verify reminder.triggered event published

---

### Phase 6: Implement Recurring Task Service

**Duration**: 3-4 hours

**Steps**:

1. Create recurring task service in `backend/src/services/recurring_tasks.py`:
```python
from dapr.ext.fastapi import DaprApp
from datetime import timedelta

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub_name="kafka-pubsub", topic="task-events")
async def handle_task_event(event: TaskEvent):
    if event.event_type != EventType.TASK_COMPLETED:
        return

    if event.payload["recurrence_pattern"] == "none":
        return

    # Check idempotency
    event_key = f"processed-event:{event.event_id}"
    existing = await dapr_client.get_state("statestore", event_key)
    if existing:
        return

    # Calculate next due date
    original_task = event.payload["original_task"]
    next_due_date = calculate_next_due_date(
        original_task["due_date"],
        event.payload["recurrence_pattern"]
    )

    # Create next instance
    await add_task_impl(
        user_id=event.user_id,
        title=original_task["title"],
        description=original_task["description"],
        priority=original_task["priority"],
        tags=original_task["tags"],
        due_date=next_due_date,
        recurrence_pattern=event.payload["recurrence_pattern"],
        reminder_time=original_task.get("reminder_time")
    )

    # Mark as processed
    await dapr_client.save_state(
        "statestore",
        event_key,
        "processed",
        state_metadata={"ttlInSeconds": "604800"}
    )

def calculate_next_due_date(current_due_date: datetime, pattern: str) -> datetime:
    if pattern == "daily":
        return current_due_date + timedelta(days=1)
    elif pattern == "weekly":
        return current_due_date + timedelta(weeks=1)
    elif pattern == "monthly":
        return current_due_date + timedelta(days=30)  # Approximate
```

**Validation**:
- Create recurring task
- Complete the task
- Verify next instance created automatically
- Verify idempotency (complete same task twice)

---

### Phase 7: Frontend Integration

**Duration**: 2-3 hours

**Steps**:

1. Update ChatKit message rendering to display new fields:
```typescript
// frontend/src/components/TaskMessage.tsx
function TaskMessage({ task }) {
  return (
    <div className="task-message">
      <h3>{task.title}</h3>
      <p>{task.description}</p>
      <div className="task-metadata">
        <span className={`priority-${task.priority}`}>{task.priority}</span>
        {task.tags.map(tag => <span className="tag">{tag}</span>)}
        {task.due_date && <span>Due: {formatDate(task.due_date)}</span>}
        {task.recurrence_pattern !== 'none' && <span>Repeats: {task.recurrence_pattern}</span>}
      </div>
    </div>
  );
}
```

2. Add WebSocket subscription for real-time updates:
```typescript
// frontend/src/services/websocket.ts
const ws = new WebSocket(`ws://backend/ws/${userId}`);

ws.onmessage = (event) => {
  const taskEvent = JSON.parse(event.data);

  if (taskEvent.event_type === 'task.created') {
    addTaskToList(taskEvent.payload);
  } else if (taskEvent.event_type === 'task.updated') {
    updateTaskInList(taskEvent.payload);
  } else if (taskEvent.event_type === 'task.deleted') {
    removeTaskFromList(taskEvent.payload.task_id);
  }
};
```

**Validation**:
- Create task in one browser tab
- Verify it appears in another tab within 2 seconds
- Update task priority
- Verify update appears in all tabs

---

## Testing Checklist

### Unit Tests
- [ ] Task model validation
- [ ] MCP tool parameter validation
- [ ] Event schema validation
- [ ] Recurrence date calculation
- [ ] Search query construction
- [ ] Filter query construction

### Integration Tests
- [ ] Create task with all fields
- [ ] Update task priority and tags
- [ ] Search tasks by keyword
- [ ] Filter by priority + status
- [ ] Sort by due date
- [ ] Complete recurring task → next instance created
- [ ] Schedule reminder → notification delivered
- [ ] Multi-client sync via WebSocket

### Performance Tests
- [ ] Search 10,000 tasks < 500ms
- [ ] Filter 10,000 tasks < 200ms
- [ ] Sort 10,000 tasks < 100ms
- [ ] 1,000 concurrent users

### Edge Case Tests
- [ ] Past due date rejected
- [ ] Invalid priority rejected
- [ ] Empty search returns all tasks
- [ ] Duplicate event handled idempotently
- [ ] Reminder scheduling failure handled

---

## Deployment

### Local (Minikube)

1. Start Minikube:
```bash
minikube start --cpus=4 --memory=8192
```

2. Install Dapr:
```bash
dapr init -k
```

3. Deploy Kafka:
```bash
helm install kafka bitnami/kafka
```

4. Deploy application:
```bash
helm install todo-app ./helm/todo-app
```

### Cloud (AKS/GKE/OKE)

1. Create cluster
2. Install Dapr
3. Configure Kafka (Redpanda Cloud or Strimzi)
4. Deploy via Helm
5. Configure monitoring (Prometheus + Grafana)

---

## Troubleshooting

**Events not publishing**:
- Check Dapr sidecar logs: `kubectl logs <pod> -c daprd`
- Verify Kafka connectivity
- Check pubsub component configuration

**Reminders not triggering**:
- Check Dapr Jobs API logs
- Verify job was created: `dapr jobs list`
- Check reminder handler endpoint

**Search not working**:
- Verify search_vector column populated
- Check trigger is active: `\d+ tasks`
- Test query directly in psql

**Recurring tasks not generating**:
- Check Recurring Task Service logs
- Verify event subscription active
- Check idempotency state store

---

## Performance Optimization

1. Add database indexes (already in migration)
2. Enable query result caching
3. Use connection pooling (20 connections)
4. Enable Dapr state store caching
5. Optimize event payload size
6. Use pagination for large result sets

---

## Monitoring

Track these metrics:
- Task operations per second
- Search query latency
- Filter query latency
- Event processing latency
- Reminder delivery success rate
- Recurring task generation success rate
- Multi-client sync latency

Set up alerts for:
- Query latency > 1 second
- Event processing errors > 1%
- Reminder delivery failures > 5%
- Consumer lag > 1000 messages
