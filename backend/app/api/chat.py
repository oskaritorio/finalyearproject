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


#Helper functions to read the wellbeing application

async def get_wellbeing_summary(user_id: str, db: AsyncSession) -> str:
    """Get user's latest wellbeing assessment with full details"""
    latest = WellbeingService.get_latest_assessment(user_id)
    
    if not latest:
        return "You haven't completed a wellbeing assessment yet. Would you like to take one? You can find it in the Mood & Wellbeing section."
    
    category = latest.get('category', 'Unknown')
    total_score = latest.get('total_score', 0)
    date = latest.get('date', '')[:10]
    
    # Category-specific advice
    advice_map = {
        "Excellent": "🌟 You're thriving! Keep up your great habits.",
        "Good": "🌱 You're doing well. Small improvements can make a difference.",
        "Moderate": "🌿 You're managing. Focus on small, positive steps.",
        "Concerning": "🫂 Your wellbeing matters. Consider reaching out for support.",
        "Critical": "🆘 Please reach out for support immediately."
    }
    
    advice = advice_map.get(category, "Take care of yourself.")
    
    response = f"📊 Your Latest Wellbeing Assessment\n\n"
    response += f"📅 Date: {date}\n"
    response += f"📈 Score: {total_score}/5\n"
    response += f"🏷️ Category: {category}\n\n"
    response += f"💚 {advice}"
    
    return response


async def get_wellbeing_trend(user_id: str, db: AsyncSession) -> str:
    """Analyse wellbeing trend over multiple assessments"""
    history = WellbeingService.get_user_history(user_id)
    
    if not history:
        return "You haven't completed any wellbeing assessments yet. Take one in the Mood & Wellbeing section!"
    
    if len(history) < 2:
        return f"You've completed {len(history)} assessment. Take another one to see your progress over time!"
    
    #Get scores from last 3 assessments
    scores = []
    dates = []
    for item in history[:3]:
        scores.append(float(item.get('total_score', 0)))
        dates.append(item.get('date', '')[:10])
    
    #Calculate trend
    if len(scores) >= 2:
        first = scores[-1]
        last = scores[0]
        diff = last - first
        
        if diff > 0.3:
            trend = "improving 📈"
        elif diff < -0.3:
            trend = "declining 📉"
        else:
            trend = "stable 📊"
    else:
        trend = "stable"
    
    response = f"📈 Wellbeing Trend Analysis\n\n"
    response += f"Based on your last {len(history)} assessments:\n"
    for i, (score, date) in enumerate(zip(scores[:3], dates[:3])):
        response += f"  {date}: {score}/5\n"
    response += f"\n📊 Overall trend: {trend}"
    
    return response


async def get_wellbeing_tips(user_id: str, db: AsyncSession) -> str:
    """Get personalised wellbeing tips based on assessment category"""
    latest = WellbeingService.get_latest_assessment(user_id)
    
    if not latest:
        return "Please complete a wellbeing assessment first to get personalised tips! You can find it in the Mood & Wellbeing section."
    
    category = latest.get('category', 'Moderate')
    
    tips_by_category = {
        "Excellent": [
            "🌟 Keep up your great habits! You're doing amazing.",
            "📝 Try a gratitude journal - write 3 good things each day.",
            "💪 Share what's working with someone who might benefit.",
            "🧘 Maintain your wellbeing with regular self-care."
        ],
        "Good": [
            "🌱 Add one new positive activity to your routine this week.",
            "📖 Read something uplifting or listen to a happy podcast.",
            "💚 Connect with a friend - social bonds boost wellbeing.",
            "🧘 Try 5 minutes of mindfulness each day."
        ],
        "Moderate": [
            "🌿 Focus on small steps. Even a 5-minute walk helps.",
            "📝 Write down one small win each day to build momentum.",
            "💬 Talk to someone you trust about how you're feeling.",
            "🧘 Try the breathing exercise on the dashboard."
        ],
        "Concerning": [
            "🫂 Your wellbeing matters. Consider talking to someone you trust.",
            "📞 Mind helpline: 0300 123 3393",
            "📞 Samaritans: 116 123 (24/7 confidential support)",
            "🌿 Try a wellbeing journal to track your feelings."
        ],
        "Critical": [
            "🆘 Please reach out for support immediately:",
            "📞 Samaritans: 116 123 (24/7)",
            "📞 NHS 111: 111 (medical help)",
            "📞 Mind: 0300 123 3393"
        ]
    }
    
    tips = tips_by_category.get(category, tips_by_category["Moderate"])
    
    response = f"💡 Personalised Wellbeing Tips\n\n"
    for tip in tips[:3]:
        response += f"• {tip}\n"
    
    return response



