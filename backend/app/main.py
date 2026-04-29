from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api import journal, mood, chat, user, wellbeing
from app.auth import routes as auth_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    from app.models.base import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database ready")
    yield
    logger.info("Shutting down...")
    await engine.dispose()

app = FastAPI(
    title="Mental Wellbeing API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_routes.router)
app.include_router(journal.router)
app.include_router(mood.router)
app.include_router(chat.router)
app.include_router(user.router)
app.include_router(wellbeing.router)

@app.get("/")
async def root():
    return {"message": "Mental Wellbeing API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}