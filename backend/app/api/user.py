from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.user import User
from app.auth.auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])

@router.delete("/")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    await db.delete(current_user)
    await db.commit()
    
    return {"message": "Account deleted"}

@router.get("/me")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "created_at": current_user.created_at
    }