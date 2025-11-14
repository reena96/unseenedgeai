"""Integration tests for the complete assessment pipeline."""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import numpy as np
import joblib
from pathlib import Path

from app.services.skill_inference import SkillInferenceService
from app.services.evidence_fusion import EvidenceFusionService
from app.services.reasoning_generator import ReasoningGeneratorService
from app.models.assessment import SkillType
from app.models.features import LinguisticFeatures, BehavioralFeatures
from app.models.student import Student


class TestAssessmentPipeline:
    """Integration tests for end-to-end assessment pipeline."""

    @pytest.fixture
    def mock_models_dir(self, tmp_path):
        """Create mock models directory."""
        models_dir = tmp_path / "models"
        models_dir.mkdir()

        # Create mock XGBoost models for all skills
        for skill_type in [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]:
            model = Mock()
            model.predict = Mock(return_value=np.array([0.75]))
            model.feature_importances_ = np.random.rand(26)  # 26 features

            model_path = models_dir / f"{skill_type.value}_model.pkl"
            joblib.dump(model, model_path)

            # Feature names (26 features)
            features_path = models_dir / f"{skill_type.value}_features.pkl"
            feature_names = [f"feature_{i}" for i in range(26)]
            joblib.dump(feature_names, features_path)

        return str(models_dir)

    @pytest.fixture
    def mock_student_data(self):
        """Create mock student with features."""
        student = Mock(spec=Student)
        student.id = "test_student_123"
        student.grade_level = 3

        # Linguistic features
        ling_features = Mock(spec=LinguisticFeatures)
        ling_features.features_json = {
            "empathy_markers": 8,
            "problem_solving_language": 5,
            "perseverance_indicators": 6,
            "social_processes": 10,
            "cognitive_processes": 7,
            "positive_sentiment": 0.7,
            "negative_sentiment": 0.1,
            "avg_sentence_length": 12.5,
            "syntactic_complexity": 0.4,
            "word_count": 200,
            "unique_word_count": 90,
            "readability_score": 8.5,
            "noun_count": 50,
            "verb_count": 35,
            "adj_count": 20,
            "adv_count": 15,
        }

        # Behavioral features
        beh_features = Mock(spec=BehavioralFeatures)
        beh_features.features_json = {
            "task_completion_rate": 0.85,
            "time_efficiency": 0.75,
            "retry_count": 3,
            "recovery_rate": 0.67,
            "distraction_resistance": 0.90,
            "focus_duration": 45.0,
            "collaboration_indicators": 4,
            "leadership_indicators": 2,
            "event_count": 60,
        }

        return student, ling_features, beh_features

    @pytest.mark.asyncio
    async def test_full_pipeline_single_skill(self, mock_models_dir, mock_student_data):
        """Test complete pipeline for single skill assessment."""
        student, ling_features, beh_features = mock_student_data

        # Setup services
        inference_service = SkillInferenceService(models_dir=mock_models_dir)
        fusion_service = EvidenceFusionService(inference_service=inference_service)
        reasoning_service = ReasoningGeneratorService(api_key="test_key")

        # Mock database session
        mock_session = AsyncMock()

        # Setup query results
        student_result = Mock()
        student_result.scalar_one_or_none = Mock(return_value=student)

        ling_result = Mock()
        ling_result.scalar_one_or_none = Mock(return_value=ling_features)

        beh_result = Mock()
        beh_result.scalar_one_or_none = Mock(return_value=beh_features)

        mock_session.execute = AsyncMock(
            side_effect=[
                student_result,
                ling_result,
                beh_result,
                ling_result,
                beh_result,
            ]
        )

        # Step 1: ML Inference
        score, confidence, importance = await inference_service.infer_skill(
            mock_session, student.id, SkillType.EMPATHY
        )

        assert 0.0 <= score <= 1.0
        assert 0.0 <= confidence <= 1.0
        assert isinstance(importance, dict)

        # Step 2: Evidence Fusion
        fused_score, fused_confidence, evidence = (
            await fusion_service.fuse_skill_evidence(
                mock_session, student.id, SkillType.EMPATHY
            )
        )

        assert 0.0 <= fused_score <= 1.0
        assert 0.0 <= fused_confidence <= 1.0
        assert len(evidence) > 0

        # Step 3: Reasoning Generation (with mock)
        with patch.object(
            reasoning_service, "_generate_fallback_reasoning"
        ) as mock_fallback:
            from app.services.reasoning_generator import SkillReasoning

            mock_fallback.return_value = SkillReasoning(
                skill_type=SkillType.EMPATHY,
                score=fused_score,
                reasoning="Student shows strong empathy skills.",
                strengths=["Uses empathy language", "Shows concern for others"],
                growth_suggestions=[
                    "Practice perspective-taking",
                    "Reflect on feelings",
                ],
            )

            reasoning = await reasoning_service.generate_reasoning(
                SkillType.EMPATHY,
                fused_score,
                fused_confidence,
                evidence,
                student_grade=student.grade_level,
            )

            assert reasoning.skill_type == SkillType.EMPATHY
            assert len(reasoning.reasoning) > 0
            assert len(reasoning.strengths) >= 2
            assert len(reasoning.growth_suggestions) >= 2

    @pytest.mark.asyncio
    async def test_full_pipeline_all_skills(self, mock_models_dir, mock_student_data):
        """Test complete pipeline for all skills."""
        student, ling_features, beh_features = mock_student_data

        # Setup services
        inference_service = SkillInferenceService(models_dir=mock_models_dir)
        fusion_service = EvidenceFusionService(inference_service=inference_service)
        reasoning_service = ReasoningGeneratorService(api_key="test_key")

        # Mock database session
        mock_session = AsyncMock()

        def create_mock_result(value):
            result = Mock()
            result.scalar_one_or_none = Mock(return_value=value)
            return result

        # Setup multiple query results for all skills
        query_results = [
            create_mock_result(student),
            create_mock_result(ling_features),
            create_mock_result(beh_features),
        ] * 8  # 4 skills * 2 queries per skill (for fusion)

        mock_session.execute = AsyncMock(side_effect=query_results)

        # Run pipeline for all skills
        all_results = {}

        for skill_type in [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]:
            # Inference
            score, confidence, importance = await inference_service.infer_skill(
                mock_session, student.id, skill_type
            )

            # Fusion
            fused_score, fused_confidence, evidence = (
                await fusion_service.fuse_skill_evidence(
                    mock_session, student.id, skill_type
                )
            )

            # Store results
            all_results[skill_type] = {
                "score": fused_score,
                "confidence": fused_confidence,
                "evidence_count": len(evidence),
            }

        # Verify all skills were assessed
        assert len(all_results) == 4
        assert all(0.0 <= r["score"] <= 1.0 for r in all_results.values())
        assert all(0.0 <= r["confidence"] <= 1.0 for r in all_results.values())
        assert all(r["evidence_count"] > 0 for r in all_results.values())

    @pytest.mark.asyncio
    async def test_pipeline_latency_requirement(
        self, mock_models_dir, mock_student_data
    ):
        """Test that pipeline meets <30s latency requirement."""
        student, ling_features, beh_features = mock_student_data

        # Setup services
        inference_service = SkillInferenceService(models_dir=mock_models_dir)
        fusion_service = EvidenceFusionService(inference_service=inference_service)

        # Mock database session
        mock_session = AsyncMock()

        def create_mock_result(value):
            result = Mock()
            result.scalar_one_or_none = Mock(return_value=value)
            return result

        # Setup query results for all 4 skills
        query_results = [
            create_mock_result(student),
            create_mock_result(ling_features),
            create_mock_result(beh_features),
        ] * 8

        mock_session.execute = AsyncMock(side_effect=query_results)

        # Measure latency for all skills
        start_time = time.time()

        for skill_type in [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]:
            score, confidence, evidence = await fusion_service.fuse_skill_evidence(
                mock_session, student.id, skill_type
            )

        elapsed_time = time.time() - start_time

        # Verify latency requirement (excluding GPT-4 for this test)
        # With mocked models, should be very fast (<1s)
        assert (
            elapsed_time < 5.0
        ), f"Pipeline took {elapsed_time}s for 4 skills (expected <5s without GPT-4)"

        # Note: In production with real models and GPT-4, target is <30s total

    @pytest.mark.asyncio
    async def test_pipeline_error_recovery(self, mock_models_dir, mock_student_data):
        """Test pipeline handles errors gracefully."""
        student, ling_features, beh_features = mock_student_data

        # Setup services
        inference_service = SkillInferenceService(models_dir=mock_models_dir)
        fusion_service = EvidenceFusionService(inference_service=inference_service)

        # Mock database session
        mock_session = AsyncMock()

        # Simulate missing features for ML inference
        student_result = Mock()
        student_result.scalar_one_or_none = Mock(return_value=student)

        ling_result = Mock()
        ling_result.scalar_one_or_none = Mock(return_value=None)  # Missing!

        beh_result = Mock()
        beh_result.scalar_one_or_none = Mock(return_value=beh_features)

        mock_session.execute = AsyncMock(
            side_effect=[
                student_result,
                ling_result,
                beh_result,
            ]
        )

        # ML inference should fail gracefully
        with pytest.raises(ValueError, match="No features found"):
            await inference_service.infer_skill(
                mock_session, student.id, SkillType.EMPATHY
            )

    @pytest.mark.asyncio
    async def test_pipeline_with_partial_data(self, mock_models_dir, mock_student_data):
        """Test pipeline works with partial data (only linguistic OR behavioral)."""
        student, ling_features, beh_features = mock_student_data

        # Setup services
        inference_service = SkillInferenceService(models_dir=mock_models_dir)

        # Mock database session
        mock_session = AsyncMock()

        # Only linguistic features available
        student_result = Mock()
        student_result.scalar_one_or_none = Mock(return_value=student)

        ling_result = Mock()
        ling_result.scalar_one_or_none = Mock(return_value=ling_features)

        beh_result = Mock()
        beh_result.scalar_one_or_none = Mock(return_value=None)  # No behavioral data

        mock_session.execute = AsyncMock(
            side_effect=[
                student_result,
                ling_result,
                beh_result,
            ]
        )

        # Should still work with just linguistic features
        score, confidence, importance = await inference_service.infer_skill(
            mock_session, student.id, SkillType.EMPATHY
        )

        assert 0.0 <= score <= 1.0
        assert 0.0 <= confidence <= 1.0

    @pytest.mark.asyncio
    async def test_parallel_evidence_collection(
        self, mock_models_dir, mock_student_data
    ):
        """Test that evidence collection can be parallelized."""
        student, ling_features, beh_features = mock_student_data

        # Setup services
        inference_service = SkillInferenceService(models_dir=mock_models_dir)
        fusion_service = EvidenceFusionService(inference_service=inference_service)

        # Mock database session
        mock_session = AsyncMock()

        def create_mock_result(value):
            result = Mock()
            result.scalar_one_or_none = Mock(return_value=value)
            return result

        query_results = [
            create_mock_result(student),
            create_mock_result(ling_features),
            create_mock_result(beh_features),
            create_mock_result(ling_features),
            create_mock_result(beh_features),
        ]

        mock_session.execute = AsyncMock(side_effect=query_results)

        # Collect evidence with timing
        start_time = time.time()

        # This should be fast because evidence collection is I/O bound
        # and can be parallelized
        score, confidence, evidence = await fusion_service.fuse_skill_evidence(
            mock_session, student.id, SkillType.EMPATHY
        )

        elapsed_time = time.time() - start_time

        # With mocked database, should be very fast
        assert elapsed_time < 1.0

        # Verify evidence was collected from multiple sources
        from app.services.evidence_fusion import EvidenceSource

        evidence_sources = {e.source for e in evidence}
        assert len(evidence_sources) > 1  # Should have multiple sources
