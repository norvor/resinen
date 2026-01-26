# backend/app/go_ai.py
import random
import copy

# 0 = Empty, 1 = Black (Player), 2 = White (Bot)
SIZE = 9

class GoBoard:
    def __init__(self, board=None):
        self.board = board if board else [[0]*SIZE for _ in range(SIZE)]

    def get_liberties(self, r, c, color):
        # Flood fill to find the group and its liberties
        stack = [(r, c)]
        visited = set()
        visited.add((r, c))
        liberties = set()
        group = set()
        group.add((r, c))
        
        while stack:
            curr_r, curr_c = stack.pop()
            
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < SIZE and 0 <= nc < SIZE:
                    if self.board[nr][nc] == 0:
                        liberties.add((nr, nc))
                    elif self.board[nr][nc] == color and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        group.add((nr, nc))
                        stack.append((nr, nc))
        
        return liberties, group

    def make_move(self, r, c, color):
        # 1. Place stone
        self.board[r][c] = color
        opponent = 1 if color == 2 else 2
        captured = []

        # 2. Check for captures of opponent
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE and self.board[nr][nc] == opponent:
                libs, group = self.get_liberties(nr, nc, opponent)
                if len(libs) == 0:
                    captured.extend(list(group))

        # 3. Remove captured stones
        for cr, cc in captured:
            self.board[cr][cc] = 0

        # 4. Check suicide (if no liberties and no captures made)
        libs, _ = self.get_liberties(r, c, color)
        if len(libs) == 0 and len(captured) == 0:
            self.board[r][c] = 0 # Undo
            return False, []

        return True, captured

def get_bot_move(board_state):
    # board_state is List[List[int]]
    game = GoBoard(board_state)
    
    # 1. Try to capture
    possible_moves = []
    for r in range(SIZE):
        for c in range(SIZE):
            if game.board[r][c] == 0:
                # Simulate move
                test_game = GoBoard(copy.deepcopy(game.board))
                valid, captured = test_game.make_move(r, c, 2) # Bot is 2
                if valid:
                    score = len(captured) * 10
                    # Heuristic: Prefer center/corners slightly
                    if 2 <= r <= 6 and 2 <= c <= 6: score += 1
                    possible_moves.append({"r": r, "c": c, "score": score})
    
    if not possible_moves: return None
    
    # Sort by best score
    possible_moves.sort(key=lambda x: x['score'], reverse=True)
    
    # Pick one of the best (add randomness to avoid loops)
    best_score = possible_moves[0]['score']
    candidates = [m for m in possible_moves if m['score'] == best_score]
    choice = random.choice(candidates)
    
    return {"r": choice['r'], "c": choice['c']}