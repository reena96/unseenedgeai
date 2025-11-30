"""Train XGBoost models for skill inference."""

import logging
import argparse
import sys
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.models.assessment import SkillType  # noqa: E402
from app.ml.model_metadata import ModelRegistry  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillModelTrainer:
    """Train XGBoost models for skill inference."""

    def __init__(
        self, data_path: str, models_dir: str = "./models", model_version: str = "1.0.0"
    ):
        """
        Initialize the model trainer.

        Args:
            data_path: Path to training data CSV
            models_dir: Directory to save trained models
            model_version: Version string for trained models
        """
        self.data_path = Path(data_path)
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.model_version = model_version

        # Initialize model registry
        self.registry = ModelRegistry(models_dir=str(self.models_dir))

        # Skill types to train
        self.skill_types = [
            SkillType.EMPATHY,
            SkillType.ADAPTABILITY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
            SkillType.COMMUNICATION,
            SkillType.COLLABORATION,
        ]

        logger.info(f"Initialized trainer with data from {self.data_path}")
        logger.info(f"Model version: {self.model_version}")

    def load_data(self) -> pd.DataFrame:
        """
        Load training data from CSV.

        Expected columns:
        - student_id
        - Linguistic features (16 columns)
        - Behavioral features (9 columns)
        - Skill-specific derived features (1 column per skill)
        - Target scores for each skill (empathy_score, problem_solving_score, etc.)

        Returns:
            DataFrame with training data
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")

        df = pd.read_csv(self.data_path)
        logger.info(
            f"Loaded {len(df)} training examples with {len(df.columns)} features"
        )

        return df

    def get_feature_names(self, skill_type: SkillType) -> List[str]:
        """
        Get feature names for a specific skill.

        Args:
            skill_type: Skill type

        Returns:
            List of feature names
        """
        # Base linguistic features (16)
        linguistic_features = [
            "empathy_markers",
            "problem_solving_language",
            "perseverance_indicators",
            "social_processes",
            "cognitive_processes",
            "positive_sentiment",
            "negative_sentiment",
            "avg_sentence_length",
            "syntactic_complexity",
            "word_count",
            "unique_word_count",
            "readability_score",
            "noun_count",
            "verb_count",
            "adj_count",
            "adv_count",
        ]

        # Base behavioral features (9)
        behavioral_features = [
            "task_completion_rate",
            "time_efficiency",
            "retry_count",
            "recovery_rate",
            "distraction_resistance",
            "focus_duration",
            "collaboration_indicators",
            "leadership_indicators",
            "event_count",
        ]

        # Skill-specific derived feature
        skill_feature_map = {
            SkillType.EMPATHY: "empathy_social_interaction",
            SkillType.ADAPTABILITY: "adaptability_flexibility",
            SkillType.PROBLEM_SOLVING: "problem_solving_cognitive",
            SkillType.SELF_REGULATION: "self_regulation_focus",
            SkillType.RESILIENCE: "resilience_recovery",
            SkillType.COMMUNICATION: "communication_expression",
            SkillType.COLLABORATION: "collaboration_teamwork",
        }

        all_features = linguistic_features + behavioral_features
        all_features.append(skill_feature_map.get(skill_type, "derived_feature"))

        return all_features

    def prepare_data(
        self,
        df: pd.DataFrame,
        skill_type: SkillType,
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare features and target for training.

        Args:
            df: Training data
            skill_type: Skill to train

        Returns:
            Tuple of (X, y, feature_names)
        """
        feature_names = self.get_feature_names(skill_type)
        target_col = f"{skill_type.value}_score"

        # Check if all feature columns exist
        missing_cols = [col for col in feature_names if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing feature columns: {missing_cols}")
            # Fill missing columns with zeros
            for col in missing_cols:
                df[col] = 0

        # Check if target column exists
        if target_col not in df.columns:
            raise ValueError(f"Target column {target_col} not found in data")

        # Extract features and target
        X = df[feature_names].values
        y = df[target_col].values

        # Handle missing values
        X = np.nan_to_num(X, nan=0.0)
        y = np.nan_to_num(y, nan=0.5)

        # Ensure target is in 0-1 range
        y = np.clip(y, 0.0, 1.0)

        logger.info(
            f"Prepared {len(X)} samples with {len(feature_names)} features for {skill_type.value}"
        )

        return X, y, feature_names

    def train_model(
        self,
        X: np.ndarray,
        y: np.ndarray,
        skill_type: SkillType,
    ) -> Tuple[xgb.XGBRegressor, Dict[str, float]]:
        """
        Train XGBoost model for a skill.

        Args:
            X: Feature matrix
            y: Target scores
            skill_type: Skill type

        Returns:
            Tuple of (trained model, performance metrics dict)
        """
        logger.info(f"Training XGBoost model for {skill_type.value}")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Configure XGBoost
        model = xgb.XGBRegressor(
            objective="reg:squarederror",
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
        )

        # Train model
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )

        # Evaluate on test set
        y_pred = model.predict(X_test)
        y_pred = np.clip(y_pred, 0.0, 1.0)

        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        logger.info(f"Model performance for {skill_type.value}:")
        logger.info(f"  MSE: {mse:.4f}")
        logger.info(f"  MAE: {mae:.4f}")
        logger.info(f"  R2: {r2:.4f}")

        # Cross-validation
        cv_scores = cross_val_score(
            model, X, y, cv=5, scoring="neg_mean_squared_error", n_jobs=-1
        )
        cv_mse = -cv_scores.mean()
        cv_std = cv_scores.std()

        logger.info(f"  CV MSE: {cv_mse:.4f} (+/- {cv_std:.4f})")

        # Collect metrics
        metrics = {
            "mse": float(mse),
            "mae": float(mae),
            "r2": float(r2),
            "cv_mse": float(cv_mse),
            "cv_std": float(cv_std),
        }

        return model, metrics

    def save_model(
        self,
        model: xgb.XGBRegressor,
        feature_names: List[str],
        skill_type: SkillType,
        performance_metrics: Dict[str, float],
        training_samples: int,
    ):
        """
        Save trained model, feature names, and metadata.

        Args:
            model: Trained model
            feature_names: List of feature names
            skill_type: Skill type
            performance_metrics: Performance metrics from evaluation
            training_samples: Number of training samples
        """
        model_path = self.models_dir / f"{skill_type.value}_model.pkl"
        features_path = self.models_dir / f"{skill_type.value}_features.pkl"

        # Save model and features
        joblib.dump(model, model_path)
        joblib.dump(feature_names, features_path)

        logger.info(f"Saved model to {model_path}")
        logger.info(f"Saved feature names to {features_path}")

        # Register model with metadata
        hyperparameters = {
            "n_estimators": model.n_estimators,
            "max_depth": model.max_depth,
            "learning_rate": model.learning_rate,
            "subsample": model.subsample,
            "colsample_bytree": model.colsample_bytree,
        }

        self.registry.register_model(
            skill_type=skill_type.value,
            version=self.model_version,
            model_type="XGBRegressor",
            hyperparameters=hyperparameters,
            performance_metrics=performance_metrics,
            feature_count=len(feature_names),
            training_samples=training_samples,
        )

        logger.info(
            f"Registered model {skill_type.value} v{self.model_version} in registry"
        )

    def train_all_skills(self):
        """Train models for all skills."""
        # Load data
        df = self.load_data()

        # Train each skill model
        for skill_type in self.skill_types:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Training model for {skill_type.value}")
                logger.info(f"{'='*60}")

                # Prepare data
                X, y, feature_names = self.prepare_data(df, skill_type)

                # Train model and get metrics
                model, metrics = self.train_model(X, y, skill_type)

                # Save model with metadata
                self.save_model(
                    model,
                    feature_names,
                    skill_type,
                    performance_metrics=metrics,
                    training_samples=len(X),
                )

                logger.info(f"Successfully trained model for {skill_type.value}\n")

            except Exception as e:
                logger.error(f"Failed to train model for {skill_type.value}: {e}")
                continue

        logger.info(f"\nTraining complete. Models saved to {self.models_dir}")


def main():
    """Main entry point for training script."""
    parser = argparse.ArgumentParser(
        description="Train XGBoost models for skill inference"
    )
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Path to training data CSV file",
    )
    parser.add_argument(
        "--models-dir",
        type=str,
        default="./models",
        help="Directory to save trained models",
    )

    args = parser.parse_args()

    # Train models
    trainer = SkillModelTrainer(args.data, args.models_dir)
    trainer.train_all_skills()


if __name__ == "__main__":
    main()
