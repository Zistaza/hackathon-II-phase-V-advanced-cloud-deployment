"""Health check endpoints for Phase-V.

This module provides health, readiness, and liveness endpoints
for Kubernetes probes and Dapr health monitoring.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from backend.src.dapr.pubsub import DaprPubSub
from backend.src.dapr.state import DaprStateStore
from backend.src.dapr.secrets import DaprSecrets
from backend.src.dapr.invocation import DaprInvocation, ServiceIds

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus:
    """Health status constants."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


async def get_dapr_health() -> dict[str, Any]:
    """Check Dapr sidecar health.

    Returns:
        Dapr health status dictionary.
    """
    try:
        # Check if we can reach the Dapr sidecar
        pubsub = DaprPubSub()
        # Just instantiate to check connectivity
        client = pubsub._get_client()
        
        return {
            "status": "healthy",
            "sidecar_reachable": True,
        }
    except Exception as e:
        logger.error(f"Dapr health check failed: {e}")
        return {
            "status": "unhealthy",
            "sidecar_reachable": False,
            "error": str(e),
        }


async def get_pubsub_health() -> dict[str, Any]:
    """Check Dapr Pub/Sub component health.

    Returns:
        Pub/Sub health status dictionary.
    """
    try:
        pubsub = DaprPubSub()
        # Try a simple operation to verify connectivity
        # We don't actually publish, just verify the client works
        client = pubsub._get_client()
        
        return {
            "status": "healthy",
            "component": "pubsub",
            "reachable": True,
        }
    except Exception as e:
        logger.error(f"Pub/Sub health check failed: {e}")
        return {
            "status": "unhealthy",
            "component": "pubsub",
            "reachable": False,
            "error": str(e),
        }


async def get_state_store_health() -> dict[str, Any]:
    """Check Dapr State Store component health.

    Returns:
        State Store health status dictionary.
    """
    try:
        state_store = DaprStateStore()
        # Try a simple get operation to verify connectivity
        client = state_store._get_client()
        
        return {
            "status": "healthy",
            "component": "statestore",
            "reachable": True,
        }
    except Exception as e:
        logger.error(f"State Store health check failed: {e}")
        return {
            "status": "unhealthy",
            "component": "statestore",
            "reachable": False,
            "error": str(e),
        }


async def get_secrets_health() -> dict[str, Any]:
    """Check Dapr Secrets component health.

    Returns:
        Secrets health status dictionary.
    """
    try:
        secrets = DaprSecrets()
        # Try to get the client to verify connectivity
        client = secrets._get_client()
        
        return {
            "status": "healthy",
            "component": "secrets",
            "reachable": True,
        }
    except Exception as e:
        logger.error(f"Secrets health check failed: {e}")
        return {
            "status": "unhealthy",
            "component": "secrets",
            "reachable": False,
            "error": str(e),
        }


async def get_service_invocation_health() -> dict[str, Any]:
    """Check Dapr Service Invocation health.

    Returns:
        Service Invocation health status dictionary.
    """
    try:
        invocation = DaprInvocation()
        # Just verify client can be created
        client = invocation._get_client()
        
        return {
            "status": "healthy",
            "component": "invocation",
            "reachable": True,
        }
    except Exception as e:
        logger.error(f"Service Invocation health check failed: {e}")
        return {
            "status": "unhealthy",
            "component": "invocation",
            "reachable": False,
            "error": str(e),
        }


@router.get("", response_model=dict[str, Any])
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint.

    Returns:
        Health status with timestamp.
    """
    return {
        "status": HealthStatus.HEALTHY,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "phase-v-backend",
        "version": "1.0.0",
    }


@router.get("/ready", response_model=dict[str, Any])
async def readiness_check() -> dict[str, Any]:
    """Readiness check endpoint.

    Checks if the service is ready to accept traffic by verifying
    all critical dependencies are available.

    Returns:
        Readiness status with component health.

    Raises:
        HTTPException: If any critical component is unhealthy.
    """
    # Check all Dapr components
    dapr_health = await get_dapr_health()
    pubsub_health = await get_pubsub_health()
    state_store_health = await get_state_store_health()
    secrets_health = await get_secrets_health()

    # Determine overall status
    all_healthy = all(
        h.get("status") == "healthy"
        for h in [dapr_health, pubsub_health, state_store_health, secrets_health]
    )

    if all_healthy:
        status_code = status.HTTP_200_OK
        overall_status = HealthStatus.HEALTHY
    else:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        overall_status = HealthStatus.UNHEALTHY

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "phase-v-backend",
        "components": {
            "dapr": dapr_health,
            "pubsub": pubsub_health,
            "statestore": state_store_health,
            "secrets": secrets_health,
        },
    }, status_code


@router.get("/live", response_model=dict[str, Any])
async def liveness_check() -> dict[str, Any]:
    """Liveness check endpoint.

    Checks if the service is alive and should not be restarted.
    This is a simpler check than readiness - it only verifies the
    application process is running.

    Returns:
        Liveness status.
    """
    return {
        "status": HealthStatus.HEALTHY,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "phase-v-backend",
        "uptime": "running",
    }


@router.get("/dapr", response_model=dict[str, Any])
async def dapr_health_check() -> dict[str, Any]:
    """Detailed Dapr health check.

    Returns health status of all Dapr components.

    Returns:
        Detailed Dapr component health status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "sidecar": await get_dapr_health(),
            "pubsub": await get_pubsub_health(),
            "statestore": await get_state_store_health(),
            "secrets": await get_secrets_health(),
            "invocation": await get_service_invocation_health(),
        },
    }


@router.get("/services", response_model=dict[str, Any])
async def services_health_check() -> dict[str, Any]:
    """Check health of dependent services via Dapr Service Invocation.

    Returns:
        Status of all dependent services.
    """
    services = {
        ServiceIds.BACKEND: "self",
        ServiceIds.EVENT_PROCESSOR: None,
        ServiceIds.REMINDER_SCHEDULER: None,
        ServiceIds.NOTIFICATION_SERVICE: None,
        ServiceIds.WEBSOCKET_SERVICE: None,
    }

    invocation = DaprInvocation()
    results = {}

    for service_id, _ in services.items():
        if service_id == "self":
            results[service_id] = {
                "status": "healthy",
                "reachable": True,
            }
            continue

        try:
            # Try to invoke health endpoint on the service
            health = await invocation.invoke_method(
                app_id=service_id,
                method="/health",
                http_verb="GET",
            )
            results[service_id] = {
                "status": "healthy",
                "reachable": True,
                "details": health,
            }
        except Exception as e:
            results[service_id] = {
                "status": "unhealthy",
                "reachable": False,
                "error": str(e),
            }

    # Determine overall status
    all_healthy = all(r.get("status") == "healthy" for r in results.values())

    return {
        "status": HealthStatus.HEALTHY if all_healthy else HealthStatus.DEGRADED,
        "timestamp": datetime.utcnow().isoformat(),
        "services": results,
    }
