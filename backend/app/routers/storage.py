from fastapi import APIRouter, Depends, Body
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from app.database import get_session
from app.models import UserStorage

router = APIRouter(prefix="/storage", tags=["User Storage"])

@router.get("/sync/all")
async def sync_all_data(
    user_email: str, 
    session: AsyncSession = Depends(get_session)
):
    """Get ALL widget data for a user to hydrate the dashboard"""
    statement = select(UserStorage).where(UserStorage.user_email == user_email)
    result = await session.exec(statement)
    results = result.all()
    
    # Convert DB rows to a single JSON object: { "resinen_projects": {...}, ... }
    synced_data = {}
    for row in results:
        synced_data[row.key] = row.value
    return synced_data

@router.post("/{key}")
async def save_data(
    key: str, 
    payload: Dict[str, Any] = Body(...), 
    session: AsyncSession = Depends(get_session)
):
    """Save/Update a specific widget"""
    user_email = payload.get("user_email")
    data_content = payload.get("data")
    
    if not user_email:
        user_email = "default_user" # Fallback

    # Upsert Logic (Update if exists, Insert if new)
    statement = select(UserStorage).where(
        UserStorage.user_email == user_email,
        UserStorage.key == key
    )
    result = await session.exec(statement)
    entry = result.first()

    if entry:
        entry.value = data_content
        session.add(entry)
    else:
        new_entry = UserStorage(user_email=user_email, key=key, value=data_content)
        session.add(new_entry)
    
    await session.commit()
    return {"status": "saved", "key": key}