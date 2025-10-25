"""
Demo Bank API - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, accounts, recipients, transfers, payments, notifications

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Demo Bank API for EchoBank integration with Paystack transfers",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
@app.on_event("startup")
def startup_event():
    """Create database tables on startup"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started!")
    print(f"📝 API Documentation: http://localhost:{settings.PORT}/docs")


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(accounts.router, prefix=settings.API_V1_PREFIX)
app.include_router(recipients.router, prefix=settings.API_V1_PREFIX)
app.include_router(transfers.router, prefix=settings.API_V1_PREFIX)
app.include_router(payments.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Demo Bank API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
