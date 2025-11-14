"""
Auto-label skill scores using GPT-4.

This script uses GPT-4 to generate expert-level skill scores (0.0-1.0)
for student responses, eliminating the need for manual labeling.

Usage:
    python scripts/auto_label_skills.py --input data/full_features.csv --output data/training_data.csv --use-openai
    python scripts/auto_label_skills.py --input data/full_features.csv --output data/training_data.csv  # Use heuristics
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd
import numpy as np
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


class SkillAutoLabeler:
    """Auto-label skill scores using GPT-4 or heuristics."""

    def __init__(self, use_openai: bool = False, model: str = "gpt-4o-mini"):
        """
        Initialize labeler.

        Args:
            use_openai: If True, use OpenAI API. If False, use heuristic labeling.
            model: OpenAI model to use
        """
        self.use_openai = use_openai
        self.model = model

        if use_openai:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                print("⚠️  OpenAI library not installed. Using heuristic labeling instead.")
                self.use_openai = False

        self.skills = ['empathy', 'problem_solving', 'self_regulation', 'resilience']

    async def label_with_openai(
        self, response: str, skill: str, skill_level: str, grade: int
    ) -> float:
        """
        Use GPT-4 to label skill score.

        Args:
            response: Student text response
            skill: Skill type
            skill_level: Original skill level tag (for validation)
            grade: Grade level

        Returns:
            Skill score (0.0-1.0)
        """
        if not self.use_openai:
            raise ValueError("OpenAI not configured")

        skill_descriptions = {
            'empathy': 'understanding and sharing the feelings of others, showing care and compassion',
            'problem_solving': 'approaching challenges systematically, trying different strategies, and finding solutions',
            'self_regulation': 'managing emotions, maintaining focus, and controlling impulses appropriately',
            'resilience': 'persisting through difficulties, learning from setbacks, and bouncing back from failures',
        }

        level_guidelines = """
Scoring Guidelines:
- 0.0-0.3: Minimal or no evidence of the skill
- 0.3-0.5: Developing - basic awareness, needs significant support
- 0.5-0.7: Proficient - clear demonstration, age-appropriate
- 0.7-0.85: Advanced - strong, consistent demonstration
- 0.85-1.0: Exceptional - sophisticated, beyond grade level

Consider:
- Age-appropriateness for grade {grade}
- Depth and authenticity of demonstration
- Consistency with skill definition
"""

        prompt = f"""You are an expert educational psychologist specializing in social-emotional learning assessment.

Rate this Grade {grade} student's response for **{skill.replace('_', ' ').title()}** skill.

**Skill Definition:** {skill_descriptions[skill]}

**Student Response:**
"{response}"

{level_guidelines}

**Instructions:**
1. Analyze the response for evidence of {skill.replace('_', ' ')}
2. Consider age-appropriateness for Grade {grade}
3. Return ONLY a number between 0.0 and 1.0 (e.g., 0.75)
4. Be consistent: similar responses should get similar scores

