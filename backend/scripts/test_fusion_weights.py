# -*- coding: utf-8 -*-
"""
Test different fusion weighting schemes with synthetic data.

This script validates the multi-source fusion algorithm by:
1. Generating synthetic data from all 3 sources (transcript, game, teacher)
2. Testing different weighting schemes
3. Comparing against ground truth
4. Determining optimal skill-specific weights

Task 21 Deliverable: Optimal fusion weights documented
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class SyntheticEvidenceGenerator:
    """Generate synthetic evidence from multiple sources."""

    def __init__(self, seed: int = 42):
        """Initialize generator."""
        np.random.seed(seed)
        self.rng = np.random.default_rng(seed)
        self.skills = [
            "empathy",
            "collaboration",
            "problem_solving",
            "self_regulation",
            "resilience",
            "adaptability",
            "communication",
        ]

    def generate_ground_truth(
        self, n_students: int = 300
    ) -> Dict[int, Dict[str, float]]:
        """
        Generate ground truth skill scores for synthetic students.

        Args:
            n_students: Number of students

        Returns:
            Dict mapping student_id to skill scores (0.0-1.0)
        """
        ground_truth = {}

        for student_id in range(n_students):
            # Generate correlated skill scores (students good at one
            # skill tend to be good at others)
            base_ability = self.rng.normal(0.5, 0.15)
            base_ability = np.clip(base_ability, 0.0, 1.0)

            scores = {}
            for skill in self.skills:
                # Add skill-specific variation
                skill_score = base_ability + self.rng.normal(0, 0.1)
                scores[skill] = float(np.clip(skill_score, 0.0, 1.0))

            ground_truth[student_id] = scores

        return ground_truth

    def generate_evidence(
        self,
        ground_truth: Dict[int, Dict[str, float]],
        source: str,
        noise_level: float = 0.1,
    ) -> Dict[int, Dict[str, float]]:
        """
        Generate noisy evidence from a source based on ground truth.

        Args:
            ground_truth: True skill scores
            source: Evidence source ('transcript', 'game', 'teacher')
            noise_level: Amount of noise to add (0.0-1.0)

        Returns:
            Dict mapping student_id to predicted skill scores
        """
        evidence = {}

        # Source-specific biases and noise patterns
        source_config = {
            "transcript": {"bias": 0.0, "noise": 0.12, "reliability": 0.85},
            "game": {"bias": -0.05, "noise": 0.10, "reliability": 0.90},
            "teacher": {"bias": 0.05, "noise": 0.15, "reliability": 0.75},
        }

        config = source_config.get(
            source, {"bias": 0.0, "noise": 0.1, "reliability": 0.8}
        )

        for student_id, true_scores in ground_truth.items():
            predicted_scores = {}

            for skill, true_score in true_scores.items():
                # Add bias and noise
                noise = self.rng.normal(config["bias"], config["noise"] * noise_level)
                predicted_score = true_score + noise

                # Clip to valid range
                predicted_scores[skill] = float(np.clip(predicted_score, 0.0, 1.0))

            evidence[student_id] = predicted_scores

        return evidence


class FusionWeightOptimizer:
    """Test and optimize fusion weights."""

    def __init__(self, skills: List[str]):
        """Initialize optimizer."""
        self.skills = skills
        self.sources = ["transcript", "game", "teacher"]

    def fuse_scores(
        self,
        evidence: Dict[str, Dict[int, Dict[str, float]]],
        weights: Dict[str, float],
        skill: str,
    ) -> Dict[int, float]:
        """
        Fuse evidence from multiple sources using specified weights.

        Args:
            evidence: Evidence from all sources
            weights: Fusion weights {source: weight}
            skill: Skill to fuse

        Returns:
            Dict mapping student_id to fused score
        """
        fused = {}

        # Get all student IDs
        student_ids = set()
        for source_evidence in evidence.values():
            student_ids.update(source_evidence.keys())

        for student_id in student_ids:
            total_weight = 0.0
            weighted_sum = 0.0

            for source in self.sources:
                if source in evidence and student_id in evidence[source]:
                    weight = weights.get(source, 0.0)
                    score = evidence[source][student_id].get(skill, 0.5)

                    weighted_sum += weight * score
                    total_weight += weight

            if total_weight > 0:
                fused[student_id] = weighted_sum / total_weight
            else:
                fused[student_id] = 0.5  # Default

        return fused

    def evaluate_weights(
        self,
        fused_scores: Dict[int, float],
        ground_truth: Dict[int, Dict[str, float]],
        skill: str,
    ) -> Dict[str, float]:
        """
        Evaluate fusion weights against ground truth.

        Args:
            fused_scores: Fused scores
            ground_truth: True scores
            skill: Skill name

        Returns:
            Dict with evaluation metrics
        """
        # Align fused scores with ground truth
        student_ids = sorted(fused_scores.keys())
        y_true = [ground_truth[sid][skill] for sid in student_ids]
        y_pred = [fused_scores[sid] for sid in student_ids]

        # Calculate metrics
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        correlation, p_value = pearsonr(y_true, y_pred)

        return {
            "mae": float(mae),
            "rmse": float(rmse),
            "correlation": float(correlation),
            "p_value": float(p_value),
            "n_students": len(student_ids),
        }

    def test_weighting_schemes(
        self,
        evidence: Dict[str, Dict[int, Dict[str, float]]],
        ground_truth: Dict[int, Dict[str, float]],
        skill: str,
    ) -> Dict[str, Dict]:
        """
        Test different weighting schemes for a skill.

        Args:
            evidence: Evidence from all sources
            ground_truth: True scores
            skill: Skill to optimize

        Returns:
            Dict mapping scheme name to results
        """
        schemes = {
            "equal": {"transcript": 1 / 3, "game": 1 / 3, "teacher": 1 / 3},
            "transcript_heavy": {"transcript": 0.60, "game": 0.25, "teacher": 0.15},
            "game_heavy": {"transcript": 0.20, "game": 0.60, "teacher": 0.20},
            "teacher_heavy": {"transcript": 0.25, "game": 0.25, "teacher": 0.50},
            "optimized_empathy": {"transcript": 0.50, "game": 0.25, "teacher": 0.25},
            "optimized_collaboration": {
                "transcript": 0.25,
                "game": 0.50,
                "teacher": 0.25,
            },
            "optimized_problem_solving": {
                "transcript": 0.30,
                "game": 0.45,
                "teacher": 0.25,
            },
            "optimized_self_regulation": {
                "transcript": 0.30,
                "game": 0.30,
                "teacher": 0.40,
            },
            "optimized_resilience": {"transcript": 0.25, "game": 0.50, "teacher": 0.25},
            "optimized_adaptability": {
                "transcript": 0.20,
                "game": 0.55,
                "teacher": 0.25,
            },
            "optimized_communication": {
                "transcript": 0.60,
                "game": 0.15,
                "teacher": 0.25,
            },
        }

        results = {}

        for scheme_name, weights in schemes.items():
            # Fuse evidence with this scheme
            fused_scores = self.fuse_scores(evidence, weights, skill)

            # Evaluate
            metrics = self.evaluate_weights(fused_scores, ground_truth, skill)
            metrics["weights"] = weights

            results[scheme_name] = metrics

        return results

    def find_optimal_weights(
        self,
        evidence: Dict[str, Dict[int, Dict[str, float]]],
        ground_truth: Dict[int, Dict[str, float]],
        skill: str,
        n_trials: int = 100,
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Find optimal weights through grid search.

        Args:
            evidence: Evidence from all sources
            ground_truth: True scores
            skill: Skill to optimize
            n_trials: Number of random trials

        Returns:
            (best_weights, best_metrics)
        """
        best_weights = None
        best_correlation = -1.0
        best_metrics = None

        for _ in range(n_trials):
            # Generate random weights that sum to 1.0
            weights_array = np.random.dirichlet([1, 1, 1])
            weights = {
                "transcript": float(weights_array[0]),
                "game": float(weights_array[1]),
                "teacher": float(weights_array[2]),
            }

            # Fuse and evaluate
            fused_scores = self.fuse_scores(evidence, weights, skill)
            metrics = self.evaluate_weights(fused_scores, ground_truth, skill)

            # Check if better
            if metrics["correlation"] > best_correlation:
                best_correlation = metrics["correlation"]
                best_weights = weights
                best_metrics = metrics

        return best_weights, best_metrics


