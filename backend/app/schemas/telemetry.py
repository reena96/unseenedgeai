"""Pydantic schemas for telemetry validation."""

from pydantic import BaseModel, Field, UUID4, field_validator, ConfigDict
from typing import Dict, Any, List, Optional
from datetime import datetime


class TelemetryEventCreate(BaseModel):
    """Schema for creating a single telemetry event."""

    model_config = ConfigDict(str_strip_whitespace=True)

    event_id: UUID4 = Field(..., description="Unique event identifier")
    student_id: UUID4 = Field(..., description="Student identifier")
    event_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type of event (e.g., mission_start, choice_made)",
    )
    timestamp: datetime = Field(..., description="Event timestamp (UTC)")
    data: Dict[str, Any] = Field(
        default_factory=dict, description="Event-specific data"
    )
    session_id: UUID4 = Field(..., description="Game session identifier")
    mission_id: Optional[str] = Field(
        None, max_length=100, description="Mission identifier if applicable"
    )
    game_version: str = Field(
        default="1.0.0", max_length=20, description="Game version"
    )

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        """Validate event_type contains only lowercase letters and underscores."""
        if not v.replace("_", "").isalnum():
            raise ValueError(
                "event_type must contain only alphanumeric characters and underscores"
            )
        if not v.islower():
            raise ValueError("event_type must be lowercase")
        return v

    @field_validator("data")
    @classmethod
    def validate_data_size(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event_data is not too large."""
        import json

        data_size = len(json.dumps(v))
        if data_size > 10000:  # 10KB limit
            raise ValueError(f"event_data too large: {data_size} bytes (max 10KB)")
        return v

    @field_validator("game_version")
    @classmethod
    def validate_version_format(cls, v: str) -> str:
        """Validate game version follows semver-like pattern."""
        if not v or len(v) > 20:
            raise ValueError("game_version must be 1-20 characters")
        # Basic version validation (allows formats like "1.0.0", "1.0", "v1.2.3")
        return v


class TelemetryBatchCreate(BaseModel):
    """Schema for creating a batch of telemetry events."""

    model_config = ConfigDict(str_strip_whitespace=True)

    events: List[TelemetryEventCreate] = Field(
        ..., description="List of telemetry events"
    )
    batch_id: UUID4 = Field(..., description="Batch identifier")
    client_version: str = Field(
        ..., max_length=20, description="Game client version"
    )

    @field_validator("events")
    @classmethod
    def validate_batch_size(cls, v: List[TelemetryEventCreate]) -> List[TelemetryEventCreate]:
        """Validate batch is not too large."""
        if len(v) > 1000:
            raise ValueError(
                f"Batch too large: {len(v)} events (max 1000)"
            )
        if len(v) == 0:
            raise ValueError("Batch must contain at least one event")
        return v


class SessionCloseRequest(BaseModel):
    """Schema for closing a game session."""

    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: UUID4 = Field(..., description="Session identifier to close")
    reason: Optional[str] = Field(
        None, max_length=200, description="Reason for closing session"
    )
