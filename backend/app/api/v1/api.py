from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, 
    users, 
    communities, 
    chapters, 
    social,
    websockets,
    # The 10 Engines
    listings,   # 1. Bazaar
    governance, # 2. Senate
    academy,    # 3. Academy
    arena,      # 4. Arena
    club,       # 5. Club
    library,    # 6. Library
    stage,      # 7. Stage
    bunker,     # 8. Bunker
    guild,      # 9. Guild
    garden      # 10. Garden
)

api_router = APIRouter()

# --- CORE ---
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(communities.router, prefix="/communities", tags=["communities"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["chapters"])
api_router.include_router(social.router, tags=["social"]) # Default Feed
api_router.include_router(websockets.router, tags=["websockets"])

# --- THE 10 ENGINES ---
api_router.include_router(listings.router, prefix="/listings", tags=["engine-bazaar"])
api_router.include_router(governance.router, prefix="/governance", tags=["engine-senate"])
api_router.include_router(academy.router, prefix="/academy", tags=["engine-academy"])
api_router.include_router(arena.router, prefix="/arena", tags=["engine-arena"])
api_router.include_router(club.router, prefix="/club", tags=["engine-club"])
api_router.include_router(library.router, prefix="/library", tags=["engine-library"])
api_router.include_router(stage.router, prefix="/stage", tags=["engine-stage"])
api_router.include_router(bunker.router, prefix="/bunker", tags=["engine-bunker"])
api_router.include_router(guild.router, prefix="/guild", tags=["engine-guild"])
api_router.include_router(garden.router, prefix="/garden", tags=["engine-garden"])