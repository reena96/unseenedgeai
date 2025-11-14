"""
Generate synthetic student responses using GPT-4.

This script uses GPT-4 to generate realistic student speech patterns
across different grade levels, skill types, and proficiency levels.

Usage:
    python scripts/generate_synthetic_responses.py --count 100 --output data/synthetic_responses.csv
    python scripts/generate_synthetic_responses.py --count 1000 --use-openai  # Full dataset
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict
import pandas as pd
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

# Import existing realistic responses as examples
from realistic_student_responses import (
    EMPATHY_RESPONSES,
    PROBLEM_SOLVING_RESPONSES,
    SELF_REGULATION_RESPONSES,
    RESILIENCE_RESPONSES,
)


class SyntheticResponseGenerator:
    """Generate synthetic student responses using GPT-4 or template expansion."""

    def __init__(self, use_openai: bool = False):
        """
        Initialize generator.

        Args:
            use_openai: If True, use OpenAI API. If False, use template expansion.
        """
        self.use_openai = use_openai
        if use_openai:
            try:
                from openai import OpenAI

                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                print(
                    "⚠️  OpenAI library not installed. Install with: pip install openai"
                )
                self.use_openai = False

        # Skill configurations
        self.skills = {
            "empathy": EMPATHY_RESPONSES,
            "problem_solving": PROBLEM_SOLVING_RESPONSES,
            "self_regulation": SELF_REGULATION_RESPONSES,
            "resilience": RESILIENCE_RESPONSES,
        }

        self.skill_levels = ["high", "medium", "developing"]
        self.grades = [2, 3, 4, 5, 6, 7, 8]

    def get_example_responses(
        self, skill: str, level: str, count: int = 3
    ) -> List[str]:
        """Get example responses for a skill and level."""
        responses = self.skills.get(skill, {}).get(level, [])
        if not responses:
            return []
        return random.sample(responses, min(count, len(responses)))

    async def generate_with_openai(
        self, skill: str, level: str, grade: int, count: int = 10
    ) -> List[Dict[str, str]]:
        """
        Generate responses using GPT-4.

        Args:
            skill: Skill type (empathy, problem_solving, etc.)
            level: Proficiency level (high, medium, developing)
            grade: Grade level (2-8)
            count: Number of responses to generate

        Returns:
            List of response dictionaries
        """
        if not self.use_openai:
            raise ValueError("OpenAI not configured")

        # Get example responses
        examples = self.get_example_responses(skill, level, count=3)
        examples_text = "\n".join(f"{i+1}. {ex}" for i, ex in enumerate(examples))

        # Build prompt
        prompt = f"""You are helping create a dataset of realistic student speech patterns for educational assessment.

Generate {count} realistic student responses that demonstrate {level.upper()} level {skill.replace('_', ' ')} for a grade {grade} student.

EXAMPLES of {level} level {skill.replace('_', ' ')} from grade {grade-1} to {grade+1} students:
{examples_text}

REQUIREMENTS:
- Age-appropriate vocabulary for grade {grade}
- 15-50 words per response
- Natural, authentic student language (not overly formal)
- Varied scenarios (classroom, playground, group work, home, etc.)
- Each response should demonstrate {skill.replace('_', ' ')} at the {level} level
- Avoid repeating the same phrases or scenarios
- Include realistic speech patterns (incomplete sentences, filler words occasionally)

OUTPUT FORMAT:
Return ONLY a JSON array of strings, one response per element.
Example: ["response 1", "response 2", "response 3"]

