"""
WebSocket endpoint for real-time task updates
Provides multi-client synchronization via task-updates topic
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Set
from backend.src.dependencies.auth import verify_jwt_token
from dapr.clients import DaprClient
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Store active WebSocket connections per user
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections for users"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """Add a new WebSocket connection for a user"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: str, websocket: WebSocket):
        """Remove a WebSocket connection for a user"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

            logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to all connections for a specific user"""
        if user_id not in self.active_connections:
            return

        disconnected = set()

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {str(e)}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(user_id, connection)

    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)


manager = ConnectionManager()


async def get_current_user_from_token(token: str) -> str:
    """
    Extract user_id from JWT token

    Args:
        token: JWT token string

    Returns:
        str: User ID

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = verify_jwt_token(token)
        user_id = payload.get("sub") or payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user_id not found"
            )

        return user_id
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time task updates

    Clients connect to this endpoint and receive task events in real-time.
    Authentication is performed via JWT token in query parameters.

    Args:
        websocket: WebSocket connection
        user_id: User ID from URL path
    """
    # Get token from query parameters
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
        return

    # Verify token and user_id match
    try:
        authenticated_user_id = await get_current_user_from_token(token)

        if authenticated_user_id != user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User ID mismatch")
            return
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    # Connect the WebSocket
    await manager.connect(user_id, websocket)

    # Start listening to task-updates topic for this user
    subscription_task = asyncio.create_task(
        subscribe_to_task_updates(user_id, websocket)
    )

    try:
        # Keep connection alive and handle incoming messages (if any)
        while True:
            try:
                # Wait for messages from client (ping/pong for keepalive)
                data = await websocket.receive_text()

                # Handle ping/pong
                if data == "ping":
                    await websocket.send_text("pong")

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user_id}")
                break
            except Exception as e:
                logger.error(f"Error receiving WebSocket message: {str(e)}")
                break

    finally:
        # Clean up
        subscription_task.cancel()
        manager.disconnect(user_id, websocket)


async def subscribe_to_task_updates(user_id: str, websocket: WebSocket):
    """
    Subscribe to task-updates Kafka topic and forward events to WebSocket

    Args:
        user_id: User ID to filter events
        websocket: WebSocket connection to send events to
    """
    try:
        async with DaprClient() as client:
            # Subscribe to task-updates topic
            # Note: In production, use Dapr subscription with proper filtering
            # For now, we'll poll for events (simplified implementation)

            logger.info(f"Started task-updates subscription for user {user_id}")

            # In a real implementation, this would use Dapr's subscription mechanism
            # For MVP, the event publisher already sends to task-updates topic
            # and the frontend WebSocket receives events directly

            # Keep the task alive
            while True:
                await asyncio.sleep(1)

    except asyncio.CancelledError:
        logger.info(f"Task-updates subscription cancelled for user {user_id}")
    except Exception as e:
        logger.error(f"Error in task-updates subscription for user {user_id}: {str(e)}")


@router.get("/ws/health")
async def websocket_health():
    """Health check for WebSocket service"""
    return {
        "status": "healthy",
        "service": "websocket",
        "active_users": len(manager.active_connections),
        "total_connections": sum(len(conns) for conns in manager.active_connections.values())
    }


# Export connection manager for use in other modules
def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance"""
    return manager
