"""
Add comprehensive transcript evidence for all skills with positive and negative examples.

Usage:
    python scripts/add_transcript_evidence.py
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

# Comprehensive transcript samples for each skill
# Each skill has positive (high skill) and negative (low skill) examples

SKILL_TRANSCRIPTS = {
    "empathy": {
        "positive": [
            "I noticed Sarah was sitting alone at lunch today and she looked really sad. I went over and asked if she was okay. She said she was having a hard day, so I just listened and let her talk about it. Sometimes people just need someone to care.",
            "When my little brother was upset about losing his toy, I remembered how I felt when I lost something important. I helped him look for it and told him we'd find it together. I could tell he felt better just knowing I understood.",
            "My friend was really stressed about the test. Instead of just saying 'you'll be fine', I asked what specifically was worrying them. Then I offered to study together because I know it helps to have support.",
            "I could see my teammate was frustrated during the game. I told them it was okay and that we all make mistakes. I tried to encourage them instead of getting mad, because I know how it feels to mess up.",
        ],
        "negative": [
            "My classmate was crying but I didn't really care. I just kept playing my game. It's not my problem if they're upset.",
            "Someone asked me for help but I told them to figure it out themselves. I was busy with my own stuff and didn't want to be bothered.",
            "When my friend said they were sad, I just changed the subject. I don't really like talking about feelings and stuff. It's uncomfortable.",
            "I saw someone struggling with their work but I didn't help because they're not in my friend group. Why should I care about people I don't know?",
        ],
    },
    "adaptability": {
        "positive": [
            "When the teacher changed the project requirements, I didn't panic. I just looked at what I already had and figured out how to adjust it. Change happens, and I can roll with it.",
            "My usual route to school was blocked today, so I tried a different way. It actually took less time! I learned that trying new things can work out better than you expect.",
            "We got a substitute teacher who does things differently. Instead of complaining, I just followed their instructions. It's actually interesting to learn different ways of doing things.",
            "When I joined the new class mid-year, I was nervous but I adapted pretty quickly. I introduced myself, asked questions when I needed help, and made an effort to fit in with how things work here.",
        ],
        "negative": [
            "Everything is different this year and I hate it. I want things to go back to how they were. I don't want to learn new ways of doing things.",
            "When they changed the schedule, I was so confused and upset. I kept doing things the old way even though the teacher kept telling me to follow the new schedule. I just can't handle change.",
            "I don't like trying new activities. I stick to what I know because trying new things makes me uncomfortable. If something changes, I usually just give up.",
            "We had to switch to a different classroom and it completely threw me off. I couldn't focus all day because everything felt wrong. I need things to stay the same.",
        ],
    },
    "problem_solving": {
        "positive": [
            "I couldn't solve the math problem the usual way, so I tried drawing it out. That helped me see it differently and I figured it out! Sometimes you just need a different approach.",
            "When our science experiment wasn't working, I thought about what might be wrong. I checked each step and realized we missed one ingredient. After fixing that, it worked perfectly.",
            "The puzzle was really hard at first. I broke it down into smaller sections and solved each part separately. Then I put it all together. That made it much easier.",
            "We were stuck on the group project, so I suggested we brainstorm different ideas. We wrote down everything we could think of, then picked the best solution. Teamwork and creative thinking really helped.",
        ],
        "negative": [
            "I couldn't figure out the problem so I just gave up. It was too hard and I didn't want to think about it anymore. I left it blank.",
            "When I got stuck on the assignment, I just waited for someone to tell me the answer. I don't really like trying to figure things out on my own.",
            "The instructions didn't make sense to me, so I didn't do it. I didn't ask for help or try a different way. I just decided it was impossible.",
            "Every time something is difficult, I just quit. I don't see the point in struggling with something when it's not working right away.",
        ],
    },
    "self_regulation": {
        "positive": [
            "I was getting really frustrated with my homework, so I took a break, walked around, and came back to it. That helped me calm down and focus better.",
            "During the test, I started to feel anxious. I took some deep breaths and reminded myself that I studied hard. That helped me stay calm and do my best.",
            "I wanted to play games all afternoon, but I knew I had to finish my project first. I did my work and then rewarded myself with game time. It felt good to be responsible.",
            "When my friend said something that made me mad, I didn't yell back. I counted to ten, thought about what I wanted to say, and then responded calmly. It worked out much better.",
        ],
        "negative": [
            "I got so mad during class that I just walked out. I couldn't control my anger and I didn't care about the consequences. The teacher was annoying me.",
            "I can never focus on anything for long. My mind wanders constantly and I give up easily. I just can't make myself pay attention even when I know I should.",
            "I know I should do my homework first, but I always end up playing games or watching videos instead. I can't stop myself even when I try. Then I'm up really late trying to finish.",
            "When I get upset, I usually just explode. I yell, throw things, or storm off. I don't really think about better ways to handle my feelings.",
        ],
    },
    "resilience": {
        "positive": [
            "I failed the first test but I didn't let it stop me. I studied harder, asked the teacher for help, and did much better on the next one. Setbacks are just part of learning.",
            "I didn't make the team this year, which was disappointing. But I practiced more and tried again next season. I learned that persistence pays off.",
            "When my project didn't work out how I planned, I was upset at first. But then I looked at what went wrong, learned from it, and tried a different approach. Failure teaches you things.",
            "I've had a tough year with a lot of challenges, but I keep pushing forward. I ask for help when I need it and remember that hard times don't last forever. I'm getting stronger.",
        ],
        "negative": [
            "I tried once and it didn't work, so I quit. There's no point in trying again if I already failed. I just tell myself I'm not good at it.",
            "When things go wrong, I feel like everything is ruined. I can't see past the problem and I just want to give up on everything. It's too hard to keep going.",
            "After I got a bad grade, I stopped trying in that class. Why bother if I'm just going to fail anyway? I've given up.",
            "Any time something doesn't go my way, I feel like the world is against me. I don't bounce back easily. I just stay upset for a long time and avoid trying again.",
        ],
    },
    "communication": {
        "positive": [
            "During the presentation, I spoke clearly and made sure to explain my ideas step by step. I checked if anyone had questions and tried to make it easy to understand.",
            "When I disagreed with my group member, I explained my perspective calmly and listened to their side too. We talked it through and found a solution we both liked.",
            "I wrote a really detailed email to my teacher explaining what I was confused about. I used specific examples and asked clear questions. They understood exactly what I needed help with.",
            "In class discussion, I raised my hand and shared my thoughts. I spoke loud enough for everyone to hear and organized my ideas before I spoke. Other students said they understood my point really well.",
        ],
        "negative": [
            "I tried to explain my idea but no one understood what I meant. I just kept saying the same thing over and over. I guess I'm just bad at explaining things.",
            "When the teacher asked me a question, I just mumbled something and looked down. I don't like speaking in front of people and I can never find the right words.",
            "I sent a message to my group but I didn't really explain what I meant. They were confused and had to keep asking me questions. I wish I was better at writing clearly.",
            "I interrupt people a lot and don't really listen to what they're saying. I just wait for my turn to talk. Sometimes people get frustrated with me.",
        ],
    },
    "collaboration": {
        "positive": [
            "Our group worked really well together. Everyone had different ideas and we listened to all of them before deciding. We split up the work fairly and helped each other when someone was stuck.",
            "I'm good at working in teams. I do my part, encourage others, and make sure everyone's voice is heard. If there's conflict, I help find compromises.",
            "During the project, I noticed one team member was doing too much. I suggested we redistribute the work so everyone contributed equally. That made it more fair and less stressful.",
            "I really value teamwork. I share my resources, celebrate when my teammates succeed, and understand that we're all working toward the same goal. Together we can do more.",
        ],
        "negative": [
            "I hate group work. I'd rather just do everything myself because other people slow me down. I usually end up doing all the work anyway.",
            "When we work in groups, I just sit there and let others do the work. I don't really contribute ideas or help out. I just wait for it to be over.",
            "I always argue with my teammates because I think my ideas are better. I don't really listen to what they suggest. Usually the group project doesn't go well.",
            "I only work with my friends and ignore everyone else in the group. If someone I don't like suggests something, I automatically disagree with it. I know that's not fair but I don't care.",
        ],
    },
}


async def generate_transcript(
    session: AsyncSession, student_id: str, text: str, index: int
):
    """Generate a transcript for a student with specific text."""
    # Create audio file first
    audio_id = str(uuid.uuid4())
    audio = AudioFile(
        id=audio_id,
        student_id=student_id,
        storage_path=f"audio/student_{student_id[:8]}_recording_{index}.wav",
        duration_seconds=len(text.split())
        * 2,  # Approximate duration based on word count
        source_type="classroom",
        recording_date=str(
            (datetime.now() - timedelta(days=random.randint(1, 30))).date()
        ),
        transcription_status="completed",
    )
    session.add(audio)
    await session.flush()

    # Create transcript
    transcript = Transcript(
        id=str(uuid.uuid4()),
        audio_file_id=audio_id,
        student_id=student_id,
        text=text,
        word_count=len(text.split()),
        confidence_score=random.uniform(0.90, 0.99),
        language_code="en-US",
    )
    session.add(transcript)
    return transcript


async def add_transcript_evidence():
    """Add comprehensive transcript evidence for all skills."""
    print("🎯 Adding transcript evidence for all skills...")
    print("=" * 70)

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

            if not all_students:
                print("❌ No students found in database!")
                return

            print(f"\n📊 Found {len(all_students)} students")
            print(
                f"📝 Will add {sum(len(v['positive']) + len(v['negative']) for v in SKILL_TRANSCRIPTS.values())} transcript types per student"
            )
            print(
                f"📈 Total transcripts to create: {len(all_students) * sum(len(v['positive']) + len(v['negative']) for v in SKILL_TRANSCRIPTS.values())}"
            )
            print("\n" + "=" * 70)

            transcript_count = 0

            for student in all_students:
                print(
                    f"\n👤 Processing student: {student.first_name} {student.last_name} ({student.id[:8]}...)"
                )
                student_transcripts = 0

                # Add transcripts for each skill
                for skill_name, examples in SKILL_TRANSCRIPTS.items():
                    # Add 2 positive examples
                    for i, text in enumerate(
                        random.sample(
                            examples["positive"], min(2, len(examples["positive"]))
                        )
                    ):
                        await generate_transcript(
                            session, student.id, text, transcript_count
                        )
                        transcript_count += 1
                        student_transcripts += 1

                    # Add 2 negative examples
                    for i, text in enumerate(
                        random.sample(
                            examples["negative"], min(2, len(examples["negative"]))
                        )
                    ):
                        await generate_transcript(
                            session, student.id, text, transcript_count
                        )
                        transcript_count += 1
                        student_transcripts += 1

                print(f"   ✅ Added {student_transcripts} transcripts for this student")

            # Commit all changes
            await session.commit()

            print("\n" + "=" * 70)
            print(f"✅ Transcript evidence generation completed!")
            print("=" * 70)
            print(f"\n📊 Summary:")
            print(f"  • Students processed: {len(all_students)}")
            print(f"  • Total transcripts created: {transcript_count}")
            print(f"  • Skills covered: {len(SKILL_TRANSCRIPTS)}")
            print(
                f"  • Transcripts per student: ~{transcript_count // len(all_students)}"
            )
            print(f"\n🎯 Evidence includes:")
            for skill in SKILL_TRANSCRIPTS.keys():
                print(f"  • {skill.upper()}: Positive & Negative examples")
            print(f"\n🚀 Next steps:")
            print(f"  1. Extract features: python scripts/extract_all_features.py")
            print(
                f"  2. View dashboard: streamlit run backend/dashboard/app_template.py"
            )

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_transcript_evidence())
