from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import joinedload
import uuid

from app.api import deps
from app.models.user import User
from app.models.arena import ArenaMatch, ArenaTeam, ArenaPrediction, MatchStatus 
# Ensure these schemas exist or adjust imports
from app.schemas.arena import MatchRead, PredictionCreate, ScoreUpdate, TeamRead 

router = APIRouter()

# --- 1. GET SCHEDULE ---
@router.get("/", response_model=List[MatchRead])
async def get_matches(
    community_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    # 1. Fetch Matches
    stmt = select(ArenaMatch).where(ArenaMatch.community_id == community_id).order_by(ArenaMatch.start_time.desc())
    result = await db.execute(stmt)
    matches = result.scalars().all()
    
    # 2. Fetch User's Picks
    match_ids = [m.id for m in matches]
    user_picks = {}
    
    if match_ids:
        user_picks_stmt = select(ArenaPrediction).where(
            ArenaPrediction.user_id == current_user.id,
            ArenaPrediction.match_id.in_(match_ids)
        )
        picks_result = await db.execute(user_picks_stmt)
        picks = picks_result.scalars().all()
        user_picks = {p.match_id: p.picked_team_id for p in picks}

    results = []
    for m in matches:
        # Load Teams
        team_a = await db.get(ArenaTeam, m.team_a_id)
        team_b = await db.get(ArenaTeam, m.team_b_id)
        
        if not team_a or not team_b:
            continue

        # Mock Stats for now
        total = 100 
        pct_a = 60  
        
        m_read = MatchRead(
            id=m.id,
            status=m.status,
            start_time=m.start_time,
            score_a=m.score_a, 
            score_b=m.score_b,
            time_display=m.time_display,
            team_a=TeamRead(**team_a.dict()),
            team_b=TeamRead(**team_b.dict()),
            total_predictions=total,
            pick_pct_a=pct_a,
            pick_pct_b=100-pct_a,
            user_pick_id=user_picks.get(m.id)
        )
        results.append(m_read)
        
    return results

# --- 2. MAKE PREDICTION ---
@router.post("/predict", response_model=Any)
async def make_prediction(
    pred: PredictionCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    # Check Lock
    match = await db.get(ArenaMatch, pred.match_id)
    if not match or match.status != MatchStatus.SCHEDULED:
        raise HTTPException(status_code=400, detail="Match is closed for predictions")

    # Upsert Logic
    query = select(ArenaPrediction).where(
        ArenaPrediction.user_id == current_user.id,
        ArenaPrediction.match_id == pred.match_id
    )
    result = await db.execute(query)
    existing = result.scalars().first()

    if existing:
        existing.picked_team_id = pred.team_id
        db.add(existing)
    else:
        new_pred = ArenaPrediction(
            user_id=current_user.id, 
            match_id=pred.match_id, 
            picked_team_id=pred.team_id
        )
        db.add(new_pred)
    
    await db.commit()
    return {"status": "success"}

# --- 3. ADMIN: UPDATE LIVE SCORE ---
@router.post("/{match_id}/score", response_model=Any)
async def update_score(
    match_id: str,
    update: ScoreUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    match = await db.get(ArenaMatch, match_id)
    if not match:
        raise HTTPException(404, "Match not found")
        
    match.score_a = update.score_a
    match.score_b = update.score_b
    match.status = update.status
    match.time_display = update.time_display
    
    db.add(match)
    await db.commit()
    
    return {"status": "updated"}

@router.get("/{community_id}/matches", response_model=List[ArenaMatch])
async def read_matches(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Fetch all matches for a community.
    Includes the 'teams' relationship so the frontend can display names.
    """
    # 1. Query Matches with Joined Loads for Teams
    query = (
        select(ArenaMatch)
        .where(ArenaMatch.community_id == community_id)
        .options(
            joinedload(ArenaMatch.team_a),
            joinedload(ArenaMatch.team_b)
        )
        .order_by(ArenaMatch.start_time.desc())
    )
    
    result = await db.execute(query)
    matches = result.scalars().all()
    return matches

@router.post("/{community_id}/matches", response_model=ArenaMatch)
async def create_match(
    community_id: uuid.UUID,
    match_in: ArenaMatchCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    match_obj = ArenaMatch.model_validate(match_in, update={"community_id": community_id})
    db.add(match_obj)
    await db.commit()
    await db.refresh(match_obj)
    return match_obj