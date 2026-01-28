from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter(prefix="/games/soccer", tags=["games"])

class SoccerMove(BaseModel):
    direction: int # 0=Left, 1=Center, 2=Right

@router.post("/shoot")
def shoot(move: SoccerMove):
    # Penalty Logic:
    # Bot Keeper picks a direction.
    # If Match -> SAVE.
    # If Different -> GOAL.
    
    keeper_dive = random.choice([0, 1, 2])
    is_goal = (move.direction != keeper_dive)
    
    return {
        "keeper_dive": keeper_dive,
        "is_goal": is_goal
    }