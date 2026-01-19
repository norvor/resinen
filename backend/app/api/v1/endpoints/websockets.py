import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, ExpiredSignatureError, jwt
from app.core.config import settings
from app.core.security import ALGORITHM
from app.services.socket_manager import manager

# --- 1. SETUP LOGGING ---
# This creates a logger specifically for WebSockets that will print to your console/pm2 logs
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)

router = APIRouter()

@router.websocket("/ws/{community_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    community_id: str,
    token: str = Query(...)
):
    """
    Robust WebSocket endpoint with detailed Auth debugging.
    """
    
    # --- 2. LOG CONNECTION ATTEMPT ---
    # We log the first 10 chars of the token to ensure it's being received correctly
    masked_token = f"{token[:10]}..." if token else "None"
    logger.info(f"🔌 [WS START] Connection attempt for Community: {community_id}")
    logger.info(f"🔑 [WS AUTH] Received Token: {masked_token}")

    user_id = None

    # --- 3. ROBUST AUTHENTICATION ---
    try:
        # A. Verify Key Integrity (Optional Debugging)
        # This helps check if the server restarted and changed the random key
        key_fingerprint = settings.SECRET_KEY[:5]
        logger.info(f"🛡️ [WS AUTH] Validating against System Key starting with: {key_fingerprint}***")

        # B. Decode Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            logger.error("❌ [WS AUTH FAIL] Token decoded successfully, but 'sub' (User ID) is missing.")
            await websocket.close(code=1008, reason="Invalid Token Payload")
            return
        
        logger.info(f"✅ [WS AUTH SUCCESS] User Authorized: {user_id}")

    except ExpiredSignatureError:
        logger.warning("❌ [WS AUTH FAIL] Token has EXPIRED. User needs to refresh login.")
        await websocket.close(code=1008, reason="Token Expired")
        return
        
    except JWTError as e:
        logger.error(f"❌ [WS AUTH FAIL] JWT Decoding Error: {str(e)}")
        await websocket.close(code=1008, reason="Invalid Token")
        return
        
    except Exception as e:
        logger.error(f"❌ [WS CRITICAL] Unexpected Auth Error: {str(e)}")
        await websocket.close(code=1011) # Internal Error
        return

    # --- 4. ACCEPT CONNECTION ---
    await manager.connect(community_id, websocket)

    # --- 5. EVENT LOOP ---
    try:
        while True:
            # Wait for data
            data = await websocket.receive_json()
            
            # Construct standard message payload
            message_payload = {
                "type": "message",
                "community_id": community_id,
                "user_id": user_id,
                "content": data.get("content"),
                "username": data.get("username", "Unknown"),
                "avatar_url": data.get("avatar_url", "")
            }
            
            # Broadcast
            await manager.broadcast(community_id, message_payload)

    except WebSocketDisconnect:
        logger.info(f"👋 [WS DISCONNECT] User {user_id} left Community {community_id}")
        manager.disconnect(community_id, websocket)
        
    except Exception as e:
        logger.error(f"⚠️ [WS LOOP ERROR] Connection dropped: {str(e)}")
        manager.disconnect(community_id, websocket)