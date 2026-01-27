# backend/app/routers/saataath.py
from fastapi import APIRouter
from pydantic import BaseModel
from ..saataath_ai import active_game

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
        "phase": active_game.phase,
        # New fields for UI animation (Trick Resolution)
        "last_trick": getattr(active_game, "last_trick", None),
        "last_winner": getattr(active_game, "last_winner", None)
    }

@router.post("/new")
def new_game():
    # Use the reset method to keep the same object instance
    active_game.reset_game()
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
    # 1. Player Move
    success, msg = active_game.play_card(0, req.card_idx)
    if not success: return {"error": msg}
    
    # 2. Bot Response Logic (Auto-Follow)
    # We only auto-play if the bot is FOLLOWING (current_trick has 1 card).
    # If the bot won the trick (current_trick is 0), we WAIT for the frontend 
    # to trigger 'bot-lead' after the animation finishes.
    if active_game.phase == "PLAYING" and active_game.turn == 1 and len(active_game.current_trick) == 1:
        bot_idx = active_game.get_bot_move_idx()
        active_game.play_card(1, bot_idx)
        
    return get_state()

@router.post("/bot-lead")
def bot_lead():
    # This is called by Frontend after the "Trick Result" animation finishes
    # Only acts if it's actually the bot's turn to lead a new trick
    if active_game.phase == "PLAYING" and active_game.turn == 1 and len(active_game.current_trick) == 0:
        bot_idx = active_game.get_bot_move_idx()
        active_game.play_card(1, bot_idx)
    return get_state()