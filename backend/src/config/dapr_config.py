"""Dapr-based configuration loader for Phase-V.

This module provides configuration loading using Dapr Secrets
for secure retrieval of sensitive data from Kubernetes secrets.
"""

import logging
import os
from typing import Any, Optional

from backend.src.dapr.secrets import DaprSecrets, SecretNames, SecretKeys

logger = logging.getLogger(__name__)


class DaprConfigLoader:
    """Load configuration from Dapr Secrets.

    This class provides a centralized way to load sensitive configuration
    from Kubernetes secrets using Dapr's Secrets building block.
    """

    def __init__(self, secret_store_name: Optional[str] = None):
        """Initialize the Dapr config loader.

        Args:
            secret_store_name: Name of the Dapr secret store component.
        """
        self.secret_store_name = secret_store_name
        self._secrets_client: Optional[DaprSecrets] = None
        self._cache: dict[str, dict[str, str]] = {}

    def _get_secrets_client(self) -> DaprSecrets:
        """Get or create the Dapr secrets client.

        Returns:
            DaprSecrets instance.
        """
        if self._secrets_client is None:
            self._secrets_client = DaprSecrets(
                secret_store_name=self.secret_store_name or "kubernetes-secrets"
            )
        return self._secrets_client

    async def get_database_url(self) -> str:
        """Get database connection URL from secrets.

        Returns:
            Database connection URL.

        Raises:
            ValueError: If secret is not found.
        """
        # Try Dapr secrets first
        try:
            secrets_client = self._get_secrets_client()
            secret_value = await secrets_client.get_secret(
                secret_name="neon-secret",
                key="connectionString"
            )
            if secret_value:
                logger.info("Loaded database URL from Dapr secrets")
                return secret_value
        except Exception as e:
            logger.warning(f"Failed to load database URL from Dapr: {e}")

        # Fallback to environment variable
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            logger.info("Loaded database URL from environment")
            return db_url

        raise ValueError("Database URL not found in secrets or environment")

    async def get_jwt_secret(self) -> str:
        """Get JWT secret key from secrets.

        Returns:
            JWT secret key.

        Raises:
            ValueError: If secret is not found.
        """
        # Try Dapr secrets first
        try:
            secrets_client = self._get_secrets_client()
            secret_value = await secrets_client.get_secret(
                secret_name="jwt-secret",
                key="secret"
            )
            if secret_value:
                logger.info("Loaded JWT secret from Dapr secrets")
                return secret_value
        except Exception as e:
            logger.warning(f"Failed to load JWT secret from Dapr: {e}")

        # Fallback to environment variable
        jwt_secret = os.getenv("JWT_SECRET")
        if jwt_secret:
            logger.info("Loaded JWT secret from environment")
            return jwt_secret

        raise ValueError("JWT secret not found in secrets or environment")

    async def get_redis_password(self) -> str:
        """Get Redis password from secrets.

        Returns:
            Redis password.

        Raises:
            ValueError: If secret is not found.
        """
        # Try Dapr secrets first
        try:
            secrets_client = self._get_secrets_client()
            secret_value = await secrets_client.get_secret(
                secret_name="redis-secret",
                key="password"
            )
            if secret_value:
                logger.info("Loaded Redis password from Dapr secrets")
                return secret_value
        except Exception as e:
            logger.warning(f"Failed to load Redis password from Dapr: {e}")

        # Fallback to environment variable
        redis_password = os.getenv("REDIS_PASSWORD")
        if redis_password:
            logger.info("Loaded Redis password from environment")
            return redis_password

        raise ValueError("Redis password not found in secrets or environment")

    async def get_redpanda_credentials(self) -> dict[str, str]:
        """Get Redpanda Cloud credentials from secrets.

        Returns:
            Dictionary with username and password.

        Raises:
            ValueError: If secrets are not found.
        """
        try:
            secrets_client = self._get_secrets_client()
            secrets = await secrets_client.get_bulk_secrets("redpanda-secret")

            if secrets:
                logger.info("Loaded Redpanda credentials from Dapr secrets")
                return {
                    "username": secrets.get("username", ""),
                    "password": secrets.get("password", ""),
                }
        except Exception as e:
            logger.warning(f"Failed to load Redpanda credentials from Dapr: {e}")

        # Fallback to environment variables
        username = os.getenv("REDPANDA_USERNAME")
        password = os.getenv("REDPANDA_PASSWORD")

        if username and password:
            logger.info("Loaded Redpanda credentials from environment")
            return {"username": username, "password": password}

        raise ValueError("Redpanda credentials not found in secrets or environment")

    async def get_openai_api_key(self) -> str:
        """Get OpenAI API key from secrets.

        Returns:
            OpenAI API key.

        Raises:
            ValueError: If secret is not found.
        """
        # Try Dapr secrets first
        try:
            secrets_client = self._get_secrets_client()
            secret_value = await secrets_client.get_secret(
                secret_name="openai-secret",
                key="api-key"
            )
            if secret_value:
                logger.info("Loaded OpenAI API key from Dapr secrets")
                return secret_value
        except Exception as e:
            logger.warning(f"Failed to load OpenAI API key from Dapr: {e}")

        # Fallback to environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            logger.info("Loaded OpenAI API key from environment")
            return api_key

        raise ValueError("OpenAI API key not found in secrets or environment")

    async def get_all_secrets(self) -> dict[str, Any]:
        """Get all configuration secrets.

        Returns:
            Dictionary of all configuration values.
        """
        try:
            secrets = {}

            # Load each secret
            try:
                secrets["database_url"] = await self.get_database_url()
            except ValueError:
                secrets["database_url"] = None

            try:
                secrets["jwt_secret"] = await self.get_jwt_secret()
            except ValueError:
                secrets["jwt_secret"] = None

            try:
                secrets["redis_password"] = await self.get_redis_password()
            except ValueError:
                secrets["redis_password"] = None

            try:
                secrets["redpanda_credentials"] = await self.get_redpanda_credentials()
            except ValueError:
                secrets["redpanda_credentials"] = None

            try:
                secrets["openai_api_key"] = await self.get_openai_api_key()
            except ValueError:
                secrets["openai_api_key"] = None

            return secrets

        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
            return {}

    async def close(self) -> None:
        """Close the secrets client."""
        if self._secrets_client:
            await self._secrets_client.close()
            self._secrets_client = None


# Global config loader instance
_config_loader: Optional[DaprConfigLoader] = None


def get_config_loader() -> DaprConfigLoader:
    """Get the global config loader instance.

    Returns:
        DaprConfigLoader instance.
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = DaprConfigLoader()
    return _config_loader


async def close_config_loader() -> None:
    """Close the global config loader."""
    global _config_loader
    if _config_loader:
        await _config_loader.close()
        _config_loader = None
