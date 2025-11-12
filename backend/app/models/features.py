"""Feature extraction models for ML pipeline."""

from sqlalchemy import String, ForeignKey, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Dict, Any, Optional

from app.models.base import Base, TimestampMixin, UUIDMixin


class LinguisticFeatures(Base, UUIDMixin, TimestampMixin):
    """Extracted linguistic features from transcripts."""

    __tablename__ = "linguistic_features"

    transcript_id: Mapped[str] = mapped_column(String(36), ForeignKey("transcripts.id"), nullable=False, unique=True)
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id"), nullable=False, index=True)

    # LIWC categories (Linguistic Inquiry and Word Count)
    empathy_markers: Mapped[int] = mapped_column(Integer, default=0)
    problem_solving_language: Mapped[int] = mapped_column(Integer, default=0)
    perseverance_indicators: Mapped[int] = mapped_column(Integer, default=0)
    social_processes: Mapped[int] = mapped_column(Integer, default=0)
    cognitive_processes: Mapped[int] = mapped_column(Integer, default=0)

    # Sentiment scores
    positive_sentiment: Mapped[float] = mapped_column(Float, default=0.0)
    negative_sentiment: Mapped[float] = mapped_column(Float, default=0.0)

    # Syntactic complexity
    avg_sentence_length: Mapped[float] = mapped_column(Float, default=0.0)
    syntactic_complexity: Mapped[float] = mapped_column(Float, default=0.0)

    # Word embeddings (stored as JSON for flexibility)
    word_embeddings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # All features as JSON for ML models
    features_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Relationships
    transcript = relationship("Transcript", back_populates="linguistic_features")

    def __repr__(self):
        return f"<LinguisticFeatures for Transcript {self.transcript_id}>"


class BehavioralFeatures(Base, UUIDMixin, TimestampMixin):
    """Aggregated behavioral features from game telemetry."""

    __tablename__ = "behavioral_features"

    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("game_sessions.id"), nullable=False)

    # Task completion metrics
    task_completion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    time_efficiency: Mapped[float] = mapped_column(Float, default=0.0)

    # Persistence and resilience
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    recovery_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # Focus and self-regulation
    distraction_resistance: Mapped[float] = mapped_column(Float, default=0.0)
    focus_duration: Mapped[float] = mapped_column(Float, default=0.0)

    # Collaboration
    collaboration_indicators: Mapped[int] = mapped_column(Integer, default=0)
    leadership_indicators: Mapped[int] = mapped_column(Integer, default=0)

    # All features as JSON for ML models
    features_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Relationships
    session = relationship("GameSession")

    def __repr__(self):
        return f"<BehavioralFeatures for Student {self.student_id}, Session {self.session_id}>"
