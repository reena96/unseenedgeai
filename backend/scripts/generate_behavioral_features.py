"""
Generate synthetic behavioral features based on skill levels.

This script simulates realistic game telemetry behavioral patterns
for students based on their skill proficiency levels.

Features generated:
- Task completion rate
- Time efficiency
- Retry count
- Recovery rate
- Distraction resistance
- Focus duration
- Collaboration indicators
- Leadership indicators
- Event count

Usage:
    python scripts/generate_behavioral_features.py --input data/responses_with_linguistic.csv --output data/full_features.csv
"""

import argparse
import sys
from pathlib import Path
from typing import Dict
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class BehavioralFeatureGenerator:
    """Generate synthetic behavioral features based on skill levels."""

    def __init__(self, seed: int = 42):
        """
        Initialize generator.

        Args:
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        self.rng = np.random.default_rng(seed)

    def generate_features(
        self, skill_level: str, grade: int, skill_type: str = None
    ) -> Dict[str, float]:
        """
        Generate behavioral features for a student.

        Args:
            skill_level: Proficiency level (high, medium, developing)
            grade: Grade level (2-8)
            skill_type: Specific skill being assessed (optional)

        Returns:
            Dictionary of 9 behavioral features
        """
        # Base parameters by skill level
        if skill_level == "high":
            completion_mean, completion_std = 0.85, 0.05
            efficiency_mean, efficiency_std = 0.78, 0.08
            retry_lambda = 2.0
            recovery_mean, recovery_std = 0.82, 0.06
            distraction_mean, distraction_std = 0.80, 0.07
            focus_mean, focus_std = 12.0, 2.0
            collab_mean, collab_std = 0.75, 0.10
            leadership_mean, leadership_std = 0.65, 0.12
            event_lambda = 15.0

        elif skill_level == "medium":
            completion_mean, completion_std = 0.70, 0.08
            efficiency_mean, efficiency_std = 0.60, 0.10
            retry_lambda = 4.0
            recovery_mean, recovery_std = 0.65, 0.10
            distraction_mean, distraction_std = 0.60, 0.12
            focus_mean, focus_std = 8.0, 2.5
            collab_mean, collab_std = 0.60, 0.12
            leadership_mean, leadership_std = 0.45, 0.15
            event_lambda = 12.0

        else:  # developing
            completion_mean, completion_std = 0.50, 0.12
            efficiency_mean, efficiency_std = 0.45, 0.12
            retry_lambda = 6.0
            recovery_mean, recovery_std = 0.48, 0.12
            distraction_mean, distraction_std = 0.45, 0.15
            focus_mean, focus_std = 5.0, 2.0
            collab_mean, collab_std = 0.50, 0.15
            leadership_mean, leadership_std = 0.30, 0.15
            event_lambda = 8.0

        # Adjust for grade level (older students generally have more developed skills)
        grade_factor = (grade - 2) / 6  # Normalize to 0-1 for grades 2-8

        # Generate features with realistic distributions
        features = {
            # Task completion: higher for older students and higher skill levels
            'task_completion_rate': self._clip(
                self.rng.normal(completion_mean + grade_factor * 0.05, completion_std),
                0.2, 1.0
            ),

            # Time efficiency: how quickly they complete tasks
            'time_efficiency': self._clip(
                self.rng.normal(efficiency_mean + grade_factor * 0.08, efficiency_std),
                0.2, 1.0
            ),

            # Retry count: Poisson distribution (discrete)
            'retry_count': max(0, int(self.rng.poisson(retry_lambda))),

            # Recovery rate: bounce back from failures
            'recovery_rate': self._clip(
                self.rng.normal(recovery_mean + grade_factor * 0.06, recovery_std),
                0.2, 1.0
            ),

            # Distraction resistance: focus maintenance
            'distraction_resistance': self._clip(
                self.rng.normal(distraction_mean + grade_factor * 0.10, distraction_std),
                0.2, 1.0
            ),

            # Focus duration: minutes of sustained attention
            'focus_duration': max(1.0,
                self.rng.normal(focus_mean + grade_factor * 2.0, focus_std)
            ),

            # Collaboration indicators: teamwork signals
            'collaboration_indicators': self._clip(
                self.rng.normal(collab_mean, collab_std),
                0.0, 1.0
            ),

            # Leadership indicators: taking initiative
            'leadership_indicators': self._clip(
                self.rng.normal(leadership_mean + grade_factor * 0.08, leadership_std),
                0.0, 1.0
            ),

            # Event count: total interaction events in game session
            'event_count': max(1, int(self.rng.poisson(event_lambda + grade_factor * 3))),
        }

        # Add skill-specific adjustments
        if skill_type:
            features = self._adjust_for_skill_type(features, skill_type, skill_level)

        return features

    def _adjust_for_skill_type(
        self, features: Dict[str, float], skill_type: str, skill_level: str
    ) -> Dict[str, float]:
        """
        Apply skill-specific adjustments to behavioral features.

        Args:
            features: Base behavioral features
            skill_type: Skill being assessed
            skill_level: Proficiency level

        Returns:
            Adjusted features
        """
        adjustment_factor = 1.0 if skill_level == "high" else 0.9 if skill_level == "medium" else 0.8

        if skill_type == "empathy":
            # Empathy correlates with collaboration
            features['collaboration_indicators'] *= (1.0 + (adjustment_factor - 0.9) * 0.2)

        elif skill_type == "problem_solving":
            # Problem-solving correlates with efficiency and lower retry count
            features['time_efficiency'] *= (1.0 + (adjustment_factor - 0.9) * 0.15)
            features['retry_count'] = int(features['retry_count'] * (1.1 - adjustment_factor * 0.3))

        elif skill_type == "self_regulation":
            # Self-regulation correlates with focus and distraction resistance
            features['focus_duration'] *= (1.0 + (adjustment_factor - 0.9) * 0.25)
            features['distraction_resistance'] *= (1.0 + (adjustment_factor - 0.9) * 0.20)

        elif skill_type == "resilience":
            # Resilience correlates with recovery rate and completion despite retries
            features['recovery_rate'] *= (1.0 + (adjustment_factor - 0.9) * 0.25)
            features['task_completion_rate'] *= (1.0 + (adjustment_factor - 0.9) * 0.10)

        # Clip all values to valid ranges
        for key in features:
            if key not in ['retry_count', 'event_count', 'focus_duration']:
                features[key] = self._clip(features[key], 0.0, 1.0)

        return features

    def _clip(self, value: float, min_val: float, max_val: float) -> float:
        """Clip value to range."""
        return max(min_val, min(max_val, value))

    def generate_derived_feature(
        self, skill_type: str, behavioral_features: Dict[str, float], linguistic_features: Dict[str, float]
    ) -> float:
        """
        Generate skill-specific derived feature.

        Combines behavioral and linguistic features for each skill.

        Args:
            skill_type: Skill being assessed
            behavioral_features: Behavioral feature dict
            linguistic_features: Linguistic feature dict

        Returns:
            Derived feature value (0.0-1.0)
        """
        if skill_type == "empathy":
            # Empathy = social language × collaboration
            return self._clip(
                (linguistic_features.get('social_processes', 0.0) * 0.6 +
                 behavioral_features.get('collaboration_indicators', 0.0) * 0.4),
                0.0, 1.0
            )

        elif skill_type == "problem_solving":
            # Problem-solving = cognitive processes × efficiency
            return self._clip(
                (linguistic_features.get('cognitive_processes', 0.0) * 0.5 +
                 behavioral_features.get('time_efficiency', 0.0) * 0.3 +
                 (1.0 - min(1.0, behavioral_features.get('retry_count', 5) / 10.0)) * 0.2),
                0.0, 1.0
            )

        elif skill_type == "self_regulation":
            # Self-regulation = focus × distraction resistance
            return self._clip(
                (behavioral_features.get('distraction_resistance', 0.0) * 0.5 +
                 min(1.0, behavioral_features.get('focus_duration', 0.0) / 15.0) * 0.5),
                0.0, 1.0
            )

        elif skill_type == "resilience":
            # Resilience = recovery × perseverance language
            return self._clip(
                (behavioral_features.get('recovery_rate', 0.0) * 0.6 +
                 linguistic_features.get('perseverance_indicators', 0.0) * 0.4),
                0.0, 1.0
            )

        return 0.5  # Default

    def process_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate behavioral features for entire dataset.

        Args:
            df: DataFrame with skill_level, grade, and skill columns

        Returns:
            DataFrame with added behavioral features
        """
        print(f"🎮 Generating behavioral features for {len(df)} samples...")

        behavioral_features_list = []
        derived_features_dict = {
            'empathy_social_interaction': [],
            'problem_solving_cognitive': [],
            'self_regulation_focus': [],
            'resilience_recovery': [],
        }

        for idx, row in df.iterrows():
            if idx % 100 == 0 and idx > 0:
                print(f"   Processed {idx}/{len(df)} samples...")

            skill_level = row.get('skill_level', 'medium')
            grade = row.get('grade', 5)
            skill = row.get('skill', 'empathy')

            # Generate behavioral features
            behavioral = self.generate_features(skill_level, grade, skill)
            behavioral_features_list.append(behavioral)

            # Generate derived features for all skills
            # Extract linguistic features from current row
            ling_features = {
                'social_processes': row.get('social_processes', 0.0),
                'cognitive_processes': row.get('cognitive_processes', 0.0),
                'perseverance_indicators': row.get('perseverance_indicators', 0.0),
            }

            for skill_type in ['empathy', 'problem_solving', 'self_regulation', 'resilience']:
                derived_col_name = {
                    'empathy': 'empathy_social_interaction',
                    'problem_solving': 'problem_solving_cognitive',
                    'self_regulation': 'self_regulation_focus',
                    'resilience': 'resilience_recovery',
                }[skill_type]

                derived_value = self.generate_derived_feature(
                    skill_type, behavioral, ling_features
                )
                derived_features_dict[derived_col_name].append(derived_value)

        # Convert to DataFrames
        behavioral_df = pd.DataFrame(behavioral_features_list)
        derived_df = pd.DataFrame(derived_features_dict)

        # Combine with original DataFrame
        result = pd.concat([
            df.reset_index(drop=True),
            behavioral_df,
            derived_df
        ], axis=1)

        print(f"✅ Generated {len(behavioral_df.columns)} behavioral features")
        print(f"✅ Generated {len(derived_df.columns)} derived features")

        # Show statistics
        print(f"\n📊 Behavioral Feature Statistics:")
        print(behavioral_df.describe().round(3))

        return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate behavioral features for synthetic data"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input CSV file with linguistic features",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output CSV file with all features",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )

    args = parser.parse_args()

    # Load data
    print(f"📂 Loading data from {args.input}...")
    df = pd.read_csv(args.input)
    print(f"   Loaded {len(df)} samples with {len(df.columns)} columns")

    # Generate behavioral features
    generator = BehavioralFeatureGenerator(seed=args.seed)
    result_df = generator.process_dataset(df)

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_path, index=False)

    print(f"\n💾 Saved to {output_path}")
    print(f"   Total columns: {len(result_df.columns)}")
    print(f"   Total features: {len(result_df.columns) - len(df.columns)} new columns added")


if __name__ == "__main__":
    main()
