from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db # <--- CHANGED FROM create_db_and_tables
from routers import (
    auth, widgets, # Core
    news, cricket, soccer, cinema, payment, # Apps
    chess, sudoku, battleship, poker, tetris, go, minesweeper # Games
)

# --- LIFESPAN (Startup/Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    await init_db()
    yield
    # Shutdown: Clean up (if needed)

# --- APP INITIALIZATION ---
app = FastAPI(
    title="RESINEN OS API",
    version="2.0.0",
    lifespan=lifespan
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", 'localhost:5173'], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER REGISTRATION ---
# Core
app.include_router(auth.router)
app.include_router(widgets.router)
app.include_router(payment.router)

# Apps
app.include_router(news.router)
app.include_router(cinema.router)

# Games
app.include_router(chess.router)
app.include_router(poker.router)
app.include_router(tetris.router)
app.include_router(sudoku.router)
app.include_router(go.router)
app.include_router(minesweeper.router)
app.include_router(battleship.router)
app.include_router(soccer.router)
app.include_router(cricket.router)

@app.get("/")
async def root():
    return {
        "system": "RESINEN OS", 
        "status": "ONLINE", 
        "time": "NOW"
    }