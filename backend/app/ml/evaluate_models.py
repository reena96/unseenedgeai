"""Evaluate trained XGBoost models against teacher ratings."""

import logging
import argparse
import sys
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)
from scipy.stats import pearsonr, spearmanr
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.models.assessment import SkillType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate trained models against ground truth teacher ratings."""

    def __init__(
        self,
        models_dir: str = "./models",
        test_data_path: Optional[str] = None,
    ):
        """
        Initialize the model evaluator.

        Args:
            models_dir: Directory containing trained models
            test_data_path: Path to test data CSV with teacher ratings
        """
        self.models_dir = Path(models_dir)
        self.test_data_path = Path(test_data_path) if test_data_path else None
        self.models: Dict[SkillType, Any] = {}
        self.feature_names: Dict[SkillType, List[str]] = {}

        # Skill types to evaluate
        self.skill_types = [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]

        self._load_models()
        logger.info(f"Initialized ModelEvaluator with models from {self.models_dir}")

    def _load_models(self):
        """Load trained models from disk."""
        for skill_type in self.skill_types:
            model_path = self.models_dir / f"{skill_type.value}_model.pkl"
            features_path = self.models_dir / f"{skill_type.value}_features.pkl"

            if model_path.exists():
                try:
                    self.models[skill_type] = joblib.load(model_path)
                    logger.info(f"Loaded model for {skill_type.value}")

                    if features_path.exists():
                        self.feature_names[skill_type] = joblib.load(features_path)
                except Exception as e:
                    logger.error(f"Failed to load model for {skill_type.value}: {e}")
            else:
                logger.warning(f"Model not found: {model_path}")

    def load_test_data(self) -> pd.DataFrame:
        """
        Load test data with teacher ratings.

        Expected columns:
        - student_id
        - Features (linguistic + behavioral + derived)
        - Teacher ratings: empathy_teacher, problem_solving_teacher, etc.

        Returns:
            DataFrame with test data
        """
        if not self.test_data_path or not self.test_data_path.exists():
            raise FileNotFoundError(f"Test data not found: {self.test_data_path}")

        df = pd.read_csv(self.test_data_path)
        logger.info(f"Loaded {len(df)} test examples with teacher ratings")

        return df

    def extract_features(
        self,
        df: pd.DataFrame,
        skill_type: SkillType,
    ) -> np.ndarray:
        """
        Extract feature matrix for predictions.

        Args:
            df: Test data
            skill_type: Skill type

        Returns:
            Feature matrix
        """
        feature_names = self.feature_names.get(skill_type, [])

        if not feature_names:
            raise ValueError(f"No feature names found for {skill_type.value}")

        # Check if all features exist
        missing_cols = [col for col in feature_names if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing feature columns: {missing_cols}")
            for col in missing_cols:
                df[col] = 0

        # Extract features
        X = df[feature_names].values
        X = np.nan_to_num(X, nan=0.0)

        return X

    def calculate_correlation(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict[str, float]:
        """
        Calculate correlation metrics between predictions and teacher ratings.

        Args:
            y_true: True teacher ratings
            y_pred: Model predictions

        Returns:
            Dictionary of correlation metrics
        """
        # Pearson correlation (linear relationship)
        pearson_r, pearson_p = pearsonr(y_true, y_pred)

        # Spearman correlation (rank-based, more robust)
        spearman_r, spearman_p = spearmanr(y_true, y_pred)

        return {
            "pearson_r": float(pearson_r),
            "pearson_p_value": float(pearson_p),
            "spearman_r": float(spearman_r),
            "spearman_p_value": float(spearman_p),
        }

    def calculate_regression_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict[str, float]:
        """
        Calculate regression performance metrics.

        Args:
            y_true: True values
            y_pred: Predicted values

        Returns:
            Dictionary of metrics
        """
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        # Calculate percentage of predictions within tolerance
        tolerance_10 = np.mean(np.abs(y_true - y_pred) <= 0.1)
        tolerance_15 = np.mean(np.abs(y_true - y_pred) <= 0.15)
        tolerance_20 = np.mean(np.abs(y_true - y_pred) <= 0.2)

        return {
            "mse": float(mse),
            "rmse": float(rmse),
            "mae": float(mae),
            "r2_score": float(r2),
            "within_0.1": float(tolerance_10),
            "within_0.15": float(tolerance_15),
            "within_0.2": float(tolerance_20),
        }

    def evaluate_skill(
        self,
        df: pd.DataFrame,
        skill_type: SkillType,
    ) -> Dict[str, Any]:
        """
        Evaluate model for a single skill.

        Args:
            df: Test data with teacher ratings
            skill_type: Skill to evaluate

        Returns:
            Dictionary of evaluation metrics
        """
        if skill_type not in self.models:
            logger.warning(f"No model loaded for {skill_type.value}")
            return {}

        logger.info(f"Evaluating {skill_type.value} model")

        # Get model and features
        model = self.models[skill_type]
        X = self.extract_features(df, skill_type)

        # Get teacher ratings (ground truth)
        teacher_col = f"{skill_type.value}_teacher"
        if teacher_col not in df.columns:
            raise ValueError(f"Teacher rating column {teacher_col} not found")

        y_true = df[teacher_col].values
        y_true = np.nan_to_num(y_true, nan=0.5)
        y_true = np.clip(y_true, 0.0, 1.0)

        # Make predictions
        y_pred = model.predict(X)
        y_pred = np.clip(y_pred, 0.0, 1.0)

        # Calculate metrics
        correlation_metrics = self.calculate_correlation(y_true, y_pred)
        regression_metrics = self.calculate_regression_metrics(y_true, y_pred)

        # Combine all metrics
        metrics = {
            "skill": skill_type.value,
            "n_samples": len(y_true),
            **correlation_metrics,
            **regression_metrics,
        }

        # Log results
        logger.info(f"Results for {skill_type.value}:")
        logger.info(
            f"  Pearson r: {correlation_metrics['pearson_r']:.3f} (p={correlation_metrics['pearson_p_value']:.4f})"
        )
        logger.info(f"  Spearman r: {correlation_metrics['spearman_r']:.3f}")
        logger.info(f"  RMSE: {regression_metrics['rmse']:.3f}")
        logger.info(f"  MAE: {regression_metrics['mae']:.3f}")
        logger.info(f"  R²: {regression_metrics['r2_score']:.3f}")
        logger.info(f"  Within ±0.1: {regression_metrics['within_0.1']*100:.1f}%")

        return metrics

    def evaluate_all_skills(
        self,
        df: Optional[pd.DataFrame] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate all skill models.

        Args:
            df: Test data (loads from path if not provided)

        Returns:
            Dictionary of evaluation results for all skills
        """
        if df is None:
            df = self.load_test_data()

        results = {}
        summary_metrics = {
            "avg_pearson_r": [],
            "avg_spearman_r": [],
            "avg_rmse": [],
            "avg_mae": [],
            "avg_r2": [],
        }

        for skill_type in self.skill_types:
            if skill_type in self.models:
                try:
                    metrics = self.evaluate_skill(df, skill_type)
                    results[skill_type.value] = metrics

                    # Collect for averaging
                    summary_metrics["avg_pearson_r"].append(metrics["pearson_r"])
                    summary_metrics["avg_spearman_r"].append(metrics["spearman_r"])
                    summary_metrics["avg_rmse"].append(metrics["rmse"])
                    summary_metrics["avg_mae"].append(metrics["mae"])
                    summary_metrics["avg_r2"].append(metrics["r2_score"])

                except Exception as e:
                    logger.error(f"Failed to evaluate {skill_type.value}: {e}")
                    continue

        # Calculate averages
        summary = {
            "avg_pearson_r": float(np.mean(summary_metrics["avg_pearson_r"])),
            "avg_spearman_r": float(np.mean(summary_metrics["avg_spearman_r"])),
            "avg_rmse": float(np.mean(summary_metrics["avg_rmse"])),
            "avg_mae": float(np.mean(summary_metrics["avg_mae"])),
            "avg_r2": float(np.mean(summary_metrics["avg_r2"])),
        }

        results["summary"] = summary

        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY ACROSS ALL SKILLS")
        logger.info("=" * 60)
        logger.info(f"Average Pearson r: {summary['avg_pearson_r']:.3f}")
        logger.info(f"Average Spearman r: {summary['avg_spearman_r']:.3f}")
        logger.info(f"Average RMSE: {summary['avg_rmse']:.3f}")
        logger.info(f"Average MAE: {summary['avg_mae']:.3f}")
        logger.info(f"Average R²: {summary['avg_r2']:.3f}")

        return results

    def save_evaluation_report(
        self,
        results: Dict[str, Any],
        output_path: str = "./evaluation_report.json",
    ):
        """
        Save evaluation report to JSON file.

        Args:
            results: Evaluation results
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Saved evaluation report to {output_path}")


def main():
    """Main entry point for evaluation script."""
    parser = argparse.ArgumentParser(description="Evaluate XGBoost skill models")
    parser.add_argument(
        "--test-data",
        type=str,
        required=True,
        help="Path to test data CSV with teacher ratings",
    )
    parser.add_argument(
        "--models-dir",
        type=str,
        default="./models",
        help="Directory containing trained models",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./evaluation_report.json",
        help="Output path for evaluation report",
    )

    args = parser.parse_args()

    # Evaluate models
    evaluator = ModelEvaluator(args.models_dir, args.test_data)
    results = evaluator.evaluate_all_skills()

    # Save report
    evaluator.save_evaluation_report(results, args.output)


if __name__ == "__main__":
    main()
