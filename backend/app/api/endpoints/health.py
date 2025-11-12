"""Health check endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime
import sys

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    version: str
    python_version: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response."""

    status: str
    timestamp: datetime
    version: str
    python_version: str
    services: dict


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic application health status",
)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0",
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )


@router.get(
    "/health/detailed",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Detailed health check",
    description="Returns detailed health status including service dependencies",
)
async def detailed_health_check():
    """Detailed health check including service status."""
    # TODO: Add actual service health checks
    services = {
        "database": "unknown",  # TODO: Check database connection
        "redis": "unknown",  # TODO: Check Redis connection
        "storage": "unknown",  # TODO: Check Cloud Storage access
    }

    return DetailedHealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0",
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        services=services,
    )


@router.get(
    "/readiness",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Kubernetes readiness probe endpoint",
)
async def readiness():
    """Readiness probe for Kubernetes."""
    # TODO: Check if application is ready to serve traffic
    return {"ready": True}


@router.get(
    "/liveness",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Kubernetes liveness probe endpoint",
)
async def liveness():
    """Liveness probe for Kubernetes."""
    return {"alive": True}
