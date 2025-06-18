import asyncio
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time

from app.api.v1.api import api_router
from app.core.database import create_tables, close_db, check_database_health, analyze_database
from app.core.cache import initialize_cache, cleanup_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with optimizations"""
    # Startup
    logger.info("🚀 Starting Wallet Backend Application...")
    
    try:
        # Initialize database
        await create_tables()
        logger.info("✅ Database tables created/verified")
        
        # Initialize cache system
        await initialize_cache()
        logger.info("✅ Cache system initialized")
        
        # Run database optimizations
        await analyze_database()
        logger.info("✅ Database optimizations applied")
        
        # Health check
        if await check_database_health():
            logger.info("✅ Database health check passed")
        else:
            logger.warning("⚠️ Database health check failed")
        
        logger.info("🎉 Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Wallet Backend Application...")
    
    try:
        await cleanup_cache()
        logger.info("✅ Cache cleanup completed")
        
        await close_db()
        logger.info("✅ Database connections closed")
        
        logger.info("👋 Application shutdown completed")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

# Create FastAPI application with optimizations
app = FastAPI(
    title="Personal Finance Wallet API",
    description="A comprehensive personal finance management API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add performance middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header for performance monitoring"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests (> 1 second)
    if process_time > 1.0:
        logger.warning(f"Slow request: {request.method} {request.url} took {process_time:.2f}s")
    
    return response

# Add GZIP compression for better performance
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add CORS middleware with optimized settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Application health check endpoint"""
    try:
        db_healthy = await check_database_health()
        
        return JSONResponse(
            status_code=200 if db_healthy else 503,
            content={
                "status": "healthy" if db_healthy else "unhealthy",
                "database": "connected" if db_healthy else "disconnected",
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )

# Metrics endpoint for monitoring
@app.get("/metrics")
async def get_metrics():
    """Application metrics endpoint"""
    try:
        # You can expand this with more metrics
        import psutil
        import os
        
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "process_id": os.getpid(),
            "timestamp": time.time()
        }
    except ImportError:
        return {
            "message": "Metrics require psutil package",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": time.time()
        }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with logging"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url),
            "timestamp": time.time()
        }
    )

if __name__ == "__main__":
    # Production-ready server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload for production
        workers=1,  # Single worker for SQLite, increase for PostgreSQL
        access_log=True,
        log_level="info",
        loop="uvloop",  # Use uvloop for better performance (install with: pip install uvloop)
        http="httptools"  # Use httptools for better HTTP parsing (install with: pip install httptools)
    ) 