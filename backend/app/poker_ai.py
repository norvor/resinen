# backend/app/poker_ai.py
from treys import Card, Evaluator, Deck
import random

evaluator = Evaluator()

# --- 1. CARD UTILS ---
def pretty_card(int_card):
    return Card.int_to_str(int_card)

def get_rank_int(int_card):
    return Card.get_rank_int(int_card)

def get_suit_int(int_card):
    return Card.get_suit_int(int_card)

# --- 2. THE BOT BRAIN ---
def bot_decision(bot_hand_ints, community_ints, current_bet, bot_chips, pot_size, stage):
    # If we have no community cards (Pre-flop), play tight-aggressive
    if not community_ints:
        # Simple high card logic
        ranks = [Card.get_rank_int(c) for c in bot_hand_ints]
        high_card = max(ranks)
        if high_card >= 10 or (ranks[0] == ranks[1]): # Pair or high card
            return "call" if current_bet <= bot_chips else "all-in"
        else:
            # Bluff chance
            return "raise" if random.random() < 0.2 else "call" # Passive pre-flop

    # Post-flop: Calculate Hand Strength
    # 0 = Best (Royal Flush), 7462 = Worst
    score = evaluator.evaluate(community_ints, bot_hand_ints)
    percentile = 1.0 - (score / 7462.0) # 1.0 is best, 0.0 is worst

    # Decision Logic based on Hand Strength
    if percent_to_win(percentile) > 0.7:
        return "raise" # Strong hand
    elif percent_to_win(percentile) > 0.4:
        return "call"  # Decent hand
    else:
        # Weak hand - Bluff or Fold?
        if current_bet == 0: return "check"
        return "fold" if random.random() > 0.1 else "call" # 10% bluff call

def percent_to_win(strength):
    # Rough mapping of strength to win probability
    return strength ** 2 # Convex curve

# --- 3. GAME STATE MANAGER (Stateless Helper) ---
# In a real app, we'd use a DB. Here we re-simulate simple states or just evaluate.
def evaluate_winner(player_hand_strs, bot_hand_strs, board_strs):
    # Convert string cards (e.g. "Ah", "Td") back to Integers for Treys
    p_hand = [Card.new(c) for c in player_hand_strs]
    b_hand = [Card.new(c) for c in bot_hand_strs]
    board = [Card.new(c) for c in board_strs]

    p_score = evaluator.evaluate(board, p_hand)
    b_score = evaluator.evaluate(board, b_hand)
    
    p_class = evaluator.get_rank_class(p_score)
    b_class = evaluator.get_rank_class(b_score)

    return {
        "player_score": p_score,
        "bot_score": b_score,
        "player_rank": evaluator.class_to_string(p_class),
        "bot_rank": evaluator.class_to_string(b_class),
        "winner": "player" if p_score < b_score else "bot" if b_score < p_score else "split"
    }

def deal_hand():
    deck = Deck()
    p_hand = deck.draw(2)
    b_hand = deck.draw(2)
    board = deck.draw(5) # We draw all 5 but hide them based on phase
    
    return {
        "player": [Card.int_to_str(c) for c in p_hand],
        "bot": [Card.int_to_str(c) for c in b_hand],
        "board": [Card.int_to_str(c) for c in board]
    }