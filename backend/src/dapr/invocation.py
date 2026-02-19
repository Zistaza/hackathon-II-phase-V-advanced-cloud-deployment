"""Dapr Service Invocation client for Phase-V.

This module provides a client for service-to-service communication
using Dapr's Service Invocation building block.
"""

import asyncio
import json
import logging
from typing import Any, Optional

import httpx
from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class DaprInvocation:
    """Dapr Service Invocation client for service-to-service communication."""

    def __init__(
        self,
        dapr_address: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """Initialize the Dapr Service Invocation client.

        Args:
            dapr_address: Optional Dapr sidecar address (uses default if not provided).
            timeout: HTTP request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
        """
        self.dapr_address = dapr_address
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[DaprClient] = None
        self._http_client: Optional[httpx.AsyncClient] = None

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

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client.

        Returns:
            httpx.AsyncClient instance.
        """
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._http_client

    async def invoke_method(
        self,
        app_id: str,
        method: str,
        data: Optional[dict[str, Any]] = None,
        http_verb: str = "POST",
        content_type: str = "application/json",
        metadata: Optional[dict[str, str]] = None,
    ) -> Optional[dict[str, Any]]:
        """Invoke a method on another service.

        Args:
            app_id: The target service's Dapr app-id.
            method: The method name to invoke.
            data: Optional request body data.
            http_verb: HTTP method (GET, POST, PUT, DELETE, etc.).
            content_type: Content type of the request.
            metadata: Optional metadata for the request.

        Returns:
            Response data as dictionary, or None for no-content responses.

        Raises:
            DaprInternalError: If the invocation fails.
        """
        client = self._get_client()
        try:
            # Prepare request data
            if data and content_type == "application/json":
                request_data = json.dumps(data).encode("utf-8")
            else:
                request_data = data if data else b""

            # Invoke the method
            response = client.invoke_method(
                app_id=app_id,
                method=method,
                http_verb=http_verb,
                data=request_data,
                content_type=content_type,
                metadata=metadata,
            )

            # Parse response
            if response.content_type == "application/json" and response.data:
                return json.loads(response.data.decode("utf-8"))
            elif response.data:
                return {"data": response.data.decode("utf-8")}
            return None

        except DaprInternalError as e:
            logger.error(f"Failed to invoke method '{method}' on app '{app_id}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error invoking method: {e}")
            raise

    async def invoke_url(
        self,
        app_id: str,
        url: str,
        method: str = "POST",
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Optional[dict[str, Any]]:
        """Invoke a URL on another service using Dapr's service invocation.

        This method uses HTTP directly to call another service through Dapr's
        service invocation endpoint.

        Args:
            app_id: The target service's Dapr app-id.
            url: The URL path to invoke (e.g., "/api/tasks").
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            data: Optional request body data.
            params: Optional query parameters.
            headers: Optional HTTP headers.

        Returns:
            Response data as dictionary, or None for no-content responses.

        Raises:
            httpx.HTTPError: If the invocation fails.
        """
        http_client = await self._get_http_client()

        # Dapr service invocation URL format
        # http://localhost:3500/v1.0/invoke/{app_id}/method/{method}
        dapr_port = 3500
        base_url = f"http://localhost:{dapr_port}/v1.0/invoke/{app_id}/method"
        invoke_url = f"{base_url}{url}"

        for attempt in range(self.max_retries):
            try:
                response = await http_client.request(
                    method=method.upper(),
                    url=invoke_url,
                    json=data if data and method.upper() in ["POST", "PUT", "PATCH"] else None,
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()

                # Parse response
                if response.status_code == 204:
                    return None

                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    return response.json()
                else:
                    return {"data": response.text}

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error invoking {method} {url} on app {app_id}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff

            except httpx.RequestError as e:
                logger.error(f"Request error invoking {method} {url} on app {app_id}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff

        return None

    async def invoke_service_with_retry(
        self,
        app_id: str,
        method: str,
        data: Optional[dict[str, Any]] = None,
        http_verb: str = "POST",
        retry_delay: float = 1.0,
        max_retries: Optional[int] = None,
    ) -> Optional[dict[str, Any]]:
        """Invoke a service method with retry logic.

        Args:
            app_id: The target service's Dapr app-id.
            method: The method name to invoke.
            data: Optional request body data.
            http_verb: HTTP method (GET, POST, PUT, DELETE, etc.).
            retry_delay: Base delay between retries in seconds.
            max_retries: Override default max retries.

        Returns:
            Response data as dictionary, or None for no-content responses.

        Raises:
            DaprInternalError: If all retries fail.
        """
        retries = max_retries or self.max_retries

        for attempt in range(retries):
            try:
                return await self.invoke_method(
                    app_id=app_id,
                    method=method,
                    data=data,
                    http_verb=http_verb,
                )
            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"All {retries} retries failed for {method} on {app_id}")
                    raise

                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f"Retry {attempt + 1}/{retries} for {method} on {app_id} after {wait_time}s"
                )
                await asyncio.sleep(wait_time)

        return None

    async def close(self) -> None:
        """Close the Dapr and HTTP clients."""
        if self._client:
            self._client.close()
            self._client = None

        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

    def __enter__(self) -> "DaprInvocation":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


# Service ID constants
class ServiceIds:
    """Standard service IDs for Phase-V services."""

    BACKEND = "phase-v-backend"
    EVENT_PROCESSOR = "phase-v-event-processor"
    REMINDER_SCHEDULER = "phase-v-reminder-scheduler"
    NOTIFICATION_SERVICE = "phase-v-notification-service"
    WEBSOCKET_SERVICE = "phase-v-websocket-service"
    FRONTEND = "phase-v-frontend"


# Method name constants
class Methods:
    """Standard method names for service invocation."""

    # Backend methods
    GET_TASKS = "/api/tasks"
    CREATE_TASK = "/api/tasks"
    UPDATE_TASK = "/api/tasks/{task_id}"
    DELETE_TASK = "/api/tasks/{task_id}"
    COMPLETE_TASK = "/api/tasks/{task_id}/complete"

    # Reminder methods
    SCHEDULE_REMINDER = "/api/reminders"
    CANCEL_REMINDER = "/api/reminders/{reminder_id}"

    # Notification methods
    SEND_NOTIFICATION = "/api/notifications"
    SEND_EMAIL = "/api/notifications/email"
    SEND_PUSH = "/api/notifications/push"

    # Health checks
    HEALTH = "/health"
    READY = "/ready"
    LIVE = "/live"
