"""Dapr Secrets client for Phase-V.

This module provides a client for retrieving secrets using Dapr's
Secrets building block.
"""

import logging
from typing import Optional

from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class DaprSecrets:
    """Dapr Secrets client for secure secret retrieval."""

    def __init__(
        self,
        secret_store_name: str = "kubernetes-secrets",
        dapr_address: Optional[str] = None,
    ):
        """Initialize the Dapr Secrets client.

        Args:
            secret_store_name: Name of the Dapr secret store component.
            dapr_address: Optional Dapr sidecar address (uses default if not provided).
        """
        self.secret_store_name = secret_store_name
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

    async def get_secret(self, secret_name: str, key: str) -> Optional[str]:
        """Get a secret value.

        Args:
            secret_name: Name of the Kubernetes secret.
            key: The key within the secret.

        Returns:
            The secret value if found, None otherwise.

        Raises:
            DaprInternalError: If the secret retrieval fails.
        """
        client = self._get_client()
        try:
            response = client.get_secret(
                store_name=self.secret_store_name,
                key=secret_name,
                metadata={"key": key},
            )

            if response.secret and key in response.secret:
                return response.secret[key]
            return None

        except DaprInternalError as e:
            logger.error(f"Failed to get secret '{secret_name}/{key}': {e}")
            raise

    async def get_bulk_secrets(self, secret_name: str) -> dict[str, str]:
        """Get all keys from a secret.

        Args:
            secret_name: Name of the Kubernetes secret.

        Returns:
            Dictionary of all secret keys and values.

        Raises:
            DaprInternalError: If the secret retrieval fails.
        """
        client = self._get_client()
        try:
            response = client.get_secret(
                store_name=self.secret_store_name,
                key=secret_name,
            )

            return response.secret if response.secret else {}

        except DaprInternalError as e:
            logger.error(f"Failed to get bulk secrets '{secret_name}': {e}")
            raise

    async def close(self) -> None:
        """Close the Dapr client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "DaprSecrets":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


# Secret name constants
class SecretNames:
    """Standard secret names for Phase-V."""

    POSTGRES = "postgres-secret"
    JWT = "jwt-secret"
    REDIS = "redis-secret"
    REDPANDA = "redpanda-secret"


# Secret key constants
class SecretKeys:
    """Standard secret key names for Phase-V."""

    CONNECTION_STRING = "connection-string"
    SECRET = "secret"
    PASSWORD = "password"
    USERNAME = "username"
