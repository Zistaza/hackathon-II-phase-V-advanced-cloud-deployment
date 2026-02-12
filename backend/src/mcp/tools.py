"""
MCP Tool Implementations for Phase-V Advanced Features
Extended implementations for add_task, update_task, complete_task, delete_task, list_tasks
"""
from backend.src.models.task import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority
from backend.src.models.events import TaskEvent, EventType, TaskCreatedPayload, TaskUpdatedPayload, TaskCompletedPayload, TaskDeletedPayload
from backend.src.events.publisher import publish_task_event
from backend.src.services.reminder_scheduler import schedule_reminder, cancel_reminder
from backend.src.db.queries import build_combined_query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


async def add_task_impl(
    user_id: str,
    title: str,
    description: str = None,
    priority: str = "medium",
    tags: list = None,
    due_date: str = None,
    recurrence_pattern: str = "none",
    reminder_time: str = None,
    session: AsyncSession = None
) -> dict:
    """
    Create a new task with advanced features

    Args:
        user_id: User ID from JWT
        title: Task title
        description: Task description
        priority: Priority level (low/medium/high/urgent)
        tags: Array of tags
        due_date: Due date (ISO 8601)
        recurrence_pattern: Recurrence pattern (none/daily/weekly/monthly)
        reminder_time: Reminder time relative to due_date (e.g., "1h")
        session: Database session

    Returns:
        dict: Created task data with success status
    """
    try:
        # Parse due_date if provided
        due_date_obj = datetime.fromisoformat(due_date) if due_date else None

        # Create task
        task = Task(
            id=str(uuid4()),
            user_id=user_id,
            title=title,
            description=description,
            status=TaskStatus.INCOMPLETE,
            priority=TaskPriority(priority),
            tags=tags or [],
            due_date=due_date_obj,
            recurrence_pattern=recurrence_pattern,
            reminder_time=reminder_time,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save to database
        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Schedule reminder if due_date and reminder_time provided
        reminder_scheduled = False
        if due_date_obj and reminder_time:
            try:
                await schedule_reminder(
                    task_id=task.id,
                    user_id=user_id,
                    task_title=title,
                    due_date=due_date_obj,
                    reminder_time=reminder_time
                )
                reminder_scheduled = True
            except Exception as e:
                logger.error(f"Failed to schedule reminder for task {task.id}: {str(e)}")

        # Publish task.created event
        event = TaskEvent(
            event_id=uuid4(),
            event_type=EventType.TASK_CREATED,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            payload=TaskCreatedPayload(
                task_id=task.id,
                title=task.title,
                description=task.description,
                status=task.status.value,
                priority=task.priority.value,
                tags=task.tags,
                due_date=task.due_date,
                recurrence_pattern=task.recurrence_pattern.value,
                reminder_time=task.reminder_time
            )
        )
        await publish_task_event(event)

        logger.info(f"Created task {task.id} for user {user_id}")

        return {
            "success": True,
            "task_id": task.id,
            "message": f"Task '{title}' created successfully",
            "reminder_scheduled": reminder_scheduled
        }

    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}")
        await session.rollback()
        raise


async def update_task_impl(
    user_id: str,
    task_id: str,
    title: str = None,
    description: str = None,
    priority: str = None,
    tags: list = None,
    due_date: str = None,
    recurrence_pattern: str = None,
    reminder_time: str = None,
    session: AsyncSession = None
) -> dict:
    """
    Update an existing task

    Args:
        user_id: User ID from JWT
        task_id: Task ID to update
        title: New title
        description: New description
        priority: New priority
        tags: New tags
        due_date: New due date
        recurrence_pattern: New recurrence pattern
        reminder_time: New reminder time
        session: Database session

    Returns:
        dict: Update status
    """
    try:
        # Fetch task
        task = await session.get(Task, task_id)
        if not task or task.user_id != user_id:
            return {"success": False, "error": "Task not found or unauthorized"}

        # Track updated fields
        updated_fields = {}
        old_due_date = task.due_date
        old_reminder_time = task.reminder_time

        # Update fields
        if title is not None:
            task.title = title
            updated_fields["title"] = title
        if description is not None:
            task.description = description
            updated_fields["description"] = description
        if priority is not None:
            task.priority = TaskPriority(priority)
            updated_fields["priority"] = priority
        if tags is not None:
            task.tags = tags
            updated_fields["tags"] = tags
        if due_date is not None:
            task.due_date = datetime.fromisoformat(due_date)
            updated_fields["due_date"] = due_date
        if recurrence_pattern is not None:
            task.recurrence_pattern = recurrence_pattern
            updated_fields["recurrence_pattern"] = recurrence_pattern
        if reminder_time is not None:
            task.reminder_time = reminder_time
            updated_fields["reminder_time"] = reminder_time

        task.updated_at = datetime.utcnow()

        await session.commit()

        # Handle reminder rescheduling
        reminder_rescheduled = False
        if (due_date is not None or reminder_time is not None) and old_due_date:
            try:
                # Cancel old reminder
                old_job_id = f"reminder-{task_id}-{int(old_due_date.timestamp())}"
                await cancel_reminder(old_job_id)

                # Schedule new reminder if both due_date and reminder_time exist
                if task.due_date and task.reminder_time:
                    await schedule_reminder(
                        task_id=task_id,
                        user_id=user_id,
                        task_title=task.title,
                        due_date=task.due_date,
                        reminder_time=task.reminder_time
                    )
                    reminder_rescheduled = True
            except Exception as e:
                logger.error(f"Failed to reschedule reminder for task {task_id}: {str(e)}")

        # Publish task.updated event
        event = TaskEvent(
            event_id=uuid4(),
            event_type=EventType.TASK_UPDATED,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            payload=TaskUpdatedPayload(
                task_id=task_id,
                updated_fields=updated_fields
            )
        )
        await publish_task_event(event)

        logger.info(f"Updated task {task_id} for user {user_id}")

        return {
            "success": True,
            "task_id": task_id,
            "message": "Task updated successfully",
            "updated_fields": list(updated_fields.keys()),
            "reminder_rescheduled": reminder_rescheduled
        }

    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {str(e)}")
        await session.rollback()
        raise


