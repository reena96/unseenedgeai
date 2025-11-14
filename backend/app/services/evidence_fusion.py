"""Evidence fusion service for combining multiple evidence sources."""

import asyncio
import logging
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.assessment import SkillType, Evidence, EvidenceType
from app.models.features import LinguisticFeatures, BehavioralFeatures
from app.services.skill_inference import SkillInferenceService
from app.core.fusion_config import (
    get_fusion_config_manager,
    FusionConfig,
    EvidenceSource as ConfigEvidenceSource,
)

logger = logging.getLogger(__name__)


class EvidenceSource(str, Enum):
    """Evidence source types."""

    ML_INFERENCE = "ml_inference"
    LINGUISTIC_FEATURES = "linguistic_features"
    BEHAVIORAL_FEATURES = "behavioral_features"
    TEACHER_OBSERVATION = "teacher_observation"
    PEER_FEEDBACK = "peer_feedback"


@dataclass
class EvidenceItem:
    """Individual piece of evidence."""

    source: EvidenceSource
    evidence_type: EvidenceType
    content: str
    score: float  # 0-1 scale
    confidence: float  # 0-1 scale
    relevance: float  # 0-1 scale
    weight: float = 1.0  # Skill-specific weight


class EvidenceFusionService:
    """
    Service for fusing evidence from multiple sources into final skill assessments.

    Combines:
    1. ML model predictions (primary)
    2. Linguistic feature evidence
    3. Behavioral feature evidence
    4. Teacher observations (if available)
    5. Peer feedback (if available)
    """

    def __init__(
        self,
        inference_service: Optional[SkillInferenceService] = None,
        config_path: Optional[Path] = None,
    ):
        """
        Initialize evidence fusion service.

        Args:
            inference_service: ML inference service instance
            config_path: Optional path to fusion config file
        """
        self.inference_service = inference_service or SkillInferenceService()

        # Initialize config manager
        if config_path is None:
            # Default path in project directory
            config_path = Path(
                os.getenv("FUSION_CONFIG_PATH", "./config/fusion_weights.json")
            )

        self.config_manager = get_fusion_config_manager(config_path)
        self.config = self.config_manager.get_config()

        # Skill-specific weights for different evidence sources (kept for backward compatibility)
        self.source_weights = self._initialize_source_weights()

        logger.info(
            f"Initialized EvidenceFusionService with config version {self.config.version}"
        )

    def _initialize_source_weights(
        self,
    ) -> Dict[SkillType, Dict[EvidenceSource, float]]:
        """
        Initialize skill-specific weights for evidence sources.

        Returns:
            Dictionary mapping skills to source weights
        """
        # Default weights (can be tuned based on validation data)
        default_weights = {
            EvidenceSource.ML_INFERENCE: 0.50,  # Primary source
            EvidenceSource.LINGUISTIC_FEATURES: 0.20,
            EvidenceSource.BEHAVIORAL_FEATURES: 0.20,
            EvidenceSource.TEACHER_OBSERVATION: 0.10,
            EvidenceSource.PEER_FEEDBACK: 0.05,
        }

        # Skill-specific adjustments
        weights = {
            SkillType.EMPATHY: {
                **default_weights,
                EvidenceSource.LINGUISTIC_FEATURES: 0.25,  # Higher weight for empathy language
                EvidenceSource.BEHAVIORAL_FEATURES: 0.15,
            },
            SkillType.PROBLEM_SOLVING: {
                **default_weights,
                EvidenceSource.BEHAVIORAL_FEATURES: 0.25,  # Higher weight for task completion
                EvidenceSource.LINGUISTIC_FEATURES: 0.15,
            },
            SkillType.SELF_REGULATION: {
                **default_weights,
                EvidenceSource.BEHAVIORAL_FEATURES: 0.30,  # Highest weight for focus/distraction data
                EvidenceSource.LINGUISTIC_FEATURES: 0.10,
            },
            SkillType.RESILIENCE: {
                **default_weights,
                EvidenceSource.BEHAVIORAL_FEATURES: 0.25,  # Higher weight for retry/recovery
                EvidenceSource.LINGUISTIC_FEATURES: 0.15,
            },
        }

        return weights

    def _normalize_score(self, score: float) -> float:
        """Normalize score to 0-1 range."""
        return float(np.clip(score, 0.0, 1.0))

    async def _collect_ml_evidence(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
    ) -> List[EvidenceItem]:
        """
        Collect ML inference evidence.

        Args:
            session: Database session
            student_id: Student ID
            skill_type: Skill type

        Returns:
            List of evidence items from ML inference
        """
        evidence_items = []

        try:
            score, confidence, importance = await self.inference_service.infer_skill(
                session, student_id, skill_type
            )

            # Main ML prediction evidence
            evidence_items.append(
                EvidenceItem(
                    source=EvidenceSource.ML_INFERENCE,
                    evidence_type=EvidenceType.BEHAVIORAL,
                    content=f"ML model prediction: {score:.2f} (confidence: {confidence:.2f})",
                    score=score,
                    confidence=confidence,
                    relevance=1.0,
                    weight=self.source_weights[skill_type][EvidenceSource.ML_INFERENCE],
                )
            )

            # Top 3 feature importance evidence
            if importance:
                top_features = sorted(
                    importance.items(), key=lambda x: x[1], reverse=True
                )[:3]

                for feature_name, importance_score in top_features:
                    evidence_items.append(
                        EvidenceItem(
                            source=EvidenceSource.ML_INFERENCE,
                            evidence_type=EvidenceType.CONTEXTUAL,
                            content=f"Key factor: {feature_name.replace('_', ' ')} (importance: {importance_score:.2f})",
                            score=score,
                            confidence=confidence * 0.8,  # Slightly lower confidence
                            relevance=importance_score,
                        )
                    )

        except Exception as e:
            logger.warning(f"Failed to collect ML evidence: {e}")

        return evidence_items

    async def _collect_linguistic_evidence(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
    ) -> List[EvidenceItem]:
        """
        Collect linguistic feature evidence.

        Args:
            session: Database session
            student_id: Student ID
            skill_type: Skill type

        Returns:
            List of evidence items from linguistic features
        """
        evidence_items = []

        try:
            # Fetch most recent linguistic features
            result = await session.execute(
                select(LinguisticFeatures)
                .where(LinguisticFeatures.student_id == student_id)
                .order_by(LinguisticFeatures.created_at.desc())
                .limit(1)
            )
            ling_features = result.scalar_one_or_none()

            if ling_features and ling_features.features_json:
                features = ling_features.features_json

                # Skill-specific linguistic evidence
                if skill_type == SkillType.EMPATHY:
                    empathy_markers = features.get("empathy_markers", 0)
                    social_proc = features.get("social_processes", 0)

                    if empathy_markers > 0:
                        evidence_items.append(
                            EvidenceItem(
                                source=EvidenceSource.LINGUISTIC_FEATURES,
                                evidence_type=EvidenceType.LINGUISTIC,
                                content=f"Used {empathy_markers} empathy markers in speech",
                                score=min(1.0, empathy_markers / 10),  # Normalize
                                confidence=0.7,
                                relevance=0.9,
                                weight=self.source_weights[skill_type][
                                    EvidenceSource.LINGUISTIC_FEATURES
                                ],
                            )
                        )

                    if social_proc > 0:
                        evidence_items.append(
                            EvidenceItem(
                                source=EvidenceSource.LINGUISTIC_FEATURES,
                                evidence_type=EvidenceType.LINGUISTIC,
                                content=f"Showed {social_proc} social process indicators",
                                score=min(1.0, social_proc / 15),
                                confidence=0.6,
                                relevance=0.7,
                            )
                        )

                elif skill_type == SkillType.PROBLEM_SOLVING:
                    ps_lang = features.get("problem_solving_language", 0)
                    cognitive = features.get("cognitive_processes", 0)

                    if ps_lang > 0:
                        evidence_items.append(
                            EvidenceItem(
                                source=EvidenceSource.LINGUISTIC_FEATURES,
                                evidence_type=EvidenceType.LINGUISTIC,
                                content=f"Used {ps_lang} problem-solving terms",
                                score=min(1.0, ps_lang / 10),
                                confidence=0.75,
                                relevance=0.9,
                                weight=self.source_weights[skill_type][
                                    EvidenceSource.LINGUISTIC_FEATURES
                                ],
                            )
                        )

                elif skill_type == SkillType.RESILIENCE:
                    perseverance = features.get("perseverance_indicators", 0)

                    if perseverance > 0:
                        evidence_items.append(
                            EvidenceItem(
                                source=EvidenceSource.LINGUISTIC_FEATURES,
                                evidence_type=EvidenceType.LINGUISTIC,
                                content=f"Expressed {perseverance} perseverance indicators",
                                score=min(1.0, perseverance / 8),
                                confidence=0.7,
                                relevance=0.85,
                                weight=self.source_weights[skill_type][
                                    EvidenceSource.LINGUISTIC_FEATURES
                                ],
                            )
                        )

        except Exception as e:
            logger.warning(f"Failed to collect linguistic evidence: {e}")

        return evidence_items

    async def _collect_behavioral_evidence(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
    ) -> List[EvidenceItem]:
        """
        Collect behavioral feature evidence.

        Args:
            session: Database session
            student_id: Student ID
            skill_type: Skill type

        Returns:
            List of evidence items from behavioral features
        """
        evidence_items = []

        try:
            # Fetch most recent behavioral features
            result = await session.execute(
                select(BehavioralFeatures)
                .where(BehavioralFeatures.student_id == student_id)
                .order_by(BehavioralFeatures.created_at.desc())
                .limit(1)
            )
            beh_features = result.scalar_one_or_none()

            if beh_features and beh_features.features_json:
                features = beh_features.features_json

                # Skill-specific behavioral evidence
                if skill_type == SkillType.PROBLEM_SOLVING:
                    completion_rate = features.get("task_completion_rate", 0)

                    evidence_items.append(
                        EvidenceItem(
                            source=EvidenceSource.BEHAVIORAL_FEATURES,
                            evidence_type=EvidenceType.BEHAVIORAL,
                            content=f"Completed {completion_rate*100:.0f}% of tasks",
                            score=completion_rate,
                            confidence=0.8,
                            relevance=0.95,
                            weight=self.source_weights[skill_type][
                                EvidenceSource.BEHAVIORAL_FEATURES
                            ],
                        )
                    )

                elif skill_type == SkillType.SELF_REGULATION:
                    distraction_res = features.get("distraction_resistance", 1.0)
                    focus_dur = features.get("focus_duration", 0)

                    evidence_items.append(
                        EvidenceItem(
                            source=EvidenceSource.BEHAVIORAL_FEATURES,
                            evidence_type=EvidenceType.BEHAVIORAL,
                            content=f"Maintained {distraction_res*100:.0f}% focus with avg {focus_dur:.0f}s duration",
                            score=distraction_res,
                            confidence=0.85,
                            relevance=0.95,
                            weight=self.source_weights[skill_type][
                                EvidenceSource.BEHAVIORAL_FEATURES
                            ],
                        )
                    )

                elif skill_type == SkillType.RESILIENCE:
                    retry_count = features.get("retry_count", 0)
                    recovery_rate = features.get("recovery_rate", 0)

                    if retry_count > 0:
                        evidence_items.append(
                            EvidenceItem(
                                source=EvidenceSource.BEHAVIORAL_FEATURES,
                                evidence_type=EvidenceType.BEHAVIORAL,
                                content=f"Retried {retry_count} times with {recovery_rate*100:.0f}% recovery rate",
                                score=recovery_rate,
                                confidence=0.8,
                                relevance=0.9,
                                weight=self.source_weights[skill_type][
                                    EvidenceSource.BEHAVIORAL_FEATURES
                                ],
                            )
                        )

        except Exception as e:
            logger.warning(f"Failed to collect behavioral evidence: {e}")

        return evidence_items

    def _fuse_evidence(
        self,
        evidence_items: List[EvidenceItem],
        skill_type: SkillType,
    ) -> Tuple[float, float, List[EvidenceItem]]:
        """
        Fuse evidence from multiple sources into final assessment.

        Args:
            evidence_items: List of evidence items
            skill_type: Skill type

        Returns:
            Tuple of (fused_score, fused_confidence, top_evidence)
        """
        if not evidence_items:
            return 0.5, 0.3, []

        # Calculate weighted score
        total_weight = 0.0
        weighted_score = 0.0
        weighted_confidence = 0.0

        for item in evidence_items:
            weight = item.weight * item.relevance * item.confidence
            weighted_score += item.score * weight
            weighted_confidence += item.confidence * weight
            total_weight += weight

        if total_weight == 0:
            return 0.5, 0.3, []

        # Normalize
        fused_score = self._normalize_score(weighted_score / total_weight)
        fused_confidence = self._normalize_score(weighted_confidence / total_weight)

        # Select top evidence items (max 5)
        top_evidence = sorted(
            evidence_items,
            key=lambda x: x.weight * x.relevance * x.confidence,
            reverse=True,
        )[:5]

        logger.info(
            f"Fused {len(evidence_items)} evidence items for {skill_type.value}: "
            f"score={fused_score:.3f}, confidence={fused_confidence:.3f}"
        )

        return fused_score, fused_confidence, top_evidence

    async def fuse_skill_evidence(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
    ) -> Tuple[float, float, List[EvidenceItem]]:
        """
        Fuse all available evidence for a skill.

        Args:
            session: Database session
            student_id: Student ID
            skill_type: Skill type

        Returns:
            Tuple of (score, confidence, evidence_items)
        """
        logger.info(f"Fusing evidence for {skill_type.value} (student: {student_id})")

        # Collect evidence from all sources
        # Collect all evidence in parallel for 3x speedup
        ml_evidence_task = self._collect_ml_evidence(session, student_id, skill_type)
        ling_evidence_task = self._collect_linguistic_evidence(
            session, student_id, skill_type
        )
        beh_evidence_task = self._collect_behavioral_evidence(
            session, student_id, skill_type
        )

        # Wait for all evidence collection to complete concurrently
        ml_evidence, ling_evidence, beh_evidence = await asyncio.gather(
            ml_evidence_task,
            ling_evidence_task,
            beh_evidence_task,
            return_exceptions=True,  # Continue even if one source fails
        )

        # Handle exceptions gracefully
        all_evidence = []

        if isinstance(ml_evidence, Exception):
            logger.warning(f"ML evidence collection failed: {ml_evidence}")
            ml_evidence = []
        all_evidence.extend(ml_evidence)

        if isinstance(ling_evidence, Exception):
            logger.warning(f"Linguistic evidence collection failed: {ling_evidence}")
            ling_evidence = []
        all_evidence.extend(ling_evidence)

        if isinstance(beh_evidence, Exception):
            logger.warning(f"Behavioral evidence collection failed: {beh_evidence}")
            beh_evidence = []
        all_evidence.extend(beh_evidence)

        # Fuse all evidence
        score, confidence, top_evidence = self._fuse_evidence(all_evidence, skill_type)

        return score, confidence, top_evidence

    async def fuse_all_skills(
        self,
        session: AsyncSession,
        student_id: str,
    ) -> Dict[SkillType, Tuple[float, float, List[EvidenceItem]]]:
        """
        Fuse evidence for all skills.

        Args:
            session: Database session
            student_id: Student ID

        Returns:
            Dictionary mapping skills to (score, confidence, evidence)
        """
        results = {}

        for skill_type in [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]:
            try:
                score, confidence, evidence = await self.fuse_skill_evidence(
                    session, student_id, skill_type
                )
                results[skill_type] = (score, confidence, evidence)
            except Exception as e:
                logger.error(f"Failed to fuse evidence for {skill_type.value}: {e}")
                continue

        return results
