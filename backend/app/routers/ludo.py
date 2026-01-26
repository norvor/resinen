# backend/app/routers/ludo.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from ..ludo_ai import get_best_move

router = APIRouter(prefix="/games/ludo", tags=["games"])

class LudoState(BaseModel):
    turn: int
    dice: int
    positions: List[List[int]]

@router.post("/bot-move")
def calculate_bot_move(state: LudoState):
    move_idx = get_best_move(state.dict())
    return {"token_idx": move_idx}