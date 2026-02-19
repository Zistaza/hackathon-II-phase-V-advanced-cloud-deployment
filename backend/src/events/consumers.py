"""Event consumers for Phase-V.

This module provides consumer services for processing events
from the event bus, including recurring task processing and audit logging.
"""

import logging
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from prometheus_client import Counter, Gauge, Histogram

from backend.src.dapr.pubsub import DaprPubSub, Topics
from backend.src.dapr.state import DaprStateStore
from backend.src.events.handlers import (
    IdempotentEventHandler,
    RecurrenceEventHandler,
    TaskEventHandler,
)

logger = logging.getLogger(__name__)

# Prometheus metrics
EVENT_CONSUME_COUNTER = Counter(
    "task_events_consumed_total",
    "Total number of task events consumed",
    ["event_type", "status"],  # status: success, failure, duplicate
)

EVENT_CONSUME_LATENCY = Histogram(
    "task_event_consume_latency_seconds",
    "Latency of task event consumption",
    ["event_type"],
)

EVENT_CONSUME_ERRORS = Counter(
    "task_event_consume_errors_total",
    "Total number of task event consumption errors",
    ["event_type"],
)

ACTIVE_EVENTS_GAUGE = Gauge(
    "task_events_processing_active",
    "Number of events currently being processed",
    ["event_type"],
)


class TaskEventConsumer(TaskEventHandler):
    """Consumer for task-related events.

    Processes task events and triggers appropriate business logic.
    """

    def __init__(
        self,
        state_store: Optional[DaprStateStore] = None,
        pubsub: Optional[DaprPubSub] = None,
    ):
        """Initialize the task event consumer.

        Args:
            state_store: Dapr state store for idempotency tracking.
            pubsub: Dapr Pub/Sub client for publishing follow-up events.
        """
        super().__init__(state_store)
        self.pubsub = pubsub

    async def _process_event(self, event: dict[str, Any]) -> None:
        """Process a task event.

        Args:
            event: The task event data.
        """
        event_type = event.get("metadata", {}).get("event_type", "")
        event_id = event.get("metadata", {}).get("event_id", "")

        logger.info(f"Processing task event {event_type}: {event_id}")

        # Route to specific handler based on event type
        if event_type == "task.created":
            await self._handle_task_created(event)
        elif event_type == "task.updated":
            await self._handle_task_updated(event)
        elif event_type == "task.completed":
            await self._handle_task_completed(event)
        elif event_type == "task.deleted":
            await self._handle_task_deleted(event)
        else:
            logger.warning(f"Unknown task event type: {event_type}")

    async def _handle_task_created(self, event: dict[str, Any]) -> None:
        """Handle task.created event.

        Args:
            event: The event data.
        """
        data = event.get("data", {})
        task_id = data.get("task_id")
        logger.info(f"Task created: {task_id}")
        # TODO: Add business logic for task creation
        # e.g., send welcome notification, update analytics, etc.

    async def _handle_task_updated(self, event: dict[str, Any]) -> None:
        """Handle task.updated event.

        Args:
            event: The event data.
        """
        data = event.get("data", {})
        task_id = data.get("task_id")
        updated_fields = data.get("updated_fields", {})
        logger.info(f"Task updated: {task_id}, fields: {list(updated_fields.keys())}")
        # TODO: Add business logic for task updates
        # e.g., notify collaborators, update search index, etc.

    async def _handle_task_completed(self, event: dict[str, Any]) -> None:
        """Handle task.completed event.

        Args:
            event: The event data.
        """
        data = event.get("data", {})
        task_id = data.get("task_id")
        logger.info(f"Task completed: {task_id}")
        # TODO: Add business logic for task completion
        # e.g., send completion notification, update statistics, etc.

    async def _handle_task_deleted(self, event: dict[str, Any]) -> None:
        """Handle task.deleted event.

        Args:
            event: The event data.
        """
        data = event.get("data", {})
        task_id = data.get("task_id")
        logger.info(f"Task deleted: {task_id}")
        # TODO: Add business logic for task deletion
        # e.g., clean up related data, notify collaborators, etc.

    def _get_event_id(self, event: dict[str, Any]) -> str:
        """Get event ID from task event."""
        return event.get("metadata", {}).get("event_id", "")

    def _get_event_type(self, event: dict[str, Any]) -> str:
        """Get event type from task event."""
        return event.get("metadata", {}).get("event_type", "")


