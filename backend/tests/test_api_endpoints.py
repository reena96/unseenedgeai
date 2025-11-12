"""Tests for API endpoints."""

import pytest


@pytest.mark.unit
def test_root_endpoint(client):
    """Test root endpoint returns correct information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "MASS API"
    assert "version" in data
    assert data["status"] == "operational"
    assert "docs" in data


@pytest.mark.integration
def test_openapi_json(client):
    """Test OpenAPI JSON schema is accessible."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "MASS API"
    assert "paths" in data
    assert len(data["paths"]) > 0


@pytest.mark.integration
def test_swagger_ui_docs(client):
    """Test Swagger UI documentation is accessible."""
    response = client.get("/api/v1/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.integration
def test_redoc_docs(client):
    """Test ReDoc documentation is accessible."""
    response = client.get("/api/v1/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
