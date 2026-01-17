from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.api import deps
from app.models.engine import Engine, CommunityEngine
from app.models.community import Community

router = APIRouter()

# 1. GET /engines (The "App Store" List)
@router.get("/", response_model=List[Engine])
async def list_available_engines(
    db: any = Depends(deps.get_db)
):
    # Returns the "Menu" of features you offer
    result = await db.execute(select(Engine))
    return result.scalars().all()

# 2. POST /engines/install (The "Install" Button)
@router.post("/install/{community_id}/{engine_key}")
async def install_engine(
    community_id: str,
    engine_key: str,
    db: any = Depends(deps.get_db),
    current_user: any = Depends(deps.get_current_active_user)
):
    # 1. Get the Engine
    engine_query = await db.execute(select(Engine).where(Engine.key == engine_key))
    engine = engine_query.scalars().first()
    if not engine:
        raise HTTPException(404, "Engine not found")

    # 2. Check if already installed
    link_query = await db.execute(
        select(CommunityEngine)
        .where(CommunityEngine.community_id == community_id)
        .where(CommunityEngine.engine_id == engine.id)
    )
    existing = link_query.scalars().first()
    
    if existing:
        existing.is_active = True # Re-activate if disabled
        db.add(existing)
    else:
        # Create new installation
        link = CommunityEngine(community_id=community_id, engine_id=engine.id)
        db.add(link)
    
    await db.commit()
    return {"status": "installed", "engine": engine.name}