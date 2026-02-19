"""Dapr State Store client for Phase-V.

This module provides a client for state management using Dapr's
State Store building block.
"""

import json
import logging
from typing import Any, Optional

from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class DaprStateStore:
    """Dapr State Store client for persistent state management."""

    def __init__(
        self,
        store_name: str = "statestore",
        dapr_address: Optional[str] = None,
    ):
        """Initialize the Dapr State Store client.

        Args:
            store_name: Name of the Dapr State Store component.
            dapr_address: Optional Dapr sidecar address (uses default if not provided).
        """
        self.store_name = store_name
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

    async def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get a value from the state store.

        Args:
            key: The state key.

        Returns:
            The value if found, None otherwise.

        Raises:
            DaprInternalError: If the get operation fails.
        """
        client = self._get_client()
        try:
            response = client.get_state(store_name=self.store_name, key=key)
            if response.data:
                return json.loads(response.data.decode("utf-8"))
            return None

        except DaprInternalError as e:
            logger.error(f"Failed to get state for key '{key}': {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode state for key '{key}': {e}")
            return None

    async def save(
        self,
        key: str,
        value: dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """Save a value to the state store.

        Args:
            key: The state key.
            value: The value to save.
            ttl_seconds: Optional TTL in seconds.

        Returns:
            True if the value was saved successfully.

        Raises:
            DaprInternalError: If the save operation fails.
        """
        client = self._get_client()
        try:
            data = json.dumps(value).encode("utf-8")

            # Prepare state options with TTL if provided
            state_options = None
            if ttl_seconds:
                from dapr.clients.grpc._state import StateOptions
                state_options = StateOptions(
                    ttl=ttl_seconds,
                )

            client.save_state(
                store_name=self.store_name,
                key=key,
                value=data,
                state_options=state_options,
            )

            logger.info(f"Saved state for key '{key}'")
            return True

        except DaprInternalError as e:
            logger.error(f"Failed to save state for key '{key}': {e}")
            raise

    async def delete(self, key: str) -> bool:
        """Delete a value from the state store.

        Args:
            key: The state key.

        Returns:
            True if the value was deleted successfully.

        Raises:
            DaprInternalError: If the delete operation fails.
        """
        client = self._get_client()
        try:
            client.delete_state(store_name=self.store_name, key=key)
            logger.info(f"Deleted state for key '{key}'")
            return True

        except DaprInternalError as e:
            logger.error(f"Failed to delete state for key '{key}': {e}")
            raise

    async def get_bulk(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from the state store.

        Args:
            keys: List of state keys.

        Returns:
            Dictionary mapping keys to values.

        Raises:
            DaprInternalError: If the bulk get operation fails.
        """
        client = self._get_client()
        try:
            response = client.get_bulk_state(store_name=self.store_name, keys=keys)
            result = {}
            for item in response.items:
                if item.data:
                    result[item.key] = json.loads(item.data.decode("utf-8"))
                else:
                    result[item.key] = None
            return result

        except DaprInternalError as e:
            logger.error(f"Failed to get bulk state: {e}")
            raise

    async def save_bulk(self, items: list[tuple[str, dict[str, Any]]]) -> bool:
        """Save multiple values to the state store.

        Args:
            items: List of (key, value) tuples.

        Returns:
            True if all values were saved successfully.

        Raises:
            DaprInternalError: If the bulk save operation fails.
        """
        client = self._get_client()
        try:
            for key, value in items:
                data = json.dumps(value).encode("utf-8")
                client.save_state(store_name=self.store_name, key=key, value=data)

            logger.info(f"Saved {len(items)} state items")
            return True

        except DaprInternalError as e:
            logger.error(f"Failed to save bulk state: {e}")
            raise

    async def close(self) -> None:
        """Close the Dapr client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "DaprStateStore":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
