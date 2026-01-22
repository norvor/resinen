from fastapi import APIRouter
from app.api.v1.endpoints import journal, auth, users, engines # <--- Import engines

api_router = APIRouter()

# Auth Router (The Gatekeeper)
api_router.include_router(auth.router, prefix="/auth", tags=["login"])

# Engine Routers (The Arsenal)
api_router.include_router(journal.router, prefix="/journal", tags=["Journal"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(engines.router, prefix="/engines", tags=["Engines"])