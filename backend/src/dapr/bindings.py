"""Dapr Bindings client for Phase-V.

This module provides a client for interacting with Dapr Bindings,
which enable integration with external systems and cron triggers.
"""

import json
import logging
from typing import Any, Optional

from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class DaprBindings:
    """Dapr Bindings client for external system integration."""

    def __init__(
        self,
        dapr_address: Optional[str] = None,
    ):
        """Initialize the Dapr Bindings client.

        Args:
            dapr_address: Optional Dapr sidecar address (uses default if not provided).
        """
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

    async def invoke_output_binding(
        self,
        binding_name: str,
        data: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> Optional[dict[str, Any]]:
        """Invoke an output binding.

        Args:
            binding_name: Name of the binding to invoke.
            data: Optional data to send to the binding.
            metadata: Optional metadata for the binding invocation.

        Returns:
            The response from the binding, if any.

        Raises:
            DaprInternalError: If the binding invocation fails.
        """
        client = self._get_client()
        try:
            data_bytes = None
            if data:
                data_bytes = json.dumps(data).encode("utf-8")

            response = client.invoke_binding(
                binding_name=binding_name,
                operation="create",
                data=data_bytes,
                metadata=metadata,
            )

            if response.data:
                return json.loads(response.data.decode("utf-8"))
            return None

        except DaprInternalError as e:
            logger.error(f"Failed to invoke binding '{binding_name}': {e}")
            raise

    async def handle_input_binding(
        self,
        binding_name: str,
        handler: callable,
    ) -> None:
        """Handle input binding events.

        Note: Dapr handles input bindings via HTTP callbacks. This method
        is provided for documentation purposes.

        Args:
            binding_name: Name of the input binding.
            handler: The event handler function.
        """
        logger.info(f"Input binding '{binding_name}' configured via Dapr component")
        # Input bindings are configured via Dapr component YAML files
        # Dapr calls the application's /bindings/{binding_name} endpoint
        # when the binding receives data (e.g., cron triggers)

    async def close(self) -> None:
        """Close the Dapr client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "DaprBindings":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


# Binding name constants
class Bindings:
    """Standard binding names for Phase-V."""

    CRON = "cron-binding"
