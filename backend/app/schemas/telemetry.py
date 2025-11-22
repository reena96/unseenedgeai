"""Pydantic schemas for telemetry validation."""

from pydantic import BaseModel, Field, UUID4, field_validator, ConfigDict
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4


class TelemetryEventCreate(BaseModel):
    """Schema for creating a single telemetry event."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "event_id": "550e8400-e29b-41d4-a716-446655440001",
                    "student_id": "550e8400-e29b-41d4-a716-446655440099",
                    "event_type": "mission_start",
                    "timestamp": "2025-01-19T12:00:00Z",
                    "data": {"mission_name": "Empathy Quest", "difficulty": "medium"},
                    "session_id": "550e8400-e29b-41d4-a716-446655440100",
                    "mission_id": "mission_001",
                    "game_version": "1.0.0",
                },
                {
                    "event_id": "550e8400-e29b-41d4-a716-446655440002",
                    "student_id": "550e8400-e29b-41d4-a716-446655440099",
                    "event_type": "choice_made",
                    "timestamp": "2025-01-19T12:05:00Z",
                    "data": {
                        "choice_id": "choice_a",
                        "choice_text": "Help the character",
                        "time_taken_seconds": 15,
                    },
                    "session_id": "550e8400-e29b-41d4-a716-446655440100",
                    "mission_id": "mission_001",
                    "game_version": "1.0.0",
                },
            ]
        },
    )

    event_id: UUID4 = Field(..., description="Unique event identifier")
    student_id: UUID4 = Field(..., description="Student identifier")
    event_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type of event (e.g., mission_start, choice_made)",
        examples=["mission_start", "choice_made", "mission_complete"],
    )
    timestamp: datetime = Field(..., description="Event timestamp (UTC)")
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data",
        examples=[{"mission_name": "Empathy Quest", "difficulty": "medium"}],
    )
    session_id: UUID4 = Field(..., description="Game session identifier")
    mission_id: Optional[str] = Field(
        None,
        max_length=100,
        description="Mission identifier if applicable",
        examples=["mission_001", "mission_002"],
    )
    game_version: str = Field(
        default="1.0.0",
        max_length=20,
        description="Game version",
        examples=["1.0.0", "1.1.0"],
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

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "events": [
                        {
                            "event_id": "550e8400-e29b-41d4-a716-446655440001",
                            "student_id": "550e8400-e29b-41d4-a716-446655440099",
                            "event_type": "mission_start",
                            "timestamp": "2025-01-19T12:00:00Z",
                            "data": {"mission_name": "Empathy Quest"},
                            "session_id": "550e8400-e29b-41d4-a716-446655440100",
                            "mission_id": "mission_001",
                            "game_version": "1.0.0",
                        }
                    ],
                    "batch_id": "550e8400-e29b-41d4-a716-446655440200",
                    "client_version": "1.0.0",
                }
            ]
        },
    )

    events: List[TelemetryEventCreate] = Field(
        ..., description="List of telemetry events"
    )
    batch_id: UUID4 = Field(..., description="Batch identifier")
    client_version: str = Field(
        ...,
        max_length=20,
        description="Game client version",
        examples=["1.0.0", "1.1.0"],
    )

    @field_validator("events")
    @classmethod
    def validate_batch_size(
        cls, v: List[TelemetryEventCreate]
    ) -> List[TelemetryEventCreate]:
        """Validate batch is not too large."""
        if len(v) > 1000:
            raise ValueError(f"Batch too large: {len(v)} events (max 1000)")
        if len(v) == 0:
            raise ValueError("Batch must contain at least one event")
        return v


class SessionCloseRequest(BaseModel):
    """Schema for closing a game session."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440100",
                    "reason": "User logged out",
                },
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440101",
                    "reason": "Session timeout",
                },
            ]
        },
    )

    session_id: UUID4 = Field(..., description="Session identifier to close")
    reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Reason for closing session",
        examples=["User logged out", "Session timeout", "Game completed"],
    )
