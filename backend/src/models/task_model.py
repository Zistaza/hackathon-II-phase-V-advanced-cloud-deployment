from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


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
    """
    Base model for task with common fields
    """
    title: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    priority: str = Field(default="medium")  # Phase V: Priority as string enum


class Task(TaskBase, table=True):
    """
    Task model for database storage with Phase V advanced features

    Fields:
    - id: Unique task identifier
    - title: Task title (required)
    - description: Task description (optional)
    - completed: Completion status (default: False)
    - priority: Priority level (low/medium/high/urgent)
    - tags: Array of tags (Phase V)
    - due_date: Due date timestamp (Phase V)
    - recurrence_pattern: Recurrence pattern (Phase V)
    - reminder_time: Reminder time relative to due_date (Phase V)
    - user_id: Reference to the user who owns this task
    - created_at: Task creation timestamp
    - updated_at: Last update timestamp
    """
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    priority: str = Field(default="medium")
    tags: Optional[List[str]] = Field(default=[], sa_column=Column(JSONB))  # Phase V
    due_date: Optional[datetime] = Field(default=None)  # Phase V
    recurrence_pattern: str = Field(default="none")  # Phase V
    reminder_time: Optional[str] = Field(default=None)  # Phase V
    search_vector: Optional[str] = Field(default=None, sa_column=Column(TSVECTOR))  # Phase V (managed by trigger)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    """
    Model for creating a new task with Phase V features
    """
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = "medium"
    tags: Optional[List[str]] = []  # Phase V
    due_date: Optional[datetime] = None  # Phase V
    recurrence_pattern: str = "none"  # Phase V
    reminder_time: Optional[str] = None  # Phase V


class TaskUpdate(SQLModel):
    """
    Model for updating task information with Phase V features
    """
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None  # Phase V
    due_date: Optional[datetime] = None  # Phase V
    recurrence_pattern: Optional[str] = None  # Phase V
    reminder_time: Optional[str] = None  # Phase V


class TaskResponse(SQLModel):
    """
    Response model for API endpoints - maps 'id' to 'task_id' for frontend compatibility
    """
    task_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    completed: bool
    priority: str
    tags: List[str] = []
    due_date: Optional[datetime] = None
    recurrence_pattern: str = "none"
    reminder_time: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_task(cls, task: "Task") -> "TaskResponse":
        """Convert Task model to TaskResponse"""
        # Handle priority conversion from int to string if needed
        priority = task.priority
        if isinstance(priority, int):
            # Map integer priorities to string values
            priority_map = {
                1: "low",
                2: "medium",
                3: "high",
                4: "urgent"
            }
            priority = priority_map.get(priority, "medium")
        elif not isinstance(priority, str):
            priority = "medium"

        return cls(
            task_id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            priority=priority,
            tags=task.tags or [],
            due_date=task.due_date,
            recurrence_pattern=task.recurrence_pattern,
            reminder_time=task.reminder_time,
            created_at=task.created_at,
            updated_at=task.updated_at
        )