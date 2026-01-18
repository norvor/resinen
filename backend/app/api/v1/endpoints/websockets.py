from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from app.services.socket_manager import manager
from app.core import security
from app.core.config import settings
from app.core.database import async_session_factory
from app.models.user import User
from jose import jwt, JWTError

router = APIRouter()

# --- Helper: Authenticate via Query Param ---
async def get_user_from_socket(
    token: str = Query(...)
) -> User:
    """
    WebSockets can't easily send Headers, so we read the token from the URL.
    ws://.../ws?token=ey...
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    # Retrieve user from DB (Short lived session)
    async with async_session_factory() as session:
        user = await session.get(User, user_id)
        return user

# --- The Endpoint ---
@router.websocket("/{community_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    community_id: str,
    token: str = Query(...) # Require token in URL
):
    # 1. Authenticate
    user = await get_user_from_socket(token)
    if not user:
        # If invalid, close immediately with Policy Violation code
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Connect to the Room
    await manager.connect(community_id, websocket)

    # 3. Notify others (Optional "User Joined" message)
    await manager.broadcast(community_id, {
        "type": "event",
        "event": "user_joined",
        "user": user.full_name or "Anonymous",
        "avatar": user.avatar_url
    })

    try:
        # 4. Listen Loop (Keep connection open)
        while True:
            data = await websocket.receive_json()
            # Echo the message back to the room (Basic Chat)
            # In the future, we will save this to the DB here.
            await manager.broadcast(community_id, {
                "type": "message",
                "user": user.full_name,
                "avatar": user.avatar_url,
                "content": data.get("content")
            })
            
    except WebSocketDisconnect:
        # 5. Handle Disconnect
        manager.disconnect(community_id, websocket)
        await manager.broadcast(community_id, {
            "type": "event",
            "event": "user_left",
            "user": user.full_name
        })