class RecurringTaskConsumer(RecurrenceEventHandler):
    """Consumer for recurring task events.

    Handles creation and triggering of recurring task instances.
    """

    def __init__(
        self,
        state_store: Optional[DaprStateStore] = None,
        pubsub: Optional[DaprPubSub] = None,
    ):
        """Initialize the recurring task consumer.

        Args:
            state_store: Dapr state store for idempotency tracking.
            pubsub: Dapr Pub/Sub client for publishing follow-up events.
        """
        super().__init__(state_store)
        self.pubsub = pubsub

    async def _process_event(self, event: dict[str, Any]) -> None:
        """Process a recurrence event.

        Args:
            event: The recurrence event data.
        """
        event_type = event.get("metadata", {}).get("event_type", "")
        event_id = event.get("metadata", {}).get("event_id", "")

        logger.info(f"Processing recurrence event {event_type}: {event_id}")

        if event_type == "task.recurrence.created":
            await self._handle_recurrence_created(event)
        elif event_type == "task.recurrence.triggered":
            await self._handle_recurrence_triggered(event)
        elif event_type == "task.recurrence.updated":
            await self._handle_recurrence_updated(event)
        elif event_type == "task.recurrence.deleted":
            await self._handle_recurrence_deleted(event)
        else:
            logger.warning(f"Unknown recurrence event type: {event_type}")

    async def _handle_recurrence_created(self, event: dict[str, Any]) -> None:
        """Handle task.recurrence.created event.

        Creates the initial recurring task instance and schedules future instances.

        Args:
            event: The event data.
        """
        data = event.get("data", {})
        recurrence_id = data.get("recurrence_id")
        task_id = data.get("task_id")
        pattern = data.get("pattern")

        logger.info(f"Recurring task created: {recurrence_id}, pattern: {pattern}")

        # Store recurrence configuration
        if self.state_store:
            await self.state_store.save(
                f"recurrence:{recurrence_id}",
                {
                    "recurrence_id": recurrence_id,
                    "task_id": task_id,
                    "pattern": pattern,
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat(),
                },
            )

    async def _handle_recurrence_triggered(self, event: dict[str, Any]) -> None:
        """Handle task.recurrence.triggered event.

        Creates a new task instance from the recurring task configuration.

        Args:
            event: The event data.
        """
        data = event.get("data", {})
        recurrence_id = data.get("recurrence_id")
        new_task_id = data.get("new_task_id")
        occurrence_number = data.get("occurrence_number", 1)

        logger.info(
            f"Recurring task triggered: {recurrence_id}, occurrence: {occurrence_number}, new task: {new_task_id}"
        )

        # Update occurrence tracking
        if self.state_store:
            recurrence_data = await self.state_store.get(f"recurrence:{recurrence_id}")
            if recurrence_data:
                recurrence_data["last_triggered_at"] = datetime.utcnow().isoformat()
                recurrence_data["occurrence_count"] = occurrence_number
                await self.state_store.save(f"recurrence:{recurrence_id}", recurrence_data)

    async def _handle_recurrence_updated(self, event: dict[str, Any]) -> None:
        """Handle task.recurrence.updated event.

        Args:
            event: The event data.
        """
        data = event.get("data", {})
        recurrence_id = data.get("recurrence_id")
        updated_fields = data.get("updated_fields", {})

        logger.info(f"Recurring task updated: {recurrence_id}, fields: {list(updated_fields.keys())}")

        # Update stored recurrence configuration
        if self.state_store:
            recurrence_data = await self.state_store.get(f"recurrence:{recurrence_id}")
            if recurrence_data:
                recurrence_data.update(updated_fields)
                recurrence_data["updated_at"] = datetime.utcnow().isoformat()
                await self.state_store.save(f"recurrence:{recurrence_id}", recurrence_data)

    async def _handle_recurrence_deleted(self, event: dict[str, Any]) -> None:
        """Handle task.recurrence.deleted event.

        Args:
            event: The event data.
        """
        data = event.get("data", {})
        recurrence_id = data.get("recurrence_id")
        delete_future_instances = data.get("delete_future_instances", True)

        logger.info(
            f"Recurring task deleted: {recurrence_id}, delete future: {delete_future_instances}"
        )

        # Remove recurrence configuration
        if self.state_store:
            await self.state_store.delete(f"recurrence:{recurrence_id}")

    def _get_event_id(self, event: dict[str, Any]) -> str:
        """Get event ID from recurrence event."""
        return event.get("metadata", {}).get("event_id", "")

    def _get_event_type(self, event: dict[str, Any]) -> str:
        """Get event type from recurrence event."""
        return event.get("metadata", {}).get("event_type", "")