def main():
    parser = argparse.ArgumentParser(description="Test fusion weight schemes")
    parser.add_argument(
        "--n-students", type=int, default=300, help="Number of synthetic students"
    )
    parser.add_argument(
        "--noise-level", type=float, default=0.1, help="Evidence noise level (0-1)"
    )
    parser.add_argument(
        "--output", type=str, default="fusion_weight_results.json", help="Output file"
    )
    parser.add_argument(
        "--optimize", action="store_true", help="Run optimization search"
    )
    parser.add_argument(
        "--n-trials", type=int, default=100, help="Number of optimization trials"
    )

    args = parser.parse_args()

    print("Testing Fusion Weight Schemes")
    print("=" * 60)
    print(f"Students: {args.n_students}")
    print(f"Noise Level: {args.noise_level}")
    print()

    # Generate synthetic data
    print("Generating synthetic evidence...")
    generator = SyntheticEvidenceGenerator()
    ground_truth = generator.generate_ground_truth(args.n_students)

    evidence = {
        "transcript": generator.generate_evidence(
            ground_truth, "transcript", args.noise_level
        ),
        "game": generator.generate_evidence(ground_truth, "game", args.noise_level),
        "teacher": generator.generate_evidence(
            ground_truth, "teacher", args.noise_level
        ),
    }

    print(f"Generated evidence for {args.n_students} students")
    print()

    # Test weighting schemes for each skill
    optimizer = FusionWeightOptimizer(generator.skills)
    all_results = {}

    for skill in generator.skills:
        print(f"Testing fusion weights for: {skill}")
        print("-" * 60)

        # Test predefined schemes
        scheme_results = optimizer.test_weighting_schemes(evidence, ground_truth, skill)

        # Find best scheme
        best_scheme = max(scheme_results.items(), key=lambda x: x[1]["correlation"])
        print(f"  Best Scheme: {best_scheme[0]}")
        print(f"  Correlation: {best_scheme[1]['correlation']:.3f}")
        print(f"  MAE: {best_scheme[1]['mae']:.3f}")
        print(f"  Weights: {best_scheme[1]['weights']}")

        # Optional: Run optimization
        if args.optimize:
            print(f"  Running optimization ({args.n_trials} trials)...")
            opt_weights, opt_metrics = optimizer.find_optimal_weights(
                evidence, ground_truth, skill, args.n_trials
            )
            print(f"  Optimized Correlation: {opt_metrics['correlation']:.3f}")
            print(f"  Optimized Weights: {opt_weights}")

            scheme_results["optimized_search"] = {
                **opt_metrics,
                "weights": opt_weights,
            }

        all_results[skill] = scheme_results
        print()

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()

    # Summary
    print("Summary - Best Weights per Skill")
    print("=" * 60)

    for skill, results in all_results.items():
        best = max(results.items(), key=lambda x: x[1]["correlation"])
        weights = best[1]["weights"]

        print(
            f"{skill.capitalize():20} | "
            f"Transcript: {weights['transcript']:.2f} | "
            f"Game: {weights['game']:.2f} | "
            f"Teacher: {weights['teacher']:.2f} | "
            f"r={best[1]['correlation']:.3f}"
        )

    print()
    print("Fusion weight testing complete!")


if __name__ == "__main__":
    main()
