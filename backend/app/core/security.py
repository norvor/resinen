from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.core.config import settings

# --- CONFIGURATION ---
ALGORITHM = "HS256"

# --- PYDANTIC MODEL ---
class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

# --- PASSWORD HASHING ---
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the raw password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Transforms raw password into a secure hash."""
    return pwd_context.hash(password)

# --- TOKEN GENERATION ---
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Generates the JWT Token for the frontend."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 🚨 ADDED THIS MISSING FUNCTION ---
def is_active(user: Any) -> bool:
    """Helper to check if a user is active."""
    return user.is_active