from sqlalchemy import Column, String, DateTime
from datetime import datetime
import uuid
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)