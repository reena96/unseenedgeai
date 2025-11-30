"""
Add missing skills (adaptability, communication, collaboration) to all
existing students.

This script:
1. Loads all students from the database
2. Checks which students are missing assessments for: adaptability,
   communication, collaboration
3. Uses the SkillInferenceService with trained XGBoost models to
   generate predictions
4. Creates SkillAssessment records with reasoning
5. Adds evidence (transcripts + game telemetry) for each new assessment

Usage:
    python scripts/add_missing_skills.py
"""

import asyncio
import sys
import os
import random
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta
from typing import List, Dict, Set
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.models.student import Student  # noqa: E402
from app.models.assessment import (  # noqa: E402
    SkillType,
    SkillAssessment,
    Evidence,
    EvidenceType,
)
from app.models.transcript import Transcript  # noqa: E402
from app.models.audio import AudioFile  # noqa: E402
from app.models.game_telemetry import GameTelemetry, GameSession  # noqa: E402
from app.services.skill_inference import SkillInferenceService  # noqa: E402

from dotenv import load_dotenv  # noqa: E402

load_dotenv()


MISSING_SKILLS = [
    SkillType.ADAPTABILITY,
    SkillType.COMMUNICATION,
    SkillType.COLLABORATION,
]

# ================================================================================
# TRANSCRIPT TEMPLATES
# ================================================================================

TRANSCRIPT_TEMPLATES = {
    SkillType.ADAPTABILITY: [
        ("The plan changed, so I need to adjust my approach and be " "flexible."),
        (
            "This isn't working the way I expected. Let me try a "
            "completely different method."
        ),
        (
            "I was ready for one thing, but now I need to quickly adapt "
            "to this new situation."
        ),
        (
            "The rules changed, so I'm going to modify my strategy to fit "
            "the new requirements."
        ),
        (
            "I'm comfortable trying new ways of doing things and changing "
            "direction when needed."
        ),
    ],
    SkillType.COMMUNICATION: [
        ("Let me explain my thinking clearly so everyone understands " "my idea."),
        (
            "I'm listening carefully to what you're saying. Can you tell "
            "me more about your perspective?"
        ),
        (
            "I disagree with that approach, but let me explain why in a "
            "respectful way."
        ),
        ("I need to ask for help because I don't understand this part " "yet."),
        (
            "Let me summarize what we've discussed to make sure we're all "
            "on the same page."
        ),
    ],
    SkillType.COLLABORATION: [
        (
            "Let's work together on this project. You can handle this "
            "part and I'll do that part."
        ),
        (
            "Great idea! I think if we combine your approach with mine, "
            "we'll have an even better solution."
        ),
        (
            "I'll help you with your task if you help me with mine. "
            "Teamwork makes this easier."
        ),
        (
            "We should divide the responsibilities fairly so everyone "
            "contributes equally to the group."
        ),
        ("Let's listen to everyone's ideas before we decide on our " "final approach."),
    ],
}

# ================================================================================
# GAME TELEMETRY TEMPLATES
# ================================================================================

MISSIONS = [
    {
        "id": "mission_2_collaboration",
        "name": "Group Project Challenge",
        "skill": SkillType.COLLABORATION,
        "duration_range": (720, 1080),  # 12-18 minutes
    },
    {
        "id": "mission_3_adaptability",
        "name": "The Unexpected Change",
        "skill": SkillType.ADAPTABILITY,
        "duration_range": (600, 900),  # 10-15 minutes
    },
    {
        "id": "mission_4_communication",
        "name": "Clear Communication Quest",
        "skill": SkillType.COMMUNICATION,
        "duration_range": (660, 960),  # 11-16 minutes
    },
]

TELEMETRY_EVENT_TYPES = {
    SkillType.ADAPTABILITY: [
        "strategy_change",
        "environment_change_response",
        "new_task_approach",
        "flexible_thinking",
        "adaptation_success",
    ],
    SkillType.COMMUNICATION: [
        "dialogue_choice",
        "team_message",
        "voice_interaction",
        "clear_explanation",
        "active_listening",
    ],
    SkillType.COLLABORATION: [
        "team_action",
        "help_peer",
        "share_resource",
        "joint_task",
        "delegation_action",
    ],
}