async def get_journal_summary(user_id: str, db: AsyncSession) -> str:
    from app.models.journal import JournalEntry
    
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.created_at.desc())
        .limit(7)
    )
    entries = result.scalars().all()
    
    if not entries:
        return "You haven't written any journal entries yet. Would you like to write one now?"
    
    #Count sentiments
    sentiments = [e.sentiment_label for e in entries if e.sentiment_label]
    sentiment_counts = Counter(sentiments) if sentiments else {}
    
    #Calculate average mood
    mood_scores = [e.mood_score for e in entries if e.mood_score]
    avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 0
    
    response = f"📊 Journal Summary\n\n"
    response += f"You've written {len(entries)} entries recently.\n"
    response += f"Average mood: {avg_mood:.1f}/5\n\n"
    
    if sentiment_counts:
        response += f"Sentiment breakdown:\n"
        for label, count in sentiment_counts.items():
            emoji = "😊" if label == "positive" else "😔" if label == "negative" else "😐"
            response += f"  {emoji} {label}: {count}\n"
        response += "\n"
    
    #Latest entry preview
    latest = entries[0]
    preview = latest.encrypted_content[:150] + "..." if len(latest.encrypted_content) > 150 else latest.encrypted_content
    response += f"📝 Latest entry:\n{preview}"
    
    return response


async def analyze_mood_trend(user_id: str, db: AsyncSession) -> str:
    """Analyse mood trends from journal entries"""
    from app.models.journal import JournalEntry
    
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.created_at.desc())
        .limit(14)
    )
    entries = result.scalars().all()
    
    if len(entries) < 3:
        return "You don't have enough journal entries yet to analyse mood trends. Write a few more entries!"
    
    #Get sentiment scores
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
        trend = "stable"
        advice = "Keep journaling to see clearer patterns!"
    
    response = f"📈 Mood Trend Analysis\n\n"
    response += f"Based on your last {len(entries)} journal entries:\n"
    response += f"Overall trend: {trend}\n\n"
    response += advice
    
    return response




@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    msg_lower = request.message.lower()
    
    
    if "wellbeing tips" in msg_lower or "wellbeing advice" in msg_lower or "self care tips" in msg_lower:
        tips = await get_wellbeing_tips(current_user.id, db)
        return ChatResponse(reply=tips, category="wellbeing_tips", crisis_help=None)
    
    if "wellbeing trend" in msg_lower or "am i improving" in msg_lower or "wellbeing progress" in msg_lower:
        trend = await get_wellbeing_trend(current_user.id, db)
        return ChatResponse(reply=trend, category="wellbeing_trend", crisis_help=None)
    
    if "how is my wellbeing" in msg_lower or "wellbeing assessment" in msg_lower or "my wellbeing" in msg_lower or "latest assessment" in msg_lower:
        summary = await get_wellbeing_summary(current_user.id, db)
        return ChatResponse(reply=summary, category="wellbeing_summary", crisis_help=None)
    
    
    #Journal summary
    if any(phrase in msg_lower for phrase in ["what did i write", "show me my journal", "journal summary", "my entries", "summarise my journal", "journal recap"]):
        summary = await get_journal_summary(current_user.id, db)
        return ChatResponse(reply=summary, category="journal_summary", crisis_help=None)
    
    #Journal trend
    if any(phrase in msg_lower for phrase in ["journal trend", "my journal trend", "what is my journal trend", "how is my journal trend", "journal progress", "am i improving in my journal", "how are my journals"]):
        analysis = await analyze_mood_trend(current_user.id, db)
        return ChatResponse(reply=analysis, category="mood_analysis", crisis_help=None)
    
    #Simple mood trend 
    if any(phrase in msg_lower for phrase in ["how is my mood", "mood trend", "am i getting better", "track my mood"]):
        analysis = await analyze_mood_trend(current_user.id, db)
        return ChatResponse(reply=analysis, category="mood_analysis", crisis_help=None)
    
    #Find or create session
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
    
    #Get last 5 messages for context
    msg_result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.timestamp.desc())
        .limit(5)
    )
    last_msgs = msg_result.scalars().all()
    context = [{"sender": m.sender, "content": m.content} for m in reversed(last_msgs)]
    
    #Save user message
    user_msg = Message(
        id=str(uuid.uuid4()),
        session_id=session.id,
        sender="user",
        content=request.message
    )
    db.add(user_msg)
    
    #Get reply from chatbot
    reply_text, category, crisis_help = await chatbot.get_reply(request.message, context)
    
    if category == "CRISIS":
        session.crisis_detected = True
    
    #Save bot reply
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


@router.get("/export/all")
async def export_all_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export ALL chat sessions as JSON"""
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
        "messages": [
            {
                "sender": m.sender,
                "content": m.content,
                "timestamp": m.timestamp.isoformat()
            }
            for m in messages
        ]
    }


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