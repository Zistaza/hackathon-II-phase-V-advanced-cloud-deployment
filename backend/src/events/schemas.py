"""Event schemas for Phase-V event-driven architecture.

This module defines Pydantic models for all events in the system,
including task events, reminder events, and recurrence events.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Enumeration of all event types in the system."""

    # Task events
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"

    # Reminder events
    REMINDER_SCHEDULED = "reminder.scheduled"
    REMINDER_DUE = "reminder.due"
    REMINDER_CANCELLED = "reminder.cancelled"

    # Recurrence events
    TASK_RECURRENCE_CREATED = "task.recurrence.created"
    TASK_RECURRENCE_TRIGGERED = "task.recurrence.triggered"
    TASK_RECURRENCE_UPDATED = "task.recurrence.updated"
    TASK_RECURRENCE_DELETED = "task.recurrence.deleted"


class EventMetadata(BaseModel):
    """Metadata for event tracking and tracing."""

    event_id: UUID = Field(default_factory=uuid4)
    correlation_id: Optional[UUID] = None
    causation_id: Optional[UUID] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    version: str = "1.0"
    source: str = "phase-v-backend"
    user_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None


class BaseEvent(BaseModel):
    """Base class for all domain events."""

    metadata: EventMetadata
    data: dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


# =============================================================================
# Task Events
# =============================================================================


class TaskCreatedEventData(BaseModel):
    """Data for task.created event."""

    task_id: UUID
    title: str
    description: Optional[str] = None
    status: str = "pending"
    priority: str = "medium"
    due_date: Optional[datetime] = None
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskCreatedEvent(BaseEvent):
    """Event emitted when a task is created."""

    metadata: EventMetadata = Field(
        default_factory=lambda: EventMetadata(event_type=EventType.TASK_CREATED.value)
    )
    data: TaskCreatedEventData


class TaskUpdatedEventData(BaseModel):
    """Data for task.updated event."""

    task_id: UUID
    updated_fields: dict[str, Any]
    updated_by: UUID
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskUpdatedEvent(BaseEvent):
    """Event emitted when a task is updated."""

    metadata: EventMetadata = Field(
        default_factory=lambda: EventMetadata(event_type=EventType.TASK_UPDATED.value)
    )
    data: TaskUpdatedEventData


class TaskCompletedEventData(BaseModel):
    """Data for task.completed event."""

    task_id: UUID
    completed_by: UUID
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    completion_notes: Optional[str] = None


class TaskCompletedEvent(BaseEvent):
    """Event emitted when a task is completed."""

    metadata: EventMetadata = Field(
        default_factory=lambda: EventMetadata(event_type=EventType.TASK_COMPLETED.value)
    )
    data: TaskCompletedEventData


class TaskDeletedEventData(BaseModel):
    """Data for task.deleted event."""

    task_id: UUID
    deleted_by: UUID
    deleted_at: datetime = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None


class TaskDeletedEvent(BaseEvent):
    """Event emitted when a task is deleted."""

    metadata: EventMetadata = Field(
        default_factory=lambda: EventMetadata(event_type=EventType.TASK_DELETED.value)
    )
    data: TaskDeletedEventData


# =============================================================================
# Reminder Events
# =============================================================================


class ReminderScheduledEventData(BaseModel):
    """Data for reminder.scheduled event."""

    reminder_id: UUID
    task_id: UUID
    reminder_time: datetime
    message: str
    channel: str = "notification"
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReminderScheduledEvent(BaseEvent):
    """Event emitted when a reminder is scheduled."""

    metadata: EventMetadata = Field(
        default_factory=lambda: EventMetadata(event_type=EventType.REMINDER_SCHEDULED.value)
    )
    data: ReminderScheduledEventData


class ReminderDueEventData(BaseModel):
    """Data for reminder.due event."""

    reminder_id: UUID
    task_id: UUID
    message: str
    channel: str = "notification"
    due_at: datetime = Field(default_factory=datetime.utcnow)


class ReminderDueEvent(BaseEvent):
    """Event emitted when a reminder is due."""

    metadata: EventMetadata = Field(
        default_factory=lambda: EventMetadata(event_type=EventType.REMINDER_DUE.value)
    )
    data: ReminderDueEventData


class ReminderCancelledEventData(BaseModel):
    """Data for reminder.cancelled event."""

    reminder_id: UUID
    task_id: UUID
    cancelled_by: UUID
    cancelled_at: datetime = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None


class ReminderCancelledEvent(BaseEvent):
    """Event emitted when a reminder is cancelled."""

    metadata: EventMetadata = Field(
        default_factory=lambda: EventMetadata(event_type=EventType.REMINDER_CANCELLED.value)
    )
    data: ReminderCancelledEventData


# =============================================================================
# Task Recurrence Events
# =============================================================================


class RecurrencePattern(str, Enum):
    """Recurrence pattern types."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class TaskRecurrenceCreatedEventData(BaseModel):
    """Data for task.recurrence.created event."""

    recurrence_id: UUID
    task_id: UUID
    pattern: RecurrencePattern
    interval: int = 1
    start_date: datetime
    end_date: Optional[datetime] = None
    days_of_week: Optional[list[int]] = None
    day_of_month: Optional[int] = None
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskRecurrenceCreatedEvent(BaseEvent):
    """Event emitted when a recurring task is created."""

    metadata: EventMetadata = Field(
        default_factory=lambda: EventMetadata(event_type=EventType.TASK_RECURRENCE_CREATED.value)
    )
    data: TaskRecurrenceCreatedEventData


class TaskRecurrenceTriggeredEventData(BaseModel):
    """Data for task.recurrence.triggered event."""

    recurrence_id: UUID
    task_id: UUID
    new_task_id: UUID
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    occurrence_number: int = 1


class TaskRecurrenceTriggeredEvent(BaseEvent):
    """Event emitted when a recurring task triggers a new instance."""

    metadata: EventMetadata = Field(
        default_factory=lambda: EventMetadata(event_type=EventType.TASK_RECURRENCE_TRIGGERED.value)
    )
    data: TaskRecurrenceTriggeredEventData


class TaskRecurrenceUpdatedEventData(BaseModel):
    """Data for task.recurrence.updated event."""

    recurrence_id: UUID
    task_id: UUID
    updated_fields: dict[str, Any]
    updated_by: UUID
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskRecurrenceUpdatedEvent(BaseEvent):
    """Event emitted when a recurring task configuration is updated."""

    metadata: EventMetadata = Field(
        default_factory=lambda: EventMetadata(event_type=EventType.TASK_RECURRENCE_UPDATED.value)
    )
    data: TaskRecurrenceUpdatedEventData


class TaskRecurrenceDeletedEventData(BaseModel):
    """Data for task.recurrence.deleted event."""

    recurrence_id: UUID
    task_id: UUID
    deleted_by: UUID
    deleted_at: datetime = Field(default_factory=datetime.utcnow)
    delete_future_instances: bool = True


class TaskRecurrenceDeletedEvent(BaseEvent):
    """Event emitted when a recurring task is deleted."""

    metadata: EventMetadata = Field(
        default_factory=lambda: EventMetadata(event_type=EventType.TASK_RECURRENCE_DELETED.value)
    )
    data: TaskRecurrenceDeletedEventData


# =============================================================================
# WebSocket Task Update Event
# =============================================================================


class TaskUpdateEvent(BaseModel):
    """Event for real-time task updates via WebSocket."""

    type: str = "task_update"
    task_id: UUID
    action: str  # created, updated, completed, deleted
    data: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[UUID] = None
