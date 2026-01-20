import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import joinedload

# 1. Correct Imports
from app.core import deps
from app.models.user import User
from app.models.arena import ArenaMatch, ArenaTeam, ArenaPrediction, MatchStatus
# We use the generic Read/Create schemas to keep it simple and working
from app.schemas.arena import (
    ArenaMatchRead, 
    ArenaMatchCreate, 
    ArenaTeamRead, 
    ArenaTeamCreate,
    ArenaPredictionCreate, # Ensure you have this or generic PredictionCreate
    ArenaScoreUpdate       # Ensure you have this or generic ScoreUpdate
)

router = APIRouter()

# ==========================================
# 1. TEAMS (Dropdowns & Lists)
# ==========================================

@router.get("/{community_id}/teams", response_model=List[ArenaTeamRead])
async def read_teams(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
):
    """Fetch all teams to populate dropdowns."""
    query = select(ArenaTeam).where(ArenaTeam.community_id == community_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{community_id}/teams", response_model=ArenaTeamRead)
async def create_team(
    community_id: uuid.UUID,
    team_in: ArenaTeamCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    team = ArenaTeam.model_validate(team_in, update={"community_id": community_id})
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


# ==========================================
# 2. MATCHES (The Dashboard Core)
# ==========================================

@router.get("/{community_id}/matches", response_model=List[ArenaMatchRead])
async def read_matches(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Fetch matches with Teams joined (High Performance).
    """
    # 1. Fetch Matches with Teams efficiently
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

    # (Optional) You can inject "User Picked" status here later if needed.
    # For now, let's just get the data on the screen.
    return matches


@router.post("/{community_id}/matches", response_model=ArenaMatchRead)
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


# ==========================================
# 3. ACTIONS (Predicting & Scoring)
# ==========================================

@router.post("/predict", response_model=Any)
async def make_prediction(
    pred: ArenaPredictionCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """User locks in a team prediction."""
    # 1. Check if Match is Open
    match = await db.get(ArenaMatch, pred.match_id)
    if not match:
        raise HTTPException(404, "Match not found")
    if match.status != MatchStatus.SCHEDULED:
        raise HTTPException(400, "Match is locked or finished")

    # 2. Check for existing prediction (Update vs Insert)
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
    return {"status": "success", "picked": pred.team_id}


@router.post("/{match_id}/score", response_model=Any)
async def update_score(
    match_id: uuid.UUID,
    update: ArenaScoreUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Admin updates the live score."""
    match = await db.get(ArenaMatch, match_id)
    if not match:
        raise HTTPException(404, "Match not found")
        
    if update.score_a is not None: match.score_a = update.score_a
    if update.score_b is not None: match.score_b = update.score_b
    if update.status is not None: match.status = update.status
    if update.time_display is not None: match.time_display = update.time_display
    
    db.add(match)
    await db.commit()
    
    return {"status": "updated", "match_id": match_id}