# backend/app/routers/poker.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..poker_ai import deal_hand, evaluate_winner, bot_decision, Card

router = APIRouter(prefix="/games/poker", tags=["games"])

class PokerState(BaseModel):
    player_hand: List[str]
    bot_hand: List[str]
    board: List[str]
    stage: str # preflop, flop, turn, river, showdown
    pot: int
    player_chips: int
    bot_chips: int
    current_bet: int

@router.get("/deal")
def deal():
    return deal_hand()

@router.post("/bot-move")
def move(state: PokerState):
    # Convert visible board cards based on stage
    visible_count = 0
    if state.stage == "flop": visible_count = 3
    if state.stage == "turn": visible_count = 4
    if state.stage == "river": visible_count = 5
    
    board_ints = [Card.new(c) for c in state.board[:visible_count]]
    bot_hand_ints = [Card.new(c) for c in state.bot_hand]
    
    action = bot_decision(bot_hand_ints, board_ints, state.current_bet, state.bot_chips, state.pot, state.stage)
    return {"action": action}

@router.post("/winner")
def winner(state: PokerState):
    # Reveal all logic
    return evaluate_winner(state.player_hand, state.bot_hand, state.board)