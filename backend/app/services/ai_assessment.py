"""AI-powered skill assessment service using Claude/OpenAI."""

import logging
import os
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.models.assessment import SkillType, SkillAssessment, Evidence, EvidenceType
from app.models.features import LinguisticFeatures, BehavioralFeatures
from app.models.student import Student

logger = logging.getLogger(__name__)


class SkillAssessmentService:
    """Service for generating AI-powered skill assessments."""

    def __init__(self, api_key: Optional[str] = None, provider: str = "openai"):
        """
        Initialize the skill assessment service.

        Args:
            api_key: API key for AI provider (defaults to environment variable)
            provider: AI provider to use ("openai" or "anthropic")
        """
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            logger.warning(
                f"No API key found for {self.provider}. "
                f"Set OPENAI_API_KEY environment variable."
            )

        logger.info(
            f"Initialized SkillAssessmentService with provider: {self.provider}"
        )

    def _get_prompt_template(self, skill_type: SkillType) -> Dict[str, str]:
        """
        Get the prompt template for a specific skill type.

        Args:
            skill_type: The skill to assess

        Returns:
            Dictionary with prompt template and skill info
        """
        base_instructions = """You are an educational psychologist \
specializing in assessing non-academic skills in students.

INSTRUCTIONS:
1. Analyze the provided data to assess the student's skill
2. Assign a score from 0.0 to 1.0 (where 0 = no evidence, 1 = exceptional)
3. Provide a confidence score (0.0 to 1.0) indicating your certainty
4. Explain your reasoning with specific evidence from the data
5. Provide 2-3 actionable recommendations for improvement

Respond in the following JSON format:
{
    "score": 0.0,
    "confidence": 0.0,
    "reasoning": "Detailed explanation with evidence",
    "evidence_quotes": ["quote 1", "quote 2", "quote 3"],
    "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
}
"""

        skill_definitions = {
            SkillType.EMPATHY: {
                "name": "Empathy",
                "definition": """Empathy is the ability to understand and \
share the feelings of others.
It involves:
- Recognizing emotions in others
- Perspective-taking
- Expressing concern and care
- Responding appropriately to others' needs""",
                "criteria": """HIGH (0.7-1.0):
- Frequent use of empathy markers ("understand", "feel", "care")
- Demonstrates perspective-taking in language
- Shows awareness of others' emotions
- Offers help or support to peers

MEDIUM (0.4-0.7):
- Some empathy markers present
- Occasional perspective-taking
- Basic awareness of others' feelings

DEVELOPING (0.0-0.4):
- Few or no empathy markers
- Limited perspective-taking
- Self-focused language""",
            },
            SkillType.PROBLEM_SOLVING: {
                "name": "Problem-Solving",
                "definition": """Problem-solving is the ability to analyze \
challenges and develop effective solutions.
It involves:
- Identifying problems
- Analyzing situations
- Generating solutions
- Testing and adapting strategies""",
                "criteria": """HIGH (0.7-1.0):
- Frequent problem-solving language ("solve", "analyze", "figure out")
- Demonstrates systematic approach
- Shows persistence in face of challenges
- Tests multiple strategies

MEDIUM (0.4-0.7):
- Some problem-solving language
- Basic analytical thinking
- Occasional strategy changes

DEVELOPING (0.0-0.4):
- Limited problem-solving language
- Random trial-and-error
- Quick to give up""",
            },
            SkillType.SELF_REGULATION: {
                "name": "Self-Regulation",
                "definition": """Self-regulation is the ability to manage \
emotions, thoughts, and behaviors.
It involves:
- Impulse control
- Emotional regulation
- Focus and attention
- Goal-directed behavior""",
                "criteria": """HIGH (0.7-1.0):
- High distraction resistance in behavioral data
- Long focus durations
- Evidence of pause-and-think strategies
- Manages frustration constructively

MEDIUM (0.4-0.7):
- Moderate focus and attention
- Some impulse control
- Occasional emotional regulation

DEVELOPING (0.0-0.4):
- Frequent distractions
- Impulsive behaviors
- Difficulty managing emotions""",
            },
            SkillType.RESILIENCE: {
                "name": "Resilience",
                "definition": """Resilience is the ability to recover from \
setbacks and persist through challenges.
It involves:
- Persistence after failure
- Learning from mistakes
- Maintaining effort
- Positive coping strategies""",
                "criteria": """HIGH (0.7-1.0):
- High retry count and recovery rate
- Perseverance language ("keep trying", "don't give up")
- Learns from failures
- Maintains positive attitude

MEDIUM (0.4-0.7):
- Some persistence
- Occasional recovery after failure
- Mixed attitude toward challenges

DEVELOPING (0.0-0.4):
- Quick to give up
- Negative response to failure
- Limited persistence""",
            },
            SkillType.ADAPTABILITY: {
                "name": "Adaptability",
                "definition": """Adaptability is the ability to adjust to new \
conditions and handle change effectively.
It involves:
- Flexibility in thinking
- Openness to new approaches
- Adjusting strategies when needed
- Handling unexpected situations""",
                "criteria": """HIGH (0.7-1.0):
- Readily adjusts approach when needed
- Uses flexibility language ("try different", "change", "adapt")
- Comfortable with new situations
- Quick to pivot strategies

MEDIUM (0.4-0.7):
- Some flexibility in approach
- Occasional strategy changes
- Moderate comfort with change

DEVELOPING (0.0-0.4):
- Rigid thinking patterns
- Resistance to change
- Difficulty adjusting to new situations""",
            },
            SkillType.COMMUNICATION: {
                "name": "Communication",
                "definition": """Communication is the ability to express ideas \
clearly and listen effectively.
It involves:
- Clear expression of thoughts
- Active listening
- Asking clarifying questions
- Appropriate verbal and non-verbal cues""",
                "criteria": """HIGH (0.7-1.0):
- Clear, well-structured expression
- Active listening indicators
- Asks thoughtful questions
- Uses communication markers ("explain", "describe", "clarify")

MEDIUM (0.4-0.7):
- Generally clear expression
- Some listening behaviors
- Occasional questions for clarity

DEVELOPING (0.0-0.4):
- Unclear or incomplete expression
- Limited listening indicators
- Rarely asks questions""",
            },
            SkillType.COLLABORATION: {
                "name": "Collaboration",
                "definition": """Collaboration is the ability to work effectively \
with others toward shared goals.
It involves:
- Teamwork and cooperation
- Sharing ideas and resources
- Supporting peers
- Contributing to group success""",
                "criteria": """HIGH (0.7-1.0):
- Strong teamwork indicators
- Uses collaboration language ("together", "we", "team", "help")
- Actively supports peers
- Contributes fairly to group work

MEDIUM (0.4-0.7):
- Some teamwork behaviors
- Occasional peer support
- Participates in group activities

DEVELOPING (0.0-0.4):
- Limited teamwork indicators
- Prefers working alone
- Minimal peer interaction""",
            },
        }

        if skill_type not in skill_definitions:
            raise ValueError(f"No prompt template for skill type: {skill_type}")

        skill_info = skill_definitions[skill_type]
        return {
            "instructions": base_instructions,
            "skill_name": skill_info["name"],
            "definition": skill_info["definition"],
            "criteria": skill_info["criteria"],
        }

    def _format_linguistic_features(self, features: LinguisticFeatures) -> str:
        """Format linguistic features for prompt."""
        if not features or not features.features_json:
            return "No linguistic features available."

        f = features.features_json
        return f"""
- Empathy markers: {f.get('empathy_markers', 0)}
- Problem-solving language: {f.get('problem_solving_language', 0)}
- Perseverance indicators: {f.get('perseverance_indicators', 0)}
- Social processes: {f.get('social_processes', 0)}
- Cognitive processes: {f.get('cognitive_processes', 0)}
- Positive sentiment: {f.get('positive_sentiment', 0):.2f}
- Negative sentiment: {f.get('negative_sentiment', 0):.2f}
- Word count: {f.get('word_count', 0)}
- Unique words: {f.get('unique_word_count', 0)}
- Average sentence length: {f.get('avg_sentence_length', 0):.1f}
- Readability score: {f.get('readability_score', 0):.1f}
"""

    def _format_behavioral_features(self, features: BehavioralFeatures) -> str:
        """Format behavioral features for prompt."""
        if not features or not features.features_json:
            return "No behavioral features available."

        f = features.features_json
        return f"""
- Task completion rate: {f.get('task_completion_rate', 0):.2f}
- Time efficiency: {f.get('time_efficiency', 0):.2f}
- Retry count: {f.get('retry_count', 0)}
- Recovery rate: {f.get('recovery_rate', 0):.2f}
- Distraction resistance: {f.get('distraction_resistance', 1.0):.2f}
- Focus duration: {f.get('focus_duration', 0):.1f} seconds
- Collaboration indicators: {f.get('collaboration_indicators', 0)}
- Leadership indicators: {f.get('leadership_indicators', 0)}
- Total events: {f.get('event_count', 0)}
"""

    async def _call_ai_api(self, prompt: str) -> Dict[str, Any]:
        """
        Call AI API to generate assessment.

        Args:
            prompt: The complete prompt

        Returns:
            Parsed JSON response from AI

        Raises:
            Exception: If API call fails
        """
        try:
            if self.provider == "openai":
                import openai

                # Use the async client
                client = openai.AsyncOpenAI(api_key=self.api_key)

                response = await client.chat.completions.create(
                    model="gpt-4o-mini",  # Fast and cost-effective
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an educational psychologist "
                                "specializing in skill assessment. "
                                "Always respond with valid JSON."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                    response_format={"type": "json_object"},
                )

                content = response.choices[0].message.content
                logger.debug(f"OpenAI response: {content}")

                return json.loads(content)

            else:
                raise ValueError(f"Unsupported AI provider: {self.provider}")

        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            raise

    async def assess_skill(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
        use_cached: bool = True,
    ) -> SkillAssessment:
        """
        Generate a skill assessment for a student.

        Args:
            session: Database session
            student_id: ID of the student
            skill_type: Skill to assess
            use_cached: If True, return recent assessment if exists

        Returns:
            SkillAssessment object

        Raises:
            ValueError: If student not found or insufficient data
        """
        logger.info(f"Assessing {skill_type.value} for student {student_id}")

        # Check if recent assessment exists (within last 7 days)
        if use_cached:
            from datetime import datetime, timedelta
            from sqlalchemy.orm import selectinload

            cutoff = datetime.utcnow() - timedelta(days=7)
            result = await session.execute(
                select(SkillAssessment)
                .options(selectinload(SkillAssessment.evidence))
                .where(
                    SkillAssessment.student_id == student_id,
                    SkillAssessment.skill_type == skill_type,
                    SkillAssessment.created_at >= cutoff,
                )
                .order_by(SkillAssessment.created_at.desc())
                .limit(1)
            )
            cached_assessment = result.scalar_one_or_none()

            if cached_assessment:
                logger.info(
                    f"Using cached assessment from {cached_assessment.created_at}"
                )
                return cached_assessment

        # Fetch student
        result = await session.execute(select(Student).where(Student.id == student_id))
        student = result.scalar_one_or_none()

        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Fetch linguistic features (aggregate from all transcripts)
        result = await session.execute(
            select(LinguisticFeatures)
            .where(LinguisticFeatures.student_id == student_id)
            .order_by(LinguisticFeatures.created_at.desc())
            .limit(5)  # Use up to 5 most recent transcripts
        )
        linguistic_features_list = result.scalars().all()

        # Fetch behavioral features (aggregate from all sessions)
        result = await session.execute(
            select(BehavioralFeatures)
            .where(BehavioralFeatures.student_id == student_id)
            .order_by(BehavioralFeatures.created_at.desc())
            .limit(5)  # Use up to 5 most recent sessions
        )
        behavioral_features_list = result.scalars().all()

        if not linguistic_features_list and not behavioral_features_list:
            raise ValueError(
                f"Insufficient data for student {student_id}. "
                "Need at least one transcript or game session with extracted features."
            )

        # Format student data
        student_data = f"""
Grade Level: {student.grade_level}
Age: {student.age if hasattr(student, 'age') else 'Unknown'}
Number of transcripts analyzed: {len(linguistic_features_list)}
Number of game sessions analyzed: {len(behavioral_features_list)}
"""

        # Aggregate linguistic features (use most recent)
        linguistic_summary = (
            self._format_linguistic_features(linguistic_features_list[0])
            if linguistic_features_list
            else "No linguistic data available."
        )

        # Aggregate behavioral features (use most recent)
        behavioral_summary = (
            self._format_behavioral_features(behavioral_features_list[0])
            if behavioral_features_list
            else "No behavioral data available."
        )

        # Build prompt
        prompt_info = self._get_prompt_template(skill_type)

        prompt = f"""{prompt_info['instructions']}

SKILL TO ASSESS: {prompt_info['skill_name']}

SKILL DEFINITION:
{prompt_info['definition']}

ASSESSMENT CRITERIA:
{prompt_info['criteria']}

STUDENT DATA:
{student_data}

LINGUISTIC FEATURES:
{linguistic_summary}

BEHAVIORAL FEATURES:
{behavioral_summary}

Please provide your assessment in the JSON format specified above.
"""

        logger.debug(f"Generated prompt ({len(prompt)} chars)")

        # Call AI
        try:
            ai_response = await self._call_ai_api(prompt)
        except Exception as e:
            logger.error(f"AI assessment failed: {e}")
            raise ValueError(f"AI assessment failed: {str(e)}")

        # Parse response
        score = float(ai_response.get("score", 0.5))
        confidence = float(ai_response.get("confidence", 0.5))
        reasoning = ai_response.get("reasoning", "No reasoning provided")
        evidence_quotes = ai_response.get("evidence_quotes", [])
        recommendations = ai_response.get("recommendations", [])

        # Validate scores
        score = max(0.0, min(1.0, score))
        confidence = max(0.0, min(1.0, confidence))

        # Create assessment
        assessment = SkillAssessment(
            id=str(uuid.uuid4()),
            student_id=student_id,
            skill_type=skill_type,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            recommendations="\n".join(recommendations) if recommendations else None,
            feature_importance=json.dumps(
                {
                    "linguistic_count": len(linguistic_features_list),
                    "behavioral_count": len(behavioral_features_list),
                }
            ),
        )

        session.add(assessment)

        # Create evidence entries
        for quote in evidence_quotes[:3]:  # Limit to 3 pieces of evidence
            evidence = Evidence(
                id=str(uuid.uuid4()),
                assessment_id=assessment.id,
                evidence_type=EvidenceType.LINGUISTIC,  # Simplified for now
                source="transcript_analysis",
                content=quote,
                relevance_score=0.8,  # Could be calculated from AI
            )
            session.add(evidence)

        await session.commit()
        await session.refresh(assessment)

        # Eagerly load evidence to avoid lazy loading issues
        from sqlalchemy.orm import selectinload

        result = await session.execute(
            select(SkillAssessment)
            .options(selectinload(SkillAssessment.evidence))
            .where(SkillAssessment.id == assessment.id)
        )
        assessment = result.scalar_one()

        logger.info(
            f"Created assessment {assessment.id}: "
            f"{skill_type.value}={score:.2f} (confidence={confidence:.2f})"
        )

        return assessment

    async def assess_all_skills(
        self, session: AsyncSession, student_id: str, use_cached: bool = True
    ) -> List[SkillAssessment]:
        """
        Generate assessments for all four primary skills.

        Args:
            session: Database session
            student_id: ID of the student
            use_cached: If True, use cached assessments where available

        Returns:
            List of SkillAssessment objects
        """
        primary_skills = [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]

        assessments = []
        for skill in primary_skills:
            try:
                assessment = await self.assess_skill(
                    session, student_id, skill, use_cached
                )
                assessments.append(assessment)
            except Exception as e:
                logger.error(f"Failed to assess {skill.value}: {e}")
                # Continue with other skills

        return assessments
