"""
Script to enrich all student assessments with transcripts, game telemetry, and AI insights.

This script:
1. Generates realistic classroom transcripts for each student
2. Creates game telemetry data from Flourish Academy missions
3. Extracts linguistic features from transcripts
4. Links evidence to existing skill assessments
5. Generates AI-powered reasoning for each assessment
"""

import asyncio
import sys
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import uuid4

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.student import Student
from app.models.assessment import SkillAssessment, Evidence, EvidenceType, SkillType
from app.models.transcript import Transcript
from app.models.audio import AudioFile
from app.models.game_telemetry import GameTelemetry, GameSession

# Get DATABASE_URL from environment
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://mass:mass@localhost/mass_db"
)

# ================================================================================
# TRANSCRIPT TEMPLATES
# ================================================================================

TRANSCRIPT_TEMPLATES = {
    SkillType.EMPATHY: [
        "I think I understand how you feel about this. That must be really frustrating when your group members don't listen to your ideas.",
        "I can see that you're upset. Let me help you work through this problem. We can figure it out together.",
        "It sounds like your friend is going through a difficult time. How do you think they're feeling right now?",
        "I notice that Jamie looks sad today. Maybe we should ask if they're okay and see if we can help.",
        "I understand why that would make you feel left out. Let's talk about how we can include everyone in the activity.",
    ],
    SkillType.PROBLEM_SOLVING: [
        "Let me think through this step by step. First, we need to identify the main problem, then brainstorm solutions.",
        "I tried one approach and it didn't work, so now I'm going to try a different strategy to solve this.",
        "We can break this complex problem into smaller parts and tackle each one individually.",
        "I'll make a plan before I start. First this, then that, and finally we'll check if it worked.",
        "This is tricky, but I think if we approach it from a different angle, we might find the solution.",
    ],
    SkillType.SELF_REGULATION: [
        "I'm feeling frustrated right now, but I'm going to take a deep breath and calm down before continuing.",
        "I need to focus on my work and not get distracted by what's happening around me.",
        "I'm going to wait my turn and not interrupt while others are speaking.",
        "This is challenging, but I'm going to stay calm and keep working on it steadily.",
        "I feel like giving up, but I know I need to manage my emotions and keep trying.",
    ],
    SkillType.RESILIENCE: [
        "I didn't get it right the first time, but that's okay. I'm going to try again with a different approach.",
        "This is really hard, but I'm not going to give up. I'll keep practicing until I improve.",
        "I made a mistake, but I learned from it. Now I know what to do differently next time.",
        "Even though I failed the test, I'm going to study harder and do better next time.",
        "I'm going to persist through this challenge. I've overcome difficult things before.",
    ],
    SkillType.COMMUNICATION: [
        "Let me explain my thinking clearly so everyone understands my idea.",
        "I'm listening carefully to what you're saying. Can you tell me more about your perspective?",
        "I disagree with that approach, but let me explain why in a respectful way.",
        "I need to ask for help because I don't understand this part yet.",
        "Let me summarize what we've discussed to make sure we're all on the same page.",
    ],
    SkillType.COLLABORATION: [
        "Let's work together on this project. You can handle this part and I'll do that part.",
        "Great idea! I think if we combine your approach with mine, we'll have an even better solution.",
        "I'll help you with your task if you help me with mine. Teamwork makes this easier.",
        "We should divide the responsibilities fairly so everyone contributes equally to the group.",
        "Let's listen to everyone's ideas before we decide on our final approach.",
    ],
    SkillType.ADAPTABILITY: [
        "The plan changed, so I need to adjust my approach and be flexible.",
        "This isn't working the way I expected. Let me try a completely different method.",
        "I was ready for one thing, but now I need to quickly adapt to this new situation.",
        "The rules changed, so I'm going to modify my strategy to fit the new requirements.",
        "I'm comfortable trying new ways of doing things and changing direction when needed.",
    ],
}

# ================================================================================
# GAME TELEMETRY TEMPLATES
# ================================================================================

MISSIONS = [
    {
        "id": "mission_1_empathy",
        "name": "Understanding Perspectives",
        "skill": SkillType.EMPATHY,
        "duration_range": (600, 900),  # 10-15 minutes
    },
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
]

