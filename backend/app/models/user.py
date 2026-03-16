from sqlalchemy import Column, String, DateTime,Boolean
from datetime import datetime
import uuid
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    #passwords - stored in hash not the real password

    hashed_passoword = Column(String(200), nullable = False)

    #user statuses in checking if running or not
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"