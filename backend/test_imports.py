
try:
    from sqlalchemy.orm import declarative_base
    from sqlalchemy.ext.asyncio import create_async_engine
    print("✅ SQLAlchemy imports working!")
except ImportError as e:
    print(f"❌ Import error: {e}")

print("Testing model imports...")

try:
    from app.models import Base, engine, get_db, User, JournalEntry
    print("✅ All models imported successfully!")
    
    print(f"✅ User model: {User.__tablename__}")
    print(f"✅ JournalEntry model: {JournalEntry.__tablename__}")
    
    # Check relationships
    if hasattr(User, 'journal_entries'):
        print("✅ User.journal_entries relationship exists")
    if hasattr(JournalEntry, 'user'):
        print("✅ JournalEntry.user relationship exists")
        
except Exception as e:
    print(f"❌ Import error: {e}")