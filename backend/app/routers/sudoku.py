# backend/app/routers/sudoku.py
from fastapi import APIRouter
from ..sudoku_ai import get_new_sudoku

router = APIRouter(prefix="/games/sudoku", tags=["games"])

@router.get("/new")
def new_game(difficulty: str = "medium"):
    return get_new_sudoku(difficulty)