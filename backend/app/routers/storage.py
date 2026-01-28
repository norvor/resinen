from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, JSON
from typing import Dict, Any
from app.database import get_session
from app.models import UserStorage

router = APIRouter(prefix="/storage", tags=["Cloud Storage"])

@router.get("/sync/all")
async def sync_all_data(
    user_email: str, 
    session: AsyncSession = Depends(get_session)
):
    # Async select
    statement = select(UserStorage).where(UserStorage.user_email == user_email)
    result = await session.exec(statement)
    results = result.all()
    
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
    user_email = payload.get("user_email")
    data_content = payload.get("data")
    
    if not user_email:
        user_email = "default_user" 

    # Async select
    statement = select(UserStorage).where(
        UserStorage.user_email == user_email,
        UserStorage.key == key
    )
    result = await session.exec(statement)
    entry = result.first()

    if entry:
        entry.value = data_content # Update
        session.add(entry)
    else:
        new_entry = UserStorage(user_email=user_email, key=key, value=data_content)
        session.add(new_entry)
    
    await session.commit()
    return {"status": "saved", "key": key}