# backend/app/routers/battleship.py
from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from ..battleship_ai import start_new_game, fire_shot

router = APIRouter(prefix="/games/battleship", tags=["games"])

@router.post("/new")
def new_game():
    token = str(uuid.uuid4())
    start_new_game(token)
    return {"token": token}

class FireRequest(BaseModel):
    token: str
    r: int
    c: int

@router.post("/fire")
def fire(req: FireRequest):
    return fire_shot(req.token, req.r, req.c)