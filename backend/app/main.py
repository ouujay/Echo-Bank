from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="EchoBank API",
    description="Voice-powered banking assistant API",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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

# Import routers here when created
# from app.api import voice, transfers, auth
# app.include_router(voice.router, prefix="/api/v1/voice", tags=["voice"])
# app.include_router(transfers.router, prefix="/api/v1/transfers", tags=["transfers"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
