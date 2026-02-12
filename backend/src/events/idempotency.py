"""
Idempotency checker for event handlers using Dapr State Store
"""
from dapr.clients import DaprClient
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

# 7-day TTL for processed event IDs (604800 seconds)
EVENT_TTL_SECONDS = 604800


async def check_and_mark_processed(event_id: UUID | str, state_store: str = "statestore") -> bool:
    """
    Check if an event has been processed and mark it as processed if not

    This function implements idempotency by storing processed event IDs in Dapr State Store
    with a 7-day TTL. If the event ID already exists, it returns True (already processed).
    If not, it stores the event ID and returns False (not yet processed).

    Args:
        event_id: Unique event identifier (UUID or string)
        state_store: Name of the Dapr State Store component (default: "statestore")

    Returns:
        bool: True if event was already processed, False if this is the first time

    Raises:
        Exception: If Dapr State Store operations fail
    """
    event_key = f"processed-event:{str(event_id)}"

    try:
        async with DaprClient() as client:
            # Check if event ID exists in state store
            state = await client.get_state(
                store_name=state_store,
                key=event_key
            )

            if state.data:
                logger.info(f"Event {event_id} already processed, skipping")
                return True

            # Mark event as processed with TTL
            await client.save_state(
                store_name=state_store,
                key=event_key,
                value="processed",
                state_metadata={"ttlInSeconds": str(EVENT_TTL_SECONDS)}
            )

            logger.debug(f"Marked event {event_id} as processed with {EVENT_TTL_SECONDS}s TTL")
            return False

    except Exception as e:
        logger.error(f"Failed to check/mark event {event_id} as processed: {str(e)}")
        raise


async def is_event_processed(event_id: UUID | str, state_store: str = "statestore") -> bool:
    """
    Check if an event has been processed (read-only check)

    Args:
        event_id: Unique event identifier (UUID or string)
        state_store: Name of the Dapr State Store component (default: "statestore")

    Returns:
        bool: True if event was already processed, False otherwise

    Raises:
        Exception: If Dapr State Store operations fail
    """
    event_key = f"processed-event:{str(event_id)}"

    try:
        async with DaprClient() as client:
            state = await client.get_state(
                store_name=state_store,
                key=event_key
            )

            return bool(state.data)

    except Exception as e:
        logger.error(f"Failed to check if event {event_id} is processed: {str(e)}")
        raise


async def mark_event_processed(event_id: UUID | str, state_store: str = "statestore") -> None:
    """
    Mark an event as processed (write-only operation)

    Args:
        event_id: Unique event identifier (UUID or string)
        state_store: Name of the Dapr State Store component (default: "statestore")

    Raises:
        Exception: If Dapr State Store operations fail
    """
    event_key = f"processed-event:{str(event_id)}"

    try:
        async with DaprClient() as client:
            await client.save_state(
                store_name=state_store,
                key=event_key,
                value="processed",
                state_metadata={"ttlInSeconds": str(EVENT_TTL_SECONDS)}
            )

            logger.debug(f"Marked event {event_id} as processed")

    except Exception as e:
        logger.error(f"Failed to mark event {event_id} as processed: {str(e)}")
        raise
