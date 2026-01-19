from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt
from app.core.config import settings
from app.core.security import ALGORITHM
from app.services.socket_manager import manager

router = APIRouter()

@router.websocket("/ws/{community_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    community_id: str,
    token: str = Query(...)
):
    """
    Real-time WebSocket connection for a specific Community.
    Auth: Handled via ?token= query parameter since headers are restricted in WS.
    """
    user_id = None
    
    # --- 1. AUTHENTICATION ---
    # We must manually validate the token here because Dependencies 
    # inside WebSockets can be tricky with connection acceptance.
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            # Code 1008 = Policy Violation (Auth failed)
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return

    # --- 2. CONNECTION ---
    await manager.connect(community_id, websocket)

    # --- 3. EVENT LOOP ---
    try:
        while True:
            # Wait for data from the client
            data = await websocket.receive_json()
            
            # Construct the message payload
            # (In Phase 4, we will also save this to the DB here)
            message_payload = {
                "type": "message",
                "community_id": community_id,
                "user_id": user_id,
                "content": data.get("content"),
                "username": data.get("username", "Unknown"),
                "avatar_url": data.get("avatar_url", "")
            }
            
            # Broadcast to everyone in this world
            await manager.broadcast(community_id, message_payload)

    except WebSocketDisconnect:
        manager.disconnect(community_id, websocket)
        
    except Exception as e:
        print(f"⚠️ [WS Error] {e}")
        manager.disconnect(community_id, websocket)