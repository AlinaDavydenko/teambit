from fastapi import WebSocket
import json
from app.core.redis_client import redis_client
import asyncio


class ConnectionManager:
    def __init__(self):
        # board_id -> connection websocket's list
        self.active_connections: dict[int, list[WebSocket]] = {}
        self.online_users: dict[int, dict[WebSocket, int]] = {}

    async def connect(self, websocket: WebSocket, board_id: int, user_id: int):
        """Connect to the board"""
        await websocket.accept()
        if board_id not in self.active_connections:
            self.active_connections[board_id] = []
            self.online_users[board_id] = {}
            asyncio.create_task(self.listen_to_board(board_id))
        self.active_connections[board_id].append(websocket)
        self.online_users[board_id][websocket] = user_id

    def disconnect(self, websocket: WebSocket, board_id: int):
        """Remove websocket"""
        self.active_connections[board_id].remove(websocket)
        if websocket in self.online_users.get(board_id, {}):
            del self.online_users[board_id][websocket]

    async def broadcast(self, board_id: int, message: dict):
        """Send message to everyone on the board"""
        if board_id in self.active_connections:
            for connection in self.active_connections[board_id]:
                await connection.send_json(message)

    async def publish(self, board_id: int, message: dict):
        """Publish a message to Redis channel for this board"""
        channel = f"board:{board_id}"
        await redis_client.publish(channel, json.dumps(message))

    async def listen_to_board(self, board_id: int):
        """Listen to Redis channel and broadcast to local connections"""
        channel = f"board:{board_id}"
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)

        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await self.broadcast(board_id, data)

    def get_online_users(self, board_id: int) -> list[int]:
        """Get unique user_ids currently online on this board"""
        if board_id not in self.online_users:
            return []
        return list(set(self.online_users[board_id].values()))


manager = ConnectionManager()
