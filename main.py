from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.core.config import get_settings

# Load environment variables
load_dotenv()

# Get settings
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Wallet API starting up...")
    
    # Try to create database tables if database is configured
    try:
        if settings.DATABASE_URL and "localhost" not in settings.DATABASE_URL:
            from app.core.database import create_tables
            await create_tables()
            print("✅ Database tables created successfully!")
        else:
            print("⚠️  Database not configured - running in demo mode")
            print("   Set DATABASE_URL in .env file to enable database features")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("   App will run in demo mode - set up database for full functionality")
    
    print(f"📊 API Documentation: http://localhost:{settings.PORT}/docs")
    
    yield
    
    # Shutdown
    print("👋 Wallet API shutting down...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Wallet API",
    description="Personal Finance Management API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "*.herokuapp.com"]
)

# Health check endpoint
@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "message": "Wallet API is running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database_configured": bool(settings.DATABASE_URL and "localhost" not in settings.DATABASE_URL)
    }

# Include API router only if we can import it (database might not be set up)
try:
    from app.api.v1.api import api_router
    app.include_router(api_router, prefix="/api/v1")
    print("✅ API routes loaded successfully")
except Exception as e:
    print(f"⚠️  API routes not loaded: {e}")
    
    # Add a demo endpoint if database isn't working
    @app.get("/demo")
    async def demo_endpoint():
        return {
            "message": "Demo mode - database not configured",
            "setup_instructions": "Create .env file with DATABASE_URL to enable full functionality"
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 