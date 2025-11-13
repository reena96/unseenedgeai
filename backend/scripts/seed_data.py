"""
Seed database with test data for development and testing.

This script creates sample students, teachers, schools, and related data
to enable testing of the API without manual data entry.

Usage:
    python scripts/seed_data.py
    python scripts/seed_data.py --clear  # Clear existing data first
"""

import asyncio
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.models.assessment import SkillAssessment, SkillType  # noqa: E402
from app.models.audio import AudioFile  # noqa: E402
from app.models.game_telemetry import GameSession, GameTelemetry  # noqa: E402
from app.models.school import School  # noqa: E402
from app.models.student import Student  # noqa: E402
from app.models.teacher import Teacher  # noqa: E402
from app.models.transcript import Transcript  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402


async def clear_data(session: AsyncSession):
    """Clear all existing test data."""
    print("🗑️  Clearing existing data...")

    # Delete in reverse order of dependencies
    await session.execute(text("DELETE FROM evidence"))
    await session.execute(text("DELETE FROM rubric_assessments"))
    await session.execute(text("DELETE FROM skill_assessments"))
    await session.execute(text("DELETE FROM linguistic_features"))
    await session.execute(text("DELETE FROM behavioral_features"))
    await session.execute(text("DELETE FROM game_telemetry"))
    await session.execute(text("DELETE FROM game_sessions"))
    await session.execute(text("DELETE FROM transcripts"))
    await session.execute(text("DELETE FROM audio_files"))
    await session.execute(text("DELETE FROM students"))
    await session.execute(text("DELETE FROM teachers"))
    await session.execute(text("DELETE FROM users"))
    await session.execute(text("DELETE FROM schools"))

    await session.commit()
    print("✅ Existing data cleared")


async def seed_schools(session: AsyncSession) -> list[School]:
    """Create sample schools."""
    print("\n🏫 Creating schools...")

    schools = [
        School(
            id=str(uuid.uuid4()),
            name="Springfield Elementary",
            district="Springfield School District",
            city="Springfield",
            state="IL",
            zip_code="62701",
        ),
        School(
            id=str(uuid.uuid4()),
            name="Lincoln Middle School",
            district="Lincoln County Schools",
            city="Lincoln",
            state="CA",
            zip_code="95648",
        ),
        School(
            id=str(uuid.uuid4()),
            name="Washington High School",
            district="Washington District",
            city="New York",
            state="NY",
            zip_code="10001",
        ),
    ]

    session.add_all(schools)
    await session.commit()

    for school in schools:
        await session.refresh(school)

    print(f"✅ Created {len(schools)} schools")
    return schools


async def seed_teachers(session: AsyncSession, schools: list[School]) -> list[Teacher]:
    """Create sample teachers and their user accounts."""
    print("\n👨‍🏫 Creating teachers...")

    teachers_data = [
        {
            "email": "john.smith@springfield.edu",
            "first_name": "John",
            "last_name": "Smith",
            "school": schools[0],
            "department": "Reading",
        },
        {
            "email": "sarah.johnson@springfield.edu",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "school": schools[0],
            "department": "Math",
        },
        {
            "email": "michael.brown@lincoln.edu",
            "first_name": "Michael",
            "last_name": "Brown",
            "school": schools[1],
            "department": "English",
        },
        {
            "email": "emily.davis@washington.edu",
            "first_name": "Emily",
            "last_name": "Davis",
            "school": schools[2],
            "department": "Language Arts",
        },
    ]

    teachers = []
    for data in teachers_data:
        # Create user account
        user = User(
            id=str(uuid.uuid4()),
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            role=UserRole.TEACHER,
            school_id=data["school"].id,
            password_hash="$2b$12$test_hashed_password_for_seeding",  # Not for production!
        )
        session.add(user)
        await session.flush()  # Get the user ID

        # Create teacher profile
        teacher = Teacher(
            id=str(uuid.uuid4()),
            user_id=user.id,
            school_id=data["school"].id,
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            department=data["department"],
        )
        session.add(teacher)
        teachers.append(teacher)

    await session.commit()

    for teacher in teachers:
        await session.refresh(teacher)

    print(f"✅ Created {len(teachers)} teachers")
    return teachers