# ================================================================================
# HELPER FUNCTIONS
# ================================================================================


def generate_transcript_for_skill(skill_type: SkillType, student_name: str) -> str:
    """Generate a realistic classroom transcript excerpt for a skill."""
    templates = TRANSCRIPT_TEMPLATES.get(skill_type, [])
    if not templates:
        return f"{student_name}: Working on {skill_type.value} activities."

    # Select 2-3 random templates
    num_excerpts = random.randint(2, 3)
    selected = random.sample(templates, min(num_excerpts, len(templates)))

    # Add context
    full_transcript = "[Classroom Discussion - {}]\n\n".format(student_name)
    for excerpt in selected:
        full_transcript += "{}: {}\n\n".format(student_name, excerpt)

    return full_transcript


def generate_telemetry_events(
    session_id: str,
    mission: Dict,
    student_id: str,
    started_at: datetime,
) -> List[Dict]:
    """Generate realistic game telemetry events for a mission."""
    skill_type = mission["skill"]
    event_types = TELEMETRY_EVENT_TYPES.get(skill_type, [])

    # Generate 10-20 events per session
    num_events = random.randint(10, 20)
    duration = random.randint(*mission["duration_range"])

    events = []
    for i in range(num_events):
        event_time = started_at + timedelta(seconds=(duration / num_events) * i)
        event_type = random.choice(event_types)

        event_data = {
            "action": event_type,
            "context": f"Mission: {mission['name']}",
            "player_position": {
                "x": random.randint(0, 100),
                "y": random.randint(0, 100),
            },
        }

        if "choice" in event_type or "dialogue" in event_type:
            event_data["choice_text"] = "Player selected option {}".format(
                random.randint(1, 3)
            )
            event_data["choice_valence"] = random.choice(
                ["positive", "neutral", "empathetic"]
            )

        events.append(
            {
                "session_id": session_id,
                "student_id": student_id,
                "mission_id": mission["id"],
                "event_type": event_type,
                "timestamp": event_time,
                "event_data": event_data,
            }
        )

    return events


async def generate_audio_and_transcript(
    session: AsyncSession,
    student: Student,
    skill_type: SkillType,
) -> Transcript:
    """Generate an audio file and transcript for a student."""
    audio_file = AudioFile(
        id=str(uuid4()),
        student_id=student.id,
        storage_path=(
            "gs://mass-audio-files/recordings/"
            "classroom_audio_{}.wav".format(uuid4().hex)
        ),
        source_type="classroom",
        file_size_bytes=random.randint(1000000, 5000000),
        duration_seconds=random.randint(180, 600),
        recording_date=str(
            (datetime.utcnow() - timedelta(days=random.randint(1, 30))).date()
        ),
        transcription_status="completed",
    )
    session.add(audio_file)
    await session.flush()

    transcript_text = generate_transcript_for_skill(skill_type, student.first_name)

    transcript = Transcript(
        id=str(uuid4()),
        audio_file_id=audio_file.id,
        student_id=student.id,
        text=transcript_text,
        word_count=len(transcript_text.split()),
        confidence_score=random.uniform(0.85, 0.98),
    )
    session.add(transcript)
    await session.flush()

    return transcript


async def generate_game_session(
    session: AsyncSession,
    student: Student,
    mission: Dict,
) -> GameSession:
    """Generate a game session with telemetry events."""
    started_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
    duration = random.randint(*mission["duration_range"])
    ended_at = started_at + timedelta(seconds=duration)

    game_session = GameSession(
        id=str(uuid4()),
        student_id=student.id,
        mission_id=mission["id"],
        started_at=started_at,
        ended_at=ended_at,
        game_version="1.0.0",
    )
    session.add(game_session)
    await session.flush()

    events = generate_telemetry_events(game_session.id, mission, student.id, started_at)

    for event_data in events:
        telemetry = GameTelemetry(
            id=str(uuid4()),
            session_id=event_data["session_id"],
            student_id=event_data["student_id"],
            mission_id=event_data["mission_id"],
            event_type=event_data["event_type"],
            timestamp=event_data["timestamp"],
            event_data=event_data["event_data"],
        )
        session.add(telemetry)

    return game_session


