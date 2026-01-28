# backend/app/routers/cricket.py
from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter(prefix="/games/cricket", tags=["games"])

class BowlRequest(BaseModel):
    difficulty: str = "normal"

class HitRequest(BaseModel):
    timing_score: int # 0 (Miss) to 100 (Perfect Middle)
    shot_type: str    # "defend", "loft", "drive"
    ball_type: str    # "fast", "spin", "yorker"

@router.post("/get-delivery")
def get_delivery(req: BowlRequest):
    # The bowler decides what to throw
    balls = [
        {"type": "fast", "speed_ms": 600, "swing": 0, "msg": "Fast ball incoming!"},
        {"type": "spin", "speed_ms": 900, "swing": 20, "msg": "Leg spinner..."},
        {"type": "yorker", "speed_ms": 500, "swing": 5, "msg": "YORKER!"},
        {"type": "bouncer", "speed_ms": 550, "swing": 0, "msg": "Bouncer! Duck or Hook!"},
    ]
    # Increase difficulty by picking harder balls
    delivery = random.choice(balls)
    return delivery

@router.post("/calculate-shot")
def calculate_shot(req: HitRequest):
    # 1. Base Probability based on Timing (0-100)
    score = 0
    comment = ""
    is_out = False
    outcome_type = "dot" # dot, run, boundary, wicket

    # Luck factor (pitch conditions)
    luck = random.randint(-5, 5)
    final_score = req.timing_score + luck

    if final_score < 20:
        # COMPLETE MISS / EDGE
        is_out = True
        outcome_type = "wicket"
        comment = random.choice(["CLEAN BOWLED!", "Edged and Taken!", "Stumps are flying!"])
    elif final_score < 50:
        # POOR CONTACT
        score = 0
        outcome_type = "dot"
        comment = "Swung and missed." if req.shot_type == "loft" else "Straight to the fielder."
    elif final_score < 80:
        # DECENT CONTACT
        if req.shot_type == "loft":
            is_out = True # Caught in the deep
            outcome_type = "wicket"
            comment = "Caught at Long On!"
        else:
            score = random.choice([1, 2])
            outcome_type = "run"
            comment = "Quick single." if score == 1 else "Good running, two runs."
    else:
        # PERFECT CONTACT (>80)
        if req.shot_type == "loft":
            score = 6
            outcome_type = "boundary"
            comment = "HUGE SIX! IT'S OUT OF THE PARK!"
        elif req.shot_type == "defend":
            score = 0
            outcome_type = "dot"
            comment = "Solid defense."
        else: # Drive
            score = 4
            outcome_type = "boundary"
            comment = "Glorious cover drive for 4!"

    return {
        "runs": score,
        "is_out": is_out,
        "comment": comment,
        "outcome": outcome_type
    }