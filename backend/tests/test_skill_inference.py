"""Tests for skill inference service."""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import joblib

from app.services.skill_inference import SkillInferenceService
from app.models.assessment import SkillType
from app.models.features import LinguisticFeatures, BehavioralFeatures
from app.models.student import Student


class TestSkillInferenceService:
    """Test SkillInferenceService."""

    @pytest.fixture
    def mock_models_dir(self, tmp_path):
        """Create mock models directory with fake models."""
        models_dir = tmp_path / "models"
        models_dir.mkdir()

        # Create mock XGBoost models
        for skill_type in [SkillType.EMPATHY, SkillType.PROBLEM_SOLVING]:
            model = Mock()
            model.predict = Mock(return_value=np.array([0.75]))
            model.feature_importances_ = np.array([0.1, 0.2, 0.3, 0.15, 0.25])

            model_path = models_dir / f"{skill_type.value}_model.pkl"
            joblib.dump(model, model_path)

            # Feature names
            features_path = models_dir / f"{skill_type.value}_features.pkl"
            joblib.dump(["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"], features_path)

        return str(models_dir)

    @pytest.fixture
    def service(self, mock_models_dir):
        """Create inference service with mock models."""
        return SkillInferenceService(models_dir=mock_models_dir)

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert len(service.models) == 2  # Empathy and problem_solving
        assert SkillType.EMPATHY in service.models
        assert SkillType.PROBLEM_SOLVING in service.models

    def test_feature_vector_extraction(self, service):
        """Test feature vector extraction."""
        # Create mock features
        ling_features = Mock(spec=LinguisticFeatures)
        ling_features.features_json = {
            'empathy_markers': 5,
            'problem_solving_language': 3,
            'perseverance_indicators': 2,
            'social_processes': 7,
            'cognitive_processes': 4,
            'positive_sentiment': 0.6,
            'negative_sentiment': 0.1,
            'avg_sentence_length': 12.5,
            'syntactic_complexity': 0.4,
            'word_count': 150,
            'unique_word_count': 80,
            'readability_score': 8.5,
            'noun_count': 40,
            'verb_count': 30,
            'adj_count': 15,
            'adv_count': 10,
        }

        beh_features = Mock(spec=BehavioralFeatures)
        beh_features.features_json = {
            'task_completion_rate': 0.85,
            'time_efficiency': 0.70,
            'retry_count': 3,
            'recovery_rate': 0.67,
            'distraction_resistance': 0.90,
            'focus_duration': 45.0,
            'collaboration_indicators': 2,
            'leadership_indicators': 1,
            'event_count': 50,
        }

        # Extract features
        features = service._extract_feature_vector(
            ling_features,
            beh_features,
            SkillType.EMPATHY
        )

        assert features.shape == (1, 26)  # 16 ling + 9 beh + 1 derived
        assert features[0, 0] == 5  # empathy_markers
        assert features[0, 16] == 0.85  # task_completion_rate

    @pytest.mark.asyncio
    async def test_infer_skill_success(self, service):
        """Test successful skill inference."""
        # Mock database session
        mock_session = AsyncMock()

        # Mock student query
        student = Mock(spec=Student)
        student.id = "student_1"

        student_result = Mock()
        student_result.scalar_one_or_none = Mock(return_value=student)

        # Mock feature queries
        ling_features = Mock(spec=LinguisticFeatures)
        ling_features.features_json = {
            'empathy_markers': 5, 'problem_solving_language': 3,
            'perseverance_indicators': 2, 'social_processes': 7,
            'cognitive_processes': 4, 'positive_sentiment': 0.6,
            'negative_sentiment': 0.1, 'avg_sentence_length': 12.5,
            'syntactic_complexity': 0.4, 'word_count': 150,
            'unique_word_count': 80, 'readability_score': 8.5,
            'noun_count': 40, 'verb_count': 30, 'adj_count': 15, 'adv_count': 10,
        }

        ling_result = Mock()
        ling_result.scalar_one_or_none = Mock(return_value=ling_features)

        beh_features = Mock(spec=BehavioralFeatures)
        beh_features.features_json = {
            'task_completion_rate': 0.85, 'time_efficiency': 0.70,
            'retry_count': 3, 'recovery_rate': 0.67,
            'distraction_resistance': 0.90, 'focus_duration': 45.0,
            'collaboration_indicators': 2, 'leadership_indicators': 1,
            'event_count': 50,
        }

        beh_result = Mock()
        beh_result.scalar_one_or_none = Mock(return_value=beh_features)

        # Setup mock execute to return different results
        mock_session.execute = AsyncMock(side_effect=[
            student_result,
            ling_result,
            beh_result,
        ])

        # Run inference
        score, confidence, importance = await service.infer_skill(
            mock_session,
            "student_1",
            SkillType.EMPATHY
        )

        # Assertions
        assert 0.0 <= score <= 1.0
        assert 0.0 <= confidence <= 1.0
        assert isinstance(importance, dict)

    @pytest.mark.asyncio
    async def test_infer_skill_no_features(self, service):
        """Test inference fails with no features."""
        mock_session = AsyncMock()

        # Mock student exists but no features
        student = Mock(spec=Student)
        student_result = Mock()
        student_result.scalar_one_or_none = Mock(return_value=student)

        ling_result = Mock()
        ling_result.scalar_one_or_none = Mock(return_value=None)

        beh_result = Mock()
        beh_result.scalar_one_or_none = Mock(return_value=None)

        mock_session.execute = AsyncMock(side_effect=[
            student_result,
            ling_result,
            beh_result,
        ])

        # Should raise ValueError
        with pytest.raises(ValueError, match="No features found"):
            await service.infer_skill(mock_session, "student_1", SkillType.EMPATHY)

    def test_confidence_calculation(self, service):
        """Test confidence score calculation."""
        model = service.models[SkillType.EMPATHY]
        features = np.array([[0.5] * 26])

        confidence = service._calculate_confidence(model, features, 0.75)

        assert 0.0 <= confidence <= 1.0

    def test_feature_importance_extraction(self, service):
        """Test feature importance extraction."""
        model = service.models[SkillType.EMPATHY]
        features = np.array([[0.5] * 26])

        importance = service._get_feature_importance(
            model, features, SkillType.EMPATHY
        )

        assert isinstance(importance, dict)
        assert len(importance) == 5  # Model has 5 features