class AuditConsumer(TaskEventHandler):
    """Consumer for audit logging of task events.

    Records all task events for audit and compliance purposes.
    """

    AUDIT_KEY_PREFIX = "audit:task:"

    def __init__(self, state_store: Optional[DaprStateStore] = None):
        """Initialize the audit consumer.

        Args:
            state_store: Dapr state store for audit log storage.
        """
        super().__init__(state_store)

    async def _process_event(self, event: dict[str, Any]) -> None:
        """Process a task event for audit logging.

        Args:
            event: The task event data.
        """
        if not self.state_store:
            logger.warning("No state store configured for audit logging")
            return

        event_id = event.get("metadata", {}).get("event_id", "")
        event_type = event.get("metadata", {}).get("event_type", "")
        timestamp = event.get("metadata", {}).get("timestamp", datetime.utcnow().isoformat())

        # Store audit log entry
        audit_key = f"{self.AUDIT_KEY_PREFIX}{event_id}"
        audit_entry = {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": timestamp,
            "data": event.get("data", {}),
            "metadata": event.get("metadata", {}),
        }

        await self.state_store.save(audit_key, audit_entry)
        logger.debug(f"Audit log entry created: {audit_key}")

    def _get_event_id(self, event: dict[str, Any]) -> str:
        """Get event ID from task event."""
        return event.get("metadata", {}).get("event_id", "")

    def _get_event_type(self, event: dict[str, Any]) -> str:
        """Get event type from task event."""
        return event.get("metadata", {}).get("event_type", "")


class EventConsumerMetrics:
    """Context manager for tracking event consumption metrics."""

    def __init__(self, event_type: str):
        """Initialize the metrics context.

        Args:
            event_type: The type of event being consumed.
        """
        self.event_type = event_type
        self.timer = None

    def __enter__(self) -> "EventConsumerMetrics":
        """Enter the metrics context."""
        ACTIVE_EVENTS_GAUGE.labels(event_type=self.event_type).inc()
        self.timer = EVENT_CONSUME_LATENCY.labels(event_type=self.event_type).time()
        self.timer.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the metrics context."""
        ACTIVE_EVENTS_GAUGE.labels(event_type=self.event_type).dec()
        self.timer.__exit__(exc_type, exc_val, exc_tb)

        if exc_type is None:
            EVENT_CONSUME_COUNTER.labels(event_type=self.event_type, status="success").inc()
        else:
            EVENT_CONSUME_COUNTER.labels(event_type=self.event_type, status="failure").inc()
            EVENT_CONSUME_ERRORS.labels(event_type=self.event_type).inc()


# Global consumer instances
_task_event_consumer: Optional[TaskEventConsumer] = None
_recurring_task_consumer: Optional[RecurringTaskConsumer] = None
_audit_consumer: Optional[AuditConsumer] = None


def get_task_event_consumer() -> TaskEventConsumer:
    """Get the global task event consumer instance.

    Returns:
        TaskEventConsumer instance.
    """
    global _task_event_consumer
    if _task_event_consumer is None:
        _task_event_consumer = TaskEventConsumer()
    return _task_event_consumer


def get_recurring_task_consumer() -> RecurringTaskConsumer:
    """Get the global recurring task consumer instance.

    Returns:
        RecurringTaskConsumer instance.
    """
    global _recurring_task_consumer
    if _recurring_task_consumer is None:
        _recurring_task_consumer = RecurringTaskConsumer()
    return _recurring_task_consumer


def get_audit_consumer() -> AuditConsumer:
    """Get the global audit consumer instance.

    Returns:
        AuditConsumer instance.
    """
    global _audit_consumer
    if _audit_consumer is None:
        _audit_consumer = AuditConsumer()
    return _audit_consumer
