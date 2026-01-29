from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from pydantic import BaseModel

from app.database import get_session
from app.models import User

# --- CONFIG ---
SECRET_KEY = "resinen-neural-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200 # 30 Days

# FIX 1: Removed prefix="/auth" so routes match frontend (e.g. /token)
router = APIRouter(tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FIX 2: Point to "token" (root relative) instead of "/auth/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- SCHEMAS ---
class UserRead(BaseModel):
    id: int
    email: str
    is_premium: bool
    country_code: str
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserRead

class UserCreate(BaseModel):
    email: str
    password: str
    country_code: str = "IN"
    data_consent: bool = True

# --- HELPERS ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- DEPENDENCY ---
async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    return user

# --- ENDPOINTS ---

# FIX 3: Renamed to /users/signup to match frontend
@router.post("/users/signup", response_model=Token)
async def signup(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    # 1. Check existing
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Create
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        country_code=user_data.country_code,
        data_consent=user_data.data_consent
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    # 3. Token
    access_token = create_access_token(
        data={"sub": new_user.email}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": new_user}

# FIX 4: Renamed to /token to match frontend
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: AsyncSession = Depends(get_session)
):
    # 1. Async Query
    statement = select(User).where(User.email == form_data.username)
    result = await session.execute(statement)
    user = result.scalars().first()
    
    # 2. Verify
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Token
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user