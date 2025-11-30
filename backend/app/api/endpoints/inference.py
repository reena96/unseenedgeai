"""ML inference API endpoints."""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import time
import os

from app.core.database import get_db, AsyncSessionLocal
from app.core.metrics import get_metrics_store
from app.services.skill_inference import SkillInferenceService
from app.services.evidence_service import EvidenceService
from app.models.assessment import SkillType
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize inference service (singleton)
_inference_service: Optional[SkillInferenceService] = None


def get_inference_service() -> SkillInferenceService:
    """Get or create inference service singleton."""
    global _inference_service
    if _inference_service is None:
        _inference_service = SkillInferenceService()
    return _inference_service


# Initialize metrics store
_metrics_store = get_metrics_store(redis_url=os.getenv("REDIS_URL"))


class EvidenceItem(BaseModel):
    """Evidence supporting a skill assessment."""

    source: str = Field(
        ...,
        description="Source of evidence (transcript/game_telemetry)",
        examples=["transcript", "game_telemetry"],
    )
    text: str = Field(
        ...,
        description="Evidence text content",
        examples=[
            "Student demonstrated empathy by helping classmate",
            "Completed problem-solving mission with 90% accuracy",
        ],
    )
    relevance: float = Field(
        ..., ge=0.0, le=1.0, description="Relevance score (0-1)", examples=[0.85, 0.92]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "source": "transcript",
                    "text": "Student demonstrated empathy by helping classmate",
                    "relevance": 0.85,
                }
            ]
        }
    }


class SkillScoreResponse(BaseModel):
    """Response model for skill score."""

    skill_type: str
    score: float = Field(..., ge=0.0, le=1.0, description="Skill score (0-1)")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in prediction (0-1)"
    )
    feature_importance: Dict[str, float] = Field(default_factory=dict)
    inference_time_ms: float = Field(
        ..., description="Time taken for inference in milliseconds"
    )
    model_version: Optional[str] = Field(
        None, description="Version of model used for inference"
    )
    evidence: Optional[List[EvidenceItem]] = Field(
        default_factory=list, description="Supporting evidence for this assessment"
    )
    reasoning: Optional[str] = Field(
        None, description="AI-generated explanation of the assessment"
    )


class StudentSkillScoresResponse(BaseModel):
    """Response model for all skill scores."""

    student_id: str
    skills: List[SkillScoreResponse]
    total_inference_time_ms: float
    timestamp: datetime
    model_versions: Optional[Dict[str, str]] = Field(
        None, description="Model versions used"
    )


class InferenceMetrics(BaseModel):
    """Inference performance metrics response model."""

    student_id: str
    skill_type: Optional[str] = None
    inference_time_ms: float
    success: bool
    error_message: Optional[str] = None
    timestamp: str  # ISO format


def record_metrics(
    student_id: str,
    inference_time_ms: float,
    skill_type: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None,
):
    """Record inference metrics to Redis/memory store."""
    _metrics_store.record_metric(
        student_id=student_id,
        inference_time_ms=inference_time_ms,
        skill_type=skill_type,
        success=success,
        error_message=error_message,
    )


