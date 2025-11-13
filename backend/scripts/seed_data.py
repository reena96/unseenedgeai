"""
Seed database with test data for development and testing.

This script creates sample students, teachers, schools, and audio files
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
from app.models.assessment import SkillAssessment  # noqa: E402
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
    await session.execute(text("DELETE FROM schools"))
    await session.execute(text("DELETE FROM users"))

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
            "subjects": ["Reading", "Writing"],
        },
        {
            "email": "sarah.johnson@springfield.edu",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "school": schools[0],
            "subjects": ["Math", "Science"],
        },
        {
            "email": "michael.brown@lincoln.edu",
            "first_name": "Michael",
            "last_name": "Brown",
            "school": schools[1],
            "subjects": ["English", "Literature"],
        },
        {
            "email": "emily.davis@washington.edu",
            "first_name": "Emily",
            "last_name": "Davis",
            "school": schools[2],
            "subjects": ["Reading", "Language Arts"],
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
            department=data["subjects"][0] if data["subjects"] else None,
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
            teacher_id=data["teacher"].id,
            student_external_id=f"STU{i:05d}",
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
        "The cat sat on the mat. It was a warm sunny day.",
        "I like to read books about dinosaurs and space.",
        "My favorite color is blue because it reminds me of the ocean.",
        "Yesterday I went to the park and played on the swings.",
        "I can count to one hundred. One, two, three, four, five...",
    ]

    audio_files = []
    transcripts = []

    # Create 2-3 audio files per student
    for student in students[:5]:  # First 5 students only for demo
        for i in range(2):
            audio_file = AudioFile(
                id=str(uuid.uuid4()),
                student_id=student.id,
                file_path=f"gs://mass-audio-dev/{student.id}/audio_{uuid.uuid4()}.wav",
                duration_seconds=15.5 + i * 5,
                sample_rate=16000,
                file_size_bytes=248000 + i * 80000,
                upload_timestamp=datetime.utcnow() - timedelta(days=i * 2),
            )
            session.add(audio_file)
            audio_files.append(audio_file)

            # Add transcript for some audio files
            if i == 0:
                await session.flush()  # Get audio_file.id

                transcript = Transcript(
                    id=str(uuid.uuid4()),
                    audio_file_id=audio_file.id,
                    text=sample_texts[len(transcripts) % len(sample_texts)],
                    confidence=0.92 + (i * 0.03),
                    word_count=len(
                        sample_texts[len(transcripts) % len(sample_texts)].split()
                    ),
                    processing_time_seconds=2.3 + i * 0.5,
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
            game_session = GameSession(
                id=str(uuid.uuid4()),
                student_id=student.id,
                game_type="word_builder",
                start_time=datetime.utcnow() - timedelta(days=session_num * 3),
                end_time=datetime.utcnow() - timedelta(days=session_num * 3, hours=-1),
                total_duration_seconds=3600,
                completion_status="completed",
            )
            session.add(game_session)
            game_sessions.append(game_session)

            await session.flush()  # Get session ID

            # Add telemetry events
            for event_num in range(5):
                telemetry = GameTelemetry(
                    id=str(uuid.uuid4()),
                    session_id=game_session.id,
                    event_type="word_attempt",
                    event_data={
                        "word": ["cat", "dog", "sun", "moon", "star"][event_num],
                        "correct": event_num % 2 == 0,
                        "time_taken_ms": 2000 + event_num * 500,
                    },
                    timestamp=game_session.start_time
                    + timedelta(minutes=event_num * 12),
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

    skills = ["phonemic_awareness", "word_recognition", "fluency", "comprehension"]

    assessments = []
    for student in students[:3]:
        for skill in skills:
            assessment = SkillAssessment(
                id=str(uuid.uuid4()),
                student_id=student.id,
                skill_name=skill,
                proficiency_level=2 + (hash(student.id) % 3),  # Level 2-4
                confidence_score=0.75 + (hash(skill) % 20) / 100,
                assessment_date=datetime.utcnow() - timedelta(days=7),
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
            print("   • Login with test credentials")
            print("   • Test endpoints at http://localhost:8000/api/v1/docs")

        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