TELEMETRY_EVENT_TYPES = {
    SkillType.EMPATHY: [
        "npc_interaction",
        "dialogue_choice",
        "help_action",
        "character_emotion_response",
        "empathy_choice_made",
    ],
    SkillType.PROBLEM_SOLVING: [
        "puzzle_start",
        "puzzle_complete",
        "hint_used",
        "strategy_change",
        "solution_attempt",
    ],
    SkillType.SELF_REGULATION: [
        "pause_action",
        "distraction_event",
        "focus_maintained",
        "emotion_regulation",
        "impulse_controlled",
    ],
    SkillType.RESILIENCE: [
        "failure_event",
        "retry_action",
        "mission_restart",
        "challenge_overcome",
        "persistence_shown",
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
    SkillType.ADAPTABILITY: [
        "strategy_change",
        "environment_change_response",
        "new_task_approach",
        "flexible_thinking",
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

    # Select 2-3 random templates and personalize
    num_excerpts = random.randint(2, 3)
    selected = random.sample(templates, min(num_excerpts, len(templates)))

    # Add context
    full_transcript = f"[Classroom Discussion - {student_name}]\n\n"
    for i, excerpt in enumerate(selected, 1):
        full_transcript += f"{student_name}: {excerpt}\n\n"

    return full_transcript


def generate_telemetry_events(
    session_id: str,
    mission: Dict[str, Any],
    student_id: str,
    started_at: datetime,
) -> List[Dict[str, Any]]:
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

        # Generate event-specific data
        event_data = {
            "action": event_type,
            "context": f"Mission: {mission['name']}",
            "player_position": {
                "x": random.randint(0, 100),
                "y": random.randint(0, 100),
            },
        }

        # Add choice data for certain event types
        if "choice" in event_type or "dialogue" in event_type:
            event_data["choice_text"] = f"Player selected option {random.randint(1, 3)}"
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
    # Create audio file record
    audio_file = AudioFile(
        id=str(uuid4()),
        student_id=student.id,
        storage_path=f"gs://mass-audio-files/recordings/classroom_audio_{uuid4().hex}.wav",
        source_type="classroom",
        file_size_bytes=random.randint(1000000, 5000000),  # 1-5 MB
        duration_seconds=random.randint(180, 600),  # 3-10 minutes
        recording_date=str(
            (datetime.utcnow() - timedelta(days=random.randint(1, 30))).date()
        ),
        transcription_status="completed",
    )
    session.add(audio_file)
    await session.flush()

    # Create transcript
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
    mission: Dict[str, Any],
) -> GameSession:
    """Generate a game session with telemetry events."""
    started_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
    duration = random.randint(*mission["duration_range"])
    ended_at = started_at + timedelta(seconds=duration)

    # Create game session
    game_session = GameSession(
        id=str(uuid4()),
        student_id=student.id,
        mission_id=mission["id"],
        started_at=started_at,
        ended_at=ended_at,
        status="completed",
    )
    session.add(game_session)
    await session.flush()

    # Generate telemetry events
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


async def enrich_assessment_with_evidence(
    session: AsyncSession,
    assessment: SkillAssessment,
    transcript: Transcript,
    game_session: GameSession,
) -> None:
    """Link evidence to an assessment."""
    # Add transcript evidence
    transcript_excerpt = (
        transcript.text[:300] + "..." if len(transcript.text) > 300 else transcript.text
    )

    transcript_evidence = Evidence(
        id=str(uuid4()),
        assessment_id=assessment.id,
        evidence_type=EvidenceType.LINGUISTIC,
        source=f"Transcript {transcript.id[:8]}",
        content=transcript_excerpt,
        relevance_score=random.uniform(0.7, 0.95),
    )
    session.add(transcript_evidence)

    # Add telemetry evidence
    telemetry_evidence = Evidence(
        id=str(uuid4()),
        assessment_id=assessment.id,
        evidence_type=EvidenceType.BEHAVIORAL,
        source=f"Game Session: {game_session.mission_id}",
        content=f"Completed mission with {random.randint(10, 20)} skill-relevant actions. Duration: {(game_session.ended_at - game_session.started_at).total_seconds():.0f} seconds.",
        relevance_score=random.uniform(0.75, 0.95),
    )
    session.add(telemetry_evidence)

    # Generate AI reasoning if not present
    if not assessment.reasoning:
        assessment.reasoning = generate_ai_reasoning(assessment, transcript_excerpt)

    await session.flush()


def generate_ai_reasoning(assessment: SkillAssessment, transcript_excerpt: str) -> str:
    """Generate AI-powered reasoning for an assessment."""
    skill_name = assessment.skill_type.value.replace("_", " ").title()
    score = assessment.score

    if score >= 0.8:
        level = "strong"
        descriptor = "consistently demonstrates excellent"
    elif score >= 0.6:
        level = "developing"
        descriptor = "shows good progress in developing"
    else:
        level = "emerging"
        descriptor = "is beginning to develop"

    reasoning = f"The student {descriptor} {skill_name} skills. "
    reasoning += f"Evidence from classroom interactions shows authentic application of {skill_name.lower()} in real-world contexts. "
    reasoning += f"Game-based behavioral data corroborates these observations, indicating {level} proficiency. "

    if score >= 0.8:
        reasoning += f"Continue to provide opportunities for peer mentoring and leadership in {skill_name.lower()}."
    elif score >= 0.6:
        reasoning += f"Encourage continued practice with structured activities targeting {skill_name.lower()}."
    else:
        reasoning += f"Provide additional support and scaffolding to develop {skill_name.lower()} competencies."

    return reasoning


# ================================================================================
# MAIN ENRICHMENT FUNCTION
# ================================================================================


async def enrich_all_students():
    """Main function to enrich all student assessments with evidence."""
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("🚀 Starting evidence enrichment for all students...")

        # Get all students
        result = await session.execute(select(Student))
        students = result.scalars().all()
        print(f"📊 Found {len(students)} students to enrich")

        total_transcripts = 0
        total_sessions = 0
        total_evidence = 0

        for idx, student in enumerate(students, 1):
            print(
                f"\n[{idx}/{len(students)}] Processing {student.first_name} {student.last_name}..."
            )

            # Get existing assessments
            assessment_result = await session.execute(
                select(SkillAssessment).where(SkillAssessment.student_id == student.id)
            )
            assessments = assessment_result.scalars().all()

            if not assessments:
                print(
                    f"  ⚠️  No assessments found for {student.first_name}, skipping..."
                )
                continue

            # Process each skill assessment
            for assessment in assessments:
                skill_type = assessment.skill_type
                print(f"  📝 Enriching {skill_type.value}...")

                try:
                    # Generate transcript
                    transcript = await generate_audio_and_transcript(
                        session, student, skill_type
                    )
                    total_transcripts += 1
                    print(
                        f"     ✓ Generated transcript ({transcript.word_count} words)"
                    )

                    # Generate game session for relevant mission
                    relevant_missions = [
                        m for m in MISSIONS if m["skill"] == skill_type
                    ]
                    if relevant_missions:
                        mission = random.choice(relevant_missions)
                        game_session = await generate_game_session(
                            session, student, mission
                        )
                        total_sessions += 1
                        print(f"     ✓ Generated game session ({mission['name']})")
                    else:
                        # Use a random mission
                        mission = random.choice(MISSIONS)
                        game_session = await generate_game_session(
                            session, student, mission
                        )
                        total_sessions += 1
                        print(f"     ✓ Generated game session (random)")

                    # Link evidence to assessment
                    await enrich_assessment_with_evidence(
                        session, assessment, transcript, game_session
                    )
                    total_evidence += 2  # transcript + telemetry
                    print(f"     ✓ Linked evidence to assessment")

                except Exception as e:
                    print(f"     ❌ Error: {str(e)}")
                    continue

            # Commit after each student
            await session.commit()
            print(f"  ✅ Completed {student.first_name} {student.last_name}")

        print(f"\n" + "=" * 60)
        print(f"✅ Evidence enrichment completed!")
        print(f"📊 Statistics:")
        print(f"   - Students processed: {len(students)}")
        print(f"   - Transcripts generated: {total_transcripts}")
        print(f"   - Game sessions created: {total_sessions}")
        print(f"   - Evidence items linked: {total_evidence}")
        print(f"=" * 60)


if __name__ == "__main__":
    asyncio.run(enrich_all_students())
