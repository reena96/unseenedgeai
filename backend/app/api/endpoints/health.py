"""Health check endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime
import sys
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


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
        python_version=(
            f"{sys.version_info.major}.{sys.version_info.minor}"
            f".{sys.version_info.micro}"
        ),
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
    services = {}

    # Check OpenAI API key for reasoning generation
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        services["openai_api"] = "configured"
        logger.debug("OpenAI API key is configured")
    else:
        services["openai_api"] = "missing"
        logger.warning("OpenAI API key is not configured")

    # Check Redis connection
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis

            client = redis.from_url(redis_url, socket_connect_timeout=2)
            client.ping()
            services["redis"] = "healthy"
            client.close()
        except Exception as e:
            services["redis"] = f"unhealthy: {str(e)}"
            logger.warning(f"Redis health check failed: {e}")
    else:
        services["redis"] = "not_configured"

    # Database check placeholder
    services["database"] = "unknown"  # TODO: Check database connection

    # Storage check placeholder
    services["storage"] = "unknown"  # TODO: Check Cloud Storage access

    # Determine overall status
    overall_status = "healthy"
    if services.get("openai_api") == "missing":
        overall_status = "degraded"  # Can still function with fallback reasoning

    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="0.1.0",
        python_version=(
            f"{sys.version_info.major}.{sys.version_info.minor}"
            f".{sys.version_info.micro}"
        ),
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
