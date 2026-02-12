"""
Notification Service - Consumes reminder events and delivers notifications
"""
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp
from backend.src.models.events import ReminderEvent
from backend.src.events.idempotency import check_and_mark_processed
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service")
dapr_app = DaprApp(app)


@dapr_app.subscribe(pubsub_name="kafka-pubsub", topic="reminders")
async def handle_reminder_event(event_data: dict):
    """
    Handle reminder events from reminders Kafka topic

    This service consumes reminder.triggered events and delivers
    notifications to users. Implements idempotent event handling.

    Args:
        event_data: Reminder event data from Kafka

    Returns:
        dict: Processing status
    """
    try:
        # Parse event
        event = ReminderEvent(**event_data)

        logger.info(
            f"Received reminder event {event.event_id} "
            f"for task {event.payload.task_id}"
        )

        # Check idempotency
        already_processed = await check_and_mark_processed(event.event_id)

        if already_processed:
            logger.info(
                f"Reminder event {event.event_id} already processed, skipping"
            )
            return {"status": "duplicate", "event_id": str(event.event_id)}

        # Deliver notification
        await deliver_notification(event)

        logger.info(
            f"Successfully delivered reminder notification for event {event.event_id}"
        )

        return {"status": "success", "event_id": str(event.event_id)}

    except Exception as e:
        logger.error(f"Failed to handle reminder event: {str(e)}")
        return {"status": "error", "error": str(e)}


async def deliver_notification(event: ReminderEvent):
    """
    Deliver notification to user

    In a production system, this would:
    - Send in-app notification
    - Send email notification
    - Send push notification
    - Log to notification history

    For MVP, we log the notification.

    Args:
        event: ReminderEvent to deliver
    """
    notification = {
        "user_id": event.user_id,
        "task_id": event.payload.task_id,
        "task_title": event.payload.task_title,
        "message": event.payload.reminder_message,
        "due_date": event.payload.due_date.isoformat(),
        "timestamp": event.timestamp.isoformat()
    }

    # TODO: Implement actual notification delivery
    # - In-app notification via WebSocket
    # - Email via SendGrid/AWS SES
    # - Push notification via Firebase/OneSignal

    logger.info(
        f"NOTIFICATION DELIVERED: User {event.user_id} - "
        f"{event.payload.reminder_message}"
    )

    # Store notification in database for history (optional)
    # await store_notification_history(notification)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "notification-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
