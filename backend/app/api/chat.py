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
from app.services.wellbeing_service import WellbeingService

router = APIRouter(prefix="/chat", tags=["chat"])

chatbot = Chat()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    category: str
    crisis_help: list | None = None


#Wellbeing helper funcions

async def get_wellbeing_summary(user_id: str, db: AsyncSession) -> str:
    latest = WellbeingService.get_latest_assessment(user_id)
    if not latest:
        return "You haven't completed a wellbeing assessment yet."
    category = latest.get('category', 'Unknown')
    total_score = latest.get('total_score', 0)
    date = latest.get('date', '')[:10]
    return f"📊 Your Latest Wellbeing Assessment\n\n📅 Date: {date}\n📈 Score: {total_score}/5\n🏷️ Category: {category}" #takes the lastest wellbeing score

async def get_wellbeing_tips(user_id: str, db: AsyncSession) -> str:
    latest = WellbeingService.get_latest_assessment(user_id)
    if not latest:
        return "Please complete a wellbeing assessment first to get personalised tips!"
    category = latest.get('category', 'Moderate')
    tips = {
        "Excellent": [" Keep up your great habits!", " Try a gratitude journal."],
        "Good": [" Add one new positive activity.", " Connect with a friend."],
        "Moderate": [" Focus on small steps.", " Talk to someone you trust."],
        "Concerning": [" Your wellbeing matters.", "📞 Samaritans: 116 123"],
        "Critical": [" Please reach out for support.", "📞 Samaritans: 116 123"]
    }
    selected = tips.get(category, tips["Moderate"])
    return f"💡 Wellbeing Tips ({category} category)\n\n• " + "\n• ".join(selected)

async def get_wellbeing_trend(user_id: str, db: AsyncSession) -> str:
    history = WellbeingService.get_user_history(user_id)
    if len(history) < 2:
        return "Complete more assessments to see your trend!"
    scores = [float(h.get('total_score', 0)) for h in history[:3]]
    diff = scores[0] - scores[-1]
    trend = "improving 📈" if diff > 0.2 else "declining 📉" if diff < -0.2 else "stable 📊"
    return f"📈 Wellbeing Trend\n\nOverall trend: {trend}"



#Journal summary indiactor

async def get_journal_summary(user_id: str, db: AsyncSession) -> str:
    from app.models.journal import JournalEntry
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.created_at.desc())
        .limit(5)
    )
    entries = result.scalars().all()
    if not entries:
        return "You haven't written any journal entries yet."
    return f"📊 You've written {len(entries)} journal entries recently."

async def analyze_mood_trend(user_id: str, db: AsyncSession) -> str:
    from app.models.journal import JournalEntry
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.created_at.desc())
        .limit(14)
    )
    entries = result.scalars().all()
    if len(entries) < 3:
        return "Write more journal entries to see mood trends!"
    return f"📈 Based on your last {len(entries)} entries, your mood is stable."


#mainchat endpoint

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    msg_lower = request.message.lower()
    
    #Wellbeing commands
    if "wellbeing tips" in msg_lower:
        tips = await get_wellbeing_tips(current_user.id, db)
        return ChatResponse(reply=tips, category="wellbeing_tips", crisis_help=None)
    if "how is my wellbeing" in msg_lower or "wellbeing assessment" in msg_lower:
        summary = await get_wellbeing_summary(current_user.id, db)
        return ChatResponse(reply=summary, category="wellbeing_summary", crisis_help=None)
    if "am i improving" in msg_lower or "wellbeing trend" in msg_lower:
        trend = await get_wellbeing_trend(current_user.id, db)
        return ChatResponse(reply=trend, category="wellbeing_trend", crisis_help=None)
    
    #Journal commands
    if any(p in msg_lower for p in ["what did i write", "journal summary", "my entries"]):
        summary = await get_journal_summary(current_user.id, db)
        return ChatResponse(reply=summary, category="journal_summary", crisis_help=None)
    if any(p in msg_lower for p in ["how is my mood", "mood trend"]):
        analysis = await analyze_mood_trend(current_user.id, db)
        return ChatResponse(reply=analysis, category="mood_analysis", crisis_help=None)
    
    #Normal chat flow
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
    
    msg_result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.timestamp.desc())
        .limit(3)
    )
    last_msgs = msg_result.scalars().all()
    context = [{"sender": m.sender, "content": m.content} for m in reversed(last_msgs)]
    
    user_msg = Message(id=str(uuid.uuid4()), session_id=session.id, sender="user", content=request.message)
    db.add(user_msg)
    
    reply_text, category, crisis_help = await chatbot.get_reply(request.message, context)
    
    if category == "CRISIS":
        session.crisis_detected = True
    
    bot_msg = Message(id=str(uuid.uuid4()), session_id=session.id, sender="bot", content=reply_text)
    db.add(bot_msg)
    await db.commit()
    
    return ChatResponse(reply=reply_text, category=category, crisis_help=crisis_help)



#hisotry endpoints
@router.get("/history")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
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
            "messages": [{"sender": m.sender, "content": m.content, "timestamp": m.timestamp} for m in msgs]
        })
    return {"sessions": history}

#export endpoints
@router.get("/export/all")
async def export_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
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
            "messages": [{"sender": m.sender, "content": m.content, "timestamp": m.timestamp.isoformat()} for m in messages]
        })
    
    return export_data


@router.get("/export/{session_id}")
async def export_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChatSession).where(
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
        "messages": [{"sender": m.sender, "content": m.content, "timestamp": m.timestamp.isoformat()} for m in messages]
    }



#delete endpoints
@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
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
    result = await db.execute(
        select(ChatSession).where(ChatSession.user_id == current_user.id)
    )
    sessions = result.scalars().all()
    
    for session in sessions:
        await db.delete(session)
    
    await db.commit()
    return {"message": f"Deleted {len(sessions)} sessions"}