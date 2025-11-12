#!/usr/bin/env python
"""Initialize the database with schema and TimescaleDB configuration."""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine
from app.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tables():
    """Create all tables."""
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✓ Tables created successfully")


async def setup_timescaledb():
    """Set up TimescaleDB extension and hypertables."""
    logger.info("Setting up TimescaleDB...")

    async with engine.begin() as conn:
        # Enable TimescaleDB extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
        logger.info("✓ TimescaleDB extension enabled")

        # Convert game_telemetry to hypertable
        try:
            await conn.execute(text("""
                SELECT create_hypertable(
                    'game_telemetry',
                    'timestamp',
                    if_not_exists => TRUE,
                    migrate_data => TRUE
                );
            """))
            logger.info("✓ game_telemetry converted to hypertable")
        except Exception as e:
            logger.warning(f"Hypertable creation warning: {e}")

        # Create time-series optimized indexes
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_game_telemetry_student_time
            ON game_telemetry (student_id, timestamp DESC);
        """))

        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_game_telemetry_event_time
            ON game_telemetry (event_type, timestamp DESC);
        """))

        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_game_telemetry_session_time
            ON game_telemetry (session_id, timestamp DESC);
        """))

        logger.info("✓ Time-series indexes created")

        # Set up continuous aggregates for analytics (optional)
        # This pre-aggregates data for faster queries
        try:
            await conn.execute(text("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS game_telemetry_hourly
                WITH (timescaledb.continuous) AS
                SELECT
                    time_bucket('1 hour', timestamp) AS hour,
                    student_id,
                    event_type,
                    COUNT(*) as event_count
                FROM game_telemetry
                GROUP BY hour, student_id, event_type;
            """))
            logger.info("✓ Continuous aggregate created for hourly stats")
        except Exception as e:
            logger.warning(f"Continuous aggregate warning: {e}")


async def create_sample_data():
    """Create sample data for development."""
    logger.info("Creating sample data...")

    async with engine.begin() as conn:
        # Create sample school
        await conn.execute(text("""
            INSERT INTO schools (id, name, district, city, state, is_active)
            VALUES (
                'school-001',
                'Sample Middle School',
                'Sample District',
                'San Francisco',
                'CA',
                true
            )
            ON CONFLICT (id) DO NOTHING;
        """))

        # Create sample user (teacher)
        await conn.execute(text("""
            INSERT INTO users (id, email, password_hash, first_name, last_name, role, school_id, is_active)
            VALUES (
                'user-001',
                'teacher@example.com',
                '$2b$12$KIXxPZH6LhHR6P8xZC9tqOZYQqU5YZYZh8xZC9tqOZYQqU5YZYZh8',
                'Jane',
                'Doe',
                'teacher',
                'school-001',
                true
            )
            ON CONFLICT (email) DO NOTHING;
        """))

        logger.info("✓ Sample data created")


async def main():
    """Main initialization function."""
    try:
        logger.info("=== Starting Database Initialization ===")

        # Step 1: Create tables
        await create_tables()

        # Step 2: Set up TimescaleDB
        await setup_timescaledb()

        # Step 3: Create sample data (optional)
        await create_sample_data()

        logger.info("=== Database Initialization Complete ===")

    except Exception as e:
        logger.error(f"Error during initialization: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
