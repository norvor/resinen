# backend/app/routers/chess.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..chess_ai import get_best_move

router = APIRouter(prefix="/games/chess", tags=["games"])

class ChessMoveRequest(BaseModel):
    fen: str
    difficulty: int = 3

@router.post("/move")
async def calculate_move(req: ChessMoveRequest):
    try:
        # Determine depth based on difficulty
        depth = min(max(req.difficulty, 1), 4) # Cap at 4 for performance
        best_move_uci = get_best_move(req.fen, depth)
        
        if not best_move_uci:
            return {"move": None, "game_over": True}
            
        return {"move": best_move_uci}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))