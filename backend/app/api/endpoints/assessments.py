"""API endpoints for AI-powered skill assessments."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.services.ai_assessment import SkillAssessmentService
from app.services.evidence_enrichment import EvidenceEnrichmentService
from app.models.assessment import SkillType, SkillAssessment
from app.schemas.assessment import (
    AssessmentRequest,
    AssessmentResponse,
    BatchAssessmentRequest,
    BatchAssessmentResponse,
    AssessmentSummary,
    EvidenceSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assessments", tags=["assessments"])

# Initialize services (singleton pattern)
assessment_service = SkillAssessmentService()
evidence_enrichment_service = EvidenceEnrichmentService()


@router.post(
    "/{student_id}",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_skill_assessment(
    student_id: str = Path(
        ...,
        description="Student ID (UUID format)",
        examples=["550e8400-e29b-41d4-a716-446655440001"],
    ),
    request: AssessmentRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an AI-powered skill assessment for a student.

    Args:
        student_id: ID of the student to assess
        request: Assessment request (skill type and caching preference)
        db: Database session

    Returns:
        Generated skill assessment

    Raises:
        HTTPException: If student not found, insufficient data, or AI call fails
    """
    try:
        logger.info(
            f"Creating {request.skill_type.value} assessment for student {student_id}"
        )

        # Convert schema enum to model enum
        skill_type = SkillType(request.skill_type.value)

        assessment = await assessment_service.assess_skill(
            db, student_id, skill_type, use_cached=request.use_cached
        )

        # Format response
        return AssessmentResponse(
            id=assessment.id,
            student_id=assessment.student_id,
            skill_type=assessment.skill_type.value,
            score=assessment.score,
            confidence=assessment.confidence,
            reasoning=assessment.reasoning,
            recommendations=assessment.recommendations,
            evidence=[
                EvidenceSchema(
                    id=e.id,
                    evidence_type=e.evidence_type.value,
                    source=e.source,
                    content=e.content,
                    relevance_score=e.relevance_score,
                )
                for e in assessment.evidence
            ],
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assessment generation failed: {str(e)}",
        )


