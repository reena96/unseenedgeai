"""
Seed sample skill assessments with reasoning for students.
This allows the dashboard to display AI reasoning immediately.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from uuid import uuid4
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.models.student import Student
from app.models.assessment import SkillAssessment, SkillType, Evidence, EvidenceType


# Sample reasoning templates for each skill
REASONING_TEMPLATES = {
    "empathy": [
        "Student demonstrates strong understanding of others' perspectives through collaborative interactions and supportive communication patterns. Shows consistent ability to recognize emotional cues and respond appropriately.",
        "Analysis of student interactions reveals developing empathy skills with good awareness of peer emotions. Shows effort to understand different viewpoints and responds with compassion in group settings.",
        "Student exhibits solid empathy through active listening and thoughtful responses to classmates. Demonstrates ability to consider multiple perspectives before forming judgments.",
    ],
    "problem_solving": [
        "Student approaches challenges systematically, breaking complex problems into manageable steps. Shows strong analytical thinking and creativity in finding solutions.",
        "Demonstrates effective problem-solving through logical reasoning and willingness to try multiple approaches. Shows persistence when facing difficult tasks.",
        "Student exhibits strong critical thinking skills, analyzing problems from various angles before selecting solutions. Shows good balance of speed and accuracy in problem-solving tasks.",
    ],
    "self_regulation": [
        "Student demonstrates good emotional control and ability to manage frustration during challenging activities. Shows effective self-monitoring and adjustment of strategies when needed.",
        "Exhibits developing self-regulation skills with ability to pause and reflect before acting. Shows improvement in managing impulses and staying focused on tasks.",
        "Student displays strong self-regulation through consistent focus and ability to redirect attention when distracted. Demonstrates effective coping strategies during stressful situations.",
    ],
    "resilience": [
        "Student shows excellent bounce-back ability after setbacks, maintaining positive attitude and trying alternative approaches. Demonstrates growth mindset and learning from mistakes.",
        "Exhibits developing resilience through persistence in face of challenges. Shows willingness to seek help when needed and apply feedback constructively.",
        "Student demonstrates strong resilience by viewing failures as learning opportunities. Shows consistent effort and optimism even when tasks are difficult.",
    ],
    "adaptability": [
        "Student shows strong flexibility in adjusting to new situations and changing requirements. Demonstrates comfort with ambiguity and ability to shift strategies effectively.",
        "Exhibits good adaptability through willingness to try new approaches and adjust plans based on feedback. Shows openness to different ways of working.",
        "Student demonstrates solid adaptability skills, transitioning smoothly between different activities and responding well to unexpected changes.",
    ],
    "communication": [
        "Student communicates ideas clearly and effectively, using appropriate language for different audiences. Shows active listening skills and asks clarifying questions when needed.",
        "Exhibits developing communication skills with improving ability to express thoughts coherently. Shows effort to ensure understanding in conversations.",
        "Student demonstrates strong verbal and written communication, articulating complex ideas in accessible ways. Shows confidence in sharing perspectives and engaging in discussions.",
    ],
    "collaboration": [
        "Student works effectively in teams, contributing ideas while respecting others' input. Shows ability to negotiate, compromise, and work toward shared goals.",
        "Exhibits good collaboration skills through active participation and support of group members. Shows willingness to take on different roles as needed.",
        "Student demonstrates strong teamwork abilities, fostering positive group dynamics and helping ensure all voices are heard. Shows leadership and followership skills as appropriate.",
    ],
}

RECOMMENDATIONS_TEMPLATES = {
    "empathy": [
        "Continue practicing perspective-taking through role-play activities and reflective discussions. Encourage exploring diverse viewpoints in literature and current events.",
        "Provide opportunities for peer mentoring and collaborative projects that require understanding others' needs. Practice identifying emotions in various contexts.",
        "Engage in community service projects to broaden understanding of different life experiences. Journal about interactions and reflect on emotional responses.",
    ],
    "problem_solving": [
        "Challenge with increasingly complex problems that require multi-step reasoning. Encourage explaining solution strategies to build metacognitive skills.",
        "Provide open-ended challenges with multiple solution paths. Practice breaking large problems into smaller components and testing different approaches.",
        "Introduce design thinking frameworks and encourage creative problem-solving through real-world applications. Celebrate both successful and unsuccessful attempts as learning opportunities.",
    ],
    "self_regulation": [
        "Practice mindfulness techniques and breathing exercises to enhance emotional awareness. Develop personalized strategies for managing stress and frustration.",
        "Set small, achievable goals with built-in reflection points. Use visual cues or timers to support focus and self-monitoring during tasks.",
        "Teach specific self-regulation strategies like the STAR technique (Stop, Think, Act, Review). Provide positive reinforcement for demonstrated self-control.",
    ],
    "resilience": [
        "Frame challenges as growth opportunities and celebrate effort alongside achievement. Share stories of perseverance and discuss strategies used by others.",
        "Teach specific resilience strategies like positive self-talk and reframing setbacks. Create a 'learning from failure' portfolio to normalize mistakes as part of learning.",
        "Build resilience through graduated challenges that stretch abilities while ensuring success is achievable. Provide mentorship connections with resilient role models.",
    ],
    "adaptability": [
        "Introduce structured change gradually while teaching flexibility strategies. Practice transitioning between different types of activities with decreasing advance notice.",
        "Engage in activities that require adjusting plans mid-course. Discuss real-world examples of successful adaptation and the skills involved.",
        "Create opportunities to work with diverse groups and in various settings. Teach specific strategies for managing uncertainty and embracing new approaches.",
    ],
    "communication": [
        "Practice communication in various contexts (written, verbal, visual). Provide feedback on clarity and encourage use of examples and analogies.",
        "Engage in structured discussions and presentations to build confidence. Teach active listening techniques and practice paraphrasing to ensure understanding.",
        "Develop communication skills through peer teaching opportunities. Practice adapting communication style for different audiences and purposes.",
    ],
    "collaboration": [
        "Provide diverse team experiences with rotating roles and responsibilities. Teach specific teamwork skills like consensus-building and constructive feedback.",
        "Create projects requiring interdependence where individual success depends on group success. Reflect on team dynamics and identify improvement areas.",
        "Practice conflict resolution strategies and teach negotiation skills. Celebrate collaborative achievements and analyze what made teamwork effective.",
    ],
}


async def create_sample_assessments():
    """Create sample assessments with reasoning for all students."""

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get all students
        result = await session.execute(select(Student))
        students = result.scalars().all()

        print(f"Creating assessments for {len(students)} students...")
        print("This will generate AI-style reasoning for each skill.\n")

        skills = [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]

        total_assessments = 0

        for i, student in enumerate(students, 1):
            print(
                f"[{i}/{len(students)}] Creating assessments for {student.first_name} {student.last_name}..."
            )

            for skill in skills:
                skill_name = skill.value

                # Generate realistic scores with some variation
                base_score = random.uniform(0.60, 0.95)
                score = round(base_score, 2)
                confidence = round(random.uniform(0.75, 0.95), 2)

                # Select random reasoning and recommendations
                reasoning = random.choice(
                    REASONING_TEMPLATES.get(skill_name, ["Analysis pending"])
                )
                recommendations = random.choice(
                    RECOMMENDATIONS_TEMPLATES.get(
                        skill_name, ["Continue current progress"]
                    )
                )

                # Create assessment
                assessment = SkillAssessment(
                    id=str(uuid4()),
                    student_id=student.id,
                    skill_type=skill,
                    score=score,
                    confidence=confidence,
                    reasoning=reasoning,
                    recommendations=recommendations,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                session.add(assessment)

                # Create sample evidence
                evidence_texts = [
                    f"Student demonstrated {skill_name.replace('_', ' ')} during classroom activities",
                    f"Observed {skill_name.replace('_', ' ')} in peer interactions",
                    f"Game telemetry shows strong {skill_name.replace('_', ' ')} indicators",
                ]

                for evidence_text in evidence_texts:
                    evidence = Evidence(
                        id=str(uuid4()),
                        assessment_id=assessment.id,
                        evidence_type=random.choice(
                            [EvidenceType.LINGUISTIC, EvidenceType.BEHAVIORAL]
                        ),
                        source=f"Session {random.randint(1, 10)}",
                        content=evidence_text,
                        relevance_score=round(random.uniform(0.70, 0.95), 2),
                    )
                    session.add(evidence)

                total_assessments += 1

            # Commit after each student
            await session.commit()

        print(f"\n✅ Successfully created {total_assessments} assessments!")
        print(f"📊 {len(students)} students now have skill assessments with reasoning")
        print(
            f"🎯 Skills assessed: Empathy, Problem Solving, Self-Regulation, Resilience"
        )
        print(f"\n🌐 View in dashboard: http://localhost:8501")

    await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("Seeding Sample Assessments with AI Reasoning")
    print("=" * 60)
    asyncio.run(create_sample_assessments())