@router.post(
    "/infer/{student_id}",
    response_model=StudentSkillScoresResponse,
    status_code=status.HTTP_200_OK,
    summary="Infer all skills for a student",
    description="Run ML inference to predict skill scores on 0-1 scale for all skills",
)
async def infer_student_skills(
    student_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    inference_service: SkillInferenceService = Depends(get_inference_service),
):
    """
    Infer all skill scores for a student using trained ML models.

    This endpoint:
    1. Loads the most recent linguistic and behavioral features
    2. Runs inference with trained XGBoost models
    3. Returns scores on 0-1 scale with confidence scores
    4. Tracks inference latency metrics

    Returns skill scores for:
    - Empathy
    - Problem-solving
    - Self-regulation
    - Resilience
    """
    start_time = time.time()

    try:
        logger.info(f"Running skill inference for student {student_id}")

        # Run inference for all skills
        results = await inference_service.infer_all_skills(db, student_id)

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No trained models available or insufficient data for student {student_id}",
            )

        # Create evidence service and save assessments with evidence
        evidence_service = EvidenceService()

        # Build response
        skill_responses = []
        for skill_type, (score, confidence, importance) in results.items():
            skill_start = time.time()
            model_version = inference_service.get_model_version(skill_type)

            # Save assessment with evidence to database
            assessment = await evidence_service.create_assessment_with_evidence(
                session=db,
                student_id=student_id,
                skill_type=skill_type,
                score=score,
                confidence=confidence,
                feature_importance=importance,
            )

            # Extract evidence for API response
            evidence_items = [
                EvidenceItem(
                    source=ev.source, text=ev.content, relevance=ev.relevance_score
                )
                for ev in assessment.evidence
            ]

            skill_responses.append(
                SkillScoreResponse(
                    skill_type=skill_type.value,
                    score=score,
                    confidence=confidence,
                    feature_importance=importance,
                    inference_time_ms=(time.time() - skill_start) * 1000,
                    model_version=model_version,
                    evidence=evidence_items,
                    reasoning=assessment.reasoning,
                )
            )

        total_time = (time.time() - start_time) * 1000

        # Record metrics in background
        background_tasks.add_task(
            record_metrics,
            student_id=student_id,
            inference_time_ms=total_time,
            success=True,
        )

        logger.info(
            f"Completed inference for student {student_id} in {total_time:.2f}ms"
        )

        return StudentSkillScoresResponse(
            student_id=student_id,
            skills=skill_responses,
            total_inference_time_ms=total_time,
            timestamp=datetime.utcnow(),
            model_versions=inference_service.get_all_model_versions(),
        )

    except ValueError as e:
        total_time = (time.time() - start_time) * 1000
        background_tasks.add_task(
            record_metrics,
            student_id=student_id,
            inference_time_ms=total_time,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        background_tasks.add_task(
            record_metrics,
            student_id=student_id,
            inference_time_ms=total_time,
            success=False,
            error_message=str(e),
        )
        logger.error(f"Inference failed for student {student_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {str(e)}",
        )


@router.post(
    "/infer/{student_id}/{skill_type}",
    response_model=SkillScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Infer specific skill for a student",
    description="Run ML inference for a single skill",
)
async def infer_single_skill(
    student_id: str,
    skill_type: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    inference_service: SkillInferenceService = Depends(get_inference_service),
):
    """
    Infer a single skill score for a student.

    Args:
        student_id: Student ID
        skill_type: One of: empathy, problem_solving, self_regulation, resilience
    """
    start_time = time.time()

    try:
        # Convert string to SkillType enum
        try:
            skill_enum = SkillType(skill_type)
        except ValueError:
            valid_skills = [s.value for s in SkillType]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid skill type: {skill_type}. Must be one of: {valid_skills}",
            )

        logger.info(f"Running {skill_type} inference for student {student_id}")

        # Run inference
        score, confidence, importance = await inference_service.infer_skill(
            db, student_id, skill_enum
        )

        total_time = (time.time() - start_time) * 1000

        # Record metrics
        background_tasks.add_task(
            record_metrics,
            student_id=student_id,
            skill_type=skill_type,
            inference_time_ms=total_time,
            success=True,
        )

        logger.info(
            f"Completed {skill_type} inference for student {student_id} in {total_time:.2f}ms"
        )

        return SkillScoreResponse(
            skill_type=skill_type,
            score=score,
            confidence=confidence,
            feature_importance=importance,
            inference_time_ms=total_time,
        )

    except ValueError as e:
        total_time = (time.time() - start_time) * 1000
        background_tasks.add_task(
            record_metrics,
            student_id=student_id,
            skill_type=skill_type,
            inference_time_ms=total_time,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        background_tasks.add_task(
            record_metrics,
            student_id=student_id,
            skill_type=skill_type,
            inference_time_ms=total_time,
            success=False,
            error_message=str(e),
        )
        logger.error(f"{skill_type} inference failed for student {student_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {str(e)}",
        )


@router.get(
    "/metrics",
    response_model=List[InferenceMetrics],
    status_code=status.HTTP_200_OK,
    summary="Get inference metrics",
    description="Get recent inference performance metrics",
)
async def get_inference_metrics(
    limit: int = 100,
):
    """
    Get recent inference metrics for monitoring.

    Returns:
        List of recent inference metrics including timing and success rates
    """
    metrics_data = _metrics_store.get_recent_metrics(limit=limit)

    # Convert to response model
    return [
        InferenceMetrics(
            student_id=m.student_id,
            skill_type=m.skill_type,
            inference_time_ms=m.inference_time_ms,
            success=m.success,
            error_message=m.error_message,
            timestamp=m.timestamp,
        )
        for m in metrics_data
    ]


class MetricsSummary(BaseModel):
    """Summary of inference metrics."""

    total_inferences: int
    successful_inferences: int
    failed_inferences: int
    avg_inference_time_ms: float
    max_inference_time_ms: float
    min_inference_time_ms: float
    p95_inference_time_ms: float
    success_rate: float


@router.get(
    "/metrics/summary",
    response_model=MetricsSummary,
    status_code=status.HTTP_200_OK,
    summary="Get metrics summary",
    description="Get aggregated inference performance metrics",
)
async def get_metrics_summary():
    """
    Get summary statistics for inference performance.

    Useful for monitoring:
    - Average latency
    - P95 latency
    - Success rate
    - Total inference count
    """
    summary_data = _metrics_store.get_metrics_summary()

    return MetricsSummary(**summary_data)


class BatchInferenceRequest(BaseModel):
    """Request model for batch inference."""

    student_ids: List[str] = Field(
        ..., min_items=1, max_items=100, description="List of student IDs (max 100)"
    )


class BatchInferenceStatus(BaseModel):
    """Status model for batch inference."""

    student_id: str
    status: str  # success, error, pending
    skills: Optional[List[SkillScoreResponse]] = None
    error_message: Optional[str] = None
    total_inference_time_ms: Optional[float] = None


class BatchInferenceResponse(BaseModel):
    """Response model for batch inference."""

    total_students: int
    successful: int
    failed: int
    total_time_ms: float
    results: List[BatchInferenceStatus]


@router.post(
    "/infer-batch",
    response_model=BatchInferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch inference for multiple students",
    description="Run ML inference for multiple students in parallel",
)
async def batch_infer_student_skills(
    request: BatchInferenceRequest,
    background_tasks: BackgroundTasks,
    inference_service: SkillInferenceService = Depends(get_inference_service),
):
    """
    Infer skills for multiple students in parallel.

    This endpoint:
    1. Accepts a list of student IDs (max 100)
    2. Runs inference for each student in parallel
    3. Returns aggregated results with success/failure status
    4. Tracks metrics for each inference

    Limits:
    - Maximum 100 students per batch
    - Processes students in parallel for efficiency
    - Failed inferences don't block successful ones

    Returns:
        Batch inference results with individual status for each student
    """
    start_time = time.time()
    student_ids = request.student_ids

    logger.info(f"Starting batch inference for {len(student_ids)} students")

    # Process students in parallel using asyncio.gather
    # Each student gets its own database session to avoid concurrent session errors
    async def infer_single_student(student_id: str) -> BatchInferenceStatus:
        """Infer skills for a single student and return status."""
        student_start = time.time()
        # Create a new session for each student to allow concurrent operations
        async with AsyncSessionLocal() as session:
            try:
                # Run inference for all skills
                results = await inference_service.infer_all_skills(session, student_id)

                if not results:
                    return BatchInferenceStatus(
                        student_id=student_id,
                        status="error",
                        error_message="No trained models available or insufficient data",
                    )

                # Create evidence service for batch assessments
                evidence_service = EvidenceService()

                # Build skill responses
                skill_responses = []
                for skill_type, (score, confidence, importance) in results.items():
                    model_version = inference_service.get_model_version(skill_type)

                    # Save assessment with evidence to database
                    assessment = await evidence_service.create_assessment_with_evidence(
                        session=session,
                        student_id=student_id,
                        skill_type=skill_type,
                        score=score,
                        confidence=confidence,
                        feature_importance=importance,
                    )

                    # Extract evidence for API response
                    evidence_items = [
                        EvidenceItem(
                            source=ev.source,
                            text=ev.content,
                            relevance=ev.relevance_score,
                        )
                        for ev in assessment.evidence
                    ]

                    skill_responses.append(
                        SkillScoreResponse(
                            skill_type=skill_type.value,
                            score=score,
                            confidence=confidence,
                            feature_importance=importance,
                            inference_time_ms=(time.time() - student_start) * 1000,
                            model_version=model_version,
                            evidence=evidence_items,
                            reasoning=assessment.reasoning,
                        )
                    )

                # Commit the session after all skills are processed
                await session.commit()

                inference_time = (time.time() - student_start) * 1000

                # Record success metric
                background_tasks.add_task(
                    record_metrics,
                    student_id=student_id,
                    inference_time_ms=inference_time,
                    success=True,
                )

                return BatchInferenceStatus(
                    student_id=student_id,
                    status="success",
                    skills=skill_responses,
                    total_inference_time_ms=inference_time,
                )

            except Exception as e:
                await session.rollback()
                inference_time = (time.time() - student_start) * 1000

                # Record failure metric
                background_tasks.add_task(
                    record_metrics,
                    student_id=student_id,
                    inference_time_ms=inference_time,
                    success=False,
                    error_message=str(e),
                )

                logger.error(f"Batch inference failed for student {student_id}: {e}")

                return BatchInferenceStatus(
                    student_id=student_id,
                    status="error",
                    error_message=str(e),
                )

    # Run all inferences in parallel
    results = await asyncio.gather(
        *[infer_single_student(student_id) for student_id in student_ids],
        return_exceptions=False,  # Already handling exceptions in infer_single_student
    )

    # Count successes and failures
    successful = sum(1 for r in results if r.status == "success")
    failed = sum(1 for r in results if r.status == "error")

    total_time = (time.time() - start_time) * 1000

    logger.info(
        f"Completed batch inference: {successful} successful, {failed} failed, "
        f"total time: {total_time:.2f}ms"
    )

    return BatchInferenceResponse(
        total_students=len(student_ids),
        successful=successful,
        failed=failed,
        total_time_ms=total_time,
        results=results,
    )
