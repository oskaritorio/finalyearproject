from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class JournalEntryBase(BaseModel):
    """
    Base schema with fields that every journal entry must have
    This is like a template - other schemas will inherit from it
    """
    encrypted_content: str  # The actual journal text (encrypted)
    mood_score: int         # 1-5 scale
    tags: Optional[str] = None  # Optional: "work,family,health"

# Schema for CREATING a new journal entry
class JournalEntryCreate(JournalEntryBase):
    """
    When a user POSTs to /journal, this is what we expect
    Inherits all fields from JournalEntryBase
    No extra fields needed for creation
    """
    pass

# Schema for UPDATING an existing journal entry
class JournalEntryUpdate(BaseModel):
    """
    All fields are optional for updates
    Users can update just one field if they want
    """
    encrypted_content: Optional[str] = None
    mood_score: Optional[int] = None
    tags: Optional[str] = None

# Schema for RETURNING a journal entry (what the API sends back)
class JournalEntryResponse(JournalEntryBase):
    """
    When we send journal data back to the frontend, include these extra fields
    """
    id: str                 # Database ID
    user_id: str            # Who owns this entry
    sentiment_score: Optional[float] = None  # From AI analysis
    created_at: datetime    # When it was written
    updated_at: datetime    # Last modified
    
    # This tells Pydantic to work with SQLAlchemy models
    class Config:
        from_attributes = True

# Schema for a list of journal entries
class JournalEntryList(BaseModel):
    """
    For returning multiple entries (like /journal endpoint)
    """
    entries: List[JournalEntryResponse]
    total: int  # Total count (for pagination later)