from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import SQLModel, Field, Session, select
from sqlalchemy import Column, JSON
from typing import Optional, Dict, Any, List
from app.database import get_session

# --- 1. THE UNIVERSAL MODEL ---
# This table acts as a Key-Value store for each user.
# It can hold Projects, Habits, Settings, or anything else.
class UserStorage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_email: str = Field(index=True)
    key: str = Field(index=True)  # e.g., "resinen_projects", "resinen_scribble"
    # We use SQLAlchemy's JSON column type to store complex data (lists, objects)
    value: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

router = APIRouter(prefix="/storage", tags=["Cloud Storage"])

# --- 2. THE API ENDPOINTS ---

@router.get("/sync/all")
async def sync_all_data(
    user_email: str, 
    session: Session = Depends(get_session)
):
    """
    Returns ALL data for a user on startup.
    Frontend uses this to hydrate the dashboard instantly.
    """
    statement = select(UserStorage).where(UserStorage.user_email == user_email)
    results = session.exec(statement).all()
    
    # Transform into a simple dictionary: { "key": value, "key2": value }
    synced_data = {}
    for row in results:
        synced_data[row.key] = row.value
        
    return synced_data

@router.post("/{key}")
async def save_data(
    key: str, 
    payload: Dict[str, Any] = Body(...),
    session: Session = Depends(get_session)
):
    """
    Saves a specific widget's state.
    Upsert logic: Updates if exists, Creates if new.
    """
    # In a real app, user_email comes from the JWT Token.
    # For now, we trust the client to send it (as per your request for simplicity).
    user_email = payload.get("user_email")
    data_content = payload.get("data")
    
    if not user_email:
        raise HTTPException(status_code=400, detail="User email required for sync")

    # Check if this key already exists for this user
    statement = select(UserStorage).where(
        UserStorage.user_email == user_email,
        UserStorage.key == key
    )
    result = session.exec(statement).first()

    if result:
        # Update existing record
        result.value = data_content
        session.add(result)
    else:
        # Create new record
        new_entry = UserStorage(user_email=user_email, key=key, value=data_content)
        session.add(new_entry)
    
    session.commit()
    return {"status": "synced", "key": key}

@router.delete("/{key}")
async def clear_data(
    key: str,
    user_email: str,
    session: Session = Depends(get_session)
):
    """Clears a specific key (e.g. resetting habits)"""
    statement = select(UserStorage).where(
        UserStorage.user_email == user_email,
        UserStorage.key == key
    )
    result = session.exec(statement).first()
    
    if result:
        session.delete(result)
        session.commit()
        
    return {"status": "deleted", "key": key}