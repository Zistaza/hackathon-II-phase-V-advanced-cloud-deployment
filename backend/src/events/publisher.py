"""
Event publisher utility for publishing task events to Kafka via Dapr Pub/Sub
"""
from dapr.clients import DaprClient
from backend.src.models.events import TaskEvent, ReminderEvent
import logging

logger = logging.getLogger(__name__)


async def publish_task_event(event: TaskEvent, topics: list[str] = None) -> bool:
    """
    Publish a task event to Kafka topics via Dapr Pub/Sub

    Args:
        event: TaskEvent to publish
        topics: List of topic names (default: ["task-events", "task-updates"])

    Returns:
        bool: True if published successfully, False otherwise

    Raises:
        Exception: If Dapr client fails to publish
    """
    if topics is None:
        topics = ["task-events", "task-updates"]

    try:
        async with DaprClient() as client:
            event_data = event.json()

            for topic in topics:
                await client.publish_event(
                    pubsub_name="kafka-pubsub",
                    topic_name=topic,
                    data=event_data,
                    data_content_type="application/json"
                )

                logger.info(
                    f"Published event {event.event_id} of type {event.event_type} "
                    f"to topic {topic} for user {event.user_id}"
                )

            return True

    except Exception as e:
        logger.error(
            f"Failed to publish event {event.event_id} of type {event.event_type}: {str(e)}"
        )
        raise


async def publish_reminder_event(event: ReminderEvent) -> bool:
    """
    Publish a reminder event to reminders topic via Dapr Pub/Sub

    Args:
        event: ReminderEvent to publish

    Returns:
        bool: True if published successfully, False otherwise

    Raises:
        Exception: If Dapr client fails to publish
    """
    try:
        async with DaprClient() as client:
            event_data = event.json()

            await client.publish_event(
                pubsub_name="kafka-pubsub",
                topic_name="reminders",
                data=event_data,
                data_content_type="application/json"
            )

            logger.info(
                f"Published reminder event {event.event_id} "
                f"for task {event.payload.task_id} to user {event.user_id}"
            )

            return True

    except Exception as e:
        logger.error(
            f"Failed to publish reminder event {event.event_id}: {str(e)}"
        )
        raise


async def publish_to_topic(
    pubsub_name: str,
    topic_name: str,
    data: dict,
    content_type: str = "application/json"
) -> bool:
    """
    Generic function to publish data to any Dapr Pub/Sub topic

    Args:
        pubsub_name: Name of the Dapr Pub/Sub component
        topic_name: Name of the topic
        data: Data to publish (will be JSON serialized)
        content_type: Content type of the data

    Returns:
        bool: True if published successfully, False otherwise
    """
    try:
        async with DaprClient() as client:
            await client.publish_event(
                pubsub_name=pubsub_name,
                topic_name=topic_name,
                data=data,
                data_content_type=content_type
            )

            logger.info(f"Published data to topic {topic_name} via {pubsub_name}")
            return True

    except Exception as e:
        logger.error(f"Failed to publish to topic {topic_name}: {str(e)}")
        raise
