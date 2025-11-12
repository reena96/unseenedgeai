"""Database connection and session management."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Ensure DATABASE_URL uses async driver
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    database_url = database_url.replace("postgres://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
)

# Create session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database with TimescaleDB extensions."""
    from app.models import Base

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Enable TimescaleDB extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

        # Convert game_telemetry to hypertable
        await conn.execute(
            """
            SELECT create_hypertable(
                'game_telemetry',
                'timestamp',
                if_not_exists => TRUE,
                migrate_data => TRUE
            );
        """
        )

        # Create indexes optimized for time-series queries
        await conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_game_telemetry_student_time
            ON game_telemetry (student_id, timestamp DESC);
        """
        )

        await conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_game_telemetry_event_time
            ON game_telemetry (event_type, timestamp DESC);
        """
        )


async def close_db():
    """Close database connections."""
    await engine.dispose()
