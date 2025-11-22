"""
Add missing skills (adaptability, communication, collaboration) to all existing students.

This uses the AI assessment service to generate assessments with reasoning
for the 3 skills that are missing from the current 4-skill setup.

Usage:
    python scripts/add_missing_skills.py
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.models.student import Student
from app.models.assessment import SkillType
from app.services.ai_assessment import SkillAssessmentService


MISSING_SKILLS = [
    SkillType.ADAPTABILITY,
    SkillType.COMMUNICATION,
    SkillType.COLLABORATION,
]


async def add_missing_skills():
    """Add missing skill assessments for all students."""
    print("=" * 70)
    print("Adding Missing Skills (Adaptability, Communication, Collaboration)")
    print("=" * 70)

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Initialize assessment service
    assessment_service = SkillAssessmentService()

    async with async_session() as session:
        # Get all students
        result = await session.execute(select(Student))
        students = result.scalars().all()

        print(f"\n📊 Found {len(students)} students")
        print(f"🎯 Will add {len(MISSING_SKILLS)} skills per student")
        print(f"📝 Total assessments to generate: {len(students) * len(MISSING_SKILLS)}\n")

        total_created = 0
        failed = 0

        for i, student in enumerate(students, 1):
            print(f"[{i}/{len(students)}] Processing {student.first_name} {student.last_name} ({student.id[:8]}...)")

            for skill in MISSING_SKILLS:
                try:
                    # Generate assessment with AI reasoning
                    assessment = await assessment_service.assess_skill(
                        session,
                        student.id,
                        skill,
                        use_cached=False  # Always generate fresh
                    )

                    print(f"  ✅ {skill.value}: {assessment.score:.2f} (confidence: {assessment.confidence:.2f})")
                    total_created += 1

                except Exception as e:
                    print(f"  ❌ {skill.value}: Failed - {e}")
                    failed += 1
                    continue

            # Commit after each student
            await session.commit()

        print("\n" + "=" * 70)
        print("✅ Skill Addition Complete!")
        print("=" * 70)
        print(f"📊 Summary:")
        print(f"   • Students processed: {len(students)}")
        print(f"   • Assessments created: {total_created}")
        print(f"   • Failed: {failed}")
        print(f"   • Success rate: {(total_created/(total_created+failed)*100):.1f}%")
        print(f"\n🔍 Verify: SELECT COUNT(*), skill_type FROM skill_assessments GROUP BY skill_type;")

    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(add_missing_skills())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
