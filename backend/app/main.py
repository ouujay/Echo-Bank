from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api import voice, transfers, recipients, voice_orchestrator, companies

app = FastAPI(
    title="EchoBank API",
    description="Voice-powered banking assistant API - Integrates into existing bank apps",
    version="2.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("EchoBank API started successfully!")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
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
# Company Registration - Banks sign up here
app.include_router(companies.router)

# Main Voice Orchestrator - Primary integration endpoint for banks
app.include_router(voice_orchestrator.router)

# Developer 2: Transfers and Recipients endpoints (legacy/direct access)
app.include_router(transfers.router)
app.include_router(recipients.router)

# Verify all routers are loaded
print(f"All API routers loaded successfully! Total routes: {len(app.routes)}")