async def seed_students(
    session: AsyncSession, schools: list[School], teachers: list[Teacher]
) -> list[Student]:
    """Create sample students."""
    print("\n👨‍🎓 Creating students...")

    students_data = [
        {
            "first_name": "Emma",
            "last_name": "Wilson",
            "grade": 3,
            "teacher": teachers[0],
        },
        {
            "first_name": "Liam",
            "last_name": "Anderson",
            "grade": 3,
            "teacher": teachers[0],
        },
        {
            "first_name": "Olivia",
            "last_name": "Martinez",
            "grade": 4,
            "teacher": teachers[1],
        },
        {
            "first_name": "Noah",
            "last_name": "Garcia",
            "grade": 4,
            "teacher": teachers[1],
        },
        {
            "first_name": "Ava",
            "last_name": "Rodriguez",
            "grade": 5,
            "teacher": teachers[1],
        },
        {
            "first_name": "Ethan",
            "last_name": "Hernandez",
            "grade": 6,
            "teacher": teachers[2],
        },
        {
            "first_name": "Sophia",
            "last_name": "Lopez",
            "grade": 6,
            "teacher": teachers[2],
        },
        {
            "first_name": "Mason",
            "last_name": "Gonzalez",
            "grade": 7,
            "teacher": teachers[2],
        },
        {
            "first_name": "Isabella",
            "last_name": "Perez",
            "grade": 8,
            "teacher": teachers[3],
        },
        {
            "first_name": "Lucas",
            "last_name": "Taylor",
            "grade": 8,
            "teacher": teachers[3],
        },
    ]

    students = []
    for i, data in enumerate(students_data, 1):
        # Assign school based on teacher
        school = schools[teachers.index(data["teacher"]) // 2]

        student = Student(
            id=str(uuid.uuid4()),
            first_name=data["first_name"],
            last_name=data["last_name"],
            grade_level=data["grade"],
            school_id=school.id,
            student_id_external=f"STU{i:05d}",
        )
        session.add(student)
        students.append(student)

    await session.commit()

    for student in students:
        await session.refresh(student)

    print(f"✅ Created {len(students)} students")
    return students


async def seed_audio_files(
    session: AsyncSession, students: list[Student]
) -> list[AudioFile]:
    """Create sample audio files and transcripts."""
    print("\n🎤 Creating audio files and transcripts...")

    sample_texts = [
        (
            "I really enjoyed helping my friend understand the math problem. "
            "It felt good to explain it in a way that made sense to them."
        ),
        (
            "When I couldn't solve the puzzle at first, I tried a different "
            "approach and finally figured it out."
        ),
        (
            "Today in class we worked together as a team to build a project. "
            "Everyone contributed their ideas."
        ),
        (
            "I was frustrated when my drawing didn't turn out right, but I took "
            "a break and tried again with a new strategy."
        ),
        (
            "My favorite book is about space exploration. I love learning about "
            "planets and astronauts."
        ),
    ]

    audio_files = []
    transcripts = []

    # Create 2 audio files per student
    for student in students[:5]:  # First 5 students only for demo
        for i in range(2):
            audio_file = AudioFile(
                id=str(uuid.uuid4()),
                student_id=student.id,
                storage_path=f"gs://mass-audio-dev/{student.id}/audio_{uuid.uuid4()}.wav",
                duration_seconds=15.5 + i * 5,
                file_size_bytes=248000 + i * 80000,
                source_type="classroom",
                recording_date=(datetime.utcnow() - timedelta(days=i * 2)).strftime(
                    "%Y-%m-%d"
                ),
                transcription_status="completed",
            )
            session.add(audio_file)
            audio_files.append(audio_file)

            # Add transcript for first audio file
            if i == 0:
                await session.flush()  # Get audio_file.id

                transcript_text = sample_texts[len(transcripts) % len(sample_texts)]
                transcript = Transcript(
                    id=str(uuid.uuid4()),
                    audio_file_id=audio_file.id,
                    student_id=student.id,
                    text=transcript_text,
                    word_count=len(transcript_text.split()),
                    confidence_score=0.92 + (i * 0.03),
                    language_code="en-US",
                )
                session.add(transcript)
                transcripts.append(transcript)

    await session.commit()

    for audio_file in audio_files:
        await session.refresh(audio_file)

    print(
        f"✅ Created {len(audio_files)} audio files and {len(transcripts)} transcripts"
    )
    return audio_files


async def seed_game_sessions(
    session: AsyncSession, students: list[Student]
) -> list[GameSession]:
    """Create sample game sessions and telemetry."""
    print("\n🎮 Creating game sessions and telemetry...")

    game_sessions = []
    telemetry_events = []

    # Create game sessions for first 3 students
    for student in students[:3]:
        for session_num in range(2):
            start_time = datetime.utcnow() - timedelta(days=session_num * 3)
            end_time = start_time + timedelta(hours=1)

            game_session = GameSession(
                id=str(uuid.uuid4()),
                student_id=student.id,
                started_at=start_time,
                ended_at=end_time,
                mission_id=f"mission_{session_num + 1}",
                game_version="1.0.0",
            )
            session.add(game_session)
            game_sessions.append(game_session)

            await session.flush()  # Get session ID

            # Add telemetry events
            for event_num in range(5):
                telemetry = GameTelemetry(
                    id=str(uuid.uuid4()),
                    timestamp=start_time + timedelta(minutes=event_num * 12),
                    student_id=student.id,
                    session_id=game_session.id,
                    event_type="word_attempt",
                    event_data={
                        "word": ["cat", "dog", "sun", "moon", "star"][event_num],
                        "correct": event_num % 2 == 0,
                        "time_taken_ms": 2000 + event_num * 500,
                    },
                    mission_id=f"mission_{session_num + 1}",
                )
                session.add(telemetry)
                telemetry_events.append(telemetry)

    await session.commit()

    print(
        f"✅ Created {len(game_sessions)} game sessions and {len(telemetry_events)} telemetry events"
    )
    return game_sessions


async def seed_assessments(session: AsyncSession, students: list[Student]):
    """Create sample skill assessments."""
    print("\n📊 Creating skill assessments...")

    skills = [
        SkillType.EMPATHY,
        SkillType.PROBLEM_SOLVING,
        SkillType.SELF_REGULATION,
        SkillType.RESILIENCE,
    ]

    assessments = []
    for student in students[:3]:
        for skill in skills:
            assessment = SkillAssessment(
                id=str(uuid.uuid4()),
                student_id=student.id,
                skill_type=skill,
                score=0.65 + (hash(student.id + skill.value) % 30) / 100,
                confidence=0.75 + (hash(skill.value) % 20) / 100,
                reasoning=(
                    f"Student demonstrates {skill.value} through consistent "
                    "positive behaviors and responses."
                ),
                recommendations=(
                    f"Continue to develop {skill.value} through targeted " "activities."
                ),
            )
            session.add(assessment)
            assessments.append(assessment)

    await session.commit()

    print(f"✅ Created {len(assessments)} skill assessments")


async def main():
    """Main seeding function."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed database with test data")
    parser.add_argument(
        "--clear", action="store_true", help="Clear existing data first"
    )
    args = parser.parse_args()

    print("🌱 Starting database seeding...")
    db_location = (
        settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "local"
    )
    print(f"📍 Database: {db_location}")

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # Clear existing data if requested
            if args.clear:
                await clear_data(session)

            # Seed data in order
            schools = await seed_schools(session)
            teachers = await seed_teachers(session, schools)
            students = await seed_students(session, schools, teachers)
            audio_files = await seed_audio_files(session, students)
            game_sessions = await seed_game_sessions(session, students)
            await seed_assessments(session, students)

            print("\n" + "=" * 50)
            print("✅ Database seeding completed successfully!")
            print("=" * 50)
            print("\n📊 Summary:")
            print(f"   • {len(schools)} schools")
            print(f"   • {len(teachers)} teachers")
            print(f"   • {len(students)} students")
            print(f"   • {len(audio_files)} audio files")
            print(f"   • {len(game_sessions)} game sessions")
            print("\n🔐 Test Login Credentials:")
            print("   Email: john.smith@springfield.edu")
            print("   Password: (use test password from your auth system)")
            print("\n🚀 Next steps:")
            print("   • Start the API: uvicorn app.main:app --reload")
            print("   • Test endpoints at http://localhost:8000/api/v1/docs")

        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
