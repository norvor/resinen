from fastapi import APIRouter
from app.api.v1.endpoints import communities, auth, chapters, academic, referral, social

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(communities.router, prefix="/communities", tags=["communities"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["chapters"])
api_router.include_router(academic.router, prefix="/academic", tags=["academic"])
api_router.include_router(referral.router, prefix="/referral", tags=["referral"])
api_router.include_router(social.router, prefix="/social", tags=["social"])
# Upload router removed