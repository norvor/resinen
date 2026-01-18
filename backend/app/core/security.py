from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# ✅ FIX: Define the Algorithm here. 
# This fixes the crash and allows deps.py to import 'security.ALGORITHM' safely.
ALGORITHM = "HS256"

# CHANGED: We now use "argon2" as the main scheme.
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the raw password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Transforms raw password into a secure hash."""
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any]) -> str:
    """Generates the JWT Token for the frontend."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # ✅ FIX: Use the local constant ALGORITHM instead of settings.ALGORITHM
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt