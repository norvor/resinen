# backend/app/routers/auth.py
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import sqlite3
import hashlib
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])
DB_FILE = "users.db"

# --- DATABASE MIGRATION ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Create table with premium columns
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, token TEXT, 
                  is_premium INTEGER DEFAULT 0, payment_id TEXT)''')
    
    # Migration check
    try:
        c.execute("SELECT is_premium FROM users LIMIT 1")
    except sqlite3.OperationalError:
        print("Migrating DB: Adding premium columns...")
        c.execute("ALTER TABLE users ADD COLUMN is_premium INTEGER DEFAULT 0")
        c.execute("ALTER TABLE users ADD COLUMN payment_id TEXT")
        
    conn.commit()
    conn.close()

init_db()

# --- UTILS ---
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_from_token(token: str):
    if not token: return None
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT email, is_premium FROM users WHERE token=?", (token,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"email": row[0], "is_premium": bool(row[1])}
    return None

# --- DEPENDENCY ---
async def require_premium(x_token: str = Header(None)):
    if not x_token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = get_user_from_token(x_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    if not user['is_premium']:
        raise HTTPException(status_code=403, detail="Premium Subscription Required")
    
    return user

# --- ENDPOINTS ---
class AuthRequest(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(req: AuthRequest):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        hashed = hash_password(req.password)
        token = str(uuid.uuid4())
        c.execute("INSERT INTO users (email, password, token, is_premium) VALUES (?, ?, ?, 0)", 
                  (req.email, hashed, token))
        conn.commit()
        return {"token": token, "email": req.email, "is_premium": False}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        conn.close()

@router.post("/login")
def login(req: AuthRequest):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    hashed = hash_password(req.password)
    c.execute("SELECT token, is_premium FROM users WHERE email=? AND password=?", (req.email, hashed))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {"token": row[0], "email": req.email, "is_premium": bool(row[1])}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")