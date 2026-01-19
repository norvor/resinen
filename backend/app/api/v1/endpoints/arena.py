import uuid
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api import deps
from app.models.user import User
from app.models.arena import Match, Prediction, Team 
# Assuming standard schemas; if you use specific Read schemas, import them here.

router = APIRouter()

@router.get("/")
async def get_matches(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_active_user),
):
    """
    Get all matches for a community, including the current user's picks.
    """
    # 1. Fetch Matches
    query = select(Match).where(Match.community_id == community_id)
    result = await db.execute(query)
    matches = result.scalars().all()

    # 2. Fetch User Picks (The fix is here)
    user_picks = {}
    if current_user and matches:
        match_ids = [m.id for m in matches]
        user_picks_stmt = select(Prediction).where(
            Prediction.user_id == current_user.id,
            Prediction.match_id.in_(match_ids)
        )
        
        # ✅ FIX: Use await db.execute(...) -> .scalars().all()
        picks_result = await db.execute(user_picks_stmt)
        picks = picks_result.scalars().all()
        
        user_picks = {p.match_id: p.team_id for p in picks} 
        # Note: Ensure property is 'team_id' or 'picked_team_id' based on your model

    # 3. Attach picks to response
    results = []
    for m in matches:
        # We convert to dict to inject the 'my_pick' field easily
        # If using Pydantic schemas, ensure the schema has 'my_pick: Optional[UUID]'
        match_data = m.model_dump() if hasattr(m, 'model_dump') else m.dict()
        match_data['my_pick'] = user_picks.get(m.id)
        results.append(match_data)

    return results

@router.post("/predict")
async def predict_match(
    match_id: uuid.UUID,
    team_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Predict the winner of a match.
    """
    # 1. Check if Match exists
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # 2. Check for existing prediction
    query = select(Prediction).where(
        Prediction.user_id == current_user.id,
        Prediction.match_id == match_id
    )
    result = await db.execute(query)
    existing_prediction = result.scalars().first()

    if existing_prediction:
        # Update existing
        existing_prediction.team_id = team_id
        db.add(existing_prediction)
        await db.commit()
        await db.refresh(existing_prediction)
        return {"status": "updated", "prediction": existing_prediction}

    # 3. Create new prediction
    new_prediction = Prediction(
        user_id=current_user.id,
        match_id=match_id,
        team_id=team_id
    )
    db.add(new_prediction)
    await db.commit()
    await db.refresh(new_prediction)
    
    return {"status": "created", "prediction": new_prediction}