from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter(prefix="/games/cricket", tags=["games"])

class CricketMove(BaseModel):
    user_choice: int  # 1-6

@router.post("/bowl")
def bowl(move: CricketMove):
    # Hand Cricket Logic:
    # Bot picks a number 1-6.
    # If Match -> OUT.
    # If No Match -> Add to score.
    bot_choice = random.randint(1, 6)
    
    is_out = (move.user_choice == bot_choice)
    runs = 0 if is_out else move.user_choice
    
    # Commentary
    comments = ["Nice shot!", "Huge six!", "Good defense.", "Caught!", "Clean bowled!"]
    comment = random.choice(comments) if not is_out else "WICKET!"
    
    return {
        "bot_choice": bot_choice,
        "is_out": is_out,
        "runs": runs,
        "comment": comment
    }