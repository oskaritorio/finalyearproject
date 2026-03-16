from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api import journal
from app.auth import routes as auth_routes  # Add this line

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.models.base import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title="Mental Wellbeing API",
    version="1.0.0",
    lifespan=lifespan
)

# Register routes
app.include_router(auth_routes.router)  # Add this line
app.include_router(journal.router)

@app.get("/")
async def root():
    return {"message": "Mental Wellbeing API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}