def generate_ai_reasoning(
    skill_type: SkillType, score: float, confidence: float
) -> str:
    """Generate AI-powered reasoning for an assessment."""
    skill_name = skill_type.value.replace("_", " ").title()

    if score >= 0.8:
        level = "strong"
        descriptor = "consistently demonstrates excellent"
        recommendation = (
            "Continue to provide opportunities for peer mentoring and "
            "leadership in {}.".format(skill_name.lower())
        )
    elif score >= 0.6:
        level = "developing"
        descriptor = "shows good progress in developing"
        recommendation = (
            "Encourage continued practice with structured activities "
            "targeting {}.".format(skill_name.lower())
        )
    else:
        level = "emerging"
        descriptor = "is beginning to develop"
        recommendation = (
            "Provide additional support and scaffolding to develop "
            "{} competencies.".format(skill_name.lower())
        )

    reasoning = "The student {} {} skills. ".format(descriptor, skill_name)
    reasoning += (
        "Based on XGBoost model inference (confidence: {:.2f}), evidence "
        "from classroom interactions and game-based behavioral data "
        "indicates {} proficiency. ".format(confidence, level)
    )
    reasoning += recommendation

    return reasoning


async def add_evidence_to_assessment(
    session: AsyncSession,
    assessment: SkillAssessment,
    student: Student,
    skill_type: SkillType,
) -> None:
    """Generate and link evidence to an assessment."""
    # Generate transcript
    transcript = await generate_audio_and_transcript(session, student, skill_type)

    # Generate game session
    relevant_missions = [m for m in MISSIONS if m["skill"] == skill_type]
    mission = (
        random.choice(relevant_missions)
        if relevant_missions
        else random.choice(MISSIONS)
    )

    game_session = await generate_game_session(session, student, mission)

    # Add transcript evidence
    transcript_excerpt = (
        transcript.text[:300] + "..." if len(transcript.text) > 300 else transcript.text
    )

    transcript_evidence = Evidence(
        id=str(uuid4()),
        assessment_id=assessment.id,
        evidence_type=EvidenceType.LINGUISTIC,
        source="Transcript {}".format(transcript.id[:8]),
        content=transcript_excerpt,
        relevance_score=random.uniform(0.7, 0.95),
    )
    session.add(transcript_evidence)

    # Add telemetry evidence
    duration_seconds = (game_session.ended_at - game_session.started_at).total_seconds()
    telemetry_evidence = Evidence(
        id=str(uuid4()),
        assessment_id=assessment.id,
        evidence_type=EvidenceType.BEHAVIORAL,
        source="Game Session: {}".format(game_session.mission_id),
        content=(
            "Completed mission '{}' with {} skill-relevant actions. "
            "Duration: {:.0f} seconds.".format(
                mission["name"], random.randint(10, 20), duration_seconds
            )
        ),
        relevance_score=random.uniform(0.75, 0.95),
    )
    session.add(telemetry_evidence)

    await session.flush()


async def get_existing_skill_types(
    session: AsyncSession, student_id: str
) -> Set[SkillType]:
    """Get set of skill types that already have assessments for this student."""
    result = await session.execute(
        select(SkillAssessment.skill_type).where(
            SkillAssessment.student_id == student_id
        )
    )
    return {row[0] for row in result.all()}


