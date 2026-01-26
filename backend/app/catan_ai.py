# backend/app/catan_ai.py
import random

RESOURCES = ["wood", "brick", "sheep", "wheat", "ore"]
NUMBERS = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
# 1 Desert, so 18 numbers. 19 Hexes total.

class CatanMap:
    def generate(self):
        # 1. Create Tile Deck
        tiles = (
            ["wood"] * 4 + ["sheep"] * 4 + ["wheat"] * 4 + 
            ["brick"] * 3 + ["ore"] * 3 + ["desert"]
        )
        random.shuffle(tiles)
        
        # 2. Create Number Deck
        nums = NUMBERS[:]
        random.shuffle(nums)
        
        # 3. Assign to Hexes (Spiral Pattern 0-18)
        # 0-18 indices map to specific coordinates in frontend
        board = []
        num_idx = 0
        
        for tile in tiles:
            hex_data = {"resource": tile, "number": None}
            if tile != "desert":
                hex_data["number"] = nums[num_idx]
                num_idx += 1
            board.append(hex_data)
            
        return board

def get_new_map():
    gen = CatanMap()
    return gen.generate()