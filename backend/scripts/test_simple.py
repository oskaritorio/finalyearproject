#!/usr/bin/env python
"""
Simple database test
"""
import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).parent.parent))

from app.models.base import AsyncSessionLocal

async def test_connection():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        value = result.scalar()
        print(f"✅ Database connection test: {value}")
        
        #List tables
        result = await session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = result.fetchall()
        print("📊 Tables found:")
        for table in tables:
            print(f"   - {table[0]}")

if __name__ == "__main__":
    asyncio.run(test_connection())