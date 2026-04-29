from sqlalchemy.orm import relationship
from .base import Base, engine, get_db
from .user import User
from .journal import JournalEntry
from .mood import MoodLog
from .chat import ChatSession, Message

# Set up relationships for Journal
User.journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
JournalEntry.user = relationship("User", back_populates="journal_entries")

# Set up relationships for Mood
User.mood_logs = relationship("MoodLog", back_populates="user", cascade="all, delete-orphan")
MoodLog.user = relationship("User", back_populates="mood_logs")

# Set up relationships for Chat
User.chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
ChatSession.user = relationship("User", back_populates="chat_sessions")

# Message relationship
ChatSession.messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
Message.session = relationship("ChatSession", back_populates="messages")

# Export all models and utilities
__all__ = [
    "Base", 
    "engine", 
    "get_db", 
    "User", 
    "JournalEntry",
    "MoodLog",
    "ChatSession",
    "Message"
]