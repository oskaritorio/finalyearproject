
try:
    from sqlalchemy.orm import declarative_base
    from sqlalchemy.ext.asyncio import create_async_engine
    print("✅ SQLAlchemy imports working!")
except ImportError as e:
    print(f"❌ Import error: {e}")