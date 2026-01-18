from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Key: Community ID (str), Value: List of Active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, community_id: str, websocket: WebSocket):
        """Accepts a connection and adds it to the specific room."""
        await websocket.accept()
        if community_id not in self.active_connections:
            self.active_connections[community_id] = []
        self.active_connections[community_id].append(websocket)
        
        # Optional: Log the connection
        print(f"🔌 User connected to Room: {community_id}. Total: {len(self.active_connections[community_id])}")

    def disconnect(self, community_id: str, websocket: WebSocket):
        """Removes a connection when a user leaves or disconnects."""
        if community_id in self.active_connections:
            if websocket in self.active_connections[community_id]:
                self.active_connections[community_id].remove(websocket)
                
            # Clean up empty rooms to save memory
            if not self.active_connections[community_id]:
                del self.active_connections[community_id]
                
    async def broadcast(self, community_id: str, message: dict):
        """Sends a JSON message to everyone in a specific room."""
        if community_id in self.active_connections:
            # Iterate over a copy of the list to avoid modification errors during iteration
            for connection in self.active_connections[community_id][:]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # If sending fails (broken pipe), remove the dead connection
                    self.disconnect(community_id, connection)

# Create a Global Instance to be used across the app
manager = ConnectionManager()