from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api import voice

app = FastAPI(
    title="EchoBank API",
    description="Voice-powered banking assistant API",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("EchoBank API started successfully!")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "EchoBank API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Register API routers
app.include_router(voice.router)

# Developer 2 will add:
# from app.api import recipients, transfers
# app.include_router(recipients.router)
# app.include_router(transfers.router)