@router.post(
    "/{student_id}/all",
    response_model=AssessmentSummary,
    status_code=status.HTTP_201_CREATED,
)
async def create_all_assessments(
    student_id: str = Path(
        ...,
        description="Student ID (UUID format)",
        examples=["550e8400-e29b-41d4-a716-446655440001"],
    ),
    use_cached: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate assessments for all primary skills for a student.

    Args:
        student_id: ID of the student to assess
        use_cached: Use cached assessments where available
        db: Database session

    Returns:
        Summary of all assessments

    Raises:
        HTTPException: If student not found or assessment fails
    """
    try:
        logger.info(f"Creating all skill assessments for student {student_id}")

        assessments = await assessment_service.assess_all_skills(
            db, student_id, use_cached=use_cached
        )

        if not assessments:
            raise ValueError(
                "No assessments could be generated. Check data availability."
            )

        # Calculate overall score
        overall_score = sum(a.score for a in assessments) / len(assessments)

        # Format response
        assessment_responses = [
            AssessmentResponse(
                id=a.id,
                student_id=a.student_id,
                skill_type=a.skill_type.value,
                score=a.score,
                confidence=a.confidence,
                reasoning=a.reasoning,
                recommendations=a.recommendations,
                evidence=[
                    EvidenceSchema(
                        id=e.id,
                        evidence_type=e.evidence_type.value,
                        source=e.source,
                        content=e.content,
                        relevance_score=e.relevance_score,
                    )
                    for e in a.evidence
                ],
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
            for a in assessments
        ]

        return AssessmentSummary(
            student_id=student_id,
            assessments=assessment_responses,
            overall_score=overall_score,
            assessed_at=assessments[0].created_at,
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating assessments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assessment generation failed: {str(e)}",
        )


@router.post(
    "/batch",
    response_model=BatchAssessmentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def batch_create_assessments(
    request: BatchAssessmentRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate assessments for multiple students.

    Args:
        request: Batch assessment request
        db: Database session

    Returns:
        Summary of batch processing

    Raises:
        HTTPException: If batch processing fails
    """
    logger.info(f"Batch creating assessments for {len(request.student_ids)} students")

    # Default to primary skills if not specified
    skill_types = request.skill_types or [
        SkillType.EMPATHY,
        SkillType.PROBLEM_SOLVING,
        SkillType.SELF_REGULATION,
        SkillType.RESILIENCE,
    ]

    results = {
        "total": len(request.student_ids) * len(skill_types),
        "successful": 0,
        "failed": 0,
        "assessments": [],
        "errors": [],
    }

    for student_id in request.student_ids:
        for skill_type in skill_types:
            try:
                # Convert schema enum to model enum
                model_skill_type = SkillType(
                    skill_type.value if hasattr(skill_type, "value") else skill_type
                )

                assessment = await assessment_service.assess_skill(
                    db, student_id, model_skill_type, use_cached=request.use_cached
                )

                results["successful"] += 1
                results["assessments"].append(
                    AssessmentResponse(
                        id=assessment.id,
                        student_id=assessment.student_id,
                        skill_type=assessment.skill_type.value,
                        score=assessment.score,
                        confidence=assessment.confidence,
                        reasoning=assessment.reasoning,
                        recommendations=assessment.recommendations,
                        evidence=[
                            EvidenceSchema(
                                id=e.id,
                                evidence_type=e.evidence_type.value,
                                source=e.source,
                                content=e.content,
                                relevance_score=e.relevance_score,
                            )
                            for e in assessment.evidence
                        ],
                        created_at=assessment.created_at,
                        updated_at=assessment.updated_at,
                    )
                )

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(
                    {
                        "student_id": student_id,
                        "skill_type": (
                            skill_type.value
                            if hasattr(skill_type, "value")
                            else str(skill_type)
                        ),
                        "error": str(e),
                    }
                )
                logger.error(f"Failed to assess {student_id}/{skill_type}: {e}")

    return BatchAssessmentResponse(**results)


@router.get(
    "/{student_id}",
    response_model=List[AssessmentResponse],
)
async def get_student_assessments(
    student_id: str = Path(
        ...,
        description="Student ID (UUID format)",
        examples=["550e8400-e29b-41d4-a716-446655440001"],
    ),
    skill_type: Optional[str] = None,
    limit: int = 100,  # Increased to ensure all skills are returned
    db: AsyncSession = Depends(get_db),
):
    """
    Get all assessments for a student.

    Args:
        student_id: ID of the student
        skill_type: Optional filter by skill type
        limit: Maximum number of assessments to return per skill
        db: Database session

    Returns:
        List of assessments

    Raises:
        HTTPException: If student not found
    """
    try:
        from sqlalchemy.orm import selectinload

        query = (
            select(SkillAssessment)
            .options(selectinload(SkillAssessment.evidence))
            .where(SkillAssessment.student_id == student_id)
        )

        if skill_type:
            try:
                skill_enum = SkillType(skill_type)
                query = query.where(SkillAssessment.skill_type == skill_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid skill type: {skill_type}",
                )

        query = query.order_by(SkillAssessment.created_at.desc()).limit(limit)

        result = await db.execute(query)
        assessments = result.scalars().all()

        return [
            AssessmentResponse(
                id=a.id,
                student_id=a.student_id,
                skill_type=a.skill_type.value,
                score=a.score,
                confidence=a.confidence,
                reasoning=a.reasoning,
                recommendations=a.recommendations,
                evidence=[
                    EvidenceSchema(
                        id=e.id,
                        evidence_type=e.evidence_type.value,
                        source=e.source,
                        content=e.content,
                        relevance_score=e.relevance_score,
                    )
                    for e in a.evidence
                ],
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
            for a in assessments
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assessments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch assessments: {str(e)}",
        )


@router.get(
    "/{student_id}/{skill_type}/latest",
    response_model=AssessmentResponse,
)
async def get_latest_assessment(
    student_id: str = Path(
        ...,
        description="Student ID (UUID format)",
        examples=["550e8400-e29b-41d4-a716-446655440001"],
    ),
    skill_type: str = Path(
        ...,
        description="Skill type to retrieve",
        examples=["empathy", "problem_solving", "self_regulation"],
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the most recent assessment for a specific skill.

    Args:
        student_id: ID of the student
        skill_type: Skill type to retrieve
        db: Database session

    Returns:
        Most recent assessment

    Raises:
        HTTPException: If no assessment found
    """
    try:
        skill_enum = SkillType(skill_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid skill type: {skill_type}",
        )

    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(SkillAssessment)
        .options(selectinload(SkillAssessment.evidence))
        .where(
            SkillAssessment.student_id == student_id,
            SkillAssessment.skill_type == skill_enum,
        )
        .order_by(SkillAssessment.created_at.desc())
        .limit(1)
    )
    assessment = result.scalar_one_or_none()

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {skill_type} assessment found for student {student_id}",
        )

    return AssessmentResponse(
        id=assessment.id,
        student_id=assessment.student_id,
        skill_type=assessment.skill_type.value,
        score=assessment.score,
        confidence=assessment.confidence,
        reasoning=assessment.reasoning,
        recommendations=assessment.recommendations,
        evidence=[
            EvidenceSchema(
                id=e.id,
                evidence_type=e.evidence_type.value,
                source=e.source,
                content=e.content,
                relevance_score=e.relevance_score,
            )
            for e in assessment.evidence
        ],
        created_at=assessment.created_at,
        updated_at=assessment.updated_at,
    )


@router.get(
    "/{assessment_id}/enriched-evidence",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_enriched_evidence(
    assessment_id: str = Path(
        ...,
        description="Assessment ID (UUID format)",
        examples=["550e8400-e29b-41d4-a716-446655440001"],
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get enriched evidence for an assessment including transcripts and telemetry data.

    This endpoint provides detailed evidence with:
    - Transcript excerpts showing student speech patterns
    - Game telemetry events demonstrating behaviors
    - AI-generated insights and analysis
    - Timeline of evidence across sessions

    Args:
        assessment_id: ID of the assessment
        db: Database session

    Returns:
        Enriched evidence data with transcripts, telemetry, and AI insights

    Raises:
        HTTPException: If assessment not found
    """
    try:
        logger.info(f"Fetching enriched evidence for assessment {assessment_id}")

        # Fetch assessment with evidence
        from sqlalchemy.orm import selectinload

        result = await db.execute(
            select(SkillAssessment)
            .options(selectinload(SkillAssessment.evidence))
            .where(SkillAssessment.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment {assessment_id} not found",
            )

        # Enrich with transcripts and telemetry
        enriched_data = await evidence_enrichment_service.enrich_assessment_evidence(
            db, assessment
        )

        return enriched_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching enriched evidence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch enriched evidence: {str(e)}",
        )


@router.post(
    "/backup",
    status_code=status.HTTP_200_OK,
    summary="Backup all assessments to JSON",
    description="Export all skill assessments to a timestamped JSON backup file",
)
async def backup_assessments(
    db: AsyncSession = Depends(get_db),
):
    """
    Create a backup of all skill assessments.

    This endpoint:
    - Exports all assessments with evidence to JSON
    - Saves to data/exports/ directory with timestamp
    - Returns the backup file path

    Returns:
        Backup file information and path
    """
    try:
        from datetime import datetime
        from pathlib import Path
        import json

        logger.info("Starting assessment backup")

        # Fetch all assessments with evidence
        from sqlalchemy.orm import selectinload

        result = await db.execute(
            select(SkillAssessment)
            .options(selectinload(SkillAssessment.evidence))
            .order_by(SkillAssessment.created_at)
        )
        assessments = result.scalars().all()

        # Serialize assessments
        backup_data = {
            "backup_timestamp": datetime.utcnow().isoformat(),
            "total_assessments": len(assessments),
            "assessments": [
                {
                    "id": a.id,
                    "student_id": a.student_id,
                    "skill_type": a.skill_type.value,
                    "score": a.score,
                    "confidence": a.confidence,
                    "reasoning": a.reasoning,
                    "recommendations": a.recommendations,
                    "feature_importance": a.feature_importance,
                    "created_at": a.created_at.isoformat(),
                    "updated_at": a.updated_at.isoformat(),
                    "evidence": [
                        {
                            "id": e.id,
                            "assessment_id": e.assessment_id,
                            "evidence_type": e.evidence_type.value,
                            "source": e.source,
                            "content": e.content,
                            "relevance_score": e.relevance_score,
                            "created_at": e.created_at.isoformat(),
                            "updated_at": e.updated_at.isoformat(),
                        }
                        for e in a.evidence
                    ],
                }
                for a in assessments
            ],
        }

        # Ensure backup directory exists
        backup_dir = Path(__file__).parent.parent.parent.parent / "data" / "exports"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamped filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"assessments_backup_{timestamp}.json"

        # Write backup file
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Successfully backed up {len(assessments)} assessments to {backup_file}"
        )

        return {
            "success": True,
            "backup_file": str(backup_file),
            "total_assessments": len(assessments),
            "timestamp": backup_data["backup_timestamp"],
        }

    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create backup: {str(e)}",
        )
