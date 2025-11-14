"""Service for extracting and managing assessment evidence."""

import logging
import uuid
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import json

from app.models.assessment import SkillAssessment, Evidence, EvidenceType, SkillType
from app.models.transcript import Transcript
from app.models.game_telemetry import GameSession
from app.models.features import LinguisticFeatures, BehavioralFeatures

logger = logging.getLogger(__name__)


class EvidenceService:
    """Service for extracting evidence to support skill assessments."""

    async def create_assessment_with_evidence(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
        score: float,
        confidence: float,
        feature_importance: Dict[str, float],
    ) -> SkillAssessment:
        """
        Create a skill assessment with supporting evidence.

        Args:
            session: Database session
            student_id: Student UUID
            skill_type: Type of skill being assessed
            score: Skill score (0-1)
            confidence: Confidence score (0-1)
            feature_importance: Feature importance weights from ML model

        Returns:
            Created SkillAssessment with evidence
        """
        # Generate reasoning based on feature importance
        reasoning = self._generate_reasoning(
            skill_type, score, confidence, feature_importance
        )

        # Create skill assessment
        assessment = SkillAssessment(
            id=str(uuid.uuid4()),
            student_id=student_id,
            skill_type=skill_type,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            feature_importance=json.dumps(feature_importance),
        )
        session.add(assessment)
        await session.flush()  # Get assessment ID

        # Extract and create evidence
        evidence_records = await self._extract_evidence(
            session, student_id, skill_type, feature_importance, assessment.id
        )

        for evidence_record in evidence_records:
            session.add(evidence_record)

        await session.commit()

        # Reload assessment with evidence relationship
        result = await session.execute(
            select(SkillAssessment)
            .options(selectinload(SkillAssessment.evidence))
            .where(SkillAssessment.id == assessment.id)
        )
        assessment = result.scalar_one()

        logger.info(
            f"Created assessment for student {student_id[:8]}..., "
            f"skill {skill_type.value} with {len(evidence_records)} evidence records"
        )

        return assessment

    def _generate_reasoning(
        self,
        skill_type: SkillType,
        score: float,
        confidence: float,
        feature_importance: Dict[str, float],
    ) -> str:
        """
        Generate meaningful reasoning text based on ML predictions and skill-specific features.

        Args:
            skill_type: Type of skill
            score: Skill score (0-1)
            confidence: Confidence in prediction (0-1)
            feature_importance: Feature importance weights

        Returns:
            Reasoning text explaining the assessment
        """
        # Map technical features to human-readable descriptions
        feature_descriptions = {
            # Linguistic features - empathy
            "empathy_markers": "use of empathetic language and emotional vocabulary",
            "social_processes": "references to social interactions and relationships",
            "positive_sentiment": "expression of positive emotions and attitudes",
            "negative_sentiment": "recognition of negative emotions",
            # Linguistic features - problem solving
            "problem_solving_language": "use of analytical and solution-focused language",
            "cognitive_processes": "demonstration of thinking and reasoning",
            "perseverance_indicators": "expressions of persistence and determination",
            # Linguistic features - self regulation
            "focus_duration": "sustained attention and concentration",
            "distraction_resistance": "ability to maintain focus despite challenges",
            # Linguistic features - resilience
            "recovery_rate": "ability to bounce back from setbacks",
            "retry_count": "willingness to attempt challenges multiple times",
            # Behavioral features
            "task_completion_rate": "successful completion of assigned tasks",
            "time_efficiency": "effective use of time in activities",
            "collaboration_indicators": "engagement in cooperative activities",
            "leadership_indicators": "taking initiative and guiding others",
            # Combined features
            "empathy_social_interaction": "empathetic engagement in social contexts",
            "problem_solving_cognitive": "analytical thinking and strategy use",
            "self_regulation_focus": "ability to maintain attention and control",
            "resilience_recovery": "persistence through difficulties",
        }

        # Define skill-specific feature groups to prioritize
        skill_priority_features = {
            SkillType.EMPATHY: [
                "empathy_markers",
                "empathy_social_interaction",
                "social_processes",
                "positive_sentiment",
                "collaboration_indicators",
            ],
            SkillType.ADAPTABILITY: [
                "cognitive_processes",
                "time_efficiency",
                "problem_solving_language",
                "perseverance_indicators",
                "task_completion_rate",
            ],
            SkillType.PROBLEM_SOLVING: [
                "problem_solving_language",
                "problem_solving_cognitive",
                "cognitive_processes",
                "perseverance_indicators",
                "retry_count",
                "task_completion_rate",
            ],
            SkillType.SELF_REGULATION: [
                "self_regulation_focus",
                "focus_duration",
                "distraction_resistance",
                "time_efficiency",
                "task_completion_rate",
            ],
            SkillType.RESILIENCE: [
                "resilience_recovery",
                "recovery_rate",
                "perseverance_indicators",
                "retry_count",
                "negative_sentiment",
            ],
            SkillType.COMMUNICATION: [
                "social_processes",
                "cognitive_processes",
                "word_count",
                "unique_word_count",
                "syntactic_complexity",
                "collaboration_indicators",
            ],
            SkillType.COLLABORATION: [
                "collaboration_indicators",
                "social_processes",
                "empathy_markers",
                "leadership_indicators",
                "task_completion_rate",
            ],
        }

        # Get relevant features for this skill
        priority_features = skill_priority_features.get(skill_type, [])

        # Find top relevant features that actually matter for this skill
        relevant_features = []
        for feature_name in priority_features:
            if feature_name in feature_importance:
                relevant_features.append(
                    (feature_name, feature_importance[feature_name])
                )

        # Sort by importance and take top 2-3
        relevant_features.sort(key=lambda x: x[1], reverse=True)
        top_relevant = relevant_features[:3] if relevant_features else []

        # If no skill-specific features, fall back to top features
        if not top_relevant:
            all_features = sorted(
                feature_importance.items(), key=lambda x: x[1], reverse=True
            )
            top_relevant = [
                (f, v) for f, v in all_features[:2] if f in feature_descriptions
            ]

        # Score interpretation with more nuance
        if score >= 0.75:
            level = "strong"
            performance_desc = "excels at"
        elif score >= 0.60:
            level = "developing well"
            performance_desc = "shows good progress in"
        elif score >= 0.50:
            level = "developing"
            performance_desc = "is building skills in"
        else:
            level = "emerging"
            performance_desc = "is beginning to develop"

        # Build meaningful reasoning
        skill_name = skill_type.value.replace("_", " ")
        reasoning = (
            f"The student {performance_desc} {skill_name} "
            f"(score: {score:.2f}, confidence: {confidence:.2f}). "
        )

        # Add specific observations based on top relevant features
        if top_relevant:
            observations = []
            for feature_name, importance in top_relevant[:2]:
                if feature_name in feature_descriptions:
                    observations.append(feature_descriptions[feature_name])

            if observations:
                reasoning += f"Key strengths include {observations[0]}"
                if len(observations) > 1:
                    reasoning += f" and {observations[1]}"
                reasoning += ". "

        # Add actionable recommendations based on score
        if score >= 0.75:
            reasoning += f"Continue fostering these {skill_name} abilities through varied practice."
        elif score >= 0.60:
            reasoning += f"With continued support, the student can strengthen their {skill_name} skills further."
        elif score >= 0.50:
            reasoning += f"Providing structured opportunities for {skill_name} development would be beneficial."
        else:
            reasoning += (
                f"Consider targeted interventions to support {skill_name} growth."
            )

        return reasoning

    async def _extract_evidence(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
        feature_importance: Dict[str, float],
        assessment_id: str,
    ) -> List[Evidence]:
        """
        Extract evidence from transcripts and game sessions.

        Args:
            session: Database session
            student_id: Student UUID
            skill_type: Type of skill
            feature_importance: Feature importance from ML model
            assessment_id: Assessment ID to link evidence to

        Returns:
            List of Evidence records
        """
        evidence_records = []

        # Extract linguistic evidence from transcripts
        linguistic_evidence = await self._extract_linguistic_evidence(
            session, student_id, skill_type, feature_importance
        )
        for content, relevance in linguistic_evidence:
            evidence_records.append(
                Evidence(
                    id=str(uuid.uuid4()),
                    assessment_id=assessment_id,
                    evidence_type=EvidenceType.LINGUISTIC,
                    source="transcript",
                    content=content,
                    relevance_score=relevance,
                )
            )

        # Extract behavioral evidence from game sessions
        behavioral_evidence = await self._extract_behavioral_evidence(
            session, student_id, skill_type, feature_importance
        )
        for content, relevance in behavioral_evidence:
            evidence_records.append(
                Evidence(
                    id=str(uuid.uuid4()),
                    assessment_id=assessment_id,
                    evidence_type=EvidenceType.BEHAVIORAL,
                    source="game_telemetry",
                    content=content,
                    relevance_score=relevance,
                )
            )

        return evidence_records[:10]  # Top 10 most relevant

    async def _extract_linguistic_evidence(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
        feature_importance: Dict[str, float],
    ) -> List[Tuple[str, float]]:
        """Extract linguistic evidence from transcripts."""
        evidence = []

        # Get transcripts for student
        result = await session.execute(
            select(Transcript)
            .where(Transcript.student_id == student_id)
            .order_by(Transcript.created_at.desc())
            .limit(10)
        )
        transcripts = result.scalars().all()

        # Skill-specific keywords
        skill_keywords = {
            SkillType.EMPATHY: [
                "feel",
                "understand",
                "help",
                "care",
                "friend",
                "support",
                "listen",
                "kind",
            ],
            SkillType.ADAPTABILITY: [
                "change",
                "adjust",
                "flexible",
                "adapt",
                "different",
                "new",
                "switch",
            ],
            SkillType.PROBLEM_SOLVING: [
                "solve",
                "figure",
                "think",
                "try",
                "idea",
                "plan",
                "work",
                "different",
            ],
            SkillType.SELF_REGULATION: [
                "calm",
                "control",
                "wait",
                "patient",
                "focus",
                "manage",
                "practice",
            ],
            SkillType.RESILIENCE: [
                "try again",
                "keep going",
                "persist",
                "challenge",
                "overcome",
                "difficult",
                "hard",
            ],
            SkillType.COMMUNICATION: [
                "explain",
                "tell",
                "say",
                "talk",
                "share",
                "describe",
                "express",
                "ask",
            ],
            SkillType.COLLABORATION: [
                "together",
                "team",
                "group",
                "cooperate",
                "share",
                "help each other",
                "work with",
            ],
        }

        keywords = skill_keywords.get(skill_type, [])

        for transcript in transcripts:
            if not transcript.text:
                continue

            # Calculate relevance based on keyword presence
            text_lower = transcript.text.lower()
            keyword_count = sum(1 for kw in keywords if kw in text_lower)
            relevance = min(keyword_count / len(keywords), 1.0) if keywords else 0.5

            if relevance > 0.15:  # Lower threshold to get more evidence
                evidence.append((transcript.text, relevance))

        # Deduplicate evidence by content (keep highest relevance for duplicates)
        unique_evidence = {}
        for content, relevance in evidence:
            if content not in unique_evidence or relevance > unique_evidence[content]:
                unique_evidence[content] = relevance

        # Convert back to list of tuples
        deduplicated = [
            (content, relevance) for content, relevance in unique_evidence.items()
        ]

        return sorted(deduplicated, key=lambda x: x[1], reverse=True)[:6]

    async def _extract_behavioral_evidence(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
        feature_importance: Dict[str, float],
    ) -> List[Tuple[str, float]]:
        """Extract behavioral evidence from game sessions."""
        evidence = []

        # Get game sessions for student
        result = await session.execute(
            select(GameSession)
            .where(GameSession.student_id == student_id)
            .order_by(GameSession.created_at.desc())
            .limit(10)
        )
        game_sessions = result.scalars().all()

        for game_session in game_sessions:
            # Get behavioral features for relevance
            behavioral_features_result = await session.execute(
                select(BehavioralFeatures)
                .where(BehavioralFeatures.session_id == game_session.id)
                .limit(1)
            )
            behavioral_features = behavioral_features_result.scalar_one_or_none()

            if not behavioral_features:
                continue

            # Generate skill-specific evidence text with meaningful insights
            evidence_items = []
            relevance = 0.5

            # Skill-specific evidence generation
            if skill_type == SkillType.EMPATHY:
                if behavioral_features.collaboration_indicators > 0.3:
                    evidence_items.append(
                        f"demonstrated collaborative behavior ({behavioral_features.collaboration_indicators:.0%})"
                    )
                    relevance += 0.2
                else:
                    evidence_items.append(
                        "showed opportunities for collaborative growth"
                    )
                if behavioral_features.distraction_resistance > 0.7:
                    evidence_items.append(
                        "maintained awareness during peer interactions"
                    )
                    relevance += 0.1

            elif skill_type == SkillType.PROBLEM_SOLVING:
                if behavioral_features.retry_count > 0:
                    evidence_items.append(
                        f"attempted {behavioral_features.retry_count} different approaches to solve challenges"
                    )
                    relevance += 0.2
                else:
                    evidence_items.append(
                        "demonstrated initial problem-solving attempts"
                    )
                if behavioral_features.time_efficiency > 0.5:
                    evidence_items.append(
                        f"worked efficiently ({behavioral_features.time_efficiency:.0%} effectiveness)"
                    )
                    relevance += 0.2
                else:
                    evidence_items.append(
                        "took time to think through problems carefully"
                    )

            elif skill_type == SkillType.SELF_REGULATION:
                if behavioral_features.focus_duration > 5:
                    evidence_items.append(
                        f"maintained focus for {behavioral_features.focus_duration:.0f} minutes"
                    )
                    relevance += 0.2
                else:
                    evidence_items.append("demonstrated attention to task")
                if behavioral_features.distraction_resistance > 0.7:
                    evidence_items.append(
                        f"resisted distractions effectively ({behavioral_features.distraction_resistance:.0%})"
                    )
                    relevance += 0.2
                else:
                    evidence_items.append("showed emerging self-control skills")

            elif skill_type == SkillType.RESILIENCE:
                if behavioral_features.recovery_rate > 0.7:
                    evidence_items.append(
                        f"recovered from setbacks successfully ({behavioral_features.recovery_rate:.0%} recovery rate)"
                    )
                    relevance += 0.3
                else:
                    evidence_items.append("persisted despite challenges")
                if behavioral_features.retry_count > 2:
                    evidence_items.append(
                        f"demonstrated persistence with {behavioral_features.retry_count} attempts"
                    )
                    relevance += 0.2
                else:
                    evidence_items.append("showed willingness to try again")

            elif skill_type == SkillType.ADAPTABILITY:
                if behavioral_features.time_efficiency > 0.6:
                    evidence_items.append(
                        f"adapted strategy efficiently ({behavioral_features.time_efficiency:.0%})"
                    )
                    relevance += 0.2
                else:
                    evidence_items.append("explored different approaches")
                if behavioral_features.retry_count > 0:
                    evidence_items.append(
                        f"tried {behavioral_features.retry_count} alternative methods"
                    )
                    relevance += 0.2

            elif skill_type == SkillType.COLLABORATION:
                if behavioral_features.collaboration_indicators > 0.5:
                    evidence_items.append(
                        f"actively engaged in team activities ({behavioral_features.collaboration_indicators:.0%})"
                    )
                    relevance += 0.3
                else:
                    evidence_items.append("participated in group activities")
                if behavioral_features.leadership_indicators > 0.4:
                    evidence_items.append("took initiative in collaborative settings")
                    relevance += 0.2

            else:  # COMMUNICATION
                if behavioral_features.collaboration_indicators > 0.4:
                    evidence_items.append("communicated effectively with peers")
                    relevance += 0.2
                if behavioral_features.event_count > 10:
                    evidence_items.append(
                        f"engaged actively with {behavioral_features.event_count} interactions"
                    )
                    relevance += 0.1

            # Combine evidence items into readable text
            if evidence_items:
                evidence_text = "During game session: " + ", ".join(evidence_items)
            else:
                evidence_text = (
                    f"Game session provided insights into {skill_type.value} indicators"
                )

            evidence.append((evidence_text, min(relevance, 1.0)))

        # Deduplicate evidence by content (keep highest relevance for duplicates)
        unique_evidence = {}
        for content, relevance in evidence:
            if content not in unique_evidence or relevance > unique_evidence[content]:
                unique_evidence[content] = relevance

        # Convert back to list of tuples
        deduplicated = [
            (content, relevance) for content, relevance in unique_evidence.items()
        ]

        return sorted(deduplicated, key=lambda x: x[1], reverse=True)[:4]
