"""
Seed historical assessments to create time-series data for trend analysis.

This creates 4-6 historical assessments per student per skill, spread across
the last 3 months, showing realistic score progression.

Usage:
    python scripts/seed_historical_assessments.py
    python scripts/seed_historical_assessments.py --points 8  # More historical points
"""

import asyncio
import argparse
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.models.student import Student
from app.models.assessment import SkillAssessment, SkillType, Evidence, EvidenceType


# All 7 skills
ALL_SKILLS = [
    SkillType.EMPATHY,
    SkillType.ADAPTABILITY,
    SkillType.PROBLEM_SOLVING,
    SkillType.SELF_REGULATION,
    SkillType.RESILIENCE,
    SkillType.COMMUNICATION,
    SkillType.COLLABORATION,
]


def generate_progression(start_score: float, num_points: int) -> list[float]:
    """
    Generate realistic score progression showing growth over time.

    Args:
        start_score: Initial score (typically 0.5-0.8)
        num_points: Number of historical points to generate

    Returns:
        List of scores showing realistic progression
    """
    scores = []
    current = start_score

    for i in range(num_points):
        # Slight upward trend with some variation
        growth = random.uniform(0.01, 0.05)  # 1-5% growth per period
        variation = random.uniform(-0.03, 0.03)  # Random variation

        current = current + growth + variation
        # Keep within valid range
        current = max(0.3, min(0.95, current))
        scores.append(round(current, 2))

    return scores


def get_reasoning_for_score(skill: SkillType, score: float) -> str:
    """Generate contextual reasoning based on score level."""
    skill_name = skill.value.replace('_', ' ').title()

    if score >= 0.8:
        templates = [
            f"Student demonstrates exceptional {skill_name.lower()} with consistent high performance across multiple contexts.",
            f"Strong mastery of {skill_name.lower()} evident through advanced application and understanding.",
            f"Outstanding {skill_name.lower()} skills with ability to mentor and support peers effectively.",
        ]
    elif score >= 0.65:
        templates = [
            f"Solid {skill_name.lower()} development with good progress in key areas.",
            f"Demonstrates competent {skill_name.lower()} with room for continued growth.",
            f"Effective {skill_name.lower()} application in most situations with occasional challenges.",
        ]
    elif score >= 0.5:
        templates = [
            f"Developing {skill_name.lower()} with visible improvement over time.",
            f"Shows emerging {skill_name.lower()} capabilities with consistent effort.",
            f"Making progress in {skill_name.lower()} development with guidance and support.",
        ]
    else:
        templates = [
            f"Early stages of {skill_name.lower()} development requiring focused support.",
            f"Foundational {skill_name.lower()} skills emerging with significant growth potential.",
            f"Working to build {skill_name.lower()} competencies through targeted practice.",
        ]

    return random.choice(templates)


def get_recommendations(skill: SkillType) -> str:
    """Get generic recommendations for a skill."""
    recommendations_map = {
        SkillType.EMPATHY: "Continue practicing perspective-taking and emotional awareness through reflective activities.",
        SkillType.ADAPTABILITY: "Engage with varied challenges and practice flexible thinking strategies.",
        SkillType.PROBLEM_SOLVING: "Apply systematic problem-solving approaches to increasingly complex scenarios.",
        SkillType.SELF_REGULATION: "Practice mindfulness techniques and develop personalized coping strategies.",
        SkillType.RESILIENCE: "Build growth mindset through celebrating effort and learning from setbacks.",
        SkillType.COMMUNICATION: "Practice clear expression across different contexts and audiences.",
        SkillType.COLLABORATION: "Participate in diverse team experiences with varied roles and responsibilities.",
    }
    return recommendations_map.get(skill, "Continue developing this important skill through practice and reflection.")


async def create_historical_assessments(num_points: int = 6):
    """Create historical assessments for all students."""
    print("=" * 70)
    print(f"Seeding Historical Assessments ({num_points} points per skill)")
    print("=" * 70)

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get all students
        result = await session.execute(select(Student))
        students = result.scalars().all()

        print(f"\n📊 Found {len(students)} students")
        print(f"📅 Creating {num_points} historical assessments per skill")
        print(f"🎯 {len(ALL_SKILLS)} skills per student")
        print(f"📝 Total assessments to create: {len(students) * len(ALL_SKILLS) * num_points}\n")

        total_created = 0
        days_between = 90 // (num_points + 1)  # Spread across 3 months

        for student_idx, student in enumerate(students, 1):
            print(f"[{student_idx}/{len(students)}] {student.first_name} {student.last_name}")

            for skill in ALL_SKILLS:
                # Generate progression for this skill
                start_score = random.uniform(0.5, 0.7)
                scores = generate_progression(start_score, num_points)

                # Create historical assessments going backwards in time
                for point_idx, score in enumerate(reversed(scores)):
                    days_ago = days_between * (num_points - point_idx)
                    assessment_date = datetime.utcnow() - timedelta(days=days_ago)

                    confidence = random.uniform(0.75, 0.92)
                    reasoning = get_reasoning_for_score(skill, score)
                    recommendations = get_recommendations(skill)

                    assessment = SkillAssessment(
                        id=str(uuid4()),
                        student_id=student.id,
                        skill_type=skill,
                        score=score,
                        confidence=confidence,
                        reasoning=reasoning,
                        recommendations=recommendations,
                        created_at=assessment_date,
                        updated_at=assessment_date,
                    )
                    session.add(assessment)

                    # Add 2-3 evidence items per assessment
                    for ev_idx in range(random.randint(2, 3)):
                        evidence = Evidence(
                            id=str(uuid4()),
                            assessment_id=assessment.id,
                            evidence_type=random.choice([EvidenceType.LINGUISTIC, EvidenceType.BEHAVIORAL]),
                            source=f"Historical Session {days_ago}d ago",
                            content=f"Demonstrated {skill.value.replace('_', ' ')} at {score*100:.0f}% level",
                            relevance_score=round(random.uniform(0.70, 0.90), 2),
                        )
                        session.add(evidence)

                    total_created += 1

                # Progress indicator
                skill_progress = f"  {skill.value}: {scores[0]:.2f} → {scores[-1]:.2f}"
                print(f"    {skill_progress}")

            # Commit after each student to avoid large transactions
            await session.commit()

        print("\n" + "=" * 70)
        print("✅ Historical Assessment Seeding Complete!")
        print("=" * 70)
        print(f"📊 Summary:")
        print(f"   • Students: {len(students)}")
        print(f"   • Skills: {len(ALL_SKILLS)}")
        print(f"   • Points per skill: {num_points}")
        print(f"   • Total assessments: {total_created}")
        print(f"   • Time span: {days_between * num_points} days ({num_points * days_between / 30:.1f} months)")
        print(f"\n🔍 Verify with:")
        print(f"   SELECT skill_type, COUNT(*), MIN(created_at), MAX(created_at)")
        print(f"   FROM skill_assessments GROUP BY skill_type;")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed historical skill assessments")
    parser.add_argument(
        "--points",
        type=int,
        default=6,
        help="Number of historical points per skill (default: 6)"
    )

    args = parser.parse_args()

    try:
        asyncio.run(create_historical_assessments(args.points))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
