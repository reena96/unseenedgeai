"""Audio file and transcript models."""

from sqlalchemy import String, ForeignKey, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base, TimestampMixin, UUIDMixin


class AudioFile(Base, UUIDMixin, TimestampMixin):
    """Audio file metadata (actual files stored in Cloud Storage)."""

    __tablename__ = "audio_files"

    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id"), nullable=False, index=True)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)  # GCS path
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # classroom, interview, etc.
    recording_date: Mapped[str] = mapped_column(String(50), nullable=True)

    # Processing status
    transcription_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True
    )  # pending, processing, completed, failed

    # Relationships
    student = relationship("Student", back_populates="audio_files")
    transcripts: Mapped["Transcript"] = relationship("Transcript", back_populates="audio_file", uselist=False)

    def __repr__(self):
        return f"<AudioFile {self.id} for Student {self.student_id}>"
