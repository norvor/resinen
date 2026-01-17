from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# CHANGED: We now use "argon2" as the main scheme.
# It is faster, more secure, and has NO length limits.
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the raw password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Transforms raw password into a secure hash."""
    # Debugging: Print length to log so we know what's happening
    print(f"DEBUG: Hashing password of length {len(password)}")
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any]) -> str:
    """Generates the JWT Token for the frontend."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt