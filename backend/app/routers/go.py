# backend/app/routers/go.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from ..go_ai import GoBoard, get_bot_move

router = APIRouter(prefix="/games/go", tags=["games"])

class GoState(BaseModel):
    board: List[List[int]]
    row: int
    col: int

@router.post("/move")
def player_move(state: GoState):
    game = GoBoard(state.board)
    valid, captured = game.make_move(state.row, state.col, 1) # Player is 1 (Black/Cyan)
    
    if not valid:
        return {"valid": False}
        
    # If valid, Bot responds
    bot_move = get_bot_move(game.board)
    bot_captured = []
    
    if bot_move:
        _, bot_captured = game.make_move(bot_move['r'], bot_move['c'], 2) # Bot is 2 (White/Yellow)
    
    return {
        "valid": True,
        "board": game.board,
        "captured_by_player": len(captured),
        "captured_by_bot": len(bot_captured),
        "bot_move": bot_move
    }