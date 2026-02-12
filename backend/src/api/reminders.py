"""
Reminder job handler endpoint for Dapr Jobs API callbacks
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from backend.src.models.events import ReminderEvent, ReminderTriggeredPayload
from backend.src.events.publisher import publish_reminder_event
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reminders", tags=["reminders"])


class ReminderJobData(BaseModel):
    """Data received from Dapr Jobs API when reminder triggers"""
    task_id: str
    user_id: str
    task_title: str
    due_date: str
    reminder_message: str
    scheduled_time: str


@router.post("/trigger")
async def handle_reminder_trigger(job_data: ReminderJobData):
    """
    Handle reminder trigger from Dapr Jobs API

    This endpoint is called by Dapr Jobs API when a scheduled reminder time arrives.
    It publishes a reminder.triggered event to the reminders Kafka topic.

    Args:
        job_data: Reminder job data from Dapr

    Returns:
        dict: Success response

    Raises:
        HTTPException: If event publishing fails
    """
    try:
        logger.info(
            f"Reminder triggered for task {job_data.task_id} "
            f"for user {job_data.user_id}"
        )

        # Create reminder event
        reminder_event = ReminderEvent(
            event_id=uuid4(),
            user_id=job_data.user_id,
            timestamp=datetime.utcnow(),
            payload=ReminderTriggeredPayload(
                reminder_id=str(uuid4()),
                task_id=job_data.task_id,
                task_title=job_data.task_title,
                due_date=datetime.fromisoformat(job_data.due_date),
                reminder_message=job_data.reminder_message
            )
        )

        # Publish to reminders topic
        await publish_reminder_event(reminder_event)

        logger.info(
            f"Published reminder event {reminder_event.event_id} "
            f"for task {job_data.task_id}"
        )

        return {
            "success": True,
            "message": "Reminder event published successfully",
            "event_id": str(reminder_event.event_id)
        }

    except Exception as e:
        logger.error(
            f"Failed to handle reminder trigger for task {job_data.task_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish reminder event: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for reminder service"""
    return {"status": "healthy", "service": "reminder-handler"}
