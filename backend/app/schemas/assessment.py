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

    skill_type: SkillTypeSchema = Field(
        ..., examples=["empathy"], description="Type of skill to assess"
    )
    use_cached: bool = Field(
        default=True, description="Use cached assessment if available (within 7 days)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"skill_type": "empathy", "use_cached": True},
                {"skill_type": "problem_solving", "use_cached": False},
            ]
        }
    }


class BatchAssessmentRequest(BaseModel):
    """Request to generate assessments for multiple students."""

    student_ids: List[str] = Field(
        ...,
        examples=[
            [
                "550e8400-e29b-41d4-a716-446655440001",
                "550e8400-e29b-41d4-a716-446655440002",
            ]
        ],
        description="List of student IDs to assess",
    )
    skill_types: Optional[List[SkillTypeSchema]] = Field(
        default=None,
        examples=[["empathy", "problem_solving"]],
        description=(
            "Skills to assess (defaults to all primary skills: "
            "empathy, problem_solving, self_regulation, resilience)"
        ),
    )
    use_cached: bool = Field(
        default=True, description="Use cached assessments where available"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "student_ids": [
                        "550e8400-e29b-41d4-a716-446655440001",
                        "550e8400-e29b-41d4-a716-446655440002",
                    ],
                    "skill_types": ["empathy", "problem_solving"],
                    "use_cached": True,
                }
            ]
        }
    }


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