Your score (number only):"""

        try:
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational psychologist. Return only numeric scores between 0.0 and 1.0.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower for consistency
                max_tokens=10,
            )

            # Extract score
            score_text = completion.choices[0].message.content.strip()

            # Try to parse as float
            try:
                score = float(score_text)
            except ValueError:
                # Try to extract number from text
                import re
                numbers = re.findall(r'0\.\d+|1\.0|0|1', score_text)
                if numbers:
                    score = float(numbers[0])
                else:
                    print(f"⚠️  Could not parse score from: {score_text}, using 0.5")
                    score = 0.5

            # Clip to valid range
            score = max(0.0, min(1.0, score))

            return score

        except Exception as e:
            print(f"⚠️  Error labeling with OpenAI: {e}")
            # Fallback to heuristic
            return self.label_with_heuristics(response, skill, skill_level, grade)

    def label_with_heuristics(
        self, response: str, skill: str, skill_level: str, grade: int
    ) -> float:
        """
        Use heuristic rules to estimate skill score.

        This is a fallback when OpenAI is not available. It maps skill_level
        tags to score ranges with some variance.

        Args:
            response: Student text response
            skill: Skill type
            skill_level: Skill level tag (high, medium, developing)
            grade: Grade level

        Returns:
            Estimated skill score (0.0-1.0)
        """
        # Base score ranges by level
        score_ranges = {
            'high': (0.70, 0.90),
            'medium': (0.50, 0.70),
            'developing': (0.30, 0.55),
        }

        base_min, base_max = score_ranges.get(skill_level, (0.40, 0.60))

        # Adjust for grade (older students tend to score slightly higher)
        grade_adjustment = (grade - 5) * 0.02  # +/- 0.06 for grades 2-8

        # Add some randomness for realistic variance
        score = np.random.uniform(base_min, base_max) + grade_adjustment

        # Slight adjustments based on response characteristics
        word_count = len(response.split())

        # Longer, more detailed responses tend to score higher
        if word_count > 40:
            score += 0.03
        elif word_count < 15:
            score -= 0.03

        # Clip to valid range
        score = max(0.1, min(0.98, score))

        return round(score, 3)

    async def label_dataset(
        self, df: pd.DataFrame, batch_size: int = 10
    ) -> pd.DataFrame:
        """
        Label entire dataset with skill scores.

        Args:
            df: DataFrame with responses and features
            batch_size: Number of concurrent API calls (if using OpenAI)

        Returns:
            DataFrame with added score columns
        """
        print(f"🏷️  Auto-labeling skill scores for {len(df)} samples...")
        print(f"   Method: {'OpenAI ' + self.model if self.use_openai else 'Heuristic Rules'}")

        # Initialize score columns
        score_columns = {
            'empathy_score': [],
            'problem_solving_score': [],
            'self_regulation_score': [],
            'resilience_score': [],
        }

        # Process in batches
        for idx, row in df.iterrows():
            if idx % 50 == 0 and idx > 0:
                print(f"   Labeled {idx}/{len(df)} samples...")

            response = row.get('response', '')
            skill = row.get('skill', 'empathy')
            skill_level = row.get('skill_level', 'medium')
            grade = row.get('grade', 5)

            # Label all 4 skills for this response
            # The primary skill gets labeled based on the response
            # Other skills get lower baseline scores
            for skill_type in self.skills:
                score_col = f"{skill_type}_score"

                if skill_type == skill:
                    # This is the primary skill - label it properly
                    if self.use_openai:
                        score = await self.label_with_openai(
                            response, skill_type, skill_level, grade
                        )
                    else:
                        score = self.label_with_heuristics(
                            response, skill_type, skill_level, grade
                        )
                else:
                    # Secondary skills - assign baseline scores with variance
                    # These should be lower and more neutral
                    if skill_level == 'high':
                        score = np.random.uniform(0.50, 0.65)
                    elif skill_level == 'medium':
                        score = np.random.uniform(0.40, 0.55)
                    else:
                        score = np.random.uniform(0.30, 0.50)

                score_columns[score_col].append(round(score, 3))

            # Add small delay for API rate limiting
            if self.use_openai and idx % batch_size == 0:
                await asyncio.sleep(0.5)

        # Add score columns to dataframe
        for col, values in score_columns.items():
            df[col] = values

        print(f"✅ Labeled all 4 skill scores for {len(df)} samples")

        # Show score statistics
        print(f"\n📊 Score Statistics:")
        score_stats = df[[
            'empathy_score',
            'problem_solving_score',
            'self_regulation_score',
            'resilience_score'
        ]].describe()
        print(score_stats.round(3))

        # Show score distribution by skill level
        print(f"\n📊 Score Distribution by Skill Level:")
        for level in ['high', 'medium', 'developing']:
            level_df = df[df['skill_level'] == level]
            if len(level_df) > 0:
                avg_scores = {
                    skill: level_df[f"{skill}_score"].mean()
                    for skill in self.skills
                }
                print(f"   {level.upper()}: {avg_scores}")

        return df


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Auto-label skill scores for training data"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input CSV file with features",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output CSV file with labeled scores",
    )
    parser.add_argument(
        "--use-openai",
        action="store_true",
        help="Use OpenAI API for labeling (requires OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for concurrent API calls (default: 10)",
    )

    args = parser.parse_args()

    # Load data
    print(f"📂 Loading data from {args.input}...")
    df = pd.read_csv(args.input)
    print(f"   Loaded {len(df)} samples with {len(df.columns)} columns")

    # Label scores
    labeler = SkillAutoLabeler(use_openai=args.use_openai, model=args.model)
    labeled_df = await labeler.label_dataset(df, batch_size=args.batch_size)

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    labeled_df.to_csv(output_path, index=False)

    print(f"\n💾 Saved to {output_path}")
    print(f"   Total columns: {len(labeled_df.columns)}")
    print(f"\n✅ Training data ready for model training!")

    # Show expected columns for training
    expected_features = [
        'empathy_markers', 'problem_solving_language', 'perseverance_indicators',
        'social_processes', 'cognitive_processes', 'positive_sentiment', 'negative_sentiment',
        'avg_sentence_length', 'syntactic_complexity', 'word_count', 'unique_word_count',
        'readability_score', 'noun_count', 'verb_count', 'adj_count', 'adv_count',
        'task_completion_rate', 'time_efficiency', 'retry_count', 'recovery_rate',
        'distraction_resistance', 'focus_duration', 'collaboration_indicators',
        'leadership_indicators', 'event_count',
        'empathy_social_interaction', 'problem_solving_cognitive',
        'self_regulation_focus', 'resilience_recovery'
    ]

    expected_targets = [
        'empathy_score', 'problem_solving_score',
        'self_regulation_score', 'resilience_score'
    ]

    missing_features = [f for f in expected_features if f not in labeled_df.columns]
    missing_targets = [t for t in expected_targets if t not in labeled_df.columns]

    if missing_features:
        print(f"\n⚠️  Missing features: {missing_features}")
    if missing_targets:
        print(f"\n⚠️  Missing target columns: {missing_targets}")

    if not missing_features and not missing_targets:
        print(f"\n✅ All required columns present! Ready to train models with:")
        print(f"   python app/ml/train_models.py --data {output_path} --models-dir models/")


if __name__ == "__main__":
    asyncio.run(main())
