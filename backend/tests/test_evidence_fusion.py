"""Tests for evidence fusion service."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.services.evidence_fusion import (
    EvidenceFusionService,
    EvidenceItem,
    EvidenceSource,
)
from app.models.assessment import SkillType, EvidenceType
from app.models.features import LinguisticFeatures, BehavioralFeatures


class TestEvidenceFusionService:
    """Test EvidenceFusionService."""

    @pytest.fixture
    def service(self):
        """Create evidence fusion service."""
        return EvidenceFusionService()

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.source_weights is not None
        assert SkillType.EMPATHY in service.source_weights
        assert EvidenceSource.ML_INFERENCE in service.source_weights[SkillType.EMPATHY]

    def test_source_weight_configuration(self, service):
        """Test skill-specific source weights are configured."""
        # Empathy should have higher linguistic weight
        empathy_weights = service.source_weights[SkillType.EMPATHY]
        assert empathy_weights[EvidenceSource.LINGUISTIC_FEATURES] == 0.25

        # Self-regulation should have higher behavioral weight
        self_reg_weights = service.source_weights[SkillType.SELF_REGULATION]
        assert self_reg_weights[EvidenceSource.BEHAVIORAL_FEATURES] == 0.30

    def test_evidence_fusion_basic(self, service):
        """Test basic evidence fusion."""
        evidence_items = [
            EvidenceItem(
                source=EvidenceSource.ML_INFERENCE,
                evidence_type=EvidenceType.BEHAVIORAL,
                content="ML prediction: 0.75",
                score=0.75,
                confidence=0.85,
                relevance=1.0,
                weight=0.5,
            ),
            EvidenceItem(
                source=EvidenceSource.LINGUISTIC_FEATURES,
                evidence_type=EvidenceType.LINGUISTIC,
                content="High empathy markers",
                score=0.80,
                confidence=0.70,
                relevance=0.9,
                weight=0.25,
            ),
            EvidenceItem(
                source=EvidenceSource.BEHAVIORAL_FEATURES,
                evidence_type=EvidenceType.BEHAVIORAL,
                content="Good task completion",
                score=0.70,
                confidence=0.75,
                relevance=0.85,
                weight=0.25,
            ),
        ]

        score, confidence, top_evidence = service._fuse_evidence(
            evidence_items,
            SkillType.EMPATHY
        )

        # Check outputs
        assert 0.0 <= score <= 1.0
        assert 0.0 <= confidence <= 1.0
        assert len(top_evidence) <= 5
        assert all(isinstance(e, EvidenceItem) for e in top_evidence)

    def test_evidence_fusion_empty(self, service):
        """Test fusion with no evidence."""
        score, confidence, top_evidence = service._fuse_evidence(
            [],
            SkillType.EMPATHY
        )

        assert score == 0.5  # Default
        assert confidence == 0.3  # Low confidence
        assert len(top_evidence) == 0

    def test_score_normalization(self, service):
        """Test score normalization."""
        assert service._normalize_score(1.5) == 1.0
        assert service._normalize_score(-0.5) == 0.0
        assert service._normalize_score(0.75) == 0.75

    @pytest.mark.asyncio
    async def test_collect_ml_evidence(self, service):
        """Test ML evidence collection."""
        # Mock inference service
        mock_inference = AsyncMock()
        mock_inference.infer_skill = AsyncMock(
            return_value=(
                0.75,  # score
                0.85,  # confidence
                {'feature_1': 0.3, 'feature_2': 0.5, 'feature_3': 0.2}  # importance
            )
        )
        service.inference_service = mock_inference

        mock_session = Mock()

        evidence = await service._collect_ml_evidence(
            mock_session,
            "student_1",
            SkillType.EMPATHY
        )

        assert len(evidence) > 0
        assert any(e.source == EvidenceSource.ML_INFERENCE for e in evidence)

    @pytest.mark.asyncio
    async def test_collect_linguistic_evidence_empathy(self, service):
        """Test linguistic evidence collection for empathy."""
        mock_session = AsyncMock()

        # Mock linguistic features
        ling_features = Mock(spec=LinguisticFeatures)
        ling_features.features_json = {
            'empathy_markers': 8,
            'social_processes': 12,
        }

        result = Mock()
        result.scalar_one_or_none = Mock(return_value=ling_features)
        mock_session.execute = AsyncMock(return_value=result)

        evidence = await service._collect_linguistic_evidence(
            mock_session,
            "student_1",
            SkillType.EMPATHY
        )

        assert len(evidence) > 0
        assert any('empathy markers' in e.content.lower() for e in evidence)

    @pytest.mark.asyncio
    async def test_collect_behavioral_evidence_self_regulation(self, service):
        """Test behavioral evidence collection for self-regulation."""
        mock_session = AsyncMock()

        # Mock behavioral features
        beh_features = Mock(spec=BehavioralFeatures)
        beh_features.features_json = {
            'distraction_resistance': 0.85,
            'focus_duration': 45.0,
        }

        result = Mock()
        result.scalar_one_or_none = Mock(return_value=beh_features)
        mock_session.execute = AsyncMock(return_value=result)

        evidence = await service._collect_behavioral_evidence(
            mock_session,
            "student_1",
            SkillType.SELF_REGULATION
        )

        assert len(evidence) > 0
        assert any('focus' in e.content.lower() for e in evidence)

    @pytest.mark.asyncio
    async def test_fuse_skill_evidence_integration(self, service):
        """Test full evidence fusion integration."""
        # Mock all collection methods
        service._collect_ml_evidence = AsyncMock(return_value=[
            EvidenceItem(
                source=EvidenceSource.ML_INFERENCE,
                evidence_type=EvidenceType.BEHAVIORAL,
                content="ML prediction: 0.75",
                score=0.75,
                confidence=0.85,
                relevance=1.0,
                weight=0.5,
            )
        ])

        service._collect_linguistic_evidence = AsyncMock(return_value=[
            EvidenceItem(
                source=EvidenceSource.LINGUISTIC_FEATURES,
                evidence_type=EvidenceType.LINGUISTIC,
                content="High empathy markers",
                score=0.80,
                confidence=0.70,
                relevance=0.9,
                weight=0.25,
            )
        ])

        service._collect_behavioral_evidence = AsyncMock(return_value=[
            EvidenceItem(
                source=EvidenceSource.BEHAVIORAL_FEATURES,
                evidence_type=EvidenceType.BEHAVIORAL,
                content="Good task completion",
                score=0.70,
                confidence=0.75,
                relevance=0.85,
                weight=0.25,
            )
        ])

        mock_session = Mock()

        score, confidence, evidence = await service.fuse_skill_evidence(
            mock_session,
            "student_1",
            SkillType.EMPATHY
        )

        # Verify results
        assert 0.0 <= score <= 1.0
        assert 0.0 <= confidence <= 1.0
        assert len(evidence) > 0
        assert len(evidence) <= 5
