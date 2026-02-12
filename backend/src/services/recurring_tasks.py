"""
Recurring Task Service - Consumes task.completed events and generates next instances
"""
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp
from backend.src.models.events import TaskEvent, EventType, TaskCompletedPayload
from backend.src.events.idempotency import check_and_mark_processed
from backend.src.mcp.tools import add_task_impl
from backend.src.database import get_session
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Recurring Task Service")
dapr_app = DaprApp(app)


def calculate_next_due_date(current_due_date: datetime, pattern: str) -> datetime:
    """
    Calculate the next due date based on recurrence pattern

    Args:
        current_due_date: Current task due date
        pattern: Recurrence pattern (daily/weekly/monthly)

    Returns:
        datetime: Next due date (UTC)
    """
    if pattern == "daily":
        return current_due_date + timedelta(days=1)
    elif pattern == "weekly":
        return current_due_date + timedelta(weeks=1)
    elif pattern == "monthly":
        # Approximate month as 30 days
        return current_due_date + timedelta(days=30)
    else:
        raise ValueError(f"Invalid recurrence pattern: {pattern}")


@dapr_app.subscribe(pubsub_name="kafka-pubsub", topic="task-events")
async def handle_task_event(event_data: dict):
    """
    Handle task events from task-events Kafka topic

    This service consumes task.completed events and generates the next
    recurring task instance if recurrence_pattern is not "none".

    Args:
        event_data: Task event data from Kafka

    Returns:
        dict: Processing status
    """
    try:
        # Parse event
        event = TaskEvent(**event_data)

        # Only process task.completed events
        if event.event_type != EventType.TASK_COMPLETED:
            return {"status": "ignored", "reason": "not_a_completed_event"}

        logger.info(
            f"Received task.completed event {event.event_id} "
            f"for task {event.payload.task_id}"
        )

        # Check if task has recurrence
        if event.payload.recurrence_pattern == "none":
            logger.debug(
                f"Task {event.payload.task_id} has no recurrence, skipping"
            )
            return {"status": "ignored", "reason": "no_recurrence"}

        # Check idempotency
        already_processed = await check_and_mark_processed(event.event_id)

        if already_processed:
            logger.info(
                f"Event {event.event_id} already processed, skipping"
            )
            return {"status": "duplicate", "event_id": str(event.event_id)}

        # Generate next task instance
        await generate_next_instance(event)

        logger.info(
            f"Successfully generated next instance for event {event.event_id}"
        )

        return {"status": "success", "event_id": str(event.event_id)}

    except Exception as e:
        logger.error(f"Failed to handle task event: {str(e)}")
        return {"status": "error", "error": str(e)}


async def generate_next_instance(event: TaskEvent):
    """
    Generate the next recurring task instance

    Args:
        event: TaskEvent with task.completed payload

    Raises:
        Exception: If task creation fails
    """
    payload = event.payload
    original_task = payload.original_task

    if not original_task:
        logger.warning(
            f"No original_task data in event {event.event_id}, cannot generate next instance"
        )
        return

    # Parse original due date
    original_due_date_str = original_task.get("due_date")
    if not original_due_date_str:
        logger.warning(
            f"No due_date in original task for event {event.event_id}, cannot generate next instance"
        )
        return

    original_due_date = datetime.fromisoformat(original_due_date_str)

    # Calculate next due date
    next_due_date = calculate_next_due_date(
        original_due_date,
        payload.recurrence_pattern
    )

    # Skip if next due date is in the past (edge case: task completed very late)
    if next_due_date < datetime.utcnow():
        logger.warning(
            f"Next due date {next_due_date.isoformat()} is in the past, "
            f"calculating next valid future date"
        )
        # Keep adding intervals until we get a future date
        while next_due_date < datetime.utcnow():
            next_due_date = calculate_next_due_date(
                next_due_date,
                payload.recurrence_pattern
            )

    # Create next task instance
    async with get_session() as session:
        result = await add_task_impl(
            user_id=event.user_id,
            title=original_task["title"],
            description=original_task.get("description"),
            priority=original_task["priority"],
            tags=original_task.get("tags", []),
            due_date=next_due_date.isoformat(),
            recurrence_pattern=payload.recurrence_pattern,
            reminder_time=original_task.get("reminder_time"),
            session=session
        )

    logger.info(
        f"Generated next recurring task instance: {result.get('task_id')} "
        f"with due date {next_due_date.isoformat()}"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "recurring-task-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
