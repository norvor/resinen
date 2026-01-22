from typing import List, Any
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.api import deps
from app.models.user import User
from app.models.engine import Engine, UserEngine
from pydantic import BaseModel

router = APIRouter()

# --- SCHEMA ---
class InstalledEngineRead(BaseModel):
    id: uuid.UUID
    key: str
    name: str
    icon: str
    description: str
    
    # User specific settings
    is_pinned: bool
    config: dict

# --- ENDPOINTS ---

@router.get("/mine", response_model=List[InstalledEngineRead])
async def read_my_engines(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get the list of engines installed by the current user.
    """
    # Join Engine and UserEngine tables
    query = (
        select(Engine, UserEngine)
        .join(UserEngine, Engine.id == UserEngine.engine_id)
        .where(UserEngine.user_id == current_user.id)
        .where(UserEngine.is_active == True)
        .order_by(Engine.name)
    )
    
    results = await db.exec(query)
    
    # Format the response
    installed_apps = []
    for engine, install in results.all():
        installed_apps.append({
            "id": engine.id,
            "key": engine.key,
            "name": engine.name,
            "icon": engine.icon,
            "description": engine.description,
            "is_pinned": install.is_pinned,
            "config": install.config
        })
        
    return installed_apps

@router.post("/{engine_key}/install")
async def install_engine(
    engine_key: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    'App Store' logic: Install an engine by key (e.g., 'vault').
    """
    # 1. Find the Engine
    res = await db.exec(select(Engine).where(Engine.key == engine_key))
    engine = res.first()
    if not engine:
        raise HTTPException(404, "Engine not found in the system registry")
        
    # 2. Check if already installed
    stmt = select(UserEngine).where(
        UserEngine.user_id == current_user.id,
        UserEngine.engine_id == engine.id
    )
    existing = await db.exec(stmt)
    if existing.first():
        return {"status": "already_installed"}

    # 3. Install
    install = UserEngine(
        user_id=current_user.id,
        engine_id=engine.id,
        is_active=True,
        is_pinned=True,
        config={}
    )
    db.add(install)
    await db.commit()
    
    return {"status": "installed", "engine": engine.name}