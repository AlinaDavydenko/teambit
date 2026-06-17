from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # board_id -> connection websocket's list
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, board_id: int):
        """Connect to the board"""
        await websocket.accept()
        if board_id not in self.active_connections:
            self.active_connections[board_id] = []
        self.active_connections[board_id].append(websocket)

    def disconnect(self, websocket: WebSocket, board_id: int):
        """Remove websocket"""
        self.active_connections[board_id].remove(websocket)

    async def broadcast(self, board_id: int, message: dict):
        """Send message to everyone on the board"""
        if board_id in self.active_connections:
            for connection in self.active_connections[board_id]:
                await connection.send_json(message)


manager = ConnectionManager()
