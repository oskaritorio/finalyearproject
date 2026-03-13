from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

# Import our API routers
from app.api import journal  # NEW - import journal endpoints

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting up...")
    
    # Import here to avoid circular imports
    from app.models.base import engine, Base
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Database tables ready")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    await engine.dispose()

# Create FastAPI app
app = FastAPI(
    title="Mental Wellbeing API",
    description="Backend for mental wellbeing application with journaling and chat support",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register routers - NEW
app.include_router(journal.router)  # Adds all /journal endpoints

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Mental Wellbeing API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "journal": "/journal",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "running"
    }

@app.get("/health/db")
async def db_health():
    """Check database connection"""
    try:
        from app.models.base import AsyncSessionLocal
        from sqlalchemy import text
        
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}