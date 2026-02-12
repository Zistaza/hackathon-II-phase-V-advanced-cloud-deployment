from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from typing import Optional, Dict, Any, List


class EventType(str, Enum):
    """Event types for task lifecycle"""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    REMINDER_SCHEDULED = "reminder.scheduled"
    REMINDER_TRIGGERED = "reminder.triggered"


class TaskCreatedPayload(BaseModel):
    """Payload for task.created event"""
    task_id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    tags: List[str]
    due_date: Optional[datetime]
    recurrence_pattern: str
    reminder_time: Optional[str]


class TaskUpdatedPayload(BaseModel):
    """Payload for task.updated event"""
    task_id: str
    updated_fields: Dict[str, Any]


class TaskCompletedPayload(BaseModel):
    """Payload for task.completed event"""
    task_id: str
    completion_timestamp: datetime
    recurrence_pattern: str
    original_task: Optional[Dict[str, Any]] = None


class TaskDeletedPayload(BaseModel):
    """Payload for task.deleted event"""
    task_id: str


class ReminderScheduledPayload(BaseModel):
    """Payload for reminder.scheduled event"""
    reminder_id: str
    task_id: str
    scheduled_time: datetime
    job_id: str


class ReminderTriggeredPayload(BaseModel):
    """Payload for reminder.triggered event"""
    reminder_id: str
    task_id: str
    task_title: str
    due_date: datetime
    reminder_message: str


class TaskEvent(BaseModel):
    """
    Base event model for all task lifecycle events

    All events follow standardized envelope format:
    - event_id: Unique identifier for idempotency
    - event_type: Type of event
    - user_id: Owner of the resource
    - timestamp: Event creation time (UTC)
    - payload: Event-specific data
    """
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: TaskCreatedPayload | TaskUpdatedPayload | TaskCompletedPayload | TaskDeletedPayload | ReminderScheduledPayload | ReminderTriggeredPayload

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ReminderEvent(BaseModel):
    """Event model for reminder triggers"""
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str = "reminder.triggered"
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: ReminderTriggeredPayload

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
