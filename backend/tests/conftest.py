"""Pytest configuration and shared fixtures."""

import os
import uuid
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

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
from app.models.game_telemetry import GameSession, GameTelemetry  # noqa: F401
from app.models.features import BehavioralFeatures, LinguisticFeatures  # noqa: F401
from app.models.assessment import (  # noqa: F401
    SkillAssessment,
    RubricAssessment,
    Evidence,
)


# Determine which database backend to use for tests
# Default to PostgreSQL since we have it running - only use SQLite if explicitly disabled
USE_POSTGRES_CONTAINER = os.environ.get("USE_POSTGRES_TESTS", "true").lower() == "true"


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(db_session):
    """Create an async HTTP client for testing async endpoints with database fixtures."""
    from app.core.database import get_db
    from unittest.mock import AsyncMock
    from datetime import datetime, timezone

    # Mock commit and refresh on the shared db_session to prevent transaction closure
    original_commit = db_session.commit
    original_refresh = db_session.refresh
    db_session.commit = AsyncMock(return_value=None)

    # Mock refresh to set timestamps if they're None
    async def mock_refresh(obj):
        if hasattr(obj, "created_at") and obj.created_at is None:
            obj.created_at = datetime.now(timezone.utc)
        if hasattr(obj, "updated_at") and obj.updated_at is None:
            obj.updated_at = datetime.now(timezone.utc)
        return None

    db_session.refresh = AsyncMock(side_effect=mock_refresh)

    # Override the get_db dependency to use the test session
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    # Restore original methods and clean up
    db_session.commit = original_commit
    db_session.refresh = original_refresh
    app.dependency_overrides.clear()


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


# PostgreSQL container fixture (session-scoped for performance)
@pytest.fixture(scope="session")
def postgres_container():
    """
    Create a PostgreSQL test container for integration tests.

    Set USE_POSTGRES_TESTS=true to enable.
    Docker must be running.
    """
    if not USE_POSTGRES_CONTAINER:
        pytest.skip(
            "PostgreSQL container tests disabled. Set USE_POSTGRES_TESTS=true to enable."
        )

    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


# Database fixtures for async testing
@pytest_asyncio.fixture
async def test_engine(postgres_container):
    """
    Create test database engine.

    Uses PostgreSQL container if USE_POSTGRES_TESTS=true,
    otherwise falls back to SQLite in-memory.
    """
    if USE_POSTGRES_CONTAINER:
        # Use PostgreSQL test container
        db_url = postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
        engine = create_async_engine(db_url, poolclass=NullPool, echo=False)
    else:
        # Use in-memory SQLite for fast tests (some integration tests may fail)
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:", poolclass=NullPool, echo=False
        )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Create a test database session with proper transaction handling."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session() as session:
        # Start a transaction
        async with session.begin():
            yield session
            # Rollback happens automatically when exiting the context


# Test data fixtures for foreign key relationships
@pytest_asyncio.fixture
async def test_school(db_session):
    """Create a test school."""
    school = School(
        id=str(uuid.uuid4()),
        name="Test School",
        district="Test District",
        city="Test City",
        state="CA",
        zip_code="12345",
    )
    db_session.add(school)
    await db_session.flush()  # Flush to database without committing
    return school


@pytest_asyncio.fixture
async def test_user(db_session, test_school):
    """Create a test user account for teacher."""
    from app.models.user import UserRole

    user = User(
        id=str(uuid.uuid4()),
        email="teacher@test.com",
        password_hash="$2b$12$test_hashed_password",  # Dummy bcrypt hash
        first_name="Test",
        last_name="Teacher",
        role=UserRole.TEACHER,
        school_id=test_school.id,
    )
    db_session.add(user)
    await db_session.flush()  # Flush to database without committing
    return user


@pytest_asyncio.fixture
async def test_teacher(db_session, test_school, test_user):
    """Create a test teacher with user account and school."""
    teacher = Teacher(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        school_id=test_school.id,
        first_name="Test",
        last_name="Teacher",
        email="test.teacher@test.com",
    )
    db_session.add(teacher)
    await db_session.flush()  # Flush to database without committing
    return teacher


@pytest_asyncio.fixture
async def test_student(db_session, test_school):
    """Create a test student with school relationship."""
    student = Student(
        id=str(uuid.uuid4()),
        first_name="Test",
        last_name="Student",
        grade_level=5,
        school_id=test_school.id,
    )
    db_session.add(student)
    await db_session.flush()  # Flush to database without committing
    return student


@pytest_asyncio.fixture
async def test_audio_file(db_session, test_student):
    """Create a test audio file linked to a student."""
    audio = AudioFile(
        id=str(uuid.uuid4()),
        student_id=test_student.id,
        file_path="gs://test-bucket/test-audio.wav",
        duration_seconds=10.5,
        sample_rate=16000,
        file_size_bytes=168000,
        status="uploaded",
    )
    db_session.add(audio)
    await db_session.flush()  # Flush to database without committing
    return audio


@pytest.fixture
def mock_rate_limiter(monkeypatch):
    """
    Mock slowapi rate limiter for tests.

    The slowapi rate limiter uses in-memory storage that conflicts with
    pytest transaction rollbacks, causing 'closed transaction' errors.
    This fixture mocks the rate limiter to be a no-op during tests.
    """
    from unittest.mock import MagicMock

    mock = MagicMock()
    # Make the limit decorator a no-op that just returns the function unchanged
    mock.limit = lambda *args, **kwargs: lambda f: f

    # Patch the limiter in the telemetry endpoints module
    monkeypatch.setattr("app.api.endpoints.telemetry.limiter", mock)

    return mock


@pytest_asyncio.fixture
async def db_session_no_commit(test_engine):
    """
    Create a test database session with mocked commit for processor tests.

    The TelemetryProcessor.process_batch() method calls commit(), which would
    close the test transaction. This fixture mocks commit() to be a no-op.
    """
    from unittest.mock import AsyncMock

    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session() as session:
        # Start a transaction
        async with session.begin():
            # Mock commit to prevent closing the transaction
            session.commit = AsyncMock(return_value=None)
            yield session
            # Rollback happens automatically when exiting the context


@pytest_asyncio.fixture
async def test_school_no_commit(db_session_no_commit):
    """Create a test school with no-commit session."""
    school = School(
        id=str(uuid.uuid4()),
        name="Test School",
        district="Test District",
        city="Test City",
        state="CA",
        zip_code="12345",
    )
    db_session_no_commit.add(school)
    await db_session_no_commit.flush()
    return school


@pytest_asyncio.fixture
async def test_student_no_commit(db_session_no_commit, test_school_no_commit):
    """Create a test student with no-commit session."""
    student = Student(
        id=str(uuid.uuid4()),
        first_name="Test",
        last_name="Student",
        grade_level=5,
        school_id=test_school_no_commit.id,
    )
    db_session_no_commit.add(student)
    await db_session_no_commit.flush()
    return student
