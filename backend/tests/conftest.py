"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    # TODO: Replace with actual token generation
    return {"Authorization": "Bearer test_token"}
