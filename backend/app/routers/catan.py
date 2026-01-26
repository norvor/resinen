# backend/app/routers/catan.py
from fastapi import APIRouter
from ..catan_ai import get_new_map

router = APIRouter(prefix="/games/catan", tags=["games"])

@router.get("/new")
def new_game():
    return {"hexes": get_new_map()}