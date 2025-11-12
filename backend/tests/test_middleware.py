"""Tests for middleware functionality."""

import pytest


@pytest.mark.unit
def test_request_id_middleware(client):
    """Test that request ID is added to responses."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) > 0


@pytest.mark.unit
def test_request_id_passthrough(client):
    """Test that provided request ID is preserved."""
    custom_id = "custom-request-id-12345"
    response = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id


@pytest.mark.unit
def test_process_time_header(client):
    """Test that process time header is added."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0


@pytest.mark.unit
def test_error_handler_middleware(client):
    """Test error handler middleware catches exceptions."""
    # Test 404 error handling
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"] == "Not Found"
