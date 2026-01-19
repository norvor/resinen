from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # In-memory store: Community ID -> List of Active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, community_id: str, websocket: WebSocket):
        """Accepts a WS connection and adds it to the community pool."""
        await websocket.accept()
        
        if community_id not in self.active_connections:
            self.active_connections[community_id] = []
        
        self.active_connections[community_id].append(websocket)
        
        # Optional: Log the connection
        print(f"🔌 [WS] Client connected to Community {community_id}. Total: {len(self.active_connections[community_id])}")

    def disconnect(self, community_id: str, websocket: WebSocket):
        """Removes a WS connection from the pool."""
        if community_id in self.active_connections:
            if websocket in self.active_connections[community_id]:
                self.active_connections[community_id].remove(websocket)
                print(f"❌ [WS] Client disconnected from Community {community_id}")
            
            # Cleanup empty rooms to save memory
            if not self.active_connections[community_id]:
                del self.active_connections[community_id]

    async def broadcast(self, community_id: str, message: dict):
        """Sends a JSON message to everyone in a specific community."""
        if community_id in self.active_connections:
            # Iterate through a copy of the list to avoid modification errors during iteration
            for connection in self.active_connections[community_id][:]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"⚠️ [WS] Failed to send to client: {e}")
                    # If sending fails, assume the client is dead and disconnect them
                    self.disconnect(community_id, connection)

# Create a singleton instance to be imported elsewhere
manager = ConnectionManager()