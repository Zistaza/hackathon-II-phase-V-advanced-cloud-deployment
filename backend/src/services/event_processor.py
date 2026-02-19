"""Event processor service for Phase-V.

This module provides the HTTP API endpoints that Dapr calls
when events are received from the Pub/Sub system.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response

from backend.src.events.consumers import (
    EventConsumerMetrics,
    get_audit_consumer,
    get_recurring_task_consumer,
    get_task_event_consumer,
)
from backend.src.events.handlers import EventProcessingError

logger = logging.getLogger(__name__)

# API router for event endpoints
event_router = APIRouter(prefix="/events", tags=["events"])


@event_router.post("/task")
async def handle_task_event(request: Request) -> Response:
    """Handle task events from Dapr Pub/Sub.

    This endpoint is called by Dapr when a task event is received.

    Args:
        request: The FastAPI request containing the event.

    Returns:
        Response indicating success or failure.

    Raises:
        HTTPException: If event processing fails.
    """
    try:
        body = await request.json()
        event_type = body.get("metadata", {}).get("event_type", "unknown")

        logger.info(f"Received task event: {event_type}")

        consumer = get_task_event_consumer()

        with EventConsumerMetrics(event_type):
            await consumer.handle(body)

        return Response(status_code=200)

    except EventProcessingError as e:
        logger.error(f"Task event processing failed: {e}")
        # Return 500 to trigger Dapr retry
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing task event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@event_router.post("/recurrence")
async def handle_recurrence_event(request: Request) -> Response:
    """Handle recurrence events from Dapr Pub/Sub.

    This endpoint is called by Dapr when a recurrence event is received.

    Args:
        request: The FastAPI request containing the event.

    Returns:
        Response indicating success or failure.

    Raises:
        HTTPException: If event processing fails.
    """
    try:
        body = await request.json()
        event_type = body.get("metadata", {}).get("event_type", "unknown")

        logger.info(f"Received recurrence event: {event_type}")

        consumer = get_recurring_task_consumer()

        with EventConsumerMetrics(event_type):
            await consumer.handle(body)

        return Response(status_code=200)

    except EventProcessingError as e:
        logger.error(f"Recurrence event processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing recurrence event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@event_router.post("/reminder")
async def handle_reminder_event(request: Request) -> Response:
    """Handle reminder events from Dapr Pub/Sub.

    This endpoint is called by Dapr when a reminder event is received.

    Args:
        request: The FastAPI request containing the event.

    Returns:
        Response indicating success or failure.

    Raises:
        HTTPException: If event processing fails.
    """
    try:
        body = await request.json()
        event_type = body.get("metadata", {}).get("event_type", "unknown")

        logger.info(f"Received reminder event: {event_type}")

        # TODO: Implement reminder consumer
        # consumer = get_reminder_consumer()
        # await consumer.handle(body)

        return Response(status_code=200)

    except Exception as e:
        logger.error(f"Error processing reminder event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@event_router.post("/notification")
async def handle_notification_event(request: Request) -> Response:
    """Handle notification events from Dapr Pub/Sub.

    This endpoint is called by Dapr when a notification event is received.

    Args:
        request: The FastAPI request containing the event.

    Returns:
        Response indicating success or failure.

    Raises:
        HTTPException: If event processing fails.
    """
    try:
        body = await request.json()
        event_type = body.get("metadata", {}).get("event_type", "unknown")

        logger.info(f"Received notification event: {event_type}")

        # TODO: Implement notification consumer
        # consumer = get_notification_consumer()
        # await consumer.handle(body)

        return Response(status_code=200)

    except Exception as e:
        logger.error(f"Error processing notification event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Health check endpoint for event processor
@event_router.get("/health")
async def event_processor_health() -> dict[str, Any]:
    """Health check endpoint for the event processor.

    Returns:
        Health status dictionary.
    """
    return {
        "status": "healthy",
        "service": "event-processor",
    }
