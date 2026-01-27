from fastapi import APIRouter, HTTPException
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
        "last_trick": getattr(active_game, "last_trick", None),
        "last_winner": getattr(active_game, "last_winner", None)
    }

@router.post("/new")
def new_game():
    active_game.reset_game()
    return get_state()

class TrumpRequest(BaseModel):
    suit: str

@router.post("/trump")
def select_trump(req: TrumpRequest):
    active_game.set_trump(req.suit)
    return get_state()

class PlayRequest(BaseModel):
    card: str

@router.post("/play")
def play_card(req: PlayRequest):
    try:
        # 1. Player Move
        success, msg = active_game.play_card(0, req.card)
        if not success: return {"error": msg}
        
        # 2. Bot Response (Auto-Follow)
        # Only auto-play if bot needs to follow suit immediately
        if active_game.phase == "PLAYING" and active_game.turn == 1 and len(active_game.current_trick) == 1:
            bot_card = active_game.get_bot_move_card()
            if bot_card:
                active_game.play_card(1, bot_card)
            
        return get_state()
    except Exception as e:
        print(f"SERVER ERROR IN PLAY: {e}")
        return {"error": "Server Error - Game State Preserved"}

@router.post("/bot-lead")
def bot_lead():
    try:
        # Helper for frontend to trigger bot lead after animation
        if active_game.phase == "PLAYING" and active_game.turn == 1 and len(active_game.current_trick) == 0:
            bot_card = active_game.get_bot_move_card()
            if bot_card:
                active_game.play_card(1, bot_card)
        return get_state()
    except Exception as e:
        print(f"SERVER ERROR IN BOT LEAD: {e}")
        return get_state()