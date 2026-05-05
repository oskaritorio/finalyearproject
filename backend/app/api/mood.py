from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.models.base import get_db
from app.models.mood import MoodLog
from app.auth.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/mood", tags=["mood"])

class MoodCreate(BaseModel):
    mood_score: int  # 1-5
    note: str | None = None

class MoodResponse(BaseModel):
    id: str
    mood_score: int
    note: str | None
    created_at: datetime

@router.post("/")
async def create_mood(
    mood: MoodCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    #Check if already logged today 
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    existing = await db.execute(
        select(MoodLog).where(
            MoodLog.user_id == current_user.id,
            MoodLog.created_at >= today_start
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Already logged mood today")
    
    mood_log = MoodLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        mood_score=mood.mood_score,
        note=mood.note,
        created_at=datetime.utcnow()
    )
    
    db.add(mood_log)
    await db.commit()
    
    return {
        "id": mood_log.id,
        "mood_score": mood_log.mood_score,
        "note": mood_log.note,
        "created_at": mood_log.created_at
    }
#retrieves the history of moods
@router.get("/")
async def get_mood_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = 7
):
    """Get mood history for last X days"""
    from datetime import timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(MoodLog)
        .where(
            MoodLog.user_id == current_user.id,
            MoodLog.created_at >= cutoff
        )
        .order_by(MoodLog.created_at.desc())
    )
    moods = result.scalars().all()
    
    #Calculate average
    avg = sum(m.mood_score for m in moods) / len(moods) if moods else 0
    
    return {
        "user": current_user.username,
        "total_entries": len(moods),
        "average_mood": round(avg, 1),
        "history": [
            {
                "date": m.created_at.date().isoformat(),
                "mood": m.mood_score,
                "note": m.note
            }
            for m in moods
        ]
    }