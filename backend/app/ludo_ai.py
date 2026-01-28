# backend/app/ludo_ai.py
import random

# Ludo Board Constants
PATH_LENGTH = 52
HOME_STRETCH_START = 52
FINISH_POS = 57
# Standard Safe Spots (Stars) on the absolute board (0-51)
SAFE_SPOTS = [0, 8, 13, 21, 26, 34, 39, 47]
# Starting offsets for players 0, 1, 2, 3
PLAYER_OFFSETS = [0, 13, 26, 39]

def get_absolute_pos(player_idx, relative_pos):
    """
    Converts a player's relative position (0-51) to the absolute board index (0-51).
    Returns None if the player is in Base (-1) or Home Stretch (>51).
    """
    if relative_pos == -1 or relative_pos >= 52:
        return None
    
    offset = PLAYER_OFFSETS[player_idx]
    return (relative_pos + offset) % 52

def get_best_move(state):
    # state = { "turn": 0-3, "dice": 1-6, "positions": [[p0_tokens...], [p1_tokens...], ...] }
    # -1 = Base, 0-51 = Main Track, 52-57 = Home Stretch, 99 = Finished
    
    player_idx = state['turn']
    roll = state['dice']
    all_positions = state['positions']
    my_tokens = all_positions[player_idx]
    
    possible_moves = []
    
    for i, pos in enumerate(my_tokens):
        if pos == 99: continue # Finished
        
        # Rule: Need 6 to leave base
        if pos == -1:
            if roll == 6: 
                # Leaving base is a very strong move
                possible_moves.append({"idx": i, "score": 100})
            continue
            
        # Rule: Calculate new relative position
        new_pos = pos + roll
        
        # Rule: Can't move if it overshoots the finish line (57)
        if new_pos > FINISH_POS: continue 
        
        # --- Heuristics Scoring ---
        score = 1 + new_pos  # Base score: further is better
        
        # 1. Capture Logic (Eating Goti)
        # We need to check if this move lands on an opponent
        move_abs_pos = get_absolute_pos(player_idx, new_pos)
        
        if move_abs_pos is not None:
            # Check collision with ALL other players
            collision_detected = False
            for opp_idx, opp_tokens in enumerate(all_positions):
                if opp_idx == player_idx: continue # Skip self
                
                for opp_pos in opp_tokens:
                    opp_abs_pos = get_absolute_pos(opp_idx, opp_pos)
                    
                    if opp_abs_pos is not None and move_abs_pos == opp_abs_pos:
                        # Collision found! Check if it's a Safe Spot
                        if move_abs_pos not in SAFE_SPOTS:
                            score += 500  # HUGE bonus for eating a goti
                            collision_detected = True
                        else:
                            # Landing on safe spot with opponent is fine, but not a kill
                            pass 
            
            # Safe Spot Bonus (Stars)
            if move_abs_pos in SAFE_SPOTS:
                score += 20

        # 2. Enter Home Stretch
        # If we were on the main track (<=51) and now we are in home stretch (>51)
        if pos <= 51 and new_pos > 51:
            score += 50 # Priority: Enter safety
        
        # 3. Progress in Home Stretch
        if new_pos > 51:
            score += 10 * (new_pos - 51) # Reward moving deeper into home
            
        # 4. Finish
        if new_pos == FINISH_POS:
            score += 1000 # Max Priority: Win the game
            
        possible_moves.append({"idx": i, "score": score})
    
    if not possible_moves:
        return None
        
    # Sort by score desc to pick the best move
    possible_moves.sort(key=lambda x: x['score'], reverse=True)
    
    # Return the index of the token to move
    return possible_moves[0]['idx']