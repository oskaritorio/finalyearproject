from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, Text
from datetime import datetime
import uuid
from .base import Base

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    encrypted_content = Column(Text, nullable=False)
    mood_score = Column(Integer, nullable=False)
    
    # Simple sentiment analysis fields
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(20), nullable=True)
    
    word_count = Column(Integer, default=0)
    tags = Column(String(200), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<JournalEntry {self.id[:8]} - Mood: {self.mood_score} - Sentiment: {self.sentiment_label}>"