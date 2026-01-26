# backend/app/minesweeper_ai.py
import random

# CONFIG
# Easy: 9x9, 10 mines
# Medium: 16x16, 40 mines
# Hard: 24x20, 99 mines

def generate_board(rows=16, cols=16, mines=40):
    # 1. Init Empty Board
    board = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # 2. Place Mines (-1)
    mines_placed = 0
    while mines_placed < mines:
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)
        if board[r][c] != -1:
            board[r][c] = -1
            mines_placed += 1
            
    # 3. Calculate Numbers
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == -1: continue
            
            # Count neighbors
            count = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0: continue
                    nr, nc = r + i, c + j
                    if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == -1:
                        count += 1
            board[r][c] = count
            
    return board

def get_new_minefield(difficulty="medium"):
    if difficulty == "easy": return generate_board(9, 9, 10)
    if difficulty == "hard": return generate_board(20, 24, 99) # Fits wide screen better
    return generate_board(16, 16, 40) # Medium