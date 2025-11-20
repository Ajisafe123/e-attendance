from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from dotenv import load_dotenv

from database import get_db
from models import User, UserRole
from schemas import TokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-insecure-default-key-REPLACE-THIS-NOW")
ALGORITHM = "HS256"

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
except (TypeError, ValueError):
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    
    if 'sub' in to_encode and not isinstance(to_encode['sub'], str):
        to_encode['sub'] = str(to_encode['sub'])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id_str: str = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")
        
        if user_id_str is None:
            raise credentials_exception
            
        user_id: int = int(user_id_str)
        
        token_data = TokenData(user_id=user_id, username=username, role=role)
        
    except (JWTError, ValueError):
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_student(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires student privileges"
        )
    return current_user

async def get_current_active_lecturer(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != UserRole.LECTURER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires lecturer privileges"
        )
    return current_user

async def get_current_lecturer_or_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role not in [UserRole.LECTURER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires lecturer or admin privileges"
        )
    return current_user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires admin privileges"
        )
    return current_user