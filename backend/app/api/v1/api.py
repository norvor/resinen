from fastapi import APIRouter
from app.api.v1.endpoints import communities, auth, chapters, academic # <--- Import academic

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(communities.router, prefix="/communities", tags=["communities"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["chapters"])
api_router.include_router(academic.router, prefix="/academic", tags=["academic"]) # <--- Add this