"""Transcript model."""

from sqlalchemy import String, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Dict, Any, List, Optional

from app.models.base import Base, TimestampMixin, UUIDMixin


class Transcript(Base, UUIDMixin, TimestampMixin):
    """Speech-to-text transcript."""

    __tablename__ = "transcripts"

    audio_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("audio_files.id"), nullable=False, unique=True)
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id"), nullable=False, index=True)

    # Transcript content
    text: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(nullable=False)

    # Transcription metadata
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)  # Average confidence
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, default="en-US")

    # Word-level data (for timestamps and confidence)
    word_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    audio_file = relationship("AudioFile", back_populates="transcripts")
    linguistic_features: Mapped["LinguisticFeatures"] = relationship(
        "LinguisticFeatures",
        back_populates="transcript",
        uselist=False
    )

    def __repr__(self):
        return f"<Transcript {self.id} ({self.word_count} words)>"
