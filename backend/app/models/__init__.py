
from sqlalchemy.orm import relationship
from .base import Base, engine, get_db
from .user import User
from .journal import JournalEntry

# Set up relationships
User.journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
JournalEntry.user = relationship("User", back_populates="journal_entries")

# Export all models and utilities
__all__ = [
    "Base", 
    "engine", 
    "get_db", 
    "User", 
    "JournalEntry"
]