# --- THE VAULT (NEW) ---
from fastapi import APIRouter
from app.api.v1.endpoints import (
    communities, 
    auth, 
    chapters, 
    social, 
    users,
    websockets,
    media # 👈 NEW: Import the Media module
    # academic,  <-- COMMENTED OUT (Ghost)
    # referral,  <-- COMMENTED OUT (Ghost)
    # content    <-- COMMENTED OUT (Ghost)
)

api_router = APIRouter()

# --- AUTHENTICATION ---
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# --- CORE MODULES ---
api_router.include_router(communities.router, prefix="/communities", tags=["communities"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["chapters"])

# --- ENGINES ---
api_router.include_router(social.router, tags=["social"])
# api_router.include_router(academic.router, prefix="/academic", tags=["academic"]) <-- DISABLED
# api_router.include_router(referral.router, prefix="/referral", tags=["referral"]) <-- DISABLED
# api_router.include_router(content.router, prefix="/content", tags=["content"])   <-- DISABLED

api_router.include_router(websockets.router, tags=["websockets"])

# --- THE VAULT (NEW) ---
api_router.include_router(media.router, prefix="/media", tags=["media"]) # 👈 PLUGGED IN # 👈 PLUGGED IN