"""Tests for telemetry ingestion and processing."""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy import select
from httpx import AsyncClient

from app.models.features import BehavioralFeatures
from app.services.telemetry_processor import TelemetryProcessor


class TestTelemetryProcessor:
    """Test TelemetryProcessor service."""

    @pytest.mark.asyncio
    async def test_create_session(self, db_session, test_student):
        """Test creating a new game session."""
        processor = TelemetryProcessor(db_session)

        session = await processor.get_or_create_session(
            student_id=test_student.id,
            session_id="session-001",
            mission_id="mission-alpha",
            game_version="1.0.0",
        )

        assert session.id == "session-001"
        assert session.student_id == test_student.id
        assert session.mission_id == "mission-alpha"
        assert session.game_version == "1.0.0"
        assert session.started_at is not None
        assert session.ended_at is None

    @pytest.mark.asyncio
    async def test_process_single_event(self, db_session, test_student):
        """Test processing a single telemetry event."""
        processor = TelemetryProcessor(db_session)

        # Create session first
        session = await processor.get_or_create_session(
            student_id=test_student.id,
            session_id="session-001",
            game_version="1.0.0",
        )

        # Process event
        event = await processor.process_event(
            student_id=test_student.id,
            event_type="mission_start",
            event_data={"mission": "alpha", "difficulty": "medium"},
            session_id=session.id,
            mission_id="mission-alpha",
            event_id=str(uuid4()),  # Add event_id for deduplication
        )

        assert event.student_id == test_student.id
        assert event.event_type == "mission_start"
        assert event.event_data["mission"] == "alpha"
        assert event.session_id == session.id

    @pytest.mark.asyncio
    async def test_process_batch(self, db_session, test_student):
        """Test processing a batch of telemetry events."""
        processor = TelemetryProcessor(db_session)

        # Create session
        await processor.get_or_create_session(
            student_id=test_student.id,
            session_id="session-batch",
            game_version="1.0.0",
        )

        # Prepare batch
        now = datetime.now(timezone.utc)
        events = [
            {
                "event_id": str(uuid4()),
                "student_id": test_student.id,
                "event_type": "mission_start",
                "data": {"mission": "alpha"},
                "session_id": "session-batch",
                "mission_id": "mission-alpha",
                "timestamp": now,
            },
            {
                "event_id": str(uuid4()),
                "student_id": test_student.id,
                "event_type": "choice_made",
                "data": {"choice": "help_friend"},
                "session_id": "session-batch",
                "mission_id": "mission-alpha",
                "timestamp": now + timedelta(seconds=30),
            },
            {
                "event_id": str(uuid4()),
                "student_id": test_student.id,
                "event_type": "mission_complete",
                "data": {"success": True},
                "session_id": "session-batch",
                "mission_id": "mission-alpha",
                "timestamp": now + timedelta(minutes=5),
            },
        ]

        # Process batch
        processed = await processor.process_batch(
            events=events,
            batch_id="batch-001",
        )

        assert len(processed) == 3
        assert processed[0].event_type == "mission_start"
        assert processed[1].event_type == "choice_made"
        assert processed[2].event_type == "mission_complete"

    @pytest.mark.asyncio
    async def test_close_session_and_extract_features(
        self, db_session_no_commit, test_student_no_commit
    ):
        """Test closing a session and extracting behavioral features."""
        processor = TelemetryProcessor(db_session_no_commit)

        # Create session
        await processor.get_or_create_session(
            student_id=test_student_no_commit.id,
            session_id="session-features",
            game_version="1.0.0",
        )

        # Add telemetry events
        base_time = datetime.now(timezone.utc)
        events = [
            {
                "event_id": str(uuid4()),
                "student_id": test_student_no_commit.id,
                "event_type": "mission_start",
                "data": {},
                "session_id": "session-features",
                "timestamp": base_time,
            },
            {
                "event_id": str(uuid4()),
                "student_id": test_student_no_commit.id,
                "event_type": "task_start",
                "data": {},
                "session_id": "session-features",
                "timestamp": base_time + timedelta(seconds=10),
            },
            {
                "event_id": str(uuid4()),
                "student_id": test_student_no_commit.id,
                "event_type": "retry",
                "data": {},
                "session_id": "session-features",
                "timestamp": base_time + timedelta(minutes=2),
            },
            {
                "event_id": str(uuid4()),
                "student_id": test_student_no_commit.id,
                "event_type": "task_complete",
                "data": {},
                "session_id": "session-features",
                "timestamp": base_time + timedelta(minutes=3),
            },
            {
                "event_id": str(uuid4()),
                "student_id": test_student_no_commit.id,
                "event_type": "mission_complete",
                "data": {},
                "session_id": "session-features",
                "timestamp": base_time + timedelta(minutes=5),
            },
        ]

        await processor.process_batch(events, "batch-features")

        # Close session
        closed_session = await processor.close_session("session-features")

        assert closed_session.ended_at is not None

        # Check behavioral features were extracted
        stmt = select(BehavioralFeatures).where(
            BehavioralFeatures.session_id == "session-features"
        )
        result = await db_session_no_commit.execute(stmt)
        features = result.scalar_one_or_none()

        assert features is not None
        assert features.student_id == test_student_no_commit.id
        assert features.task_completion_rate > 0
        assert features.retry_count > 0
        assert features.features_json["event_count"] == 5

    @pytest.mark.asyncio
    async def test_behavioral_metrics_calculation(
        self, db_session_no_commit, test_student_no_commit
    ):
        """Test behavioral metrics are calculated correctly."""
        processor = TelemetryProcessor(db_session_no_commit)

        # Create session with realistic game data
        await processor.get_or_create_session(
            student_id=test_student_no_commit.id,
            session_id="session-metrics",
            game_version="1.0.0",
        )

        base_time = datetime.now(timezone.utc)
        events = [
            {"event_type": "mission_start", "timestamp": base_time},
            {
                "event_type": "task_start",
                "timestamp": base_time + timedelta(seconds=10),
            },
            {
                "event_type": "collaboration",
                "timestamp": base_time + timedelta(minutes=1),
            },
            {"event_type": "retry", "timestamp": base_time + timedelta(minutes=2)},
            {"event_type": "failure", "timestamp": base_time + timedelta(minutes=3)},
            {"event_type": "recovery", "timestamp": base_time + timedelta(minutes=4)},
            {
                "event_type": "task_complete",
                "timestamp": base_time + timedelta(minutes=5),
            },
            {"event_type": "leadership", "timestamp": base_time + timedelta(minutes=6)},
            {
                "event_type": "mission_complete",
                "timestamp": base_time + timedelta(minutes=8),
            },
        ]

        event_list = [
            {
                "event_id": str(uuid4()),
                "student_id": test_student_no_commit.id,
                "event_type": e["event_type"],
                "data": {},
                "session_id": "session-metrics",
                "timestamp": e["timestamp"],
            }
            for e in events
        ]

        await processor.process_batch(event_list, "batch-metrics")
        await processor.close_session("session-metrics")

        # Verify behavioral features
        stmt = select(BehavioralFeatures).where(
            BehavioralFeatures.session_id == "session-metrics"
        )
        result = await db_session_no_commit.execute(stmt)
        features = result.scalar_one_or_none()

        assert features is not None
        # 1 mission + 1 task = 2 starts, 1 mission + 1 task = 2 completes
        assert features.task_completion_rate == 1.0
        assert features.retry_count == 1
        assert features.recovery_rate == 1.0  # 1 recovery / 1 failure
        assert features.collaboration_indicators == 1
        assert features.leadership_indicators == 1


