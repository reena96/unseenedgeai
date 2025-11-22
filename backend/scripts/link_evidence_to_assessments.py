"""Link existing transcripts and telemetry to assessments as evidence."""

import asyncio
import sys
import os
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from uuid import uuid4

from app.core.config import settings
from app.models.student import Student
from app.models.assessment import SkillAssessment, Evidence, EvidenceType
from app.models.transcript import Transcript
from app.models.audio import AudioFile


async def link_evidence():
    """Link transcripts to assessments as evidence."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("🔗 Linking evidence to assessments...")

        # Get all students
        students_result = await session.execute(select(Student))
        students = students_result.scalars().all()
        print(f"📊 Found {len(students)} students")

        total_evidence_added = 0

        for idx, student in enumerate(students, 1):
            print(
                f"\n[{idx}/{len(students)}] Processing {student.first_name} {student.last_name}..."
            )

            # Get assessments
            assessments_result = await session.execute(
                select(SkillAssessment).where(SkillAssessment.student_id == student.id)
            )
            assessments = assessments_result.scalars().all()

            if not assessments:
                print(f"  ⚠️  No assessments found")
                continue

            # Get transcripts for this student
            transcripts_result = await session.execute(
                select(Transcript, AudioFile)
                .join(AudioFile, Transcript.audio_file_id == AudioFile.id)
                .where(Transcript.student_id == student.id)
                .limit(20)
            )
            transcript_pairs = transcripts_result.all()

            if not transcript_pairs:
                print(f"  ⚠️  No transcripts found")
                continue

            print(
                f"  📝 Found {len(assessments)} assessments and {len(transcript_pairs)} transcripts"
            )

            # Link transcripts as evidence
            for assessment in assessments:
                # Check if evidence already exists by querying
                existing_evidence_result = await session.execute(
                    select(Evidence).where(Evidence.assessment_id == assessment.id)
                )
                existing_evidence = existing_evidence_result.scalars().all()

                if len(existing_evidence) > 0:
                    print(
                        f"    ⏩ {assessment.skill_type.value} already has {len(existing_evidence)} evidence items"
                    )
                    continue

                # Select 2-3 random transcripts for this assessment
                num_transcripts = min(random.randint(2, 3), len(transcript_pairs))
                selected_transcripts = random.sample(transcript_pairs, num_transcripts)

                for transcript, audio_file in selected_transcripts:
                    # Create excerpt (first 200-300 chars)
                    excerpt_length = random.randint(200, min(300, len(transcript.text)))
                    excerpt = transcript.text[:excerpt_length]
                    if len(transcript.text) > excerpt_length:
                        excerpt += "..."

                    # Create evidence
                    evidence = Evidence(
                        id=str(uuid4()),
                        assessment_id=assessment.id,
                        evidence_type=EvidenceType.LINGUISTIC,
                        source=f"Classroom transcript from {audio_file.recording_date or 'recent session'}",
                        content=excerpt,
                        relevance_score=random.uniform(0.75, 0.95),
                    )
                    session.add(evidence)
                    total_evidence_added += 1

                # Add a synthetic game telemetry evidence item
                game_evidence = Evidence(
                    id=str(uuid4()),
                    assessment_id=assessment.id,
                    evidence_type=EvidenceType.BEHAVIORAL,
                    source="Flourish Academy Game Session",
                    content=f"Student demonstrated {assessment.skill_type.value.replace('_', ' ')} through {random.randint(8, 15)} relevant in-game choices and actions during mission gameplay. Completed mission with {random.choice(['strong', 'good', 'developing'])} performance indicators.",
                    relevance_score=random.uniform(0.70, 0.90),
                )
                session.add(game_evidence)
                total_evidence_added += 1

                print(
                    f"    ✓ Linked {num_transcripts + 1} evidence items to {assessment.skill_type.value}"
                )

            # Commit after each student
            await session.commit()
            print(f"  ✅ Completed {student.first_name}")

        print(f"\n" + "=" * 60)
        print(f"✅ Evidence linking completed!")
        print(f"📊 Total evidence items added: {total_evidence_added}")
        print(f"=" * 60)


if __name__ == "__main__":
    asyncio.run(link_evidence())
