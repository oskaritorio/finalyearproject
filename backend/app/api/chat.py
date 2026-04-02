from fastapi import APIRouter, Depends
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

#creates a chatbot instance
chatbot = Chat()

#user input to the chatbot
class ChatRequest(BaseModel):
    message: str

#chatbot responds with
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
    #Find or create a chat session for this user
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.started_at.desc())
    )
    session = result.scalar_one_or_none()
    
    if not session:
        #Create new session
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=current_user.id
        )
        db.add(session)
        await db.flush()
    
    #Save user message
    user_msg = Message(
        id=str(uuid.uuid4()),
        session_id=session.id,
        sender="user",
        content=request.message
    )
    db.add(user_msg)
    
    # Get reply from chatbot
    reply_text, category, crisis_help = chatbot.get_reply(request.message)
    
    #mark the session if its a crisis
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
    #used for past conversations
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.started_at.desc())
    )
    sessions = result.scalars().all()
    
    all_chats = []
    for s in sessions:
        msg_result = await db.execute(
            select(Message)
            .where(Message.session_id == s.id)
            .order_by(Message.timestamp)
        )
        msgs = msg_result.scalars().all()
        
        all_chats.append({
            "session_id": s.id,
            "started": s.started_at,
            "crisis_detected": s.crisis_detected,
            "messages": [
                {"sender": m.sender, "content": m.content, "timestamp": m.timestamp}
                for m in msgs
            ]
        })
    
    return {"chats": all_chats}