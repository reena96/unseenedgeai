"""
End-to-end synthetic training data generation pipeline.

This script orchestrates the entire pipeline:
1. Generate synthetic student responses (GPT-4 or templates)
2. Extract linguistic features (NLP)
3. Generate behavioral features (simulation)
4. Auto-label skill scores (GPT-4 or heuristics)
5. Create final training CSV

Usage:
    # Generate 100 samples with heuristic labeling (FREE, ~2 minutes)
    python scripts/generate_training_data.py --count 100 --output data/training_100.csv

    # Generate 1000 samples with GPT-4 (PAID, ~$10-15, ~30 minutes)
    python scripts/generate_training_data.py --count 1000 --output data/training_1000.csv --use-openai

    # Generate 100 samples with GPT-4 text but heuristic labels (PAID ~$2, ~5 minutes)
    python scripts/generate_training_data.py --count 100 --output data/training_100_gpt.csv --use-openai --no-auto-label
"""

import asyncio
import argparse
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our pipeline modules
from generate_synthetic_responses import SyntheticResponseGenerator
from extract_linguistic_features import LinguisticFeatureExtractor
from generate_behavioral_features import BehavioralFeatureGenerator
from auto_label_skills import SkillAutoLabeler


class TrainingDataPipeline:
    """End-to-end pipeline for synthetic training data generation."""

    def __init__(
        self,
        use_openai: bool = False,
        auto_label: bool = True,
        seed: int = 42,
    ):
        """
        Initialize pipeline.

        Args:
            use_openai: Use OpenAI for text generation and labeling
            auto_label: Use auto-labeling (OpenAI or heuristics)
            seed: Random seed
        """
        self.use_openai = use_openai
        self.auto_label = auto_label
        self.seed = seed

        print("🚀 Initializing Training Data Pipeline")
        print(
            f"   Text Generation: {'OpenAI GPT-4o-mini' if use_openai else 'Template Expansion'}"
        )
        print(
            f"   Auto-Labeling: {'OpenAI GPT-4o-mini' if (use_openai and auto_label) else 'Heuristic Rules' if auto_label else 'Disabled'}"
        )

    async def run(self, count: int, output_path: str) -> pd.DataFrame:
        """
        Run complete pipeline.

        Args:
            count: Number of samples to generate
            output_path: Path to save final CSV

        Returns:
            DataFrame with training data
        """
        start_time = datetime.now()
        print(f"\n{'='*60}")
        print(f"STARTING PIPELINE: Generating {count} training samples")
        print(f"{'='*60}\n")

        # Stage 1: Generate synthetic responses
        print("📝 STAGE 1: Generating Synthetic Responses")
        print("-" * 60)
        generator = SyntheticResponseGenerator(use_openai=self.use_openai)
        df = await generator.generate_dataset(count, balanced=True)
        print(f"✅ Stage 1 complete: {len(df)} responses generated\n")

        # Stage 2: Extract linguistic features
        print("🔍 STAGE 2: Extracting Linguistic Features")
        print("-" * 60)
        extractor = LinguisticFeatureExtractor()
        df = extractor.process_dataset(df, text_column="response")
        print(f"✅ Stage 2 complete: 16 linguistic features extracted\n")

        # Stage 3: Generate behavioral features
        print("🎮 STAGE 3: Generating Behavioral Features")
        print("-" * 60)
        behav_generator = BehavioralFeatureGenerator(seed=self.seed)
        df = behav_generator.process_dataset(df)
        print(f"✅ Stage 3 complete: 9 behavioral + 4 derived features generated\n")

        # Stage 4: Auto-label skill scores
        if self.auto_label:
            print("🏷️  STAGE 4: Auto-Labeling Skill Scores")
            print("-" * 60)
            labeler = SkillAutoLabeler(use_openai=self.use_openai, model="gpt-4o-mini")
            df = await labeler.label_dataset(df, batch_size=10)
            print(f"✅ Stage 4 complete: 4 skill scores labeled\n")
        else:
            print("⏭️  STAGE 4: Skipped (auto-labeling disabled)\n")
            # Add placeholder scores
            for skill in [
                "empathy",
                "problem_solving",
                "self_regulation",
                "resilience",
            ]:
                df[f"{skill}_score"] = 0.5

        # Save results
        print("💾 STAGE 5: Saving Training Data")
        print("-" * 60)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output, index=False)
        print(f"✅ Saved to: {output}")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {len(df.columns)}\n")

        # Pipeline summary
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n{'='*60}")
        print(f"PIPELINE COMPLETE")
        print(f"{'='*60}")
        print(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"📊 Generated: {len(df)} training samples")
        print(f"📁 Output: {output}")

        # Cost estimate
        if self.use_openai:
            # Rough estimate: ~$0.01 per 100 responses + ~$0.01 per 100 labels
            est_cost = (count / 100) * 0.02
            print(f"💰 Estimated API cost: ${est_cost:.2f}")

        print(f"\n✅ Ready to train models:")
        print(f"   python app/ml/train_models.py --data {output} --models-dir models/")

        return df


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic training data for skill assessment models"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of training samples to generate (default: 100)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/training_data.csv",
        help="Output CSV file path (default: data/training_data.csv)",
    )
    parser.add_argument(
        "--use-openai",
        action="store_true",
        help="Use OpenAI API for text generation and labeling (requires OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--no-auto-label",
        action="store_true",
        help="Skip auto-labeling stage (scores will be 0.5)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    args = parser.parse_args()

    # Create pipeline
    pipeline = TrainingDataPipeline(
        use_openai=args.use_openai,
        auto_label=not args.no_auto_label,
        seed=args.seed,
    )

    # Run pipeline
    df = await pipeline.run(args.count, args.output)

    # Show sample data
    print(f"\n📋 Sample Training Data (first 3 rows):")
    print("=" * 80)
    sample_cols = [
        "response",
        "skill",
        "skill_level",
        "grade",
        "empathy_score",
        "problem_solving_score",
        "empathy_markers",
        "task_completion_rate",
    ]
    available_cols = [col for col in sample_cols if col in df.columns]
    print(df[available_cols].head(3).to_string())

    print(f"\n📊 Feature Summary:")
    print("=" * 80)
    print(f"   Linguistic features: 16")
    print(f"   Behavioral features: 9")
    print(f"   Derived features: 4")
    print(f"   Target labels: 4")
    print(f"   Total columns: {len(df.columns)}")

    # Validation
    print(f"\n🔍 Data Validation:")
    print("=" * 80)

    # Check for required columns
    required_features = [
        "empathy_markers",
        "problem_solving_language",
        "perseverance_indicators",
        "task_completion_rate",
        "time_efficiency",
    ]
    required_targets = [
        "empathy_score",
        "problem_solving_score",
        "self_regulation_score",
        "resilience_score",
    ]

    missing_features = [f for f in required_features if f not in df.columns]
    missing_targets = [t for t in required_targets if t not in df.columns]

    if missing_features:
        print(f"   ⚠️  Missing features: {missing_features}")
    else:
        print(f"   ✅ All required features present")

    if missing_targets:
        print(f"   ⚠️  Missing target labels: {missing_targets}")
    else:
        print(f"   ✅ All target labels present")

    # Check for NaN values
    nan_count = df.isna().sum().sum()
    if nan_count > 0:
        print(f"   ⚠️  Found {nan_count} NaN values")
        print(f"      Columns with NaN: {df.columns[df.isna().any()].tolist()}")
    else:
        print(f"   ✅ No missing values")

    # Check score ranges
    if not args.no_auto_label:
        for skill in ["empathy", "problem_solving", "self_regulation", "resilience"]:
            col = f"{skill}_score"
            if col in df.columns:
                min_score = df[col].min()
                max_score = df[col].max()
                mean_score = df[col].mean()

                if min_score < 0 or max_score > 1:
                    print(
                        f"   ⚠️  {col}: scores out of range [0,1] ({min_score:.3f}-{max_score:.3f})"
                    )
                else:
                    print(
                        f"   ✅ {col}: {min_score:.3f}-{max_score:.3f} (mean: {mean_score:.3f})"
                    )

    print(f"\n{'='*80}")
    print("🎉 Pipeline execution complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())
