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
from app.services.sentiment import SentimentAnalyzer

router = APIRouter(prefix="/journal", tags=["journal"])

class JournalCreate(BaseModel):
    content: str
    mood: int
    tags: str = None

class JournalResponse(BaseModel):
    id: str
    content: str
    mood_score: int
    sentiment_score: float
    sentiment_label: str
    created_at: datetime

@router.post("/")
async def create_journal(
    journal: JournalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    #Analyse sentiment
    sentiment = SentimentAnalyzer.analyze(journal.content)
    
    #Count words
    word_count = len(journal.content.split())
    
    entry = JournalEntry(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        encrypted_content=journal.content,
        mood_score=journal.mood,
        sentiment_score=sentiment["polarity"],
        sentiment_label=sentiment["label"],
        word_count=word_count,
        tags=journal.tags,
        created_at=datetime.utcnow()
    )
    
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    return {
        "id": entry.id,
        "content": entry.encrypted_content,
        "mood_score": entry.mood_score,
        "sentiment_score": entry.sentiment_score,
        "sentiment_label": entry.sentiment_label,
        "sentiment_emoji": sentiment["emoji"],
        "created_at": entry.created_at
    }

@router.get("/")
async def get_journals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    #get all the revelant journals for the user
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.created_at.desc())
    )
    entries = result.scalars().all()
    
    #Get aggregate sentiment stats
    sentiments = [e.sentiment_label for e in entries if e.sentiment_label]
    from collections import Counter
    sentiment_summary = Counter(sentiments).most_common(3) if sentiments else []
    
    return {
        "entries": [
            {
                "id": e.id,
                "content": e.encrypted_content,
                "mood_score": e.mood_score,
                "sentiment_score": e.sentiment_score,
                "sentiment_label": e.sentiment_label,
                "created_at": e.created_at
            }
            for e in entries
        ],
        "sentiment_summary": sentiment_summary,
        "total_entries": len(entries)
    }

@router.get("/sentiment-summary")
async def get_sentiment_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
   
    
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.created_at.desc())
        .limit(20)
    )
    entries = result.scalars().all()
    
    if not entries:
        return {"message": "No journal entries yet"}
    
    texts = [e.encrypted_content for e in entries if e.encrypted_content]
    batch_analysis = SentimentAnalyzer.analyze_batch(texts)
    
    #Count by label
    from collections import Counter
    labels = [e.sentiment_label for e in entries if e.sentiment_label]
    label_counts = Counter(labels) if labels else {}
    
    return {
        "total_analysed": len(entries),
        "average_sentiment": batch_analysis["avg_polarity"],
        "common_sentiment": batch_analysis["common_label"],
        "breakdown": dict(label_counts),
        "trend": "improving" if batch_analysis["avg_polarity"] > 0.1 else "stable" if batch_analysis["avg_polarity"] > -0.1 else "declining"
    }
#entry id fields to delete the journals
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