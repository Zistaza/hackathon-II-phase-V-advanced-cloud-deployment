"""Dapr Pub/Sub client for Phase-V.

This module provides a client for publishing and subscribing to events
using Dapr's Pub/Sub building block.
"""

import json
import logging
from typing import Any, Callable, Optional

from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class DaprPubSub:
    """Dapr Pub/Sub client for event publishing and subscription."""

    def __init__(
        self,
        pubsub_name: str = "pubsub",
        dapr_address: Optional[str] = None,
    ):
        """Initialize the Dapr Pub/Sub client.

        Args:
            pubsub_name: Name of the Dapr Pub/Sub component.
            dapr_address: Optional Dapr sidecar address (uses default if not provided).
        """
        self.pubsub_name = pubsub_name
        self.dapr_address = dapr_address
        self._client: Optional[DaprClient] = None

    def _get_client(self) -> DaprClient:
        """Get or create the Dapr client.

        Returns:
            DaprClient instance.
        """
        if self._client is None:
            if self.dapr_address:
                self._client = DaprClient(dapr_address=self.dapr_address)
            else:
                self._client = DaprClient()
        return self._client

    async def publish(
        self,
        topic: str,
        data: dict[str, Any],
        metadata: Optional[dict[str, str]] = None,
    ) -> bool:
        """Publish an event to a topic.

        Args:
            topic: The topic to publish to.
            data: The event data to publish.
            metadata: Optional metadata for the event.

        Returns:
            True if the event was published successfully.

        Raises:
            DaprInternalError: If publishing fails.
        """
        client = self._get_client()
        try:
            # Convert data to JSON bytes
            data_bytes = json.dumps(data).encode("utf-8")

            # Publish the event
            client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=data_bytes,
                metadata=metadata,
            )

            logger.info(f"Published event to topic '{topic}'")
            return True

        except DaprInternalError as e:
            logger.error(f"Failed to publish event to topic '{topic}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error publishing event: {e}")
            raise

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[dict[str, Any]], None],
    ) -> None:
        """Subscribe to a topic.

        Note: Dapr handles subscriptions via Kubernetes CRDs. This method
        is provided for local testing and documentation purposes.

        Args:
            topic: The topic to subscribe to.
            handler: The event handler function.
        """
        logger.info(f"Subscription to topic '{topic}' configured via Dapr Subscription CRD")
        # In Dapr, subscriptions are configured via Kubernetes Subscription CRDs
        # The handler is exposed as an HTTP endpoint that Dapr calls
        # See k8s/base/dapr-subscriptions.yaml for subscription configuration

    async def close(self) -> None:
        """Close the Dapr client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "DaprPubSub":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


# Topic constants
class Topics:
    """Standard topic names for Phase-V events."""

    TASK_EVENTS = "task.events"
    REMINDER_EVENTS = "reminder.events"
    RECURRENCE_EVENTS = "recurrence.events"
    NOTIFICATION_EVENTS = "notification.events"
