# backend/app/chess_ai.py
import chess
import random

# --- 1. KNOWLEDGE BASE (Piece-Square Tables) ---
# Scores: Positive is good for White, Negative is good for Black (from White's perspective)
# We flip these for black calculation dynamically.

PST = {
    chess.PAWN: [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ],
    chess.KNIGHT: [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ],
    chess.BISHOP: [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ],
    chess.ROOK: [
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ],
    chess.QUEEN: [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ],
    chess.KING: [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    ]
}

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# --- 2. THE EVALUATOR ---
def evaluate_board(board):
    if board.is_checkmate():
        if board.turn: return -9999 # Black wins (White turn, checkmate)
        else: return 9999 # White wins
    if board.is_stalemate() or board.is_insufficient_material(): return 0

    score = 0
    # Evaluate material & position
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece: continue
        
        # Base value
        value = PIECE_VALUES[piece.piece_type] + PST[piece.piece_type][square if piece.color == chess.WHITE else chess.square_mirror(square)]
        
        if piece.color == chess.WHITE: score += value
        else: score -= value
        
    return score

# --- 3. THE SEARCH (Minimax + Alpha-Beta) ---
def get_best_move(fen, depth=3):
    board = chess.Board(fen)
    
    best_move = None
    best_value = -99999
    alpha = -100000
    beta = 100000
    
    # We assume AI is BLACK (Minimizing player logic, but we maximize the negative for simplicity)
    # Actually, let's keep it simple: Engine always tries to maximize ITS score.
    # If Engine is Black, it wants Negative Score. If White, Positive.
    # Standard Minimax implementation:
    
    is_maximizing = board.turn == chess.WHITE
    
    # Root Call
    moves = list(board.legal_moves)
    # Sort captures first for better pruning (simple heuristic)
    # moves.sort(key=lambda m: board.is_capture(m), reverse=True) 
    
    if not moves: return None

    # Iterative Search
    for move in moves:
        board.push(move)
        board_val = minimax(board, depth - 1, alpha, beta, not is_maximizing)
        board.pop()
        
        if is_maximizing:
            if board_val > best_value:
                best_value = board_val
                best_move = move
            alpha = max(alpha, board_val)
        else:
            # If playing Black, we look for the LOWEST score
            if best_move is None: # First move init
                best_value = board_val
                best_move = move
            elif board_val < best_value:
                best_value = board_val
                best_move = move
            beta = min(beta, board_val)
            
    return best_move.uci()

def minimax(board, depth, alpha, beta, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    moves = list(board.legal_moves)
    
    if is_maximizing:
        max_eval = -99999
        for move in moves:
            board.push(move)
            eval_val = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_val)
            alpha = max(alpha, eval_val)
            if beta <= alpha: break
        return max_eval
    else:
        min_eval = 99999
        for move in moves:
            board.push(move)
            eval_val = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_val)
            beta = min(beta, eval_val)
            if beta <= alpha: break
        return min_eval