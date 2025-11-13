"""
Enhanced seed database script with realistic student data.

This version uses LLM-generated responses and patterns from real educational
datasets to create more realistic and diverse student data for testing.

Usage:
    python scripts/seed_data_enhanced.py
    python scripts/seed_data_enhanced.py --clear  # Clear existing data first
"""

import asyncio
import random
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

# Import realistic responses
from realistic_student_responses import (  # noqa: E402
    EMPATHY_RESPONSES,
    PROBLEM_SOLVING_RESPONSES,
    SELF_REGULATION_RESPONSES,
    RESILIENCE_RESPONSES,
    MIXED_SKILL_RESPONSES,
)


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
            name="Washington Elementary",
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
            password_hash="$2b$12$test_hashed_password_for_seeding",
        )
        session.add(user)
        await session.flush()

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
    """Create sample students with diverse profiles."""
    print("\n👨‍🎓 Creating students...")

    students_data = [
        # Grade 2-3 students
        {
            "first_name": "Emma",
            "last_name": "Wilson",
            "grade": 2,
            "teacher": teachers[0],
        },
        {
            "first_name": "Liam",
            "last_name": "Anderson",
            "grade": 3,
            "teacher": teachers[0],
        },
        {
            "first_name": "Sophia",
            "last_name": "Martinez",
            "grade": 3,
            "teacher": teachers[0],
        },
        # Grade 4-5 students
        {
            "first_name": "Noah",
            "last_name": "Garcia",
            "grade": 4,
            "teacher": teachers[1],
        },
        {
            "first_name": "Olivia",
            "last_name": "Rodriguez",
            "grade": 4,
            "teacher": teachers[1],
        },
        {"first_name": "Ava", "last_name": "Lopez", "grade": 5, "teacher": teachers[1]},
        {
            "first_name": "Mia",
            "last_name": "Hernandez",
            "grade": 5,
            "teacher": teachers[1],
        },
        # Grade 6-8 students
        {
            "first_name": "Ethan",
            "last_name": "Gonzalez",
            "grade": 6,
            "teacher": teachers[2],
        },
        {
            "first_name": "Isabella",
            "last_name": "Perez",
            "grade": 7,
            "teacher": teachers[2],
        },
        {
            "first_name": "Lucas",
            "last_name": "Taylor",
            "grade": 8,
            "teacher": teachers[3],
        },
        {
            "first_name": "Amelia",
            "last_name": "Brown",
            "grade": 8,
            "teacher": teachers[3],
        },
        {
            "first_name": "Mason",
            "last_name": "Davis",
            "grade": 7,
            "teacher": teachers[3],
        },
    ]

    students = []
    for i, data in enumerate(students_data, 1):
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


async def seed_audio_files_enhanced(
    session: AsyncSession, students: list[Student]
) -> list[AudioFile]:
    """Create realistic audio files and transcripts with diverse student responses."""
    print("\n🎤 Creating audio files and transcripts with realistic data...")

    # Combine all response types
    all_responses = []
    for skill_dict in [
        EMPATHY_RESPONSES,
        PROBLEM_SOLVING_RESPONSES,
        SELF_REGULATION_RESPONSES,
        RESILIENCE_RESPONSES,
    ]:
        for level in ["high", "medium", "developing"]:
            all_responses.extend(skill_dict[level])

    all_responses.extend(MIXED_SKILL_RESPONSES)

    # Shuffle for variety
    random.shuffle(all_responses)

    audio_files = []
    transcripts = []

    # Create 2-3 audio files per student
    for student_idx, student in enumerate(students):
        num_files = 2 if student_idx % 2 == 0 else 3

        for i in range(num_files):
            # Pick response appropriate for grade level
            if student.grade_level <= 3:
                # Filter for simpler responses (shorter, grade 2-3 tagged)
                suitable_responses = [
                    r
                    for r in all_responses
                    if len(r.split()) < 30 and "[Grade 6-8]" not in r
                ]
            elif student.grade_level <= 5:
                # Medium complexity
                suitable_responses = [
                    r
                    for r in all_responses
                    if "[Grade 2-3]" not in r and "[Grade 6-8]" not in r
                ]
            else:
                # All responses okay for older students
                suitable_responses = all_responses

            transcript_text = random.choice(suitable_responses)
            # Clean up grade tags if present
            transcript_text = transcript_text.replace("[Grade 2-3] ", "")
            transcript_text = transcript_text.replace("[Grade 4-5] ", "")
            transcript_text = transcript_text.replace("[Grade 6-8] ", "")

            # Calculate realistic duration based on word count (avg 2.5 words/second)
            word_count = len(transcript_text.split())
            duration = (word_count / 2.5) + random.uniform(-2, 3)
            duration = max(5, duration)  # Minimum 5 seconds

            # Realistic file size (roughly 16kB per second for 16kHz WAV)
            file_size = int(duration * 16000 * 1.2)  # 1.2x for compression variation

            audio_file = AudioFile(
                id=str(uuid.uuid4()),
                student_id=student.id,
                storage_path=f"gs://mass-audio-dev/{student.id}/audio_{uuid.uuid4()}.wav",
                duration_seconds=round(duration, 1),
                file_size_bytes=file_size,
                source_type=random.choice(
                    ["classroom", "one_on_one", "group_work", "presentation"]
                ),
                recording_date=(
                    datetime.utcnow() - timedelta(days=random.randint(1, 30))
                ).strftime("%Y-%m-%d"),
                transcription_status="completed",
            )
            session.add(audio_file)
            audio_files.append(audio_file)

            await session.flush()  # Get audio_file.id

            # Create transcript
            # Realistic confidence varies by clarity and audio quality
            confidence = random.uniform(0.88, 0.98)

            transcript = Transcript(
                id=str(uuid.uuid4()),
                audio_file_id=audio_file.id,
                student_id=student.id,
                text=transcript_text,
                word_count=word_count,
                confidence_score=round(confidence, 3),
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
    print(
        f"   📊 Average words per transcript: {sum(t.word_count for t in transcripts) / len(transcripts):.1f}"
    )
    return audio_files


async def seed_game_sessions_enhanced(
    session: AsyncSession, students: list[Student]
) -> list[GameSession]:
    """Create realistic game sessions with varied telemetry patterns."""
    print("\n🎮 Creating game sessions and telemetry with realistic patterns...")

    game_sessions = []
    telemetry_events = []

    # Realistic mission names from educational games
    missions = [
        "reading_comprehension_1",
        "math_problem_solving_2",
        "vocabulary_builder_3",
        "science_exploration_1",
        "critical_thinking_4",
    ]

    # Create 2-4 game sessions per student
    for student in students:
        num_sessions = random.randint(2, 4)

        for session_num in range(num_sessions):
            # Realistic session timing
            days_ago = random.randint(1, 45)
            start_time = datetime.utcnow() - timedelta(days=days_ago)

            # Session duration varies realistically (10-45 minutes)
            duration_minutes = random.randint(10, 45)
            end_time = start_time + timedelta(minutes=duration_minutes)

            game_session = GameSession(
                id=str(uuid.uuid4()),
                student_id=student.id,
                started_at=start_time,
                ended_at=end_time,
                mission_id=random.choice(missions),
                game_version="2.1.4",
            )
            session.add(game_session)
            game_sessions.append(game_session)

            await session.flush()  # Get session ID

            # Generate realistic telemetry events
            # Higher-grade students tend to have more events (more interactions)
            base_events = (
                8
                if student.grade_level <= 3
                else 12 if student.grade_level <= 5 else 15
            )
            num_events = random.randint(base_events, base_events + 10)

            # Distribute events across session duration
            for event_num in range(num_events):
                # Events spread across session with realistic clustering
                time_offset_minutes = (duration_minutes / num_events) * event_num
                time_offset_minutes += random.uniform(-2, 2)  # Add jitter
                time_offset_minutes = max(0, time_offset_minutes)

                event_time = start_time + timedelta(minutes=time_offset_minutes)

                # Varied event types reflecting real gameplay
                event_type = random.choice(
                    [
                        "question_attempt",
                        "hint_requested",
                        "correct_answer",
                        "incorrect_answer",
                        "level_complete",
                        "item_collected",
                        "navigation",
                    ]
                )

                # Realistic event data
                if event_type in [
                    "question_attempt",
                    "correct_answer",
                    "incorrect_answer",
                ]:
                    correct = event_type == "correct_answer" or (
                        event_type == "question_attempt" and random.random() > 0.3
                    )
                    event_data = {
                        "question_id": f"q_{random.randint(100, 999)}",
                        "correct": correct,
                        "time_taken_ms": random.randint(3000, 25000),
                        "attempts": 1 if correct else random.randint(1, 3),
                    }
                elif event_type == "hint_requested":
                    event_data = {
                        "hint_level": random.randint(1, 3),
                        "time_before_hint_ms": random.randint(5000, 30000),
                    }
                elif event_type == "level_complete":
                    event_data = {
                        "level_id": random.randint(1, 10),
                        "score": random.randint(60, 100),
                        "time_taken_ms": random.randint(60000, 300000),
                    }
                else:
                    event_data = {
                        "action": event_type,
                        "timestamp_offset": int(time_offset_minutes * 60000),
                    }

                telemetry = GameTelemetry(
                    id=str(uuid.uuid4()),
                    timestamp=event_time,
                    student_id=student.id,
                    session_id=game_session.id,
                    event_type=event_type,
                    event_data=event_data,
                    mission_id=game_session.mission_id,
                )
                session.add(telemetry)
                telemetry_events.append(telemetry)

    await session.commit()

    print(
        f"✅ Created {len(game_sessions)} game sessions and {len(telemetry_events)} telemetry events"
    )
    print(
        f"   📊 Average events per session: {len(telemetry_events) / len(game_sessions):.1f}"
    )
    return game_sessions


async def seed_assessments(session: AsyncSession, students: list[Student]):
    """Create realistic skill assessments with varied scores."""
    print("\n📊 Creating skill assessments...")

    skills = [
        SkillType.EMPATHY,
        SkillType.PROBLEM_SOLVING,
        SkillType.SELF_REGULATION,
        SkillType.RESILIENCE,
    ]

    assessments = []

    # Create varied assessments for all students
    for student in students:
        # Students have different skill profiles
        # Create a "profile" for each student
        base_skill_level = random.uniform(0.4, 0.9)

        for skill in skills:
            # Each skill varies around the base level
            score = base_skill_level + random.uniform(-0.15, 0.15)
            score = max(0.2, min(0.98, score))  # Clamp to realistic range

            # Confidence varies (newer assessments have lower confidence)
            confidence = random.uniform(0.65, 0.92)

            # Generate realistic reasoning
            reasoning_templates = {
                SkillType.EMPATHY: [
                    f"Student demonstrates {'strong' if score > 0.7 else 'developing'} empathy through peer interactions and group work.",
                    f"Shows {'consistent' if score > 0.7 else 'occasional'} awareness of others' feelings and responds appropriately.",
                ],
                SkillType.PROBLEM_SOLVING: [
                    f"Approaches challenges {'systematically' if score > 0.7 else 'with some guidance'} and tries multiple strategies.",
                    f"Demonstrates {'strong' if score > 0.7 else 'emerging'} analytical thinking in classroom activities.",
                ],
                SkillType.SELF_REGULATION: [
                    f"{'Consistently' if score > 0.7 else 'Sometimes'} manages emotions and stays focused during tasks.",
                    f"Shows {'good' if score > 0.7 else 'developing'} impulse control and follows classroom routines.",
                ],
                SkillType.RESILIENCE: [
                    f"{'Persists' if score > 0.7 else 'Shows effort'} through challenges and learns from setbacks.",
                    f"Demonstrates {'strong' if score > 0.7 else 'growing'} adaptability when faced with difficulties.",
                ],
            }

            reasoning = random.choice(reasoning_templates[skill])

            recommendations_templates = {
                SkillType.EMPATHY: "Continue fostering empathy through collaborative projects and peer mentoring opportunities.",
                SkillType.PROBLEM_SOLVING: "Encourage problem-solving by presenting open-ended challenges and celebrating creative solutions.",
                SkillType.SELF_REGULATION: "Support self-regulation development through mindfulness activities and clear routines.",
                SkillType.RESILIENCE: "Build resilience by providing appropriate challenges and celebrating growth mindset behaviors.",
            }

            recommendations = recommendations_templates[skill]

            assessment = SkillAssessment(
                id=str(uuid.uuid4()),
                student_id=student.id,
                skill_type=skill,
                score=round(score, 3),
                confidence=round(confidence, 3),
                reasoning=reasoning,
                recommendations=recommendations,
            )
            session.add(assessment)
            assessments.append(assessment)

    await session.commit()

    print(f"✅ Created {len(assessments)} skill assessments")

    # Print distribution summary
    avg_scores = {}
    for skill in skills:
        skill_scores = [a.score for a in assessments if a.skill_type == skill]
        avg_scores[skill.value] = sum(skill_scores) / len(skill_scores)

    print("   📊 Average scores by skill:")
    for skill, score in avg_scores.items():
        print(f"      • {skill}: {score:.2f}")


async def main():
    """Main seeding function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed database with enhanced realistic test data"
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear existing data first"
    )
    args = parser.parse_args()

    print("🌱 Starting ENHANCED database seeding with realistic data...")
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
            if args.clear:
                await clear_data(session)

            # Seed data in order
            schools = await seed_schools(session)
            teachers = await seed_teachers(session, schools)
            students = await seed_students(session, schools, teachers)
            audio_files = await seed_audio_files_enhanced(session, students)
            game_sessions = await seed_game_sessions_enhanced(session, students)
            await seed_assessments(session, students)

            print("\n" + "=" * 60)
            print("✅ ENHANCED database seeding completed successfully!")
            print("=" * 60)
            print("\n📊 Summary:")
            print(f"   • {len(schools)} schools")
            print(f"   • {len(teachers)} teachers")
            print(f"   • {len(students)} students (grades 2-8)")
            print(f"   • {len(audio_files)} audio files with realistic transcripts")
            print(f"   • {len(game_sessions)} game sessions with varied telemetry")
            print(f"   • {len(students) * 4} skill assessments")
            print("\n🔐 Test Login Credentials:")
            print("   Email: john.smith@springfield.edu")
            print("   Password: (use test password from your auth system)")
            print("\n🚀 Next steps:")
            print("   • Start the API: uvicorn app.main:app --reload")
            print("   • Test endpoints at http://localhost:8000/api/v1/docs")
            print("   • Run validation: bash test_features.sh")
            print("\n💡 Data Quality:")
            print("   • Transcripts use 100+ realistic student responses")
            print("   • Game telemetry reflects authentic gameplay patterns")
            print("   • Skill assessments show realistic score distributions")

        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
