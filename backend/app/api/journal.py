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

class JournalCreate(BaseModel):
    content: str
    mood: int

class JournalResponse(BaseModel):
    id: str
    content: str
    mood_score: int  # Make sure this field exists
    created_at: datetime

@router.post("/")
async def create_journal(
    journal: JournalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a journal entry"""
    
    entry = JournalEntry(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        encrypted_content=journal.content,
        mood_score=journal.mood,
        created_at=datetime.utcnow()
    )
    
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    # Return the entry with mood_score
    return {
        "id": entry.id,
        "content": entry.encrypted_content,
        "mood_score": entry.mood_score,  # CRITICAL: Include this
        "created_at": entry.created_at
    }

@router.get("/")
async def get_journals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all journal entries for current user"""
    
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.created_at.desc())
    )
    entries = result.scalars().all()
    
    # Return entries with mood_score included
    return {
        "entries": [
            {
                "id": e.id,
                "content": e.encrypted_content,
                "mood_score": e.mood_score,  # CRITICAL: Include this
                "created_at": e.created_at
            }
            for e in entries
        ]
    }

@router.delete("/{entry_id}")
async def delete_journal(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a journal entry"""
    
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
    
    return {"message": "Deleted"}