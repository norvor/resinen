# backend/app/battleship_ai.py
import random

# Board: 10x10
# Ships: 5 (Carrier), 4 (Battleship), 3 (Cruiser), 3 (Sub), 2 (Destroyer)
SHIPS = [5, 4, 3, 3, 2]

def generate_board():
    board = [[0 for _ in range(10)] for _ in range(10)]
    
    for size in SHIPS:
        placed = False
        while not placed:
            # Random orientation: 0=Horizontal, 1=Vertical
            orientation = random.randint(0, 1)
            r = random.randint(0, 9)
            c = random.randint(0, 9)
            
            # Check boundaries
            if orientation == 0 and c + size > 10: continue
            if orientation == 1 and r + size > 10: continue
            
            # Check overlap
            overlap = False
            for i in range(size):
                nr = r + (i if orientation == 1 else 0)
                nc = c + (i if orientation == 0 else 1)
                if board[nr][nc] != 0:
                    overlap = True
                    break
            
            if not overlap:
                # Place ship (mark with ship size for ID, though simplistic)
                for i in range(size):
                    nr = r + (i if orientation == 1 else 0)
                    nc = c + (i if orientation == 0 else 1)
                    board[nr][nc] = 1 # 1 = Ship present
                placed = True
                
    return board

# We need a stateful game session for this to work well (User fire -> Check hit).
# For MVP, we'll return the FULL board but mask it on the frontend, 
# relying on the frontend to be honest (or just "fog of war" it).
# A better way is to send just "Hit/Miss" but that requires persistent storage.
# Let's stick to the "Trust" model for the Resinen Zen.
# Actually, no. Let's make it cheat-proof-ish by keeping state in memory.

active_games = {} # token -> board

def start_new_game(token):
    active_games[token] = generate_board()
    return {"message": "Radar Active"}

def fire_shot(token, r, c):
    if token not in active_games: return {"error": "No Game Found"}
    board = active_games[token]
    
    hit = board[r][c] == 1
    # Check if this sunk a ship? (Complex logic, let's stick to simple Hit/Miss)
    
    return {"hit": hit}