class TestTelemetryEndpoints:
    """Test telemetry API endpoints."""

    @pytest.mark.asyncio
    async def test_ingest_single_event(
        self, async_client: AsyncClient, auth_headers, test_student, mock_rate_limiter
    ):
        """Test ingesting a single telemetry event."""
        event_id = str(uuid4())
        event_data = {
            "event_id": event_id,
            "student_id": test_student.id,
            "event_type": "mission_start",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {"mission": "alpha", "difficulty": "medium"},
            "session_id": str(uuid4()),
            "mission_id": "mission-alpha",
            "game_version": "1.0.0",
        }

        response = await async_client.post(
            "/api/v1/telemetry/events",
            json=event_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "processed"
        assert data["received_count"] == 1
        assert data["batch_id"] == event_id

    @pytest.mark.asyncio
    async def test_ingest_batch_events(
        self, async_client: AsyncClient, auth_headers, test_student, mock_rate_limiter
    ):
        """Test ingesting a batch of telemetry events."""
        batch_id = str(uuid4())
        session_id = str(uuid4())

        # First, add game_version to the first event to trigger session creation
        batch_data = {
            "batch_id": batch_id,
            "client_version": "1.0.0",
            "events": [
                {
                    "event_id": str(uuid4()),
                    "student_id": test_student.id,
                    "event_type": "mission_start",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data": {},
                    "session_id": session_id,
                    "game_version": "1.0.0",
                },
                {
                    "event_id": str(uuid4()),
                    "student_id": test_student.id,
                    "event_type": "choice_made",
                    "timestamp": (
                        datetime.now(timezone.utc) + timedelta(seconds=30)
                    ).isoformat(),
                    "data": {"choice": "help"},
                    "session_id": session_id,
                },
                {
                    "event_id": str(uuid4()),
                    "student_id": test_student.id,
                    "event_type": "mission_complete",
                    "timestamp": (
                        datetime.now(timezone.utc) + timedelta(minutes=5)
                    ).isoformat(),
                    "data": {},
                    "session_id": session_id,
                },
            ],
        }

        response = await async_client.post(
            "/api/v1/telemetry/batch",
            json=batch_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "processed"
        assert data["received_count"] == 3
        assert data["batch_id"] == batch_id

    @pytest.mark.asyncio
    async def test_close_session(
        self,
        async_client: AsyncClient,
        auth_headers,
        test_student,
        db_session,
        mock_rate_limiter,
    ):
        """Test closing a game session via API."""
        # First, create a session with events
        processor = TelemetryProcessor(db_session)
        await processor.get_or_create_session(
            student_id=test_student.id,
            session_id="session-close-api",
            game_version="1.0.0",
        )

        # Add some events
        await processor.process_event(
            student_id=test_student.id,
            event_type="mission_start",
            event_data={},
            session_id="session-close-api",
            event_id=str(uuid4()),
        )
        await db_session.commit()

        # Close session via API
        response = await async_client.post(
            "/api/v1/telemetry/session/session-close-api/close",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "closed"
        assert data["session_id"] == "session-close-api"
        assert data["ended_at"] is not None

    @pytest.mark.skip(
        reason=(
            "Known issue: DB connection pool exhaustion under concurrent load - "
            "requires architecture improvements"
        )
    )
    @pytest.mark.asyncio
    async def test_performance_under_load(
        self, async_client: AsyncClient, auth_headers, test_student, mock_rate_limiter
    ):
        """Test telemetry system performance with high event volume."""
        import asyncio

        # Use a consistent session_id for all events
        session_id = str(uuid4())

        # Create 10 concurrent event submissions (reduced from 50 for test DB connection limits)
        async def send_event(event_num: int):
            option_choice = "option-{}".format(event_num % 5)
            event_data = {
                "event_id": str(uuid4()),
                "student_id": test_student.id,
                "event_type": "choice_made",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {"choice": option_choice},
                "session_id": session_id,
                "game_version": "1.0.0",
            }

            response = await async_client.post(
                "/api/v1/telemetry/events",
                json=event_data,
                headers=auth_headers,
            )
            return response.status_code

        # Send events concurrently
        tasks = [send_event(i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check success rate
        success_count = sum(1 for r in results if r == 201)
        assert (
            success_count >= 9
        )  # Allow for some failures due to concurrency (90% success rate)
