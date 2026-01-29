# backend/app/battleship_ai.py
import random

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
                # FIX: Changed `else 1` to `else 0`
                nc = c + (i if orientation == 0 else 0) 
                
                # Check for existing ship
                if board[nr][nc] != 0:
                    overlap = True
                    break
            
            if not overlap:
                # Place ship
                for i in range(size):
                    nr = r + (i if orientation == 1 else 0)
                    # FIX: Changed `else 1` to `else 0`
                    nc = c + (i if orientation == 0 else 0)
                    board[nr][nc] = 1 # 1 = Ship present
                placed = True
                
    return board

active_games = {} # token -> board

def start_new_game(token):
    active_games[token] = generate_board()
    return {"message": "Radar Active"}

def fire_shot(token, r, c):
    if token not in active_games: return {"error": "No Game Found"}
    board = active_games[token]
    
    # Safe check in case of bad input
    if not (0 <= r < 10 and 0 <= c < 10):
        return {"error": "Coordinates out of bounds"}

    hit = board[r][c] == 1
    return {"hit": hit}