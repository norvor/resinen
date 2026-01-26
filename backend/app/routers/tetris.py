# backend/app/routers/tetris.py
from fastapi import APIRouter

router = APIRouter(prefix="/games/tetris", tags=["games"])

@router.get("/config")
def get_config():
    # Return game settings (Speed, Scoring)
    return {
        "gravity_start": 1000, # ms
        "gravity_decay": 0.9,
        "score_line": 100,
        "score_tetris": 800
    }