#!/usr/bin/env python
"""
Initialize database tables - Simplified version
"""
import asyncio
import sys
import os
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).parent.parent))

from app.models.base import engine, Base
from app.models import User, JournalEntry

async def init_db():
    """Create all tables"""
    print("🚀 Creating database tables...")
    
    # Create data directory
    os.makedirs("/app/data", exist_ok=True)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Tables created successfully!")
    
    # List tables
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = result.fetchall()
        print("\n📊 Created tables:")
        for table in tables:
            print(f"   - {table[0]}")

if __name__ == "__main__":
    asyncio.run(init_db())