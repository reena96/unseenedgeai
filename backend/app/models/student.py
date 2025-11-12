"""Student model."""

from sqlalchemy import String, Integer, Boolean, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import date

from app.models.base import Base, TimestampMixin, UUIDMixin


class Student(Base, UUIDMixin, TimestampMixin):
    """Student entity."""

    __tablename__ = "students"

    # Personal information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Academic information
    grade_level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    student_id_external: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)

    # Demographics (for equity analysis)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ethnicity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Foreign keys
    school_id: Mapped[str] = mapped_column(String(36), ForeignKey("schools.id"), nullable=False, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    # Relationships
    school = relationship("School", back_populates="students")
    user = relationship("User")
    game_sessions: Mapped[List["GameSession"]] = relationship("GameSession", back_populates="student")
    audio_files: Mapped[List["AudioFile"]] = relationship("AudioFile", back_populates="student")
    skill_assessments: Mapped[List["SkillAssessment"]] = relationship("SkillAssessment", back_populates="student")
    rubric_assessments: Mapped[List["RubricAssessment"]] = relationship("RubricAssessment", back_populates="student")

    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name} (Grade {self.grade_level})>"
