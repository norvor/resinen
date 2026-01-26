# backend/app/ludo_ai.py
import random

# Ludo Board Constants
PATH_LENGTH = 52
HOME_STRETCH = 6

def get_best_move(state):
    # state = { "turn": 0-3, "dice": 1-6, "positions": [[-1, 0, 5, -1], [...], ...] }
    # -1 = Base, 0-51 = Main Track, 52-57 = Home Stretch, 99 = Finished
    
    player_idx = state['turn']
    roll = state['dice']
    tokens = state['positions'][player_idx]
    
    possible_moves = []
    
    for i, pos in enumerate(tokens):
        if pos == 99: continue # Finished
        
        # Rule: Need 6 to leave base
        if pos == -1:
            if roll == 6: possible_moves.append({"idx": i, "score": 10})
            continue
            
        # Rule: Check if move is valid (overshooting home)
        new_pos = pos + roll
        if new_pos > 57: continue # Can't move
        
        # Scored Heuristics
        score = 1
        
        # 1. Capture Logic (Simplified: We don't have full board state of others here for brevity, 
        # but in a full implementation we would check collision).
        # We will assume moving forward is generally good.
        
        # 2. Enter Home
        if new_pos > 51: score += 5
        
        # 3. Finish
        if new_pos == 57: score += 20
        
        # 4. Safe Spots (Stars) - usually indices 0, 8, 13, etc.
        if new_pos in [0, 8, 13, 21, 26, 34, 39, 47]: score += 2
        
        possible_moves.append({"idx": i, "score": score})
    
    if not possible_moves:
        return None
        
    # Sort by score desc
    possible_moves.sort(key=lambda x: x['score'], reverse=True)
    return possible_moves[0]['idx']