async def complete_task_impl(
    user_id: str,
    task_id: str,
    session: AsyncSession = None
) -> dict:
    """
    Mark a task as complete and cancel pending reminders

    Args:
        user_id: User ID from JWT
        task_id: Task ID to complete
        session: Database session

    Returns:
        dict: Completion status
    """
    try:
        # Fetch task
        task = await session.get(Task, task_id)
        if not task or task.user_id != user_id:
            return {"success": False, "error": "Task not found or unauthorized"}

        # Mark as complete
        task.status = TaskStatus.COMPLETE
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        await session.commit()

        # Cancel pending reminder
        if task.due_date and task.reminder_time:
            try:
                job_id = f"reminder-{task_id}-{int(task.due_date.timestamp())}"
                await cancel_reminder(job_id)
            except Exception as e:
                logger.warning(f"Failed to cancel reminder for task {task_id}: {str(e)}")

        # Publish task.completed event (for recurring task generation)
        event = TaskEvent(
            event_id=uuid4(),
            event_type=EventType.TASK_COMPLETED,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            payload=TaskCompletedPayload(
                task_id=task_id,
                completion_timestamp=task.completed_at,
                recurrence_pattern=task.recurrence_pattern.value,
                original_task={
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "tags": task.tags,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                } if task.recurrence_pattern.value != "none" else None
            )
        )
        await publish_task_event(event)

        logger.info(f"Completed task {task_id} for user {user_id}")

        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task '{task.title}' marked as complete"
        }

    except Exception as e:
        logger.error(f"Failed to complete task {task_id}: {str(e)}")
        await session.rollback()
        raise


async def delete_task_impl(
    user_id: str,
    task_id: str,
    session: AsyncSession = None
) -> dict:
    """
    Delete a task and cancel pending reminders

    Args:
        user_id: User ID from JWT
        task_id: Task ID to delete
        session: Database session

    Returns:
        dict: Deletion status
    """
    try:
        # Fetch task
        task = await session.get(Task, task_id)
        if not task or task.user_id != user_id:
            return {"success": False, "error": "Task not found or unauthorized"}

        # Cancel pending reminder
        if task.due_date and task.reminder_time:
            try:
                job_id = f"reminder-{task_id}-{int(task.due_date.timestamp())}"
                await cancel_reminder(job_id)
            except Exception as e:
                logger.warning(f"Failed to cancel reminder for task {task_id}: {str(e)}")

        # Delete task
        await session.delete(task)
        await session.commit()

        # Publish task.deleted event
        event = TaskEvent(
            event_id=uuid4(),
            event_type=EventType.TASK_DELETED,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            payload=TaskDeletedPayload(task_id=task_id)
        )
        await publish_task_event(event)

        logger.info(f"Deleted task {task_id} for user {user_id}")

        return {
            "success": True,
            "task_id": task_id,
            "message": "Task deleted successfully"
        }

    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {str(e)}")
        await session.rollback()
        raise


async def list_tasks_impl(
    user_id: str,
    status: str = None,
    priority: str = None,
    tags: list = None,
    due_date_filter: str = None,
    search: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = None
) -> dict:
    """
    List tasks with advanced filtering, searching, and sorting

    Args:
        user_id: User ID from JWT
        status: Filter by status
        priority: Filter by priority
        tags: Filter by tags
        due_date_filter: Filter by due date range
        search: Search term
        sort_by: Sort field
        sort_order: Sort direction
        limit: Max results
        offset: Pagination offset
        session: Database session

    Returns:
        dict: List of tasks with total count
    """
    try:
        # Build query
        query = build_combined_query(
            user_id=user_id,
            status=TaskStatus(status) if status else None,
            priority=TaskPriority(priority) if priority else None,
            tags=tags,
            due_date_filter=due_date_filter,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )

        # Execute query
        result = await session.execute(query)
        tasks = result.scalars().all()

        # Get total count (for pagination)
        count_query = build_combined_query(
            user_id=user_id,
            status=TaskStatus(status) if status else None,
            priority=TaskPriority(priority) if priority else None,
            tags=tags,
            due_date_filter=due_date_filter,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=None,
            offset=0
        )
        count_result = await session.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Format tasks
        tasks_data = [
            {
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "tags": task.tags,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "recurrence_pattern": task.recurrence_pattern.value,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in tasks
        ]

        logger.info(f"Listed {len(tasks)} tasks for user {user_id}")

        return {
            "success": True,
            "tasks": tasks_data,
            "total_count": total_count,
            "message": f"Found {total_count} tasks"
        }

    except Exception as e:
        logger.error(f"Failed to list tasks for user {user_id}: {str(e)}")
        raise
