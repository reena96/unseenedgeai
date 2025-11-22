"""
Seed sample data into the database for testing dashboards.

This script creates:
- 50 diverse students across grades 6-12
- Multiple assessments per student showing progression
- Realistic skill scores with variation
- Evidence transcripts for each assessment
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.database import Base, Student, Assessment


# Sample student data with diversity
FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
    "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
    "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Michael",
    "Emily", "Daniel", "Elizabeth", "Matthew", "Sofia", "Jackson", "Avery",
    "Sebastian", "Ella", "David", "Scarlett", "Joseph", "Grace", "Samuel",
    "Chloe", "John", "Victoria", "Owen", "Riley", "Dylan", "Aria", "Luke",
    "Lily", "Gabriel", "Aubrey", "Anthony", "Zoey", "Isaac"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts"
]

CLASSES = [
    "Math 6A", "Math 6B", "Math 7A", "Math 7B", "Math 8A", "Math 8B",
    "English 6A", "English 6B", "English 7A", "English 7B", "English 8A",
    "Science 6A", "Science 6B", "Science 7A", "Science 7B", "Science 8A",
    "History 6A", "History 7A", "History 8A",
    "Algebra I", "Geometry", "Biology", "Chemistry", "World History",
    "US History", "English 9", "English 10", "English 11", "Physics"
]

# All 7 skills
SKILLS = [
    "empathy",
    "adaptability",
    "problem_solving",
    "self_regulation",
    "resilience",
    "communication",
    "collaboration"
]

# Sample evidence transcripts for different skill levels
EVIDENCE_TEMPLATES = {
    "empathy": [
        "Student showed understanding when classmate was upset about test results. Offered support and encouragement.",
        "Demonstrated active listening during group discussion. Asked thoughtful questions about peers' perspectives.",
        "Helped new student feel welcome. Introduced them to other classmates and explained school routines.",
        "Showed concern when partner struggled with assignment. Offered to work together and share strategies.",
    ],
    "adaptability": [
        "Quickly adjusted approach when initial strategy didn't work. Tried two alternative methods.",
        "Remained calm when class schedule changed unexpectedly. Adapted to new timeline smoothly.",
        "Modified group role when teammate was absent. Took on additional responsibilities without complaint.",
        "Flexible when technology failed. Shifted to paper-based approach and completed work efficiently.",
    ],
    "problem_solving": [
        "Broke down complex math problem into smaller steps. Identified key information systematically.",
        "Generated three possible solutions to design challenge. Evaluated pros and cons of each.",
        "Used trial and error effectively in science lab. Documented what worked and what didn't.",
        "Asked clarifying questions before starting assignment. Identified potential obstacles early.",
    ],
    "self_regulation": [
        "Took deep breath when frustrated with difficult problem. Returned with fresh perspective after break.",
        "Managed time well during test. Moved on from hard questions and returned to them later.",
        "Stayed focused during independent work time despite distractions. Completed assignment on schedule.",
        "Recognized own stress level and asked for help appropriately. Used coping strategies discussed in class.",
    ],
    "resilience": [
        "Persisted through challenging assignment even after initial setback. Didn't give up.",
        "Bounced back from disappointing quiz grade. Created study plan for improvement.",
        "Maintained positive attitude when project didn't work as expected. Tried again with modifications.",
        "Recovered quickly after making mistake during presentation. Continued with confidence.",
    ],
    "communication": [
        "Explained reasoning clearly during class discussion. Used specific examples to support ideas.",
        "Listened actively to group members' input. Paraphrased to confirm understanding.",
        "Asked thoughtful questions that helped group think more deeply about topic.",
        "Presented ideas in organized way. Made sure everyone understood main points.",
    ],
    "collaboration": [
        "Worked cooperatively with diverse team members. Valued different perspectives and approaches.",
        "Shared leadership responsibilities in group project. Made sure everyone had role to play.",
        "Helped resolve conflict between teammates. Found compromise that worked for everyone.",
        "Built on others' ideas during brainstorming. Contributed constructively to group effort.",
    ]
}


def generate_skill_score(base_level: str, variation: float = 0.15) -> float:
    """Generate a realistic skill score with some variation."""
    base_scores = {
        "emerging": 0.45,
        "developing": 0.60,
        "proficient": 0.75,
        "advanced": 0.90
    }

    base = base_scores.get(base_level, 0.60)
    # Add some random variation
    score = base + random.uniform(-variation, variation)
    # Clamp between 0.2 and 1.0
    return max(0.2, min(1.0, score))


def generate_progression_scores(initial_level: str, num_assessments: int) -> list:
    """Generate scores that show realistic progression over time."""
    scores = []
    current = generate_skill_score(initial_level)

    for _ in range(num_assessments):
        scores.append(current)
        # Small chance of improvement, small chance of decline, mostly stable
        change = random.choices(
            [0.05, 0.0, -0.03],
            weights=[0.3, 0.5, 0.2]
        )[0]
        current = max(0.2, min(1.0, current + change))

    return scores


def generate_evidence(skill: str, score: float) -> str:
    """Generate evidence text based on skill and score level."""
    templates = EVIDENCE_TEMPLATES.get(skill, ["Demonstrated skill during class activity."])

    # Choose template based on score
    if score >= 0.8:
        intensity = "Strong evidence: "
    elif score >= 0.6:
        intensity = "Good evidence: "
    else:
        intensity = "Some evidence: "

    return intensity + random.choice(templates)


async def seed_database():
    """Seed the database with sample data."""

    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=True
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    print("🌱 Seeding database with sample data...")

    async with async_session() as session:
        # Create 50 students
        students = []
        for i in range(50):
            # Random student attributes
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            grade = random.randint(6, 12)
            class_name = random.choice([c for c in CLASSES if str(grade) in c or grade >= 9])

            student = Student(
                student_id=f"STU{1000 + i:04d}",
                name=f"{first_name} {last_name}",
                grade=grade,
                class_name=class_name,
                demographics={
                    "age": grade + 6,
                    "first_name": first_name,
                    "last_name": last_name
                }
            )
            students.append(student)
            session.add(student)

        await session.commit()
        print(f"✅ Created {len(students)} students")

        # Create assessments for each student
        total_assessments = 0
        start_date = datetime.now() - timedelta(days=120)

        for student in students:
            # Each student gets 3-8 assessments over the past 4 months
            num_assessments = random.randint(3, 8)

            # Determine student's general skill level
            student_level = random.choice(["emerging", "developing", "proficient", "advanced"])

            # Generate progression for all skills
            skill_progressions = {
                skill: generate_progression_scores(student_level, num_assessments)
                for skill in SKILLS
            }

            # Create assessments spread over time
            for assessment_idx in range(num_assessments):
                days_offset = (120 / num_assessments) * assessment_idx
                assessment_date = start_date + timedelta(days=days_offset)

                # Get scores for this assessment
                skill_scores = {
                    skill: skill_progressions[skill][assessment_idx]
                    for skill in SKILLS
                }

                # Generate evidence for each skill
                evidence = {}
                for skill in SKILLS:
                    evidence[skill] = {
                        "transcript": generate_evidence(skill, skill_scores[skill]),
                        "context": f"Observed during {random.choice(['group work', 'class discussion', 'project work', 'peer interaction', 'independent work'])}",
                        "confidence": round(random.uniform(0.7, 0.95), 2)
                    }

                assessment = Assessment(
                    student_id=student.student_id,
                    assessment_date=assessment_date,
                    skill_scores=skill_scores,
                    evidence=evidence,
                    overall_score=sum(skill_scores.values()) / len(skill_scores),
                    metadata={
                        "assessment_type": random.choice(["observation", "project", "discussion", "collaboration"]),
                        "duration_minutes": random.randint(20, 45),
                        "observer": random.choice(["Ms. Johnson", "Mr. Smith", "Dr. Williams", "Ms. Davis"])
                    }
                )
                session.add(assessment)
                total_assessments += 1

        await session.commit()
        print(f"✅ Created {total_assessments} assessments")

        # Print summary statistics
        print("\n📊 Database seeded successfully!")
        print(f"   • {len(students)} students (grades 6-12)")
        print(f"   • {total_assessments} total assessments")
        print(f"   • Average {total_assessments / len(students):.1f} assessments per student")
        print(f"   • All 7 skills tracked: {', '.join(SKILLS)}")
        print(f"   • Date range: {start_date.date()} to {datetime.now().date()}")

    await engine.dispose()


if __name__ == "__main__":
    print("🚀 Starting database seed script...")
    asyncio.run(seed_database())
    print("\n✨ Done! You can now view the data in the dashboards.")
    print("\nDashboards:")
    print("  • Teacher Dashboard: http://localhost:8501")
    print("  • Admin Dashboard: http://localhost:8502")
    print("  • Student Portal: http://localhost:8503")
