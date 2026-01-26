# backend/app/routers/saataath.py
from fastapi import APIRouter
from pydantic import BaseModel
from ..saataath_ai import active_game, SaatAathGame

router = APIRouter(prefix="/games/saataath", tags=["games"])

@router.get("/state")
def get_state():
    return {
        "hand": active_game.hands[0],
        "bot_hand_count": len(active_game.hands[1]),
        "trick": active_game.current_trick,
        "tricks_won": active_game.tricks_won,
        "trump": active_game.trump,
        "turn": active_game.turn,
        "phase": active_game.phase
    }

@router.post("/new")
def new_game():
    global active_game
    active_game = SaatAathGame()
    return get_state()

class TrumpRequest(BaseModel):
    suit: str

@router.post("/trump")
def select_trump(req: TrumpRequest):
    active_game.set_trump(req.suit)
    return get_state()

class PlayRequest(BaseModel):
    card_idx: int

@router.post("/play")
def play_card(req: PlayRequest):
    success, msg = active_game.play_card(0, req.card_idx)
    if not success: return {"error": msg}
    
    # If game continues and it's bot's turn, make bot move
    if active_game.phase == "PLAYING" and active_game.turn == 1 and len(active_game.current_trick) < 2:
        bot_idx = active_game.get_bot_move_idx()
        active_game.play_card(1, bot_idx)
        
    return get_state()

@router.post("/bot-lead")
def bot_lead():
    # Helper to kickstart bot if it won previous trick
    if active_game.turn == 1 and len(active_game.current_trick) == 0:
        bot_idx = active_game.get_bot_move_idx()
        active_game.play_card(1, bot_idx)
    return get_state()