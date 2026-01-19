from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.user import User
from app.models.arena import ArenaMatch, ArenaTeam, ArenaPrediction, MatchStatus
from app.schemas.arena import MatchRead, PredictionCreate, ScoreUpdate, MatchCreate, TeamRead
from app.api.deps import get_current_user

router = APIRouter()

# --- 1. GET SCHEDULE (With Prediction Stats) ---
@router.get("/", response_model=List[MatchRead])
async def get_matches(
    community_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Fetch Matches
    stmt = select(ArenaMatch).where(ArenaMatch.community_id == community_id).order_by(ArenaMatch.start_time.desc())
    matches = (await db.exec(stmt)).all()
    
    # Fetch User's Picks
    user_picks_stmt = select(ArenaPrediction).where(
        ArenaPrediction.user_id == current_user.id,
        ArenaPrediction.match_id.in_([m.id for m in matches])
    )
    user_picks = {p.match_id: p.picked_team_id for p in (await db.exec(user_picks_stmt)).all()}

    results = []
    for m in matches:
        # Load Teams manually (assuming simple relationship load for now)
        # Note: In production, use joinedload(ArenaMatch.team_a)
        team_a = await db.get(ArenaTeam, m.team_a_id)
        team_b = await db.get(ArenaTeam, m.team_b_id)
        
        # Calc Stats (Naive count for MVP)
        # "SELECT count(*) FROM predictions WHERE match_id = X AND picked_team = A"
        # We'll skip the heavy SQL query here and assume cached or leave 0 for now
        total = 100 # Mock for UI
        pct_a = 60  # Mock for UI
        
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Check Lock
    match = await db.get(ArenaMatch, pred.match_id)
    if not match or match.status != MatchStatus.SCHEDULED:
        raise HTTPException(status_code=400, detail="Match is closed for predictions")

    # Upsert (Change vote if exists)
    existing = await db.get(ArenaPrediction, (current_user.id, pred.match_id))
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
    current_user: User = Depends(get_current_user), # Needs is_admin check later
    db: Session = Depends(get_session)
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
    
    # TODO: In the future, emit WebSocket event here!
    
    return {"status": "updated"}