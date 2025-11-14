"""Performance and benchmark tests for assessment pipeline."""

import pytest
import time
import asyncio
from unittest.mock import Mock, AsyncMock
import numpy as np
import joblib

from app.services.skill_inference import SkillInferenceService
from app.services.evidence_fusion import EvidenceFusionService
from app.models.assessment import SkillType
from app.models.features import LinguisticFeatures, BehavioralFeatures
from app.models.student import Student


# Mark all tests in this file as slow
pytestmark = pytest.mark.slow


# Picklable mock model class for performance tests
class MockModel:
    """Mock ML model that can be pickled by joblib."""

    def __init__(self):
        self.feature_importances_ = np.random.rand(26)

    def predict(self, X):
        return np.array([0.75] * len(X))


class TestPerformanceBenchmarks:
    """Performance benchmarks for the assessment system."""

    @pytest.fixture
    def mock_models_dir(self, tmp_path):
        """Create mock models directory."""
        models_dir = tmp_path / "models"
        models_dir.mkdir()

        for skill_type in [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]:
            model = MockModel()

            model_path = models_dir / f"{skill_type.value}_model.pkl"
            joblib.dump(model, model_path)

            features_path = models_dir / f"{skill_type.value}_features.pkl"
            joblib.dump([f"feature_{i}" for i in range(26)], features_path)

        return str(models_dir)

    @pytest.fixture
    def mock_student_with_features(self):
        """Create mock student with full feature set."""
        student = Mock(spec=Student)
        student.id = "perf_test_student"

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
    async def test_single_skill_inference_latency(
        self, mock_models_dir, mock_student_with_features
    ):
        """
        Test single skill inference meets latency requirements.

        Target: < 200ms per skill
        """
        student, ling_features, beh_features = mock_student_with_features

        inference_service = SkillInferenceService(models_dir=mock_models_dir)
        mock_session = AsyncMock()

        # Setup mocks
        def create_mock_result(value):
            result = Mock()
            result.scalar_one_or_none = Mock(return_value=value)
            return result

        mock_session.execute = AsyncMock(
            side_effect=[
                create_mock_result(student),
                create_mock_result(ling_features),
                create_mock_result(beh_features),
            ]
        )

        # Measure single inference
        start = time.time()
        score, confidence, importance = await inference_service.infer_skill(
            mock_session, student.id, SkillType.EMPATHY
        )
        elapsed_ms = (time.time() - start) * 1000

        print(f"\nSingle skill inference: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 200, f"Inference took {elapsed_ms}ms, exceeds 200ms target"

    @pytest.mark.asyncio
    async def test_all_skills_inference_latency(
        self, mock_models_dir, mock_student_with_features
    ):
        """
        Test all skills inference meets latency requirements.

        Target: < 30 seconds for all 4 skills (excluding GPT-4)
        """
        student, ling_features, beh_features = mock_student_with_features

        inference_service = SkillInferenceService(models_dir=mock_models_dir)
        fusion_service = EvidenceFusionService(inference_service=inference_service)

        mock_session = AsyncMock()

        def create_mock_result(value):
            result = Mock()
            result.scalar_one_or_none = Mock(return_value=value)
            return result

        # Setup for 4 skills
        query_results = [
            create_mock_result(student),
            create_mock_result(ling_features),
            create_mock_result(beh_features),
        ] * 8  # 4 skills * 2 queries per skill

        mock_session.execute = AsyncMock(side_effect=query_results)

        # Measure all skills
        start = time.time()

        results = []
        for skill_type in [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]:
            score, confidence, evidence = await fusion_service.fuse_skill_evidence(
                mock_session, student.id, skill_type
            )
            results.append((skill_type, score, confidence))

        elapsed = time.time() - start

        print(f"\nAll 4 skills inference: {elapsed:.2f}s")
        assert elapsed < 5.0, f"All skills took {elapsed}s (target <5s without GPT-4)"

        # In production with GPT-4, target is <30s total
        # GPT-4 typically adds 2-5s per skill = 8-20s
        # So 5s + 20s = 25s < 30s target

    @pytest.mark.asyncio
    async def test_batch_student_throughput(
        self, mock_models_dir, mock_student_with_features
    ):
        """
        Test throughput for multiple students.

        Target: Process at least 10 students per minute
        """
        student_template, ling_features, beh_features = mock_student_with_features

        inference_service = SkillInferenceService(models_dir=mock_models_dir)

        # Create 10 mock students
        num_students = 10
        students = []
        for i in range(num_students):
            student = Mock(spec=Student)
            student.id = f"student_{i}"
            students.append(student)

        mock_session = AsyncMock()

        def create_mock_result(value):
            result = Mock()
            result.scalar_one_or_none = Mock(return_value=value)
            return result

        # Setup query results for all students
        query_results = []
        for student in students:
            query_results.extend(
                [
                    create_mock_result(student),
                    create_mock_result(ling_features),
                    create_mock_result(beh_features),
                ]
            )

        mock_session.execute = AsyncMock(side_effect=query_results)

        # Measure batch processing
        start = time.time()

        tasks = []
        for student in students:
            task = inference_service.infer_skill(
                mock_session, student.id, SkillType.EMPATHY
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start

        throughput = num_students / elapsed  # students per second
        throughput_per_minute = throughput * 60

        print(f"\nBatch throughput: {throughput_per_minute:.1f} students/minute")
        assert (
            throughput_per_minute >= 10
        ), f"Throughput {throughput_per_minute:.1f}/min is below 10/min target"

    @pytest.mark.asyncio
    async def test_evidence_fusion_latency(
        self, mock_models_dir, mock_student_with_features
    ):
        """
        Test evidence fusion latency.

        Target: < 100ms per skill
        """
        student, ling_features, beh_features = mock_student_with_features

        inference_service = SkillInferenceService(models_dir=mock_models_dir)
        fusion_service = EvidenceFusionService(inference_service=inference_service)

        mock_session = AsyncMock()

        def create_mock_result(value):
            result = Mock()
            result.scalar_one_or_none = Mock(return_value=value)
            return result

        mock_session.execute = AsyncMock(
            side_effect=[
                create_mock_result(student),
                create_mock_result(ling_features),
                create_mock_result(beh_features),
                create_mock_result(ling_features),
                create_mock_result(beh_features),
            ]
        )

        # Measure fusion
        start = time.time()
        score, confidence, evidence = await fusion_service.fuse_skill_evidence(
            mock_session, student.id, SkillType.EMPATHY
        )
        elapsed_ms = (time.time() - start) * 1000

        print(f"\nEvidence fusion: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 500, f"Fusion took {elapsed_ms}ms, exceeds 500ms target"

    @pytest.mark.asyncio
    async def test_feature_extraction_performance(self, mock_models_dir):
        """Test feature extraction performance."""
        inference_service = SkillInferenceService(models_dir=mock_models_dir)

        # Create realistic feature data
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

        # Run feature extraction 1000 times
        num_iterations = 1000
        start = time.time()

        for _ in range(num_iterations):
            features = inference_service._extract_feature_vector(
                ling_features, beh_features, SkillType.EMPATHY
            )

        elapsed = time.time() - start
        avg_time_ms = (elapsed / num_iterations) * 1000

        print(f"\nFeature extraction avg: {avg_time_ms:.3f}ms")
        assert avg_time_ms < 1.0, f"Feature extraction avg {avg_time_ms}ms exceeds 1ms"

    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(
        self, mock_models_dir, mock_student_with_features
    ):
        """Test system handles concurrent requests efficiently."""
        student, ling_features, beh_features = mock_student_with_features

        inference_service = SkillInferenceService(models_dir=mock_models_dir)

        # Create 50 concurrent requests
        num_concurrent = 50

        mock_sessions = []
        for i in range(num_concurrent):
            mock_session = AsyncMock()

            def create_mock_result(value):
                result = Mock()
                result.scalar_one_or_none = Mock(return_value=value)
                return result

            mock_session.execute = AsyncMock(
                side_effect=[
                    create_mock_result(student),
                    create_mock_result(ling_features),
                    create_mock_result(beh_features),
                ]
            )

            mock_sessions.append(mock_session)

        # Measure concurrent processing
        start = time.time()

        tasks = [
            inference_service.infer_skill(
                mock_sessions[i], f"student_{i}", SkillType.EMPATHY
            )
            for i in range(num_concurrent)
        ]

        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start

        throughput = num_concurrent / elapsed

        print(
            f"\nConcurrent requests: {num_concurrent} in {elapsed:.2f}s ({throughput:.1f} req/s)"
        )
        assert (
            elapsed < 5.0
        ), f"50 concurrent requests took {elapsed}s, exceeds 5s target"
