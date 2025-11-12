"""Game telemetry models for Flourish Academy."""

from sqlalchemy import String, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Dict, Any
from datetime import datetime

from app.models.base import Base, TimestampMixin, UUIDMixin


class GameSession(Base, UUIDMixin, TimestampMixin):
    """Game session tracking."""

    __tablename__ = "game_sessions"

    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id"), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    mission_id: Mapped[str] = mapped_column(String(100), nullable=True)
    game_version: Mapped[str] = mapped_column(String(20), nullable=False)

    # Relationships
    student = relationship("Student", back_populates="game_sessions")
    telemetry_events: Mapped[List["GameTelemetry"]] = relationship("GameTelemetry", back_populates="session")

    __table_args__ = (
        Index("idx_game_session_student_started", "student_id", "started_at"),
    )

    def __repr__(self):
        return f"<GameSession {self.id} for Student {self.student_id}>"


class GameTelemetry(Base, UUIDMixin):
    """
    Game telemetry events (TimescaleDB hypertable).
    This table will be converted to a hypertable for efficient time-series queries.
    """

    __tablename__ = "game_telemetry"

    # Core fields
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        primary_key=False  # TimescaleDB uses composite primary key with timestamp
    )
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("game_sessions.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Event data (JSONB for flexible schema)
    event_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Optional contextual fields
    mission_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    choice_made: Mapped[str] = mapped_column(String(255), nullable=True)

    # Relationships
    session = relationship("GameSession", back_populates="telemetry_events")

    __table_args__ = (
        Index("idx_telemetry_student_timestamp", "student_id", "timestamp"),
        Index("idx_telemetry_event_type_timestamp", "event_type", "timestamp"),
    )

    def __repr__(self):
        return f"<GameTelemetry {self.event_type} at {self.timestamp}>"
