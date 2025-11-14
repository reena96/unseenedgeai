"""Telemetry ingestion endpoints for game events."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, ValidationError
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.endpoints.auth import get_current_user, TokenData
from app.core.database import get_db
from app.services.telemetry_processor import TelemetryProcessor
from app.schemas.telemetry import (
    TelemetryEventCreate,
    TelemetryBatchCreate,
)

router = APIRouter()
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


class TelemetryResponse(BaseModel):
    """Telemetry ingestion response."""

    status: str
    received_count: int
    batch_id: str
    message: str


@router.post(
    "/telemetry/events",
    response_model=TelemetryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest single telemetry event",
    description="Receive and process a single game telemetry event",
)
@limiter.limit("100/minute")
async def ingest_event(
    request: Request,
    event: TelemetryEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Ingest a single telemetry event with validation."""
    try:
        processor = TelemetryProcessor(db)

        # Ensure session exists
        await processor.get_or_create_session(
            student_id=str(event.student_id),
            session_id=str(event.session_id),
            mission_id=event.mission_id,
            game_version=event.game_version,
        )

        # Process the event
        await processor.process_event(
            student_id=str(event.student_id),
            event_type=event.event_type,
            event_data=event.data,
            session_id=str(event.session_id),
            mission_id=event.mission_id,
            timestamp=event.timestamp,
            event_id=str(event.event_id),  # Pass event_id for deduplication
        )

        await db.commit()

        return TelemetryResponse(
            status="processed",
            received_count=1,
            batch_id=str(event.event_id),
            message="Event processed and stored successfully",
        )
    except ValidationError as e:
        logger.error(f"Validation error for telemetry event: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation failed: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Failed to process telemetry event: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process event: {str(e)}",
        )


@router.post(
    "/telemetry/batch",
    response_model=TelemetryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest batch of telemetry events",
    description="Receive and process multiple game telemetry events in a single request",
)
@limiter.limit("10/minute")
async def ingest_batch(
    request: Request,
    batch: TelemetryBatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Ingest a batch of telemetry events with validation."""
    try:
        processor = TelemetryProcessor(db)

        # Ensure sessions exist for all unique session_id/student_id combinations
        sessions_created = set()
        for event in batch.events:
            session_key = (str(event.student_id), str(event.session_id))
            if session_key not in sessions_created:
                await processor.get_or_create_session(
                    student_id=str(event.student_id),
                    session_id=str(event.session_id),
                    mission_id=event.mission_id,
                    game_version=getattr(event, "game_version", "1.0.0"),
                )
                sessions_created.add(session_key)

        # Convert Pydantic models to dicts for processing
        event_dicts = []
        for event in batch.events:
            event_dicts.append(
                {
                    "event_id": str(event.event_id),  # Add event_id for deduplication
                    "student_id": str(event.student_id),
                    "event_type": event.event_type,
                    "data": event.data,
                    "session_id": str(event.session_id),
                    "mission_id": event.mission_id,
                    "timestamp": event.timestamp,
                }
            )

        # Process batch
        processed_events = await processor.process_batch(
            events=event_dicts,
            batch_id=str(batch.batch_id),
        )

        return TelemetryResponse(
            status="processed",
            received_count=len(processed_events),
            batch_id=str(batch.batch_id),
            message=(
                f"Batch processed: {len(processed_events)}/"
                f"{len(batch.events)} events stored successfully"
            ),
        )
    except ValidationError as e:
        logger.error(f"Validation error for telemetry batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation failed: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Failed to process telemetry batch: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process batch: {str(e)}",
        )


@router.post(
    "/telemetry/session/{session_id}/close",
    status_code=status.HTTP_200_OK,
    summary="Close game session",
    description="Close a game session and extract behavioral features",
)
async def close_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Close a game session and trigger behavioral feature extraction."""
    try:
        processor = TelemetryProcessor(db)
        session = await processor.close_session(session_id)

        return {
            "session_id": session_id,
            "status": "closed",
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "message": "Session closed and behavioral features extracted",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to close session: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close session: {str(e)}",
        )


@router.get(
    "/telemetry/status/{batch_id}",
    status_code=status.HTTP_200_OK,
    summary="Get batch processing status",
    description="Check the processing status of a telemetry batch",
)
async def get_batch_status(
    batch_id: str, current_user: TokenData = Depends(get_current_user)
):
    """Get processing status of a telemetry batch."""
    # This would require a job tracking system (e.g., Celery with Redis)
    # For now, return a simple response
    return {
        "batch_id": batch_id,
        "status": "completed",
        "received_at": datetime.now(timezone.utc).isoformat(),
        "message": "Batch processing completed",
    }
