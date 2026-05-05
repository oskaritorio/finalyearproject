from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class JournalEntryBase(BaseModel):
    encrypted_content: str  # The actual journal text (encrypted)
    mood_score: int         # 1-5 scale
    tags: Optional[str] = None  # Optional: "work,family,health"

#Schema for CREATING a new journal entry
class JournalEntryCreate(JournalEntryBase):
    pass

#Schema for UPDATING an existing journal entry
class JournalEntryUpdate(BaseModel):
    encrypted_content: Optional[str] = None
    mood_score: Optional[int] = None
    tags: Optional[str] = None

#Schema for RETURNING a journal entry (what the API sends back)
class JournalEntryResponse(JournalEntryBase):
    id: str                 # Database ID
    user_id: str            # Who owns this entry
    sentiment_score: Optional[float] = None  # From AI analysis
    created_at: datetime    # When it was written
    updated_at: datetime    # Last modified
    
    #This tells Pydantic to work with SQLAlchemy models
    class Config:
        from_attributes = True

#Schema for a list of journal entries
class JournalEntryList(BaseModel):
    entries: List[JournalEntryResponse]
    total: int  # Total count (for pagination later)