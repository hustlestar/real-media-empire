"""WebSocket manager for real-time updates using Socket.IO."""

import logging
from typing import Dict, Any, List, Optional
import socketio

logger = logging.getLogger(__name__)

# Create Socket.IO server with ASGI support
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",  # Configure appropriately for production
    logger=True,
    engineio_logger=True
)

# Create ASGI app for Socket.IO
socket_app = socketio.ASGIApp(sio)


class WebSocketManager:
    """Manager for WebSocket connections and broadcasting."""

    def __init__(self):
        self._active_connections: Dict[str, set] = {}  # room_id -> set of sids
        logger.info("WebSocket manager initialized")

    async def connect(self, sid: str, room: str):
        """Add client to a room."""
        if room not in self._active_connections:
            self._active_connections[room] = set()
        self._active_connections[room].add(sid)
        logger.info(f"Client {sid} connected to room {room}")

    async def disconnect(self, sid: str, room: str):
        """Remove client from a room."""
        if room in self._active_connections:
            self._active_connections[room].discard(sid)
            if not self._active_connections[room]:
                del self._active_connections[room]
        logger.info(f"Client {sid} disconnected from room {room}")

    def get_room_clients(self, room: str) -> List[str]:
        """Get all clients in a room."""
        return list(self._active_connections.get(room, set()))

    def get_active_rooms(self) -> List[str]:
        """Get all active rooms."""
        return list(self._active_connections.keys())


# Global manager instance
ws_manager = WebSocketManager()


# Socket.IO event handlers
@sio.event
async def connect(sid, environ, auth):
    """Handle client connection."""
    logger.info(f"Client connected: {sid}")
    await sio.emit("connected", {"sid": sid}, room=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {sid}")
    # Remove from all rooms
    for room in list(ws_manager._active_connections.keys()):
        await ws_manager.disconnect(sid, room)


@sio.event
async def join_room(sid, data):
    """Client joins a specific room for targeted updates."""
    room = data.get("room")
    if room:
        sio.enter_room(sid, room)
        await ws_manager.connect(sid, room)
        await sio.emit("room_joined", {"room": room}, room=sid)
        logger.info(f"Client {sid} joined room: {room}")


@sio.event
async def leave_room(sid, data):
    """Client leaves a room."""
    room = data.get("room")
    if room:
        sio.leave_room(sid, room)
        await ws_manager.disconnect(sid, room)
        await sio.emit("room_left", {"room": room}, room=sid)
        logger.info(f"Client {sid} left room: {room}")


# Broadcasting functions
async def broadcast_to_room(room: str, event: str, data: Dict[str, Any]):
    """
    Broadcast message to all clients in a room.

    Args:
        room: Room identifier
        event: Event name
        data: Event data to broadcast
    """
    logger.info(f"Broadcasting '{event}' to room '{room}': {data}")
    await sio.emit(event, data, room=room)


async def broadcast_to_all(event: str, data: Dict[str, Any]):
    """
    Broadcast message to all connected clients.

    Args:
        event: Event name
        data: Event data to broadcast
    """
    logger.info(f"Broadcasting '{event}' to all clients: {data}")
    await sio.emit(event, data)


async def send_to_client(sid: str, event: str, data: Dict[str, Any]):
    """
    Send message to a specific client.

    Args:
        sid: Client session ID
        event: Event name
        data: Event data to send
    """
    logger.info(f"Sending '{event}' to client {sid}: {data}")
    await sio.emit(event, data, room=sid)


# Event-specific broadcasting functions
async def broadcast_job_progress(job_id: str, progress: Dict[str, Any]):
    """
    Broadcast job progress update.

    Args:
        job_id: Job identifier
        progress: Progress data (current, total, status, etc.)
    """
    await broadcast_to_room(
        f"job:{job_id}",
        "job_progress",
        {
            "job_id": job_id,
            "progress": progress,
            "timestamp": progress.get("timestamp")
        }
    )


async def broadcast_job_completed(job_id: str, result: Dict[str, Any]):
    """
    Broadcast job completion.

    Args:
        job_id: Job identifier
        result: Job result data
    """
    await broadcast_to_room(
        f"job:{job_id}",
        "job_completed",
        {
            "job_id": job_id,
            "result": result,
            "status": "completed"
        }
    )


async def broadcast_job_failed(job_id: str, error: str):
    """
    Broadcast job failure.

    Args:
        job_id: Job identifier
        error: Error message
    """
    await broadcast_to_room(
        f"job:{job_id}",
        "job_failed",
        {
            "job_id": job_id,
            "error": error,
            "status": "failed"
        }
    )


async def broadcast_publishing_update(account_id: str, update: Dict[str, Any]):
    """
    Broadcast publishing status update.

    Args:
        account_id: Publishing account identifier
        update: Update data
    """
    await broadcast_to_room(
        f"publishing:{account_id}",
        "publishing_update",
        update
    )


async def broadcast_asset_uploaded(asset_id: str, asset_data: Dict[str, Any]):
    """
    Broadcast new asset upload.

    Args:
        asset_id: Asset identifier
        asset_data: Asset metadata
    """
    await broadcast_to_room(
        "assets",
        "asset_uploaded",
        {
            "asset_id": asset_id,
            "asset": asset_data
        }
    )


async def broadcast_character_created(character_id: str, character_data: Dict[str, Any]):
    """
    Broadcast new character creation.

    Args:
        character_id: Character identifier
        character_data: Character metadata
    """
    await broadcast_to_room(
        "characters",
        "character_created",
        {
            "character_id": character_id,
            "character": character_data
        }
    )
