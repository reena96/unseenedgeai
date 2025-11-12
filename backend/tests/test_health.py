"""Tests for health check endpoints."""

import pytest


@pytest.mark.unit
def test_basic_health_check(client):
    """Test basic health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "python_version" in data


@pytest.mark.unit
def test_detailed_health_check(client):
    """Test detailed health check endpoint."""
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert isinstance(data["services"], dict)


@pytest.mark.unit
def test_readiness_probe(client):
    """Test Kubernetes readiness probe."""
    response = client.get("/api/v1/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True


@pytest.mark.unit
def test_liveness_probe(client):
    """Test Kubernetes liveness probe."""
    response = client.get("/api/v1/liveness")
    assert response.status_code == 200
    data = response.json()
    assert data["alive"] is True
