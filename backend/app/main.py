from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from .database import create_db_and_tables
from .routers import news, auth, cinema, chess, sudoku, payment, battleship, saataath, poker, catan, tetris, ludo, go, minesweeper # <--- Changed this


app = FastAPI(title="The Resinen Times API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up: Initializing Database...")
    await init_db()
    print("✅ Database Initialized.")
    yield
    print("🛑 Shutting down...")

app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:5173", "http://localhost:3000", 'https://resinen.com', 'https://www.resinen.com']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(news.router)
app.include_router(cinema.router)
app.include_router(ludo.router)  # <--- Added this
app.include_router(chess.router)
app.include_router(sudoku.router)
app.include_router(poker.router) 
app.include_router(catan.router) 
app.include_router(tetris.router)
app.include_router(go.router) 
app.include_router(minesweeper.router)
app.include_router(saataath.router)
app.include_router(battleship.router)
app.include_router(auth.router)
app.include_router(payment.router) # Register it # <--- Added this

@app.get("/")
def read_root():
    return {"status": "Newsroom Online"}