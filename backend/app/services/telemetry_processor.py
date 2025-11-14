"""Telemetry processing service for game events."""

import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.game_telemetry import GameSession, GameTelemetry
from app.models.features import BehavioralFeatures
from app.core.metrics import (
    telemetry_events_total,
    telemetry_processing_time,
    telemetry_batch_size,
    telemetry_duplicates_total,
)

logger = logging.getLogger(__name__)


class TelemetryProcessor:
    """Process and store game telemetry events."""

    def __init__(self, db: AsyncSession):
        """
        Initialize telemetry processor.

        Args:
            db: Database session
        """
        self.db = db

    async def process_event(
        self,
        student_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        session_id: str,
        mission_id: str = None,
        timestamp: datetime = None,
        event_id: str = None,
    ) -> GameTelemetry:
        """
        Process and store a single telemetry event.

        Args:
            student_id: Student identifier
            event_type: Type of event
            event_data: Event-specific data
            session_id: Game session identifier
            mission_id: Mission identifier (optional)
            timestamp: Event timestamp (defaults to now)
            event_id: Event identifier for deduplication (optional)

        Returns:
            Stored GameTelemetry instance
        """
        start_time = time.time()

        try:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)

            # Check for duplicate event_id (deduplication)
            if event_id:
                stmt = select(GameTelemetry).where(GameTelemetry.id == event_id)
                result = await self.db.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    logger.info(f"Duplicate event {event_id} ignored (idempotent)")
                    telemetry_duplicates_total.inc()
                    return existing  # Return existing, don't create duplicate

            # Create telemetry event
            telemetry = GameTelemetry(
                id=event_id,  # Use provided event_id if available
                timestamp=timestamp,
                student_id=student_id,
                session_id=session_id,
                event_type=event_type,
                event_data=event_data,
                mission_id=mission_id,
                choice_made=(
                    event_data.get("choice") if event_type == "choice_made" else None
                ),
            )

            self.db.add(telemetry)
            await self.db.flush()

            logger.info(
                f"Processed telemetry event: {event_type} for student {student_id}"
            )

            # Record metrics
            telemetry_events_total.labels(event_type=event_type, status="success").inc()
            telemetry_processing_time.observe(time.time() - start_time)

            return telemetry
        except Exception as e:
            # Record failure metric
            telemetry_events_total.labels(event_type=event_type, status="failure").inc()
            raise

    async def process_batch(
        self,
        events: List[Dict[str, Any]],
        batch_id: str,
    ) -> List[GameTelemetry]:
        """
        Process a batch of telemetry events.

        Args:
            events: List of event dictionaries
            batch_id: Batch identifier

        Returns:
            List of stored GameTelemetry instances
        """
        # Record batch size metric
        telemetry_batch_size.observe(len(events))

        telemetry_events = []

        for event in events:
            try:
                telemetry = await self.process_event(
                    student_id=event.get("student_id"),
                    event_type=event.get("event_type"),
                    event_data=event.get("data", {}),
                    session_id=event.get("session_id"),
                    mission_id=event.get("mission_id"),
                    timestamp=event.get("timestamp"),
                    event_id=event.get("event_id"),  # Add event_id for deduplication
                )
                telemetry_events.append(telemetry)
            except Exception as e:
                logger.error(f"Failed to process event in batch {batch_id}: {e}")
                # Continue processing other events
                continue

        await self.db.commit()

        logger.info(
            f"Processed batch {batch_id}: {len(telemetry_events)}/{len(events)} events stored"
        )

        return telemetry_events

    async def get_or_create_session(
        self,
        student_id: str,
        session_id: str,
        mission_id: str = None,
        game_version: str = "1.0.0",
    ) -> GameSession:
        """
        Get existing session or create new one.

        Args:
            student_id: Student identifier
            session_id: Session identifier
            mission_id: Mission identifier (optional)
            game_version: Game version string

        Returns:
            GameSession instance
        """
        # Try to get existing session
        stmt = select(GameSession).where(GameSession.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if session is None:
            # Create new session
            session = GameSession(
                id=session_id,
                student_id=student_id,
                started_at=datetime.now(timezone.utc),
                mission_id=mission_id,
                game_version=game_version,
            )
            self.db.add(session)
            await self.db.flush()
            logger.info(
                f"Created new game session {session_id} for student {student_id}"
            )

        return session

    async def close_session(self, session_id: str) -> GameSession:
        """
        Close a game session and trigger behavioral feature extraction.

        Args:
            session_id: Session identifier

        Returns:
            Updated GameSession instance
        """
        stmt = select(GameSession).where(GameSession.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if session is None:
            raise ValueError(f"Session {session_id} not found")

        session.ended_at = datetime.now(timezone.utc)
        await self.db.flush()

        # Extract behavioral features from session
        try:
            features = await self.extract_behavioral_features(session_id)
            logger.info(
                f"Extracted behavioral features for session {session_id}: {features.id}"
            )
        except Exception as e:
            logger.error(
                f"Failed to extract behavioral features for session {session_id}: {e}"
            )

        await self.db.commit()

        return session

    async def extract_behavioral_features(self, session_id: str) -> BehavioralFeatures:
        """
        Extract behavioral features from a completed game session.

        Args:
            session_id: Session identifier

        Returns:
            BehavioralFeatures instance
        """
        # Get session
        stmt = select(GameSession).where(GameSession.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if session is None:
            raise ValueError(f"Session {session_id} not found")

        # Get all telemetry events for this session
        stmt = (
            select(GameTelemetry)
            .where(GameTelemetry.session_id == session_id)
            .order_by(GameTelemetry.timestamp)
        )
        result = await self.db.execute(stmt)
        events = result.scalars().all()

        if not events:
            logger.warning(f"No telemetry events found for session {session_id}")
            # Create default features
            return self._create_default_features(session)

        # Calculate behavioral metrics
        metrics = self._calculate_behavioral_metrics(events, session)

        # Create BehavioralFeatures record
        features = BehavioralFeatures(
            id=str(uuid4()),  # Explicitly generate UUID
            student_id=session.student_id,
            session_id=session_id,
            task_completion_rate=metrics["task_completion_rate"],
            time_efficiency=metrics["time_efficiency"],
            retry_count=metrics["retry_count"],
            recovery_rate=metrics["recovery_rate"],
            distraction_resistance=metrics["distraction_resistance"],
            focus_duration=metrics["focus_duration"],
            collaboration_indicators=metrics["collaboration_indicators"],
            leadership_indicators=metrics["leadership_indicators"],
            features_json=metrics,
        )

        self.db.add(features)
        await self.db.flush()

        return features

    def _calculate_behavioral_metrics(
        self, events: List[GameTelemetry], session: GameSession
    ) -> Dict[str, Any]:
        """
        Calculate behavioral metrics from telemetry events.

        Args:
            events: List of telemetry events
            session: Game session

        Returns:
            Dictionary of behavioral metrics
        """
        # Event type counts
        event_types = {}
        for event in events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1

        # Task completion
        tasks_started = event_types.get("mission_start", 0) + event_types.get(
            "task_start", 0
        )
        tasks_completed = event_types.get("mission_complete", 0) + event_types.get(
            "task_complete", 0
        )
        task_completion_rate = (
            tasks_completed / tasks_started if tasks_started > 0 else 0.0
        )

        # Retry count
        retry_count = event_types.get("retry", 0) + event_types.get("restart", 0)

        # Recovery rate (successful completions after failures)
        failures = event_types.get("failure", 0) + event_types.get("mistake", 0)
        recoveries = event_types.get("recovery", 0) + event_types.get(
            "success_after_failure", 0
        )
        recovery_rate = recoveries / failures if failures > 0 else 1.0

        # Time efficiency (based on session duration and completions)
        if session.ended_at and session.started_at:
            duration_minutes = (
                session.ended_at - session.started_at
            ).total_seconds() / 60.0
            expected_duration = tasks_completed * 3.0  # Assume 3 min per task
            time_efficiency = min(
                1.0,
                expected_duration / duration_minutes if duration_minutes > 0 else 0.0,
            )
        else:
            time_efficiency = 0.5

        # Focus duration (time between first and last event without distractions)
        distraction_count = event_types.get("distraction", 0) + event_types.get(
            "pause", 0
        )
        total_events = len(events)
        distraction_resistance = (
            1.0 - (distraction_count / total_events) if total_events > 0 else 0.0
        )

        # Focus duration (minutes)
        if events:
            focus_duration = (
                events[-1].timestamp - events[0].timestamp
            ).total_seconds() / 60.0
        else:
            focus_duration = 0.0

        # Collaboration indicators (interaction events)
        collaboration_count = (
            event_types.get("collaboration", 0)
            + event_types.get("help_given", 0)
            + event_types.get("help_received", 0)
        )
        collaboration_indicators = collaboration_count

        # Leadership indicators
        leadership_count = (
            event_types.get("initiative", 0)
            + event_types.get("leadership", 0)
            + event_types.get("decision_made", 0)
        )
        leadership_indicators = leadership_count

        return {
            "task_completion_rate": round(task_completion_rate, 3),
            "time_efficiency": round(time_efficiency, 3),
            "retry_count": retry_count,
            "recovery_rate": round(recovery_rate, 3),
            "distraction_resistance": round(distraction_resistance, 3),
            "focus_duration": round(focus_duration, 2),
            "collaboration_indicators": collaboration_indicators,
            "leadership_indicators": leadership_indicators,
            "event_count": len(events),
            "event_types": event_types,
            "session_duration_minutes": (
                (session.ended_at - session.started_at).total_seconds() / 60.0
                if session.ended_at and session.started_at
                else 0.0
            ),
        }

    def _create_default_features(self, session: GameSession) -> BehavioralFeatures:
        """
        Create default behavioral features for sessions with no events.

        Args:
            session: Game session

        Returns:
            BehavioralFeatures instance with default values
        """
        features = BehavioralFeatures(
            id=str(uuid4()),  # Explicitly generate UUID
            student_id=session.student_id,
            session_id=session.id,
            task_completion_rate=0.0,
            time_efficiency=0.0,
            retry_count=0,
            recovery_rate=0.0,
            distraction_resistance=0.0,
            focus_duration=0.0,
            collaboration_indicators=0,
            leadership_indicators=0,
            features_json={
                "event_count": 0,
                "note": "No telemetry events found for session",
            },
        )

        self.db.add(features)
        return features
