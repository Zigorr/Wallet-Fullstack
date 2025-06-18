import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./wallet.db")

# Database engine configuration with optimizations
engine_config = {
    "echo": os.getenv("DATABASE_ECHO", "false").lower() == "true",  # SQL logging
    "future": True,  # Use SQLAlchemy 2.0 style
}

# SQLite-specific optimizations
if "sqlite" in DATABASE_URL:
    engine_config.update({
        "poolclass": StaticPool,
        "pool_pre_ping": True,
        "pool_recycle": 300,  # Recycle connections every 5 minutes
        "connect_args": {
            "check_same_thread": False,
            "timeout": 20,  # Connection timeout
            "isolation_level": None,  # Autocommit mode
        },
    })
else:
    # PostgreSQL/MySQL optimizations
    engine_config.update({
        "pool_size": 10,  # Connection pool size
        "max_overflow": 20,  # Max overflow connections
        "pool_pre_ping": True,  # Validate connections before use
        "pool_recycle": 3600,  # Recycle connections every hour
        "echo_pool": False,  # Don't log connection pool events
    })

# Create async engine
engine = create_async_engine(DATABASE_URL, **engine_config)

# Configure SQLite for better performance if using SQLite
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Set SQLite pragmas for better performance"""
        cursor = dbapi_connection.cursor()
        
        # Performance optimizations
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
        cursor.execute("PRAGMA synchronous=NORMAL")  # Faster than FULL, still safe
        cursor.execute("PRAGMA cache_size=10000")  # Increase cache size (10MB)
        cursor.execute("PRAGMA temp_store=MEMORY")  # Store temporary data in memory
        cursor.execute("PRAGMA mmap_size=268435456")  # Memory-mapped I/O (256MB)
        
        # Foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")
        
        # Auto-vacuum for space efficiency
        cursor.execute("PRAGMA auto_vacuum=INCREMENTAL")
        
        cursor.close()
        logger.info("SQLite performance pragmas applied")

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autoflush=False,  # Manual control over when to flush
    autocommit=False,  # Manual transaction control
)

# Create declarative base
Base = declarative_base()

async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def create_tables():
    """Create database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")

# Health check function
async def check_database_health() -> bool:
    """Check if database is healthy"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Database maintenance functions
async def analyze_database():
    """Analyze database for query optimization (SQLite specific)"""
    if "sqlite" in DATABASE_URL:
        try:
            async with AsyncSessionLocal() as session:
                await session.execute("PRAGMA optimize")
                await session.execute("PRAGMA analysis_limit=1000")
                await session.execute("ANALYZE")
                await session.commit()
                logger.info("Database analysis completed")
        except Exception as e:
            logger.error(f"Database analysis failed: {e}")

async def vacuum_database():
    """Vacuum database to reclaim space (SQLite specific)"""
    if "sqlite" in DATABASE_URL:
        try:
            async with AsyncSessionLocal() as session:
                await session.execute("PRAGMA incremental_vacuum")
                await session.commit()
                logger.info("Database vacuum completed")
        except Exception as e:
            logger.error(f"Database vacuum failed: {e}") 