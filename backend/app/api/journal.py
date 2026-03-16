from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.models.base import get_db
from app.models.journal import JournalEntry
from app.auth.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/journal", tags=["journal"])

# Simple request/response models (no separate schemas file needed!)
class JournalCreate(BaseModel):
    content: str  # Already encrypted by frontend
    mood: int     # 1-5 scale

class JournalResponse(BaseModel):
    id: str
    content: str
    mood: int
    created_at: datetime

@router.post("/")
async def create_journal(
    journal: JournalCreate,
    current_user: User = Depends(get_current_user),  # Gets logged-in user
    db: AsyncSession = Depends(get_db)
):
    try:
        entry = JournalEntry(
            id=str(uuid.uuid4()),
            user_id=current_user.id,  # Use REAL user ID from auth
            encrypted_content=journal.content,
            mood_score=journal.mood,
            created_at=datetime.utcnow()
        )
        
        db.add(entry)
        await db.commit()
        
        return {
            "id": entry.id,
            "content": entry.encrypted_content,
            "mood": entry.mood_score,
            "created_at": entry.created_at,
            "message": "Journal entry saved!"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_my_journals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all journals for the logged-in user"""
    try:
        result = await db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == current_user.id)
            .order_by(JournalEntry.created_at.desc())
        )
        entries = result.scalars().all()
        
        return {
            "user": current_user.username,
            "count": len(entries),
            "entries": [
                {
                    "id": e.id,
                    "content": e.encrypted_content,
                    "mood": e.mood_score,
                    "created_at": e.created_at
                }
                for e in entries
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{entry_id}")
async def get_one_journal(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific journal entry"""
    try:
        result = await db.execute(
            select(JournalEntry).where(
                JournalEntry.id == entry_id,
                JournalEntry.user_id == current_user.id  # Ensure ownership
            )
        )
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return {
            "id": entry.id,
            "content": entry.encrypted_content,
            "mood": entry.mood_score,
            "created_at": entry.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{entry_id}")
async def delete_journal(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a journal entry"""
    try:
        result = await db.execute(
            select(JournalEntry).where(
                JournalEntry.id == entry_id,
                JournalEntry.user_id == current_user.id
            )
        )
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        await db.delete(entry)
        await db.commit()
        
        return {"message": "Entry deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))