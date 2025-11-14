"""ML-based skill inference service using XGBoost models."""

import logging
import os
import joblib
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.models.assessment import SkillType, SkillAssessment
from app.models.features import LinguisticFeatures, BehavioralFeatures
from app.models.student import Student
from app.ml.model_metadata import ModelRegistry

logger = logging.getLogger(__name__)

# Feature dimensions constants
NUM_LINGUISTIC_FEATURES = 16
NUM_BEHAVIORAL_FEATURES = 9
NUM_DERIVED_FEATURES = 1
EXPECTED_FEATURE_COUNT = NUM_LINGUISTIC_FEATURES + NUM_BEHAVIORAL_FEATURES + NUM_DERIVED_FEATURES


class SkillInferenceService:
    """Service for ML-based skill inference using XGBoost models."""

    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize the skill inference service.

        Args:
            models_dir: Directory containing trained XGBoost models
        """
        self.models_dir = Path(models_dir or os.getenv("MODELS_DIR", "./models"))
        self.models: Dict[SkillType, Any] = {}
        self.feature_names: Dict[SkillType, List[str]] = {}

        # Initialize model registry for version tracking
        self.registry = ModelRegistry(models_dir=str(self.models_dir))

        # Skill types to model
        self.skill_types = [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]

        self._load_models()
        logger.info(f"Initialized SkillInferenceService with models from {self.models_dir}")

    def _load_models(self):
        """Load trained XGBoost models from disk with validation."""
        for skill_type in self.skill_types:
            model_path = self.models_dir / f"{skill_type.value}_model.pkl"
            features_path = self.models_dir / f"{skill_type.value}_features.pkl"

            if model_path.exists():
                try:
                    model = joblib.load(model_path)

                    # Load feature names if available
                    if features_path.exists():
                        feature_names = joblib.load(features_path)

                        # Validate feature count matches expected dimensions
                        if len(feature_names) != EXPECTED_FEATURE_COUNT:
                            raise ValueError(
                                f"Model {skill_type.value} expects {len(feature_names)} features "
                                f"but inference extracts {EXPECTED_FEATURE_COUNT} features. "
                                f"Model may have been trained with different feature set."
                            )

                        self.feature_names[skill_type] = feature_names
                        logger.info(f"Loaded {len(feature_names)} feature names for {skill_type.value}")
                    else:
                        logger.warning(f"Feature names not found for {skill_type.value}, will use generic names")

                    # Store model after validation
                    self.models[skill_type] = model

                    # Log version info if available
                    version = self.registry.get_model_version(skill_type.value)
                    if version:
                        logger.info(f"Loaded model for {skill_type.value} (version: {version})")

                        # Verify integrity
                        if not self.registry.verify_model_integrity(skill_type.value):
                            logger.warning(f"Model checksum mismatch for {skill_type.value}!")
                    else:
                        logger.info(f"Loaded model for {skill_type.value} (no version info)")

                except Exception as e:
                    logger.error(f"Failed to load model for {skill_type.value}: {e}")
                    raise  # Fail fast - don't continue with invalid models
            else:
                logger.warning(f"Model not found for {skill_type.value} at {model_path}")

    def _extract_feature_vector(
        self,
        linguistic_features: Optional[LinguisticFeatures],
        behavioral_features: Optional[BehavioralFeatures],
        skill_type: SkillType,
    ) -> np.ndarray:
        """
        Extract feature vector for ML inference.

        Args:
            linguistic_features: Linguistic features object
            behavioral_features: Behavioral features object
            skill_type: Skill type being inferred

        Returns:
            NumPy array of features
        """
        features = []

        # Linguistic features
        if linguistic_features and linguistic_features.features_json:
            ling = linguistic_features.features_json
            features.extend([
                ling.get('empathy_markers', 0),
                ling.get('problem_solving_language', 0),
                ling.get('perseverance_indicators', 0),
                ling.get('social_processes', 0),
                ling.get('cognitive_processes', 0),
                ling.get('positive_sentiment', 0.0),
                ling.get('negative_sentiment', 0.0),
                ling.get('avg_sentence_length', 0.0),
                ling.get('syntactic_complexity', 0.0),
                ling.get('word_count', 0),
                ling.get('unique_word_count', 0),
                ling.get('readability_score', 0.0),
                ling.get('noun_count', 0),
                ling.get('verb_count', 0),
                ling.get('adj_count', 0),
                ling.get('adv_count', 0),
            ])
        else:
            features.extend([0] * NUM_LINGUISTIC_FEATURES)

        # Behavioral features
        if behavioral_features and behavioral_features.features_json:
            beh = behavioral_features.features_json
            features.extend([
                beh.get('task_completion_rate', 0.0),
                beh.get('time_efficiency', 0.0),
                beh.get('retry_count', 0),
                beh.get('recovery_rate', 0.0),
                beh.get('distraction_resistance', 1.0),
                beh.get('focus_duration', 0.0),
                beh.get('collaboration_indicators', 0),
                beh.get('leadership_indicators', 0),
                beh.get('event_count', 0),
            ])
        else:
            # Default behavioral features: all zeros except distraction_resistance=1
            features.extend([0, 0, 0, 0, 1, 0, 0, 0, 0])

        # Skill-specific derived features
        if skill_type == SkillType.EMPATHY:
            # Empathy-specific features
            empathy_score = features[0] if features[0] else 0  # empathy_markers
            social_score = features[3] if features[3] else 0  # social_processes
            features.append(empathy_score * social_score)
        elif skill_type == SkillType.PROBLEM_SOLVING:
            # Problem-solving specific features
            ps_lang = features[1] if features[1] else 0  # problem_solving_language
            cognitive = features[4] if features[4] else 0  # cognitive_processes
            features.append(ps_lang * cognitive)
        elif skill_type == SkillType.SELF_REGULATION:
            # Self-regulation specific features
            distraction_res = features[20] if len(features) > 20 else 1  # distraction_resistance
            focus_dur = features[21] if len(features) > 21 else 0  # focus_duration
            features.append(distraction_res * focus_dur)
        elif skill_type == SkillType.RESILIENCE:
            # Resilience specific features
            retry_count = features[18] if len(features) > 18 else 0  # retry_count
            recovery_rate = features[19] if len(features) > 19 else 0  # recovery_rate
            features.append(retry_count * recovery_rate)

        return np.array(features).reshape(1, -1)

    def _calculate_confidence(
        self,
        model: Any,
        features: np.ndarray,
        prediction: float,
        skill_type: SkillType,
    ) -> float:
        """
        Calculate confidence score for prediction using multiple methods.

        Uses tree variance and prediction extremity to estimate uncertainty:
        1. Tree variance: Lower variance = higher confidence
        2. Prediction extremity: Predictions near 0 or 1 have lower confidence
        3. Feature completeness: Missing features reduce confidence

        Args:
            model: Trained XGBoost model
            features: Feature vector
            prediction: Model prediction
            skill_type: Skill type being predicted

        Returns:
            Confidence score (0-1)
        """
        try:
            confidence_components = []

            # Component 1: Tree prediction variance (if available)
            if hasattr(model, 'get_booster'):
                try:
                    # Get predictions from all trees
                    booster = model.get_booster()
                    # Predict with each tree individually
                    tree_preds = []
                    for tree_idx in range(model.n_estimators):
                        pred = booster.predict(
                            features,
                            iteration_range=(tree_idx, tree_idx + 1),
                            output_margin=False
                        )
                        tree_preds.append(pred[0])

                    # Calculate variance of tree predictions
                    tree_variance = np.var(tree_preds)

                    # Convert variance to confidence (lower variance = higher confidence)
                    # Normalize variance to 0-1 range (empirically tuned)
                    var_confidence = 1.0 / (1.0 + 10 * tree_variance)
                    confidence_components.append(var_confidence)

                    logger.debug(
                        f"Tree variance: {tree_variance:.4f}, "
                        f"var_confidence: {var_confidence:.3f}"
                    )
                except Exception as e:
                    logger.debug(f"Could not calculate tree variance: {e}")

            # Component 2: Prediction extremity
            # Predictions very close to 0 or 1 are less reliable
            # Confidence peaks at mid-range values
            distance_from_edges = min(prediction, 1 - prediction)
            # Peak confidence at 0.3-0.7 range
            if distance_from_edges < 0.2:
                extremity_confidence = 0.5 + 2.5 * distance_from_edges
            else:
                extremity_confidence = 1.0
            confidence_components.append(extremity_confidence)

            # Component 3: Feature completeness
            # Check how many features are non-zero (indicates data richness)
            non_zero_features = np.count_nonzero(features)
            feature_completeness = non_zero_features / EXPECTED_FEATURE_COUNT
            # Confidence increases with feature completeness
            completeness_confidence = 0.5 + 0.5 * feature_completeness
            confidence_components.append(completeness_confidence)

            # Combine confidence components (weighted average)
            if len(confidence_components) >= 3:
                # All three components available
                weights = [0.5, 0.3, 0.2]  # Variance most important
            elif len(confidence_components) == 2:
                # No variance, use extremity and completeness
                weights = [0.6, 0.4]
            else:
                # Only one component
                weights = [1.0]

            confidence = sum(
                c * w for c, w in zip(confidence_components, weights)
            )

            # Ensure confidence is in valid range
            confidence = float(np.clip(confidence, 0.3, 0.95))

            logger.debug(
                f"Confidence for {skill_type.value}: {confidence:.3f} "
                f"(components: {[f'{c:.3f}' for c in confidence_components]})"
            )

            return confidence

        except Exception as e:
            logger.warning(f"Error calculating confidence for {skill_type.value}: {e}")
            # Fallback to simple method
            return float(min(0.85, max(0.5, prediction)))

    def _get_feature_importance(
        self,
        model: Any,
        features: np.ndarray,
        skill_type: SkillType,
    ) -> Dict[str, float]:
        """
        Get feature importance for this prediction.

        Args:
            model: Trained model
            features: Feature vector
            skill_type: Skill type

        Returns:
            Dictionary of feature names to importance scores
        """
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                feature_names = self.feature_names.get(skill_type, [])

                if len(feature_names) == len(importances):
                    return dict(zip(feature_names, importances.tolist()))
                else:
                    # Generic feature names
                    return {f"feature_{i}": imp for i, imp in enumerate(importances)}
            else:
                return {}
        except Exception as e:
            logger.warning(f"Error getting feature importance: {e}")
            return {}

    async def infer_skill(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
    ) -> Tuple[float, float, Dict[str, float]]:
        """
        Infer skill score using ML model.

        Args:
            session: Database session
            student_id: Student ID
            skill_type: Skill to infer

        Returns:
            Tuple of (score, confidence, feature_importance)

        Raises:
            ValueError: If model not loaded or insufficient data
        """
        if skill_type not in self.models:
            raise ValueError(f"Model not loaded for skill: {skill_type.value}")

        logger.info(f"Inferring {skill_type.value} for student {student_id}")

        # Optimized: Fetch student existence check and both feature types in parallel
        # This reduces database round-trips from 3 sequential to 2 parallel queries
        import asyncio

        # Check student exists (lightweight query)
        student_task = session.execute(
            select(Student.id).where(Student.id == student_id)
        )

        # Fetch both feature types in parallel
        ling_task = session.execute(
            select(LinguisticFeatures)
            .where(LinguisticFeatures.student_id == student_id)
            .order_by(LinguisticFeatures.created_at.desc())
            .limit(1)
        )

        beh_task = session.execute(
            select(BehavioralFeatures)
            .where(BehavioralFeatures.student_id == student_id)
            .order_by(BehavioralFeatures.created_at.desc())
            .limit(1)
        )

        # Wait for all queries to complete
        student_result, ling_result, beh_result = await asyncio.gather(
            student_task, ling_task, beh_task
        )

        # Check student exists
        if not student_result.scalar_one_or_none():
            raise ValueError(f"Student {student_id} not found")

        # Extract features
        linguistic_features = ling_result.scalar_one_or_none()
        behavioral_features = beh_result.scalar_one_or_none()

        if not linguistic_features and not behavioral_features:
            raise ValueError(
                f"No features found for student {student_id}. "
                "Run feature extraction first."
            )

        # Extract feature vector
        features = self._extract_feature_vector(
            linguistic_features,
            behavioral_features,
            skill_type,
        )

        # Make prediction
        model = self.models[skill_type]
        prediction = model.predict(features)[0]

        # Ensure score is in 0-1 range
        score = float(np.clip(prediction, 0.0, 1.0))

        # Calculate confidence with improved method
        confidence = self._calculate_confidence(model, features, score, skill_type)

        # Get feature importance
        feature_importance = self._get_feature_importance(model, features, skill_type)

        logger.info(
            f"Inferred {skill_type.value} for student {student_id}: "
            f"score={score:.3f}, confidence={confidence:.3f}"
        )

        return score, confidence, feature_importance

    async def infer_all_skills(
        self,
        session: AsyncSession,
        student_id: str,
    ) -> Dict[SkillType, Tuple[float, float, Dict[str, float]]]:
        """
        Infer all skills for a student.

        Args:
            session: Database session
            student_id: Student ID

        Returns:
            Dictionary mapping skill types to (score, confidence, feature_importance)
        """
        results = {}

        for skill_type in self.skill_types:
            if skill_type in self.models:
                try:
                    score, confidence, importance = await self.infer_skill(
                        session, student_id, skill_type
                    )
                    results[skill_type] = (score, confidence, importance)
                except Exception as e:
                    logger.error(f"Failed to infer {skill_type.value}: {e}")
                    # Continue with other skills

        return results

    def get_model_version(self, skill_type: SkillType) -> Optional[str]:
        """
        Get version of loaded model.

        Args:
            skill_type: Skill type

        Returns:
            Version string or None
        """
        return self.registry.get_model_version(skill_type.value)

    def get_all_model_versions(self) -> Dict[str, str]:
        """
        Get versions of all loaded models.

        Returns:
            Dictionary mapping skill types to versions
        """
        versions = {}
        for skill_type in self.skill_types:
            version = self.get_model_version(skill_type)
            if version:
                versions[skill_type.value] = version
        return versions
