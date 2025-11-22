"""Quick script to seed sample students into the database."""

import asyncio
import sys
from pathlib import Path
from datetime import date, datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.student import Student
from app.models.school import School
from app.models.base import Base


async def seed_students():
    """Seed sample students into the database."""

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # First, check if we have a school, if not create one
        from sqlalchemy import select
        result = await session.execute(select(School))
        school = result.scalar_one_or_none()

        if not school:
            print("Creating sample school...")
            school = School(
                id=str(uuid4()),
                name="Sample Middle School",
                district="Sample District",
                city="San Francisco",
                state="CA",
                is_active=True
            )
            session.add(school)
            await session.commit()
            print(f"✓ Created school: {school.name}")
        else:
            print(f"✓ Using existing school: {school.name}")

        # Sample student data - 50 students
        first_names = [
            "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
            "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
            "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Michael",
            "Emily", "Daniel", "Elizabeth", "Matthew", "Sofia", "Jackson", "Avery",
            "Sebastian", "Ella", "David", "Scarlett", "Joseph", "Grace", "Samuel",
            "Chloe", "John", "Victoria", "Owen", "Riley", "Dylan", "Aria", "Luke",
            "Lily", "Gabriel", "Aubrey", "Anthony", "Zoey", "Isaac"
        ]

        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
            "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
            "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
            "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
            "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
            "Carter", "Roberts"
        ]

        genders = ["Male", "Female"]
        ethnicities = ["White", "Hispanic", "Asian", "Black", "Mixed", "Other"]
        grades = [6, 7, 8]  # Middle school

        students_data = []
        for i in range(50):
            students_data.append({
                "first_name": first_names[i],
                "last_name": last_names[i],
                "grade_level": grades[i % 3],
                "gender": genders[i % 2],
                "ethnicity": ethnicities[i % 6]
            })

        print(f"\nCreating {len(students_data)} sample students...")

        for i, student_data in enumerate(students_data, 1):
            student = Student(
                id=str(uuid4()),
                first_name=student_data["first_name"],
                last_name=student_data["last_name"],
                email=f"{student_data['first_name'].lower()}.{student_data['last_name'].lower()}@school.edu",
                date_of_birth=date(2010, 1, 1),  # Simplified for now
                grade_level=student_data["grade_level"],
                student_id_external=f"STU{i:05d}",
                gender=student_data["gender"],
                ethnicity=student_data["ethnicity"],
                is_active=True,
                school_id=school.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(student)
            print(f"  ✓ {i:2d}. {student.first_name} {student.last_name} (Grade {student.grade_level})")

        await session.commit()

        # Verify count
        result = await session.execute(select(Student))
        count = len(result.scalars().all())

        print(f"\n✅ Successfully created {count} students in the database!")
        print(f"📝 School: {school.name}")
        print(f"🔗 Test API: curl http://localhost:8080/api/v1/students")

    await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("Seeding Sample Students")
    print("=" * 60)
    asyncio.run(seed_students())
