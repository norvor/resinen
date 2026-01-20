from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, communities, memberships,  # Core
    social, library, stage,                 # Content Engines
    arena, club, bunker,                    # Interaction Engines
    listing, guild, academy, garden,        # Growth Engines
    upload, engines,
    governance, referral                        # Utilities
)

api_router = APIRouter()

# --- CORE ---
api_router.include_router(referral.router, prefix="/referral", tags=["Referral"]) # <--- ADD THIS
api_router.include_router(governance.router, prefix="/governance", tags=["Engine: Governance"]) # <--- ADD THIS
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(communities.router, prefix="/communities", tags=["Communities"])
api_router.include_router(memberships.router, prefix="/communities", tags=["Memberships"]) # Helper endpoints
api_router.include_router(engines.router, prefix="/engines", tags=["System"])
api_router.include_router(upload.router, prefix="/media", tags=["Utilities"])

# --- CONTENT ENGINES ---
api_router.include_router(social.router, prefix="/social", tags=["Engine: Social"])
api_router.include_router(library.router, prefix="/library", tags=["Engine: Library"])
api_router.include_router(stage.router, prefix="/stage", tags=["Engine: Stage"])

# --- INTERACTION ENGINES ---
api_router.include_router(arena.router, prefix="/arena", tags=["Engine: Arena"])
api_router.include_router(club.router, prefix="/club", tags=["Engine: Club"])
api_router.include_router(bunker.router, prefix="/bunker", tags=["Engine: Bunker"])

# --- GROWTH ENGINES ---
api_router.include_router(listing.router, prefix="/listings", tags=["Engine: Bazaar"])
api_router.include_router(guild.router, prefix="/guild", tags=["Engine: Guild"])
api_router.include_router(academy.router, prefix="/academy", tags=["Engine: Academy"])
api_router.include_router(garden.router, prefix="/garden", tags=["Engine: Garden"])