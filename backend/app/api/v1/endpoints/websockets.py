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
    try:
        # --- DEBUG LOGS ---
        # print(f"🔍 [WS DEBUG] Validating Token: {token[:10]}...") 
        # print(f"🔑 [WS DEBUG] Using Secret: {settings.SECRET_KEY[:5]}***")
        # print(f"🧮 [WS DEBUG] Using Algo: {ALGORITHM}")
        
        # Validate Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            print("❌ [WS Error] Token decoded but no 'sub' (user_id) found.")
            await websocket.close(code=1008)
            return
            
        # print(f"✅ [WS Success] User {user_id} authorized.")

    except JWTError as e:
        # THIS IS THE KEY LINE: It will tell us WHY it failed
        print(f"❌ [WS Auth Failed] Reason: {str(e)}")
        await websocket.close(code=1008)
        return

    # --- Connection Success ---
    await manager.connect(community_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            
            # Construct message
            message_payload = {
                "type": "message",
                "community_id": community_id,
                "user_id": user_id,
                "content": data.get("content"),
                "username": data.get("username", "Unknown"),
                "avatar_url": data.get("avatar_url", "")
            }
            
            await manager.broadcast(community_id, message_payload)

    except WebSocketDisconnect:
        manager.disconnect(community_id, websocket)