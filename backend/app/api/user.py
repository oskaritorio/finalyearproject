from fastapi import APIRouter, Depends, HTTPException
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
    """Permanently delete user account and all associated data"""
    await db.delete(current_user)
    await db.commit()
    return {"message": "Account permanently deleted"}

@router.get("/me")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    # Format the date for display
    created_date = None
    if current_user.created_at:
        created_date = current_user.created_at.isoformat()
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "created_at": created_date
    }