Generate {count} responses now:"""

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o-mini",  # Cheaper model, good for synthetic data
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in child development and educational psychology, helping generate realistic student speech data.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.9,  # Higher temperature for variety
                max_tokens=2000,
            )

            # Parse JSON response
            content = response.choices[0].message.content.strip()

            # Try to extract JSON array
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            responses_list = json.loads(content)

            # Create response objects
            results = []
            for resp_text in responses_list[:count]:
                results.append(
                    {
                        "response": resp_text,
                        "skill": skill,
                        "skill_level": level,
                        "grade": grade,
                        "source": "gpt-4o-mini",
                    }
                )

            return results

        except Exception as e:
            print(f"⚠️  Error generating with OpenAI: {e}")
            return []

    def generate_with_templates(
        self, skill: str, level: str, grade: int, count: int = 10
    ) -> List[Dict[str, str]]:
        """
        Generate responses by expanding existing templates.

        This is a fallback method that doesn't require API calls.
        """
        examples = self.skills.get(skill, {}).get(level, [])
        if not examples:
            return []

        results = []
        for i in range(count):
            # Pick a random example and slightly modify it
            base_response = random.choice(examples)

            # Simple template expansion (could be enhanced with paraphrasing)
            response_text = base_response

            results.append(
                {
                    "response": response_text,
                    "skill": skill,
                    "skill_level": level,
                    "grade": grade,
                    "source": "template_expansion",
                }
            )

        return results

    async def generate_dataset(
        self, total_count: int, balanced: bool = True
    ) -> pd.DataFrame:
        """
        Generate a complete synthetic dataset.

        Args:
            total_count: Total number of responses to generate
            balanced: If True, balance across skills/levels/grades

        Returns:
            DataFrame with synthetic responses
        """
        print(f"🤖 Generating {total_count} synthetic student responses...")
        print(
            f"   Method: {'OpenAI GPT-4o-mini' if self.use_openai else 'Template Expansion'}"
        )

        all_responses = []

        if balanced:
            # Calculate samples per combination
            num_skills = len(self.skills)
            num_levels = len(self.skill_levels)
            num_grades = len(self.grades)

            samples_per_combo = max(
                1, total_count // (num_skills * num_levels * num_grades)
            )

            # Generate for each combination
            tasks = []
            for skill in self.skills.keys():
                for level in self.skill_levels:
                    for grade in self.grades:
                        if self.use_openai:
                            task = self.generate_with_openai(
                                skill, level, grade, count=samples_per_combo
                            )
                        else:
                            # Template expansion is synchronous, wrap it
                            task = asyncio.create_task(
                                asyncio.to_thread(
                                    self.generate_with_templates,
                                    skill,
                                    level,
                                    grade,
                                    samples_per_combo,
                                )
                            )
                        tasks.append(task)

            # Execute all tasks concurrently
            print(f"   Generating {len(tasks)} batches concurrently...")
            results = await asyncio.gather(*tasks)

            for batch in results:
                all_responses.extend(batch)

        else:
            # Random sampling
            for i in range(total_count):
                skill = random.choice(list(self.skills.keys()))
                level = random.choice(self.skill_levels)
                grade = random.choice(self.grades)

                if self.use_openai:
                    batch = await self.generate_with_openai(
                        skill, level, grade, count=1
                    )
                else:
                    batch = self.generate_with_templates(skill, level, grade, count=1)

                all_responses.extend(batch)

        # Convert to DataFrame
        df = pd.DataFrame(all_responses)

        print(f"✅ Generated {len(df)} synthetic responses")
        print(f"\n📊 Distribution:")
        print(f"   Skills: {df['skill'].value_counts().to_dict()}")
        print(f"   Levels: {df['skill_level'].value_counts().to_dict()}")
        print(f"   Grades: {df['grade'].value_counts().to_dict()}")

        return df


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate synthetic student responses")
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of responses to generate (default: 100)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/synthetic_responses.csv",
        help="Output CSV file path",
    )
    parser.add_argument(
        "--use-openai",
        action="store_true",
        help="Use OpenAI API (requires OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--balanced",
        action="store_true",
        default=True,
        help="Balance across skills/levels/grades",
    )

    args = parser.parse_args()

    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate dataset
    generator = SyntheticResponseGenerator(use_openai=args.use_openai)
    df = await generator.generate_dataset(args.count, balanced=args.balanced)

    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"\n💾 Saved to {output_path}")

    # Display sample
    print(f"\n📝 Sample responses:")
    for i, row in df.head(3).iterrows():
        print(
            f"\n{i+1}. [{row['skill']}] [{row['skill_level']}] [Grade {row['grade']}]"
        )
        print(f"   {row['response']}")


if __name__ == "__main__":
    asyncio.run(main())
