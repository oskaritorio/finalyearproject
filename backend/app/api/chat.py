from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.models.base import get_db
from app.models.chat import ChatSession, Message
from app.models.user import User
from app.auth.auth import get_current_user
from app.services.chatguide import Chat

router = APIRouter(prefix="/chat", tags=["chat"])

# Create chatbot instance
chatbot = Chat()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    category: str
    crisis_help: list | None = None


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Find or create session
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.started_at.desc())
    )
    session = result.scalar_one_or_none()
    
    if not session:
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=current_user.id
        )
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
    
    # Get reply
    reply_text, category, crisis_help = chatbot.get_reply(request.message, context)
    
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
    
    return {
        "reply": reply_text,
        "category": category,
        "crisis_help": crisis_help
    }


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


# ============================================
# DELETE CHAT HISTORY ENDPOINTS
# ============================================

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