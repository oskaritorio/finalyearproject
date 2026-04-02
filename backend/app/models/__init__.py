
from sqlalchemy.orm import relationship
from .base import Base, engine, get_db
from .user import User
from .journal import JournalEntry
from .mood import MoodLog

# Set up relationships
User.journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
JournalEntry.user = relationship("User", back_populates="journal_entries")
User.mood_logs = relationship("MoodLog", back_populates="user", cascade= "all, delete-orphan")
MoodLog.user = relationship("User", back_populates="mood_logs")
User.chat_sessions = relationship("Chatsession", back_populates="user", cascade="all, delete_orphan")
ChatSession.user = relationship("User", back_populates="chat_sessions")
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