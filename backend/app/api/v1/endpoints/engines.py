from typing import List, Any, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, col

from app.api import deps
from app.models.user import User
from app.models.engine import Engine, UserEngine
from pydantic import BaseModel

router = APIRouter()

# --- SCHEMA ---
class EngineRead(BaseModel):
    id: uuid.UUID
    key: str
    name: str
    icon: str
    description: str
    # We default these to False/Empty if the user hasn't touched them yet
    is_pinned: bool = False
    config: dict = {}

# --- ENDPOINTS ---

@router.get("/mine", response_model=List[EngineRead])
async def read_my_engines(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get ALL available engines for the user.
    """
    # 1. Get ALL System Engines (The Arsenal)
    engines_result = await db.exec(select(Engine))
    all_engines = engines_result.all()
    
    # 2. Get User's Personal Configs (Pinned, Settings, etc.)
    # We still check this to see if you pinned something, but we don't use it to filter availability.
    user_configs_result = await db.exec(
        select(UserEngine).where(UserEngine.user_id == current_user.id)
    )
    user_configs = {uc.engine_id: uc for uc in user_configs_result.all()}
    
    # 3. Merge
    result_list = []
    for engine in all_engines:
        # Get personal config if it exists, otherwise defaults
        uc = user_configs.get(engine.id)
        
        result_list.append({
            "id": engine.id,
            "key": engine.key,
            "name": engine.name,
            "icon": engine.icon,
            "description": engine.description,
            "is_pinned": uc.is_pinned if uc else False, # Default unpinned
            "config": uc.config if uc else {}
        })
        
    return result_list

# We keep this if you want to pin/unpin things later
@router.post("/{engine_key}/toggle-pin")
async def toggle_pin_engine(
    engine_key: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # Logic to toggle is_pinned would go here
    pass