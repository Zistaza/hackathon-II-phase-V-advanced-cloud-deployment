"""Event publishers for Phase-V task events.

This module provides functions for publishing task-related events
to the event bus using Dapr Pub/Sub.
"""

import logging
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from prometheus_client import Counter, Histogram

from backend.src.dapr.pubsub import DaprPubSub, Topics
from backend.src.events.schemas import (
    BaseEvent,
    EventMetadata,
    TaskCompletedEventData,
    TaskCompletedEvent,
    TaskCreatedEventData,
    TaskCreatedEvent,
    TaskDeletedEventData,
    TaskDeletedEvent,
    TaskUpdatedEventData,
    TaskUpdatedEvent,
)

logger = logging.getLogger(__name__)

# Prometheus metrics
EVENT_PUBLISH_COUNTER = Counter(
    "task_events_published_total",
    "Total number of task events published",
    ["event_type"],
)

EVENT_PUBLISH_LATENCY = Histogram(
    "task_event_publish_latency_seconds",
    "Latency of task event publishing",
    ["event_type"],
)

EVENT_PUBLISH_ERRORS = Counter(
    "task_event_publish_errors_total",
    "Total number of task event publishing errors",
    ["event_type"],
)


class TaskEventPublisher:
    """Publisher for task-related events."""

    def __init__(self, pubsub: Optional[DaprPubSub] = None):
        """Initialize the task event publisher.

        Args:
            pubsub: Dapr Pub/Sub client. Creates a new one if not provided.
        """
        self.pubsub = pubsub or DaprPubSub()

    async def publish_task_created(
        self,
        task_id: UUID,
        title: str,
        created_by: UUID,
        description: Optional[str] = None,
        status: str = "pending",
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        correlation_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None,
    ) -> bool:
        """Publish a task.created event.

        Args:
            task_id: The ID of the created task.
            title: The task title.
            created_by: The ID of the user who created the task.
            description: Optional task description.
            status: Task status.
            priority: Task priority.
            due_date: Optional due date.
            tags: Optional list of tags.
            metadata: Optional additional metadata.
            correlation_id: Optional correlation ID for tracing.
            user_id: Optional user ID for the event.
            tenant_id: Optional tenant ID for multi-tenancy.

        Returns:
            True if the event was published successfully.
        """
        event = TaskCreatedEvent(
            metadata=EventMetadata(
                event_type="task.created",
                correlation_id=correlation_id,
                user_id=user_id,
                tenant_id=tenant_id,
            ),
            data=TaskCreatedEventData(
                task_id=task_id,
                title=title,
                description=description,
                status=status,
                priority=priority,
                due_date=due_date,
                created_by=created_by,
                tags=tags or [],
                metadata=metadata or {},
            ),
        )
        return await self._publish_event(event, Topics.TASK_EVENTS)

    async def publish_task_updated(
        self,
        task_id: UUID,
        updated_fields: dict[str, Any],
        updated_by: UUID,
        correlation_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None,
    ) -> bool:
        """Publish a task.updated event.

        Args:
            task_id: The ID of the updated task.
            updated_fields: Dictionary of fields that were updated.
            updated_by: The ID of the user who updated the task.
            correlation_id: Optional correlation ID for tracing.
            user_id: Optional user ID for the event.
            tenant_id: Optional tenant ID for multi-tenancy.

        Returns:
            True if the event was published successfully.
        """
        event = TaskUpdatedEvent(
            metadata=EventMetadata(
                event_type="task.updated",
                correlation_id=correlation_id,
                user_id=user_id,
                tenant_id=tenant_id,
            ),
            data=TaskUpdatedEventData(
                task_id=task_id,
                updated_fields=updated_fields,
                updated_by=updated_by,
            ),
        )
        return await self._publish_event(event, Topics.TASK_EVENTS)

    async def publish_task_completed(
        self,
        task_id: UUID,
        completed_by: UUID,
        completion_notes: Optional[str] = None,
        correlation_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None,
    ) -> bool:
        """Publish a task.completed event.

        Args:
            task_id: The ID of the completed task.
            completed_by: The ID of the user who completed the task.
            completion_notes: Optional notes about the completion.
            correlation_id: Optional correlation ID for tracing.
            user_id: Optional user ID for the event.
            tenant_id: Optional tenant ID for multi-tenancy.

        Returns:
            True if the event was published successfully.
        """
        event = TaskCompletedEvent(
            metadata=EventMetadata(
                event_type="task.completed",
                correlation_id=correlation_id,
                user_id=user_id,
                tenant_id=tenant_id,
            ),
            data=TaskCompletedEventData(
                task_id=task_id,
                completed_by=completed_by,
                completion_notes=completion_notes,
            ),
        )
        return await self._publish_event(event, Topics.TASK_EVENTS)

    async def publish_task_deleted(
        self,
        task_id: UUID,
        deleted_by: UUID,
        reason: Optional[str] = None,
        correlation_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None,
    ) -> bool:
        """Publish a task.deleted event.

        Args:
            task_id: The ID of the deleted task.
            deleted_by: The ID of the user who deleted the task.
            reason: Optional reason for deletion.
            correlation_id: Optional correlation ID for tracing.
            user_id: Optional user ID for the event.
            tenant_id: Optional tenant ID for multi-tenancy.

        Returns:
            True if the event was published successfully.
        """
        event = TaskDeletedEvent(
            metadata=EventMetadata(
                event_type="task.deleted",
                correlation_id=correlation_id,
                user_id=user_id,
                tenant_id=tenant_id,
            ),
            data=TaskDeletedEventData(
                task_id=task_id,
                deleted_by=deleted_by,
                reason=reason,
            ),
        )
        return await self._publish_event(event, Topics.TASK_EVENTS)

    async def _publish_event(self, event: BaseEvent, topic: str) -> bool:
        """Publish an event to the specified topic.

        Args:
            event: The event to publish.
            topic: The topic to publish to.

        Returns:
            True if the event was published successfully.
        """
        event_type = event.metadata.event_type

        with EVENT_PUBLISH_LATENCY.labels(event_type=event_type).time():
            try:
                success = await self.pubsub.publish(
                    topic=topic,
                    data=event.model_dump(mode="json"),
                    metadata={"event_id": str(event.metadata.event_id)},
                )

                if success:
                    EVENT_PUBLISH_COUNTER.labels(event_type=event_type).inc()
                    logger.debug(f"Published event {event.metadata.event_id} to {topic}")

                return success

            except Exception as e:
                EVENT_PUBLISH_ERRORS.labels(event_type=event_type).inc()
                logger.error(f"Failed to publish event {event.metadata.event_id}: {e}")
                raise

    async def close(self) -> None:
        """Close the publisher."""
        await self.pubsub.close()


# Global publisher instance
_task_event_publisher: Optional[TaskEventPublisher] = None


def get_task_event_publisher() -> TaskEventPublisher:
    """Get the global task event publisher instance.

    Returns:
        TaskEventPublisher instance.
    """
    global _task_event_publisher
    if _task_event_publisher is None:
        _task_event_publisher = TaskEventPublisher()
    return _task_event_publisher


async def close_task_event_publisher() -> None:
    """Close the global task event publisher."""
    global _task_event_publisher
    if _task_event_publisher:
        await _task_event_publisher.close()
        _task_event_publisher = None