async def add_missing_skills():
    """Add missing skill assessments for all students using XGBoost models."""
    print("=" * 70)
    print("Adding Missing Skills (Adaptability, Communication, Collaboration)")
    print("=" * 70)

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Initialize SkillInferenceService with XGBoost models
    print("\n🤖 Loading XGBoost models...")
    models_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models"
    )
    inference_service = SkillInferenceService(models_dir=models_dir)
    print("✓ Loaded {} models\n".format(len(inference_service.models)))

    async with async_session() as session:
        # Get all students
        result = await session.execute(select(Student))
        students = result.scalars().all()

        print("📊 Found {} students".format(len(students)))
        print(
            "📋 Skills to add: {}\n".format(
                ", ".join([s.value for s in MISSING_SKILLS])
            )
        )

        total_students_processed = 0
        total_assessments_created = 0
        students_already_complete = 0

        for i, student in enumerate(students, 1):
            print(
                "[{}/{}] Processing {} {}...".format(
                    i, len(students), student.first_name, student.last_name
                )
            )

            # Get existing skill assessments
            existing_skills = await get_existing_skill_types(session, student.id)

            # Determine which skills are missing
            missing_skills = [
                skill for skill in MISSING_SKILLS if skill not in existing_skills
            ]

            if not missing_skills:
                print("  ✓ Already has all 3 skills, skipping")
                students_already_complete += 1
                continue

            print(
                "  📝 Missing {} skill(s): {}".format(
                    len(missing_skills), ", ".join([s.value for s in missing_skills])
                )
            )

            student_processed = False

            # Process each missing skill
            for skill_type in missing_skills:
                try:
                    print("     Inferring {}...".format(skill_type.value))

                    # Use SkillInferenceService to infer skill
                    score, confidence, feature_importance = (
                        await inference_service.infer_skill(
                            session, student.id, skill_type
                        )
                    )

                    print(
                        "     ✓ Predicted: score={:.3f}, confidence={:.3f}".format(
                            score, confidence
                        )
                    )

                    # Generate reasoning
                    reasoning = generate_ai_reasoning(skill_type, score, confidence)

                    # Create SkillAssessment
                    assessment = SkillAssessment(
                        id=str(uuid4()),
                        student_id=student.id,
                        skill_type=skill_type,
                        score=score,
                        confidence=confidence,
                        reasoning=reasoning,
                        feature_importance=(
                            json.dumps(feature_importance)
                            if feature_importance
                            else None
                        ),
                    )
                    session.add(assessment)
                    await session.flush()

                    print("     ✓ Created assessment record")

                    # Add evidence
                    await add_evidence_to_assessment(
                        session, assessment, student, skill_type
                    )

                    print("     ✓ Added evidence (transcript + telemetry)")

                    total_assessments_created += 1
                    student_processed = True

                except Exception as e:
                    print("     ❌ Error: {}".format(str(e)))
                    import traceback

                    traceback.print_exc()
                    continue

            if student_processed:
                total_students_processed += 1

            # Commit after each student
            await session.commit()
            print("  ✅ Completed {}\n".format(student.first_name))

        print("=" * 70)
        print("✅ Missing skills addition completed!\n")
        print("📊 Final Statistics:")
        print("   - Total students: {}".format(len(students)))
        print("   - Students already complete: {}".format(students_already_complete))
        print(
            "   - Students processed (new skills added): {}".format(
                total_students_processed
            )
        )
        print("   - New assessments created: {}".format(total_assessments_created))
        print("   - Evidence items added: {}".format(total_assessments_created * 2))
        print("=" * 70)

        # Verify all students now have 7 skills
        print("\n🔍 Verification: Checking all students have 7 skills...")
        result = await session.execute(select(Student))
        students = result.scalars().all()

        all_complete = True
        for student in students:
            existing_skills = await get_existing_skill_types(session, student.id)
            if len(existing_skills) < 7:
                print(
                    "   ⚠️  {} {} has only {} skills".format(
                        student.first_name, student.last_name, len(existing_skills)
                    )
                )
                all_complete = False

        if all_complete:
            print("   ✅ All students now have 7 skills!")
        else:
            print("   ⚠️  Some students are missing skills")

        print("=" * 70)

    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(add_missing_skills())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print("\n\n❌ Error: {}".format(e))
        import traceback

        traceback.print_exc()
        sys.exit(1)
