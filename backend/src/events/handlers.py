"""Event handlers with idempotency support for Phase-V.

This module provides base classes and utilities for handling events
with idempotency guarantees, retry logic, and dead-letter queue support.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from backend.src.dapr.state import DaprStateStore

logger = logging.getLogger(__name__)


class IdempotencyError(Exception):
    """Raised when an idempotency check fails."""

    pass


class EventProcessingError(Exception):
    """Raised when event processing fails."""

    pass


class IdempotentEventHandler(ABC):
    """Base class for idempotent event handlers.

    This class provides:
    - Idempotency checking using Dapr State Store
    - Retry logic with exponential backoff
    - Dead-letter queue routing for failed events
    """

    # State store key prefix for idempotency tracking
    IDEMPOTENCY_KEY_PREFIX = "idempotency:"
    # Default TTL for idempotency keys (24 hours)
    DEFAULT_IDEMPOTENCY_TTL = timedelta(hours=24)
    # Maximum retry attempts
    MAX_RETRIES = 3
    # Initial retry delay in seconds
    INITIAL_RETRY_DELAY = 1.0
    # Retry delay multiplier
    RETRY_DELAY_MULTIPLIER = 2.0

    def __init__(self, state_store: Optional[DaprStateStore] = None):
        """Initialize the event handler.

        Args:
            state_store: Dapr state store for idempotency tracking.
        """
        self.state_store = state_store

    async def handle(self, event: dict[str, Any]) -> bool:
        """Handle an event with idempotency checking.

        Args:
            event: The event data to process.

        Returns:
            True if the event was processed successfully.

        Raises:
            IdempotencyError: If the event was already processed.
            EventProcessingError: If event processing fails after all retries.
        """
        event_id = self._get_event_id(event)
        event_type = self._get_event_type(event)

        # Check idempotency
        if await self._is_duplicate(event_id):
            logger.info(f"Duplicate event detected: {event_id}")
            return True  # Return success for duplicates (idempotent)

        # Process with retry
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                await self._process_event(event)
                await self._mark_processed(event_id, event_type)
                logger.info(f"Event processed successfully: {event_id}")
                return True
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Event processing failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {event_id} - {e}"
                )
                if attempt < self.MAX_RETRIES - 1:
                    delay = self._calculate_retry_delay(attempt)
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    await self._wait(delay)

        # All retries exhausted - send to DLQ
        await self._send_to_dlq(event, str(last_error))
        raise EventProcessingError(
            f"Event processing failed after {self.MAX_RETRIES} attempts: {last_error}"
        )

    async def _is_duplicate(self, event_id: str) -> bool:
        """Check if an event has already been processed.

        Args:
            event_id: The unique event identifier.

        Returns:
            True if the event was already processed.
        """
        if not self.state_store:
            return False

        key = f"{self.IDEMPOTENCY_KEY_PREFIX}{event_id}"
        try:
            result = await self.state_store.get(key)
            return result is not None
        except Exception as e:
            logger.error(f"Idempotency check failed: {e}")
            return False

    async def _mark_processed(self, event_id: str, event_type: str) -> None:
        """Mark an event as processed.

        Args:
            event_id: The unique event identifier.
            event_type: The type of event.
        """
        if not self.state_store:
            return

        key = f"{self.IDEMPOTENCY_KEY_PREFIX}{event_id}"
        value = {
            "event_id": event_id,
            "event_type": event_type,
            "processed_at": datetime.utcnow().isoformat(),
            "handler": self.__class__.__name__,
        }
        try:
            await self.state_store.save(key, value, ttl_seconds=int(self.DEFAULT_IDEMPOTENCY_TTL.total_seconds()))
        except Exception as e:
            logger.error(f"Failed to mark event as processed: {e}")

    async def _send_to_dlq(self, event: dict[str, Any], error: str) -> None:
        """Send a failed event to the dead-letter queue.

        Args:
            event: The event data.
            error: The error message.
        """
        logger.error(f"Sending event to DLQ: {self._get_event_id(event)} - Error: {error}")
        # TODO: Implement DLQ routing via Dapr Pub/Sub
        # await self.state_store.save(f"dlq:{event_id}", {...})

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff.

        Args:
            attempt: The current attempt number (0-indexed).

        Returns:
            Delay in seconds.
        """
        return self.INITIAL_RETRY_DELAY * (self.RETRY_DELAY_MULTIPLIER ** attempt)

    async def _wait(self, seconds: float) -> None:
        """Wait for the specified number of seconds.

        Args:
            seconds: Number of seconds to wait.
        """
        import asyncio
        await asyncio.sleep(seconds)

    @abstractmethod
    async def _process_event(self, event: dict[str, Any]) -> None:
        """Process the event. Must be implemented by subclasses.

        Args:
            event: The event data to process.

        Raises:
            Exception: If processing fails.
        """
        pass

    @abstractmethod
    def _get_event_id(self, event: dict[str, Any]) -> str:
        """Extract the event ID from event data.

        Args:
            event: The event data.

        Returns:
            The unique event identifier.
        """
        pass

    @abstractmethod
    def _get_event_type(self, event: dict[str, Any]) -> str:
        """Extract the event type from event data.

        Args:
            event: The event data.

        Returns:
            The event type.
        """
        pass


class TaskEventHandler(IdempotentEventHandler):
    """Handler for task-related events."""

    async def _process_event(self, event: dict[str, Any]) -> None:
        """Process a task event.

        Args:
            event: The task event data.
        """
        # TODO: Implement task event processing logic
        logger.info(f"Processing task event: {event.get('metadata', {}).get('event_type')}")

    def _get_event_id(self, event: dict[str, Any]) -> str:
        """Get event ID from task event."""
        return event.get("metadata", {}).get("event_id", "")

    def _get_event_type(self, event: dict[str, Any]) -> str:
        """Get event type from task event."""
        return event.get("metadata", {}).get("event_type", "")


class ReminderEventHandler(IdempotentEventHandler):
    """Handler for reminder-related events."""

    async def _process_event(self, event: dict[str, Any]) -> None:
        """Process a reminder event.

        Args:
            event: The reminder event data.
        """
        # TODO: Implement reminder event processing logic
        logger.info(f"Processing reminder event: {event.get('metadata', {}).get('event_type')}")

    def _get_event_id(self, event: dict[str, Any]) -> str:
        """Get event ID from reminder event."""
        return event.get("metadata", {}).get("event_id", "")

    def _get_event_type(self, event: dict[str, Any]) -> str:
        """Get event type from reminder event."""
        return event.get("metadata", {}).get("event_type", "")


class RecurrenceEventHandler(IdempotentEventHandler):
    """Handler for recurrence-related events."""

    async def _process_event(self, event: dict[str, Any]) -> None:
        """Process a recurrence event.

        Args:
            event: The recurrence event data.
        """
        # TODO: Implement recurrence event processing logic
        logger.info(f"Processing recurrence event: {event.get('metadata', {}).get('event_type')}")

    def _get_event_id(self, event: dict[str, Any]) -> str:
        """Get event ID from recurrence event."""
        return event.get("metadata", {}).get("event_id", "")

    def _get_event_type(self, event: dict[str, Any]) -> str:
        """Get event type from recurrence event."""
        return event.get("metadata", {}).get("event_type", "")
