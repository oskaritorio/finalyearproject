
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid

from app.models.base import get_db
from app.models.user import User
from app.auth.simple_auth import hash_password

router = APIRouter(prefix="/auth", tags=["authentication"])

# Simple request/response models
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    message: str

@router.post("/register", response_model=UserResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if username exists
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    user = User(
        id=str(uuid.uuid4()),
        username=request.username,
        password_hash=hash_password(request.password)
    )
    
    db.add(user)
    await db.commit()
    
    return {
        "id": user.id,
        "username": user.username,
        "message": "User created successfully"
    }

@router.post("/login", response_model=UserResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Simple login check"""
    from app.auth.simple_auth import verify_password
    
    # Find user
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    user = result.scalar_one_or_none()
    
    # Check password
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {
        "id": user.id,
        "username": user.username,
        "message": "Login successful"
    }