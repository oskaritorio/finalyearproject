
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from datetime import datetime

#Import our models and schemas
from app.models.base import get_db
from app.models.journal import JournalEntry
from app.schemas.journal import (
    JournalEntryCreate,
    JournalEntryResponse,
    JournalEntryUpdate,
    JournalEntryList
)

#Create a router - this groups all journal-related endpoints
router = APIRouter(
    prefix="/journal",      #All endpoints will start with /journal
    tags=["journal"],       #Groups them in Swagger UI
    responses={404: {"description": "Not found"}}  # Default error response
)

#CREATE a new journal entry
@router.post("/", 
             response_model=JournalEntryResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create a new journal entry",
             description="Saves a journal entry to the database")
async def create_journal_entry(
    entry: JournalEntryCreate,  #FastAPI automatically validates using this schema
    user_id: str = "test-user-id",  # TODO: Replace with real auth later
    db: AsyncSession = Depends(get_db)  #Gets database session
):
    
    try:
        #Create a new database record
        db_entry = JournalEntry(
            id=str(uuid.uuid4()),  #Generate unique ID
            user_id=user_id,
            encrypted_content=entry.encrypted_content,
            mood_score=entry.mood_score,
            tags=entry.tags,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to database
        db.add(db_entry)
        await db.commit()  # Save changes
        await db.refresh(db_entry)  # Get updated data (like created_at)
        
        return db_entry
        
    except Exception as e:
        # If something goes wrong, undo any changes
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create journal entry: {str(e)}"
        )

# 📖 READ all journal entries for a user
@router.get("/", 
            response_model=JournalEntryList,
            summary="Get all journal entries",
            description="Returns all journal entries for the current user")
async def get_journal_entries(
    skip: int = 0,  # For pagination: how many to skip
    limit: int = 100,  # For pagination: max number to return
    user_id: str = "test-user-id",  # TODO: Replace with real auth
    db: AsyncSession = Depends(get_db)
):
   
    try:
        from sqlalchemy import select, func
        
        # Count total entries for this user
        count_query = select(func.count()).select_from(JournalEntry).where(
            JournalEntry.user_id == user_id
        )
        total = await db.scalar(count_query)
        
        # Get entries with pagination
        query = select(JournalEntry).where(
            JournalEntry.user_id == user_id
        ).order_by(
            JournalEntry.created_at.desc()  # Most recent first
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        entries = result.scalars().all()
        
        return {
            "entries": entries,
            "total": total or 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch journal entries: {str(e)}"
        )

# 📖 READ a single journal entry by ID
@router.get("/{entry_id}", 
            response_model=JournalEntryResponse,
            summary="Get a specific journal entry",
            description="Returns a single journal entry by its ID")
async def get_journal_entry(
    entry_id: str,
    user_id: str = "test-user-id",  # TODO: Replace with real auth
    db: AsyncSession = Depends(get_db)
):
   
    try:
        from sqlalchemy import select
        
        query = select(JournalEntry).where(
            JournalEntry.id == entry_id,
            JournalEntry.user_id == user_id  # Ensure user owns this entry
        )
        result = await db.execute(query)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        
        return entry
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch journal entry: {str(e)}"
        )

# ✏️ UPDATE a journal entry
@router.patch("/{entry_id}", 
              response_model=JournalEntryResponse,
              summary="Update a journal entry",
              description="Updates an existing journal entry")
async def update_journal_entry(
    entry_id: str,
    entry_update: JournalEntryUpdate,
    user_id: str = "test-user-id",  # TODO: Replace with real auth
    db: AsyncSession = Depends(get_db)
):
    
    try:
        from sqlalchemy import select
        
        # Find the entry
        query = select(JournalEntry).where(
            JournalEntry.id == entry_id,
            JournalEntry.user_id == user_id
        )
        result = await db.execute(query)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        
        # Update only fields that were sent
        update_data = entry_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entry, field, value)
        
        # Update timestamp
        entry.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(entry)
        
        return entry
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update journal entry: {str(e)}"
        )

# 🗑️ DELETE a journal entry
@router.delete("/{entry_id}", 
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a journal entry",
               description="Deletes an existing journal entry")
async def delete_journal_entry(
    entry_id: str,
    user_id: str = "test-user-id",  # TODO: Replace with real auth
    db: AsyncSession = Depends(get_db)
):
   
    try:
        from sqlalchemy import select
        
        # Find the entry
        query = select(JournalEntry).where(
            JournalEntry.id == entry_id,
            JournalEntry.user_id == user_id
        )
        result = await db.execute(query)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        
        # Delete it
        await db.delete(entry)
        await db.commit()
        
        return None  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete journal entry: {str(e)}"
        )