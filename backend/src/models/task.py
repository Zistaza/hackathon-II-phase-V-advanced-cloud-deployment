from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import validator
import uuid


class TaskStatus(str, Enum):
    """Task completion status"""
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecurrencePattern(str, Enum):
    """Task recurrence patterns"""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TaskBase(SQLModel):
    """Base model for task with common fields"""
    title: str = Field(nullable=False, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.INCOMPLETE)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSONB))
    due_date: Optional[datetime] = Field(default=None)
    recurrence_pattern: RecurrencePattern = Field(default=RecurrencePattern.NONE)
    reminder_time: Optional[str] = Field(default=None, max_length=50)


class Task(TaskBase, table=True):
    """
    Task model for database storage with Phase-V advanced features

    Fields:
    - id: Unique task identifier (UUID)
    - title: Task title (required, max 200 chars)
    - description: Task description (optional, max 2000 chars)
    - status: Completion status (incomplete/complete)
    - priority: Priority level (low/medium/high/urgent)
    - tags: Array of tag strings (JSONB)
    - due_date: Task due date (optional, UTC)
    - recurrence_pattern: Recurrence pattern (none/daily/weekly/monthly)
    - reminder_time: Reminder time relative to due_date (e.g., "1h", "1d")
    - user_id: Reference to the user who owns this task
    - created_at: Task creation timestamp
    - updated_at: Last update timestamp
    - completed_at: Task completion timestamp (optional)
    """
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, alias="task_id")
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)


class TaskCreate(SQLModel):
    """Model for creating a new task with validation"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: List[str] = Field(default_factory=list, max_items=20)
    due_date: Optional[datetime] = None
    recurrence_pattern: RecurrencePattern = RecurrencePattern.NONE
    reminder_time: Optional[str] = Field(default=None, pattern=r'^\d+[hdw]$')

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
        return v


class TaskUpdate(SQLModel):
    """Model for updating task information"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    tags: Optional[List[str]] = Field(default=None, max_items=20)
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    reminder_time: Optional[str] = Field(default=None, pattern=r'^\d+[hdw]$')

    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        if v:
            for tag in v:
                if len(tag) > 50:
                    raise ValueError('Tag length must be <= 50 characters')
        return v


class TaskPublic(TaskBase):
    """Public model for task data (includes ID and timestamps)"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


# Backward compatibility alias
class TaskModel(Task):
    """Alias for backward compatibility"""
    pass
