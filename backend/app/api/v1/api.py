from fastapi import APIRouter
from app.api.v1.endpoints import communities, auth  # <--- Import auth

api_router = APIRouter()

# Add this line:
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

api_router.include_router(communities.router, prefix="/communities", tags=["communities"])