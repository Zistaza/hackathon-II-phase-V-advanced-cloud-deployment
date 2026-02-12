"""
Base event consumer class with idempotency handling
"""
from abc import ABC, abstractmethod
from backend.src.models.events import TaskEvent
from backend.src.events.idempotency import check_and_mark_processed
import logging

logger = logging.getLogger(__name__)


class BaseEventConsumer(ABC):
    """
    Abstract base class for event consumers with built-in idempotency

    All event consumers should inherit from this class and implement
    the process_event method. Idempotency is handled automatically
    using event_id deduplication.
    """

    def __init__(self, state_store: str = "statestore"):
        """
        Initialize the event consumer

        Args:
            state_store: Name of the Dapr State Store for idempotency tracking
        """
        self.state_store = state_store

    async def handle_event(self, event: TaskEvent) -> bool:
        """
        Handle an event with automatic idempotency checking

        This method checks if the event has been processed before.
        If not, it calls process_event and marks the event as processed.

        Args:
            event: TaskEvent to handle

        Returns:
            bool: True if event was processed, False if it was a duplicate

        Raises:
            Exception: If event processing fails
        """
        try:
            # Check if event already processed
            already_processed = await check_and_mark_processed(
                event.event_id,
                self.state_store
            )

            if already_processed:
                logger.info(
                    f"Event {event.event_id} of type {event.event_type} "
                    f"already processed, skipping"
                )
                return False

            # Process the event
            logger.info(
                f"Processing event {event.event_id} of type {event.event_type} "
                f"for user {event.user_id}"
            )

            await self.process_event(event)

            logger.info(
                f"Successfully processed event {event.event_id} "
                f"of type {event.event_type}"
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to handle event {event.event_id} "
                f"of type {event.event_type}: {str(e)}"
            )
            raise

    @abstractmethod
    async def process_event(self, event: TaskEvent) -> None:
        """
        Process the event (must be implemented by subclasses)

        Args:
            event: TaskEvent to process

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement process_event method")

    async def on_error(self, event: TaskEvent, error: Exception) -> None:
        """
        Handle errors during event processing (can be overridden)

        Args:
            event: TaskEvent that failed to process
            error: Exception that occurred
        """
        logger.error(
            f"Error processing event {event.event_id} "
            f"of type {event.event_type}: {str(error)}"
        )


class TaskEventConsumer(BaseEventConsumer):
    """
    Consumer for task lifecycle events (created, updated, completed, deleted)
    """

    async def process_event(self, event: TaskEvent) -> None:
        """
        Process task lifecycle events

        Override this method in subclasses to implement specific logic
        for different event types.

        Args:
            event: TaskEvent to process
        """
        logger.info(
            f"Processing task event {event.event_type} "
            f"for task {event.payload.task_id if hasattr(event.payload, 'task_id') else 'unknown'}"
        )
        # Subclasses should implement specific logic here
        pass
