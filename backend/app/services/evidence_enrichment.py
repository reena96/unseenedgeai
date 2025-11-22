"""Service for enriching assessment evidence with transcripts and telemetry data."""

import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.models.assessment import SkillAssessment, Evidence, EvidenceType, SkillType
from app.models.transcript import Transcript
from app.models.game_telemetry import GameTelemetry, GameSession
from app.models.audio import AudioFile

logger = logging.getLogger(__name__)


class EvidenceEnrichmentService:
    """Service for enriching assessments with detailed transcript and telemetry evidence."""

    async def enrich_assessment_evidence(
        self,
        session: AsyncSession,
        assessment: SkillAssessment,
    ) -> Dict[str, Any]:
        """
        Enrich an assessment with detailed evidence from transcripts and telemetry.

        Args:
            session: Database session
            assessment: The skill assessment to enrich

        Returns:
            Dictionary with enriched evidence including transcripts and telemetry
        """
        student_id = assessment.student_id
        skill_type = assessment.skill_type

        # Get transcript evidence
        transcript_evidence = await self._get_transcript_evidence(
            session, student_id, skill_type
        )

        # Get telemetry evidence
        telemetry_evidence = await self._get_telemetry_evidence(
            session, student_id, skill_type
        )

        # Combine with existing evidence
        existing_evidence = [
            {
                "id": e.id,
                "type": e.evidence_type.value,
                "source": e.source,
                "content": e.content,
                "relevance_score": e.relevance_score,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in assessment.evidence
        ]

        return {
            "assessment_id": assessment.id,
            "student_id": student_id,
            "skill_type": skill_type.value,
            "score": assessment.score,
            "confidence": assessment.confidence,
            "reasoning": assessment.reasoning,
            "recommendations": assessment.recommendations,
            "existing_evidence": existing_evidence,
            "transcript_evidence": transcript_evidence,
            "telemetry_evidence": telemetry_evidence,
            "evidence_summary": self._create_evidence_summary(
                transcript_evidence, telemetry_evidence
            ),
        }

    async def _get_transcript_evidence(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
    ) -> List[Dict[str, Any]]:
        """
        Get transcript excerpts relevant to the skill being assessed.

        Args:
            session: Database session
            student_id: Student ID
            skill_type: Skill type being assessed

        Returns:
            List of transcript evidence dictionaries
        """
        # Get recent transcripts (last 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        result = await session.execute(
            select(Transcript, AudioFile)
            .join(AudioFile, Transcript.audio_file_id == AudioFile.id)
            .where(
                Transcript.student_id == student_id,
                Transcript.created_at >= cutoff_date,
            )
            .order_by(Transcript.created_at.desc())
            .limit(10)
        )

        transcript_pairs = result.all()

        evidence_list = []
        for transcript, audio_file in transcript_pairs:
            # Extract relevant excerpts based on skill type
            excerpts = self._extract_skill_relevant_excerpts(
                transcript.text, skill_type, transcript.word_data
            )

            for excerpt in excerpts:
                evidence_list.append({
                    "type": "transcript",
                    "transcript_id": transcript.id,
                    "audio_file_id": audio_file.id,
                    "file_name": audio_file.file_name,
                    "recorded_at": audio_file.recorded_at.isoformat() if audio_file.recorded_at else None,
                    "excerpt": excerpt["text"],
                    "word_count": excerpt["word_count"],
                    "confidence_score": transcript.confidence_score,
                    "timestamp": excerpt.get("timestamp"),
                    "relevance_indicators": excerpt.get("indicators", []),
                    "created_at": transcript.created_at.isoformat() if transcript.created_at else None,
                })

        return evidence_list

    async def _get_telemetry_evidence(
        self,
        session: AsyncSession,
        student_id: str,
        skill_type: SkillType,
    ) -> List[Dict[str, Any]]:
        """
        Get telemetry data points relevant to the skill being assessed.

        Args:
            session: Database session
            student_id: Student ID
            skill_type: Skill type being assessed

        Returns:
            List of telemetry evidence dictionaries
        """
        # Get recent game sessions (last 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        result = await session.execute(
            select(GameSession)
            .where(
                GameSession.student_id == student_id,
                GameSession.started_at >= cutoff_date,
            )
            .order_by(GameSession.started_at.desc())
            .limit(10)
        )

        sessions = result.scalars().all()

        evidence_list = []
        for game_session in sessions:
            # Get relevant telemetry events for this session
            telemetry_events = await self._get_skill_relevant_telemetry(
                session, game_session.id, skill_type
            )

            if telemetry_events:
                # Calculate session metrics
                session_metrics = self._calculate_session_metrics(telemetry_events)

                evidence_list.append({
                    "type": "telemetry_session",
                    "session_id": game_session.id,
                    "mission_id": game_session.mission_id,
                    "started_at": game_session.started_at.isoformat() if game_session.started_at else None,
                    "ended_at": game_session.ended_at.isoformat() if game_session.ended_at else None,
                    "duration_seconds": (
                        (game_session.ended_at - game_session.started_at).total_seconds()
                        if game_session.ended_at else None
                    ),
                    "event_count": len(telemetry_events),
                    "metrics": session_metrics,
                    "key_events": telemetry_events[:5],  # Top 5 most relevant events
                })

        return evidence_list

    async def _get_skill_relevant_telemetry(
        self,
        session: AsyncSession,
        session_id: str,
        skill_type: SkillType,
    ) -> List[Dict[str, Any]]:
        """
        Get telemetry events relevant to a specific skill type.

        Args:
            session: Database session
            session_id: Game session ID
            skill_type: Skill type

        Returns:
            List of relevant telemetry events
        """
        # Define relevant event types for each skill
        skill_event_types = {
            SkillType.EMPATHY: ["npc_interaction", "dialogue_choice", "help_action", "character_emotion_response"],
            SkillType.PROBLEM_SOLVING: ["puzzle_start", "puzzle_complete", "hint_used", "strategy_change", "solution_attempt"],
            SkillType.SELF_REGULATION: ["pause_action", "distraction_event", "focus_maintained", "emotion_regulation"],
            SkillType.RESILIENCE: ["failure_event", "retry_action", "mission_restart", "challenge_overcome"],
            SkillType.COMMUNICATION: ["dialogue_choice", "team_message", "voice_interaction"],
            SkillType.COLLABORATION: ["team_action", "help_peer", "share_resource", "joint_task"],
            SkillType.ADAPTABILITY: ["strategy_change", "environment_change_response", "new_task_approach"],
        }

        relevant_event_types = skill_event_types.get(skill_type, [])

        result = await session.execute(
            select(GameTelemetry)
            .where(
                GameTelemetry.session_id == session_id,
                GameTelemetry.event_type.in_(relevant_event_types) if relevant_event_types else True,
            )
            .order_by(GameTelemetry.timestamp.desc())
            .limit(20)
        )

        events = result.scalars().all()

        return [
            {
                "event_id": event.id,
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat() if event.timestamp else None,
                "data": event.event_data,
                "mission_id": event.mission_id,
                "choice_made": event.choice_made,
            }
            for event in events
        ]

    def _extract_skill_relevant_excerpts(
        self,
        full_text: str,
        skill_type: SkillType,
        word_data: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract excerpts from transcript that are relevant to the skill type.

        Args:
            full_text: Full transcript text
            skill_type: Skill type
            word_data: Optional word-level data with timestamps

        Returns:
            List of relevant excerpts
        """
        # Define skill-specific keywords and patterns
        skill_keywords = {
            SkillType.EMPATHY: ["feel", "understand", "care", "help", "sorry", "sad", "happy", "emotion"],
            SkillType.PROBLEM_SOLVING: ["solve", "figure", "think", "plan", "strategy", "try", "solution"],
            SkillType.SELF_REGULATION: ["calm", "wait", "focus", "control", "manage", "pause"],
            SkillType.RESILIENCE: ["try again", "keep going", "don't give up", "persist", "overcome"],
            SkillType.COMMUNICATION: ["say", "tell", "explain", "talk", "listen", "message"],
            SkillType.COLLABORATION: ["together", "team", "help", "share", "cooperate", "we"],
            SkillType.ADAPTABILITY: ["change", "different", "new way", "adapt", "flexible"],
        }

        keywords = skill_keywords.get(skill_type, [])

        # Split into sentences
        sentences = [s.strip() + "." for s in full_text.split(".") if s.strip()]

        excerpts = []
        for sentence in sentences:
            sentence_lower = sentence.lower()

            # Check if sentence contains skill-relevant keywords
            matching_keywords = [kw for kw in keywords if kw in sentence_lower]

            if matching_keywords:
                excerpts.append({
                    "text": sentence,
                    "word_count": len(sentence.split()),
                    "indicators": matching_keywords,
                    "timestamp": None,  # Could be extracted from word_data if available
                })

        # Return top 5 most relevant excerpts
        return sorted(excerpts, key=lambda x: len(x["indicators"]), reverse=True)[:5]

    def _calculate_session_metrics(
        self, telemetry_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate aggregate metrics from telemetry events.

        Args:
            telemetry_events: List of telemetry events

        Returns:
            Dictionary of calculated metrics
        """
        if not telemetry_events:
            return {}

        # Count event types
        event_type_counts = {}
        for event in telemetry_events:
            event_type = event["event_type"]
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

        # Calculate time-based metrics
        timestamps = [
            datetime.fromisoformat(event["timestamp"])
            for event in telemetry_events
            if event.get("timestamp")
        ]

        duration = None
        if len(timestamps) >= 2:
            duration = (max(timestamps) - min(timestamps)).total_seconds()

        return {
            "total_events": len(telemetry_events),
            "event_types": event_type_counts,
            "duration_seconds": duration,
            "events_per_minute": (
                (len(telemetry_events) / duration) * 60 if duration and duration > 0 else None
            ),
        }

    def _create_evidence_summary(
        self,
        transcript_evidence: List[Dict[str, Any]],
        telemetry_evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create a summary of all evidence sources.

        Args:
            transcript_evidence: List of transcript evidence
            telemetry_evidence: List of telemetry evidence

        Returns:
            Summary dictionary
        """
        return {
            "transcript_count": len(transcript_evidence),
            "telemetry_session_count": len(telemetry_evidence),
            "total_evidence_points": len(transcript_evidence) + sum(
                e.get("event_count", 0) for e in telemetry_evidence
            ),
            "date_range": self._get_evidence_date_range(
                transcript_evidence, telemetry_evidence
            ),
        }

    def _get_evidence_date_range(
        self,
        transcript_evidence: List[Dict[str, Any]],
        telemetry_evidence: List[Dict[str, Any]],
    ) -> Dict[str, Optional[str]]:
        """Get the date range of all evidence."""
        all_dates = []

        for t in transcript_evidence:
            if t.get("created_at"):
                all_dates.append(datetime.fromisoformat(t["created_at"]))

        for t in telemetry_evidence:
            if t.get("started_at"):
                all_dates.append(datetime.fromisoformat(t["started_at"]))

        if not all_dates:
            return {"earliest": None, "latest": None}

        return {
            "earliest": min(all_dates).isoformat(),
            "latest": max(all_dates).isoformat(),
        }
