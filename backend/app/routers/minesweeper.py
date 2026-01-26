# backend/app/routers/minesweeper.py
from fastapi import APIRouter
from ..minesweeper_ai import get_new_minefield

router = APIRouter(prefix="/games/minesweeper", tags=["games"])

@router.get("/new")
def new_game(difficulty: str = "medium"):
    return {"board": get_new_minefield(difficulty)}