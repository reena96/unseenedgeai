"""Skill assessment models."""

import enum
from sqlalchemy import String, ForeignKey, Float, Text, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from app.models.base import Base, TimestampMixin, UUIDMixin


class SkillType(enum.Enum):
    """Non-academic skill types."""

    EMPATHY = "empathy"
    ADAPTABILITY = "adaptability"
    PROBLEM_SOLVING = "problem_solving"
    SELF_REGULATION = "self_regulation"
    RESILIENCE = "resilience"
    COMMUNICATION = "communication"
    COLLABORATION = "collaboration"


class EvidenceType(enum.Enum):
    """Types of evidence supporting skill assessments."""

    LINGUISTIC = "linguistic"
    BEHAVIORAL = "behavioral"
    CONTEXTUAL = "contextual"


class Evidence(Base, UUIDMixin, TimestampMixin):
    """Evidence supporting a skill assessment."""

    __tablename__ = "evidence"

    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("skill_assessments.id"), nullable=False, index=True)
    evidence_type: Mapped[EvidenceType] = mapped_column(Enum(EvidenceType), nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)  # transcript, telemetry, etc.
    content: Mapped[str] = mapped_column(Text, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    assessment = relationship("SkillAssessment", back_populates="evidence")

    def __repr__(self):
        return f"<Evidence {self.evidence_type.value} for Assessment {self.assessment_id}>"


class SkillAssessment(Base, UUIDMixin, TimestampMixin):
    """AI-generated skill assessment."""

    __tablename__ = "skill_assessments"

    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id"), nullable=False, index=True)
    skill_type: Mapped[SkillType] = mapped_column(Enum(SkillType), nullable=False, index=True)

    # Assessment scores
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-1 scale
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # 0-1 scale

    # Reasoning and recommendations
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Feature importance (JSON string)
    feature_importance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="skill_assessments")
    evidence: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="assessment", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_skill_assessment_student_skill_created", "student_id", "skill_type", "created_at"),
    )

    def __repr__(self):
        return f"<SkillAssessment {self.skill_type.value} for Student {self.student_id}: {self.score:.2f}>"


class RubricAssessment(Base, UUIDMixin, TimestampMixin):
    """Teacher rubric-based assessment."""

    __tablename__ = "rubric_assessments"

    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id"), nullable=False, index=True)
    teacher_id: Mapped[str] = mapped_column(String(36), ForeignKey("teachers.id"), nullable=False, index=True)
    skill_type: Mapped[SkillType] = mapped_column(Enum(SkillType), nullable=False, index=True)

    # Rubric score (1-4 scale as per PRD)
    score: Mapped[int] = mapped_column(nullable=False)  # 1-4 scale

    # Optional teacher comments
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="rubric_assessments")
    teacher = relationship("Teacher", back_populates="rubric_assessments")

    __table_args__ = (
        Index("idx_rubric_assessment_student_skill_created", "student_id", "skill_type", "created_at"),
    )

    def __repr__(self):
        return f"<RubricAssessment {self.skill_type.value} for Student {self.student_id}: {self.score}/4>"
