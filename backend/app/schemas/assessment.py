"""Pydantic schemas for skill assessments."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class SkillTypeSchema(str, Enum):
    """Skill types for assessment."""

    EMPATHY = "empathy"
    ADAPTABILITY = "adaptability"
    PROBLEM_SOLVING = "problem_solving"
    SELF_REGULATION = "self_regulation"
    RESILIENCE = "resilience"
    COMMUNICATION = "communication"
    COLLABORATION = "collaboration"


class EvidenceSchema(BaseModel):
    """Evidence supporting an assessment."""

    id: str
    evidence_type: str
    source: str
    content: str
    relevance_score: float

    class Config:
        from_attributes = True


class AssessmentRequest(BaseModel):
    """Request to generate a skill assessment."""

    skill_type: SkillTypeSchema
    use_cached: bool = Field(
        default=True, description="Use cached assessment if available (within 7 days)"
    )


class BatchAssessmentRequest(BaseModel):
    """Request to generate assessments for multiple students."""

    student_ids: List[str]
    skill_types: Optional[List[SkillTypeSchema]] = Field(
        default=None,
        description=(
            "Skills to assess (defaults to all primary skills: "
            "empathy, problem_solving, self_regulation, resilience)"
        ),
    )
    use_cached: bool = Field(
        default=True, description="Use cached assessments where available"
    )


class AssessmentResponse(BaseModel):
    """Response containing a skill assessment."""

    id: str
    student_id: str
    skill_type: str
    score: float = Field(..., ge=0.0, le=1.0, description="Skill score from 0 to 1")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in assessment"
    )
    reasoning: str
    recommendations: Optional[str] = None
    evidence: List[EvidenceSchema] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BatchAssessmentResponse(BaseModel):
    """Response for batch assessment request."""

    total: int
    successful: int
    failed: int
    assessments: List[AssessmentResponse]
    errors: List[dict] = Field(default_factory=list)


class AssessmentSummary(BaseModel):
    """Summary of all skill assessments for a student."""

    student_id: str
    assessments: List[AssessmentResponse]
    overall_score: float = Field(
        ..., ge=0.0, le=1.0, description="Average score across all assessed skills"
    )
    assessed_at: datetime
