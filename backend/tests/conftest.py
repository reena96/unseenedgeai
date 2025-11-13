"""Pytest configuration and shared fixtures."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.models.base import Base
from app.api.endpoints.auth import create_access_token

# Import all models to register them with Base.metadata
from app.models.user import User  # noqa: F401
from app.models.school import School  # noqa: F401
from app.models.student import Student  # noqa: F401
from app.models.teacher import Teacher  # noqa: F401
from app.models.audio import AudioFile  # noqa: F401
from app.models.transcript import Transcript  # noqa: F401
from app.models.game_telemetry import GameTelemetry  # noqa: F401
from app.models.features import BehavioralFeatures, LinguisticFeatures  # noqa: F401
from app.models.assessment import (  # noqa: F401
    GameSession,
    SkillAssessment,
    RubricAssessment,
    Evidence,
)


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def valid_access_token():
    """Create a valid access token for testing."""
    token_data = {
        "sub": "test-user-123",
        "email": "test@example.com",
        "role": "teacher",
    }
    return create_access_token(token_data)


@pytest.fixture
def auth_headers(valid_access_token):
    """Create authentication headers with valid token."""
    return {"Authorization": f"Bearer {valid_access_token}"}


# Database fixtures for async testing
@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine."""
    # Use in-memory SQLite for fast tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", poolclass=NullPool, echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()  # Rollback any uncommitted changes
        await session.close()
