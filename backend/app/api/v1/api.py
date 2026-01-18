from fastapi import APIRouter
from app.api.v1.endpoints import (
    communities, 
    auth, 
    chapters, 
    academic, 
    referral, 
    social, 
    content,
    users # <--- IMPORT THIS
)

api_router = APIRouter()

# --- AUTHENTICATION ---
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"]) # <--- ADD THIS LINE

# --- CORE MODULES ---
api_router.include_router(communities.router, prefix="/communities", tags=["communities"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["chapters"])

# --- ENGINES ---
api_router.include_router(academic.router, prefix="/academic", tags=["academic"])
api_router.include_router(referral.router, prefix="/referral", tags=["referral"])
api_router.include_router(social.router, prefix="/social", tags=["social"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(social.router, prefix="/posts", tags=["social"])
api_router.include_router(social.router, prefix="/feed", tags=["social"])