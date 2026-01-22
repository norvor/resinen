from fastapi import APIRouter
from app.api.v1.endpoints import journal

api_router = APIRouter()
api_router.include_router(journal.router, prefix="/journal", tags=["Journal"])
# Add other engines here later (vault, brain, etc.)