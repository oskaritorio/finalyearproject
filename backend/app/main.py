from fastapi import FastAPI

app = FastAPI(
    title="Mental Wellbeing API",
    description="Backend for mental wellbeing application",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "Mental Wellbeing API",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}