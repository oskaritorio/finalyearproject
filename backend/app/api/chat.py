from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
import uuid
from collections import Counter

from app.models.base import get_db
from app.models.chat import ChatSession, Message
from app.models.user import User
from app.auth.auth import get_current_user
from app.services.chatguide import Chat

router = APIRouter(prefix="/chat", tags=["chat"])

chatbot = Chat()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    category: str
    crisis_help: list | None = None


# ============================================
# HELPER FUNCTIONS FOR JOURNAL AWARENESS
# ============================================

async def get_journal_summary(user_id: str, db: AsyncSession) -> str:
    """Get summary of recent journal entries"""
    from app.models.journal import JournalEntry
    
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.created_at.desc())
        .limit(5)
    )
    entries = result.scalars().all()
    
    if not entries:
        return "You haven't written any journal entries yet. Would you like to write one?"
    
    # Count sentiments
    sentiments = [e.sentiment_label for e in entries if e.sentiment_label]
    sentiment_counts = Counter(sentiments) if sentiments else {}
    
    # Calculate average mood
    mood_scores = [e.mood_score for e in entries if e.mood_score]
    avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 0
    
    response = f"📊 Journal Summary \n\n"
    response += f"You've written {len(entries)} entries recently.\n"
    response += f"Average mood: {avg_mood:.1f}/5\n\n"
    
    if sentiment_counts:
        response += f"Sentiment breakdown:\n"
        for label, count in sentiment_counts.items():
            emoji = "😊" if label == "positive" else "😔" if label == "negative" else "😐"
            response += f"  {emoji} {label}: {count}\n"
        response += "\n"
    
    # Latest entry preview
    latest = entries[0]
    preview = latest.encrypted_content[:100] + "..." if len(latest.encrypted_content) > 100 else latest.encrypted_content
    response += f"📝 Latest entry:\n{preview}\n"
    
    return response


async def analyze_mood_trend(user_id: str, db: AsyncSession) -> str:
    """Analyse mood trends from journals"""
    from app.models.journal import JournalEntry
    
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.created_at.desc())
        .limit(14)
    )
    entries = result.scalars().all()
    
    if len(entries) < 3:
        return "You don't have enough journal entries yet to analyse mood trends. Keep writing!"
    
    # Get sentiment scores
    sentiments = [e.sentiment_score for e in entries if e.sentiment_score is not None]
    
    if len(sentiments) >= 6:
        recent_avg = sum(sentiments[:3]) / 3
        older_avg = sum(sentiments[-3:]) / 3
        
        if recent_avg > older_avg + 0.2:
            trend = "improving 📈"
            advice = "That's great! What do you think has contributed to this positive shift?"
        elif recent_avg < older_avg - 0.2:
            trend = "declining 📉"
            advice = "I notice you've been feeling lower lately. Would you like to talk about it?"
        else:
            trend = "stable 📊"
            advice = "Your mood has been consistent. Small daily habits can make a big difference."
    else:
        trend = "insufficient data"
        advice = "Keep journaling so I can track your mood patterns!"
    
    return f"📈 Mood Trend Analysis\n\n Based on your last {len(entries)} journal entries:\n Overall trend: {trend}\n\n{advice}"


# ============================================
# MAIN CHAT ENDPOINT
# ============================================

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check for journal-aware commands FIRST
    msg_lower = request.message.lower()
    
    # Journal summary command
    journal_summary_keywords = [
        "what did i write", "show me my journal", "journal summary", 
        "what have i been writing", "read my journal", "my entries",
        "summarise my journal", "journal recap"
    ]
    
    if any(phrase in msg_lower for phrase in journal_summary_keywords):
        summary = await get_journal_summary(current_user.id, db)
        return ChatResponse(reply=summary, category="journal_summary", crisis_help=None)
    
    # Mood trend command
    mood_analysis_keywords = [
        "how is my mood", "mood trend", "am i getting better", 
        "track my mood", "mood analysis", "how have i been feeling"
    ]
    
    if any(phrase in msg_lower for phrase in mood_analysis_keywords):
        analysis = await analyze_mood_trend(current_user.id, db)
        return ChatResponse(reply=analysis, category="mood_analysis", crisis_help=None)
    
    # Normal chat flow
    # Find or create session
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.started_at.desc())
    )
    session = result.scalar_one_or_none()
    
    if not session:
        session = ChatSession(id=str(uuid.uuid4()), user_id=current_user.id)
        db.add(session)
        await db.flush()
    
    # Get last 3 messages for context
    msg_result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.timestamp.desc())
        .limit(3)
    )
    last_msgs = msg_result.scalars().all()
    context = [{"sender": m.sender, "content": m.content} for m in reversed(last_msgs)]
    
    # Save user message
    user_msg = Message(
        id=str(uuid.uuid4()),
        session_id=session.id,
        sender="user",
        content=request.message
    )
    db.add(user_msg)
    
    # Get reply from chatbot
    reply_text, category, crisis_help = await chatbot.get_reply(request.message, context)
    
    if category == "CRISIS":
        session.crisis_detected = True
    
    # Save bot reply
    bot_msg = Message(
        id=str(uuid.uuid4()),
        session_id=session.id,
        sender="bot",
        content=reply_text
    )
    db.add(bot_msg)
    
    await db.commit()
    
    return ChatResponse(reply=reply_text, category=category, crisis_help=crisis_help)


@router.get("/history")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all chat sessions for the current user"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.started_at.desc())
    )
    sessions = result.scalars().all()
    
    history = []
    for s in sessions:
        msg_result = await db.execute(
            select(Message)
            .where(Message.session_id == s.id)
            .order_by(Message.timestamp)
        )
        msgs = msg_result.scalars().all()
        history.append({
            "session_id": s.id,
            "started_at": s.started_at,
            "crisis_detected": s.crisis_detected,
            "messages": [
                {"sender": m.sender, "content": m.content, "timestamp": m.timestamp}
                for m in msgs
            ]
        })
    
    return {"sessions": history}


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a single chat session"""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.delete(session)
    await db.commit()
    
    return {"message": "Session deleted"}


@router.delete("/all")
async def delete_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete ALL chat sessions for the current user"""
    result = await db.execute(
        select(ChatSession).where(ChatSession.user_id == current_user.id)
    )
    sessions = result.scalars().all()
    
    for session in sessions:
        await db.delete(session)
    
    await db.commit()
    
    return {"message": f"Deleted {len(sessions)} sessions"}

@router.get("/export/all")
async def export_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export ALL chat sessions for the current user as JSON"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.started_at.desc())
    )
    sessions = result.scalars().all()
    
    export_data = {
        "user": current_user.username,
        "exported_at": datetime.utcnow().isoformat(),
        "total_sessions": len(sessions),
        "sessions": []
    }
    
    for session in sessions:
        msg_result = await db.execute(
            select(Message)
            .where(Message.session_id == session.id)
            .order_by(Message.timestamp)
        )
        messages = msg_result.scalars().all()
        
        export_data["sessions"].append({
            "session_id": session.id,
            "started_at": session.started_at.isoformat(),
            "crisis_detected": session.crisis_detected,
            "total_messages": len(messages),
            "messages": [
                {
                    "sender": m.sender,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in messages
            ]
        })
    
    return export_data


@router.get("/export/{session_id}")
async def export_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export a single chat session as JSON"""
    result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    msg_result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.timestamp)
    )
    messages = msg_result.scalars().all()
    
    return {
        "session_id": session.id,
        "started_at": session.started_at.isoformat(),
        "crisis_detected": session.crisis_detected,
        "total_messages": len(messages),
        "messages": [
            {
                "sender": m.sender,
                "content": m.content,
                "timestamp": m.timestamp.isoformat()
            }
            for m in messages
        ]
    }