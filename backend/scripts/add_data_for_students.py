"""
Add transcripts and game sessions for students who don't have any data.

Usage:
    python scripts/add_data_for_students.py
"""

import asyncio
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from app.core.config import settings
from app.models.student import Student
from app.models.transcript import Transcript
from app.models.audio import AudioFile
from app.models.game_telemetry import GameSession, GameTelemetry

# Sample realistic student responses
SAMPLE_RESPONSES = [
    "I really enjoyed helping my friend understand the math problem. It felt good to explain it in a way that made sense to them.",
    "When I couldn't solve the puzzle at first, I tried a different approach and it worked!",
    "I felt frustrated when things didn't go as planned, but I took a deep breath and kept going.",
    "Working with my team on the project was challenging but fun. Everyone contributed their ideas.",
    "I had to think carefully about the strategy before making my move in the game.",
    "Sometimes I get distracted, but I'm learning to focus better on my tasks.",
    "I noticed my classmate was upset, so I asked if they wanted to talk about it.",
    "The problem seemed impossible, but I broke it down into smaller steps.",
    "I didn't give up even though it was really hard. I kept trying until I figured it out.",
    "I learned that it's okay to ask for help when I need it.",
]

# Game event types
EVENT_TYPES = [
    "task_start",
    "task_complete",
    "task_fail",
    "retry_attempt",
    "hint_request",
    "progress_save",
    "level_complete",
    "achievement_unlock",
]


async def generate_transcript(session: AsyncSession, student_id: str, index: int):
    """Generate a transcript for a student."""
    # Create audio file first
    audio_id = str(uuid.uuid4())
    audio = AudioFile(
        id=audio_id,
        student_id=student_id,
        storage_path=f"audio/student_{student_id[:8]}_recording_{index}.wav",
        duration_seconds=random.randint(30, 180),
        source_type="classroom",
        recording_date=str(
            (datetime.now() - timedelta(days=random.randint(1, 30))).date()
        ),
        transcription_status="completed",
    )
    session.add(audio)
    await session.flush()

    # Create transcript
    text = random.choice(SAMPLE_RESPONSES)
    transcript = Transcript(
        id=str(uuid.uuid4()),
        audio_file_id=audio_id,
        student_id=student_id,
        text=text,
        word_count=len(text.split()),
        confidence_score=random.uniform(0.85, 0.99),
        language_code="en-US",
    )
    session.add(transcript)
    return transcript


async def generate_game_session(session: AsyncSession, student_id: str, index: int):
    """Generate a game session with telemetry for a student."""
    session_id = str(uuid.uuid4())

    # Create game session
    started = datetime.now() - timedelta(days=random.randint(1, 30))
    game_session = GameSession(
        id=session_id,
        student_id=student_id,
        started_at=started,
        ended_at=started + timedelta(hours=1),
        mission_id=f"mission_{random.randint(1, 10)}",
        game_version="1.0.0",
    )
    session.add(game_session)
    await session.flush()

    # Create telemetry events
    num_events = random.randint(3, 8)
    for i in range(num_events):
        telemetry = GameTelemetry(
            id=str(uuid.uuid4()),
            student_id=student_id,
            session_id=session_id,
            event_type=random.choice(EVENT_TYPES),
            event_data={
                "level": random.randint(1, 5),
                "duration_ms": random.randint(1000, 30000),
                "success": random.choice([True, False]),
            },
            timestamp=game_session.started_at + timedelta(minutes=i * 2),
        )
        session.add(telemetry)

    return game_session


async def add_data_for_students():
    """Add transcripts and game sessions for students without data."""
    print("🔬 Adding data for students without transcripts/game sessions...")

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # Get all students
            result = await session.execute(select(Student))
            all_students = result.scalars().all()

            students_updated = 0

            for student in all_students:
                # Check if student has transcripts
                result = await session.execute(
                    select(Transcript).where(Transcript.student_id == student.id)
                )
                has_transcripts = result.first() is not None

                # Check if student has game sessions
                result = await session.execute(
                    select(GameSession).where(GameSession.student_id == student.id)
                )
                has_sessions = result.first() is not None

                if not has_transcripts and not has_sessions:
                    print(f"\n📝 Adding data for student {student.id[:8]}...")

                    # Add 1 transcript
                    await generate_transcript(session, student.id, 1)
                    print(f"  ✅ Added 1 transcript")

                    # Add 1 game session with telemetry
                    await generate_game_session(session, student.id, 1)
                    print(f"  ✅ Added 1 game session with telemetry")

                    students_updated += 1

            # Commit all changes
            await session.commit()

            print("\n" + "=" * 60)
            print(f"✅ Data generation completed!")
            print("=" * 60)
            print(f"\n📊 Summary:")
            print(f"  • Students updated: {students_updated}")
            print(f"  • Transcripts added: {students_updated}")
            print(f"  • Game sessions added: {students_updated}")
            print(f"\n🚀 Next step: Run feature extraction")
            print(f"  python scripts/extract_all_features.py")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_data_for_students())
