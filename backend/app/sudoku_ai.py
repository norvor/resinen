# backend/app/sudoku_ai.py
import random

# --- 1. SUDOKU GENERATOR ---
class SudokuGenerator:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]

    def is_safe(self, row, col, num):
        # Check Row & Col
        for x in range(9):
            if self.board[row][x] == num or self.board[x][col] == num:
                return False
        
        # Check 3x3 Box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.board[i + start_row][j + start_col] == num:
                    return False
        return True

    def fill_diagonal(self):
        for i in range(0, 9, 3):
            self.fill_box(i, i)

    def fill_box(self, row, col):
        num = 0
        for i in range(3):
            for j in range(3):
                while True:
                    num = random.randint(1, 9)
                    if self.is_safe_in_box(row, col, num):
                        break
                self.board[row + i][col + j] = num

    def is_safe_in_box(self, row_start, col_start, num):
        for i in range(3):
            for j in range(3):
                if self.board[row_start + i][col_start + j] == num:
                    return False
        return True

    def solve(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    for num in range(1, 10):
                        if self.is_safe(i, j, num):
                            self.board[i][j] = num
                            if self.solve():
                                return True
                            self.board[i][j] = 0
                    return False
        return True

    def remove_digits(self, count):
        while count > 0:
            i = random.randint(0, 8)
            j = random.randint(0, 8)
            if self.board[i][j] != 0:
                self.board[i][j] = 0
                count -= 1

    def generate(self, difficulty=30):
        # 1. Fill diagonals (independent)
        self.fill_diagonal()
        # 2. Solve to fill the rest
        self.solve()
        # 3. Save the Solution
        solution = [row[:] for row in self.board]
        # 4. Remove digits to create puzzle
        self.remove_digits(difficulty)
        return {"puzzle": self.board, "solution": solution}

# --- EXPORT ---
def get_new_sudoku(difficulty_level="medium"):
    # Easy = 30 removed, Medium = 40, Hard = 50
    holes = 30 if difficulty_level == "easy" else 40 if difficulty_level == "medium" else 50
    gen = SudokuGenerator()
    return gen.generate(holes)