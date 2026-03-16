from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
import uuid
from .base import Base

class MoodLog(Base):
    __tablename__ = "mood_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    mood_score = Column(Integer, nullable=False)  # 1-5 scale
    note = Column(String(200), nullable=True)     # Optional short note
    created_at = Column(DateTime, default=datetime.utcnow)