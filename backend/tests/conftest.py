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
async def async_client():
    """Create an async HTTP client for testing async endpoints with database fixtures."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


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
async def test_student(db_session, test_school, test_teacher):
    """Create a test student with school and teacher relationships."""
    student = Student(
        id=str(uuid.uuid4()),
        first_name="Test",
        last_name="Student",
        grade_level=5,
        school_id=test_school.id,
        teacher_id=test_teacher.id,
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
