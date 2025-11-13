"""Feature extraction service for linguistic and behavioral analysis."""

import logging
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import textstat
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.transcript import Transcript
from app.models.features import LinguisticFeatures, BehavioralFeatures
from app.models.game_telemetry import GameSession, GameTelemetry

logger = logging.getLogger(__name__)


class LinguisticFeatureExtractor:
    """Extract linguistic features from transcripts using NLP."""

    def __init__(self):
        """Initialize the linguistic feature extractor."""
        try:
            # Load spaCy English model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model: en_core_web_sm")
        except OSError:
            logger.error(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
            raise

        # Initialize VADER sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        logger.info("Initialized VADER sentiment analyzer")

    def extract_features(self, text: str) -> Dict[str, Any]:
        """
        Extract linguistic features from text.

        Args:
            text: The transcript text to analyze

        Returns:
            Dictionary containing extracted features
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for feature extraction")
            return self._get_empty_features()

        # Process text with spaCy
        doc = self.nlp(text)

        # Extract features
        features = {
            # LIWC-style categories (approximated)
            "empathy_markers": self._count_empathy_markers(doc),
            "problem_solving_language": self._count_problem_solving_language(doc),
            "perseverance_indicators": self._count_perseverance_indicators(doc),
            "social_processes": self._count_social_processes(doc),
            "cognitive_processes": self._count_cognitive_processes(doc),
            # Sentiment scores
            "positive_sentiment": self._get_sentiment_scores(text)["positive"],
            "negative_sentiment": self._get_sentiment_scores(text)["negative"],
            # Syntactic complexity
            "avg_sentence_length": self._get_avg_sentence_length(doc),
            "syntactic_complexity": self._get_syntactic_complexity(text),
            # Word count and readability
            "word_count": len([token for token in doc if not token.is_punct]),
            "unique_word_count": len(
                set([token.lemma_.lower() for token in doc if not token.is_punct])
            ),
            "readability_score": self._get_readability_score(text),
            # Part of speech distributions
            "noun_count": len([token for token in doc if token.pos_ == "NOUN"]),
            "verb_count": len([token for token in doc if token.pos_ == "VERB"]),
            "adj_count": len([token for token in doc if token.pos_ == "ADJ"]),
            "adv_count": len([token for token in doc if token.pos_ == "ADV"]),
        }

        logger.debug(f"Extracted {len(features)} linguistic features")
        return features

    def _count_empathy_markers(self, doc) -> int:
        """Count empathy-related words and phrases."""
        empathy_words = {
            "understand",
            "feel",
            "empathy",
            "compassion",
            "care",
            "concern",
            "sorry",
            "appreciate",
            "respect",
            "support",
            "help",
            "listen",
        }
        count = sum(1 for token in doc if token.lemma_.lower() in empathy_words)
        return count

    def _count_problem_solving_language(self, doc) -> int:
        """Count problem-solving related words."""
        problem_solving_words = {
            "solve",
            "solution",
            "problem",
            "analyze",
            "think",
            "plan",
            "strategy",
            "approach",
            "figure",
            "work",
            "try",
            "test",
            "find",
        }
        count = sum(1 for token in doc if token.lemma_.lower() in problem_solving_words)
        return count

    def _count_perseverance_indicators(self, doc) -> int:
        """Count perseverance and resilience indicators."""
        perseverance_words = {
            "continue",
            "persist",
            "keep",
            "try",
            "again",
            "more",
            "never",
            "give",
            "up",
            "determined",
            "effort",
            "work",
        }
        count = sum(1 for token in doc if token.lemma_.lower() in perseverance_words)
        return count

    def _count_social_processes(self, doc) -> int:
        """Count social process words (pronouns, social references)."""
        social_pronouns = {
            "i",
            "we",
            "you",
            "they",
            "us",
            "them",
            "our",
            "your",
            "their",
        }
        count = sum(1 for token in doc if token.lemma_.lower() in social_pronouns)
        return count

    def _count_cognitive_processes(self, doc) -> int:
        """Count cognitive process words."""
        cognitive_words = {
            "think",
            "know",
            "understand",
            "believe",
            "consider",
            "reason",
            "realize",
            "recognize",
            "remember",
            "decide",
            "learn",
            "wonder",
        }
        count = sum(1 for token in doc if token.lemma_.lower() in cognitive_words)
        return count

    def _get_sentiment_scores(self, text: str) -> Dict[str, float]:
        """Get sentiment scores using VADER."""
        scores = self.sentiment_analyzer.polarity_scores(text)
        return {
            "positive": scores["pos"],
            "negative": scores["neg"],
            "neutral": scores["neu"],
            "compound": scores["compound"],
        }

    def _get_avg_sentence_length(self, doc) -> float:
        """Calculate average sentence length in words."""
        sentences = list(doc.sents)
        if not sentences:
            return 0.0

        total_words = sum(
            len([token for token in sent if not token.is_punct]) for sent in sentences
        )
        return total_words / len(sentences)

    def _get_syntactic_complexity(self, text: str) -> float:
        """Calculate syntactic complexity using Flesch Reading Ease."""
        try:
            # Flesch Reading Ease: higher score = easier to read
            # We invert it so higher = more complex
            flesch_score = textstat.flesch_reading_ease(text)
            # Normalize to 0-1 range (100 = very easy, 0 = very hard)
            complexity = max(0, min(1, (100 - flesch_score) / 100))
            return complexity
        except Exception as e:
            logger.warning(f"Error calculating syntactic complexity: {e}")
            return 0.0

    def _get_readability_score(self, text: str) -> float:
        """Get readability score (Flesch-Kincaid Grade Level)."""
        try:
            grade_level = textstat.flesch_kincaid_grade(text)
            return grade_level
        except Exception as e:
            logger.warning(f"Error calculating readability: {e}")
            return 0.0

    def _get_empty_features(self) -> Dict[str, Any]:
        """Return empty feature dictionary."""
        return {
            "empathy_markers": 0,
            "problem_solving_language": 0,
            "perseverance_indicators": 0,
            "social_processes": 0,
            "cognitive_processes": 0,
            "positive_sentiment": 0.0,
            "negative_sentiment": 0.0,
            "avg_sentence_length": 0.0,
            "syntactic_complexity": 0.0,
            "word_count": 0,
            "unique_word_count": 0,
            "readability_score": 0.0,
            "noun_count": 0,
            "verb_count": 0,
            "adj_count": 0,
            "adv_count": 0,
        }

    async def process_transcript(
        self, session: AsyncSession, transcript_id: str
    ) -> LinguisticFeatures:
        """
        Process a transcript and extract linguistic features.

        Args:
            session: Database session
            transcript_id: ID of the transcript to process

        Returns:
            LinguisticFeatures object with extracted features

        Raises:
            ValueError: If transcript not found
        """
        # Fetch transcript
        result = await session.execute(
            select(Transcript).where(Transcript.id == transcript_id)
        )
        transcript = result.scalar_one_or_none()

        if not transcript:
            raise ValueError(f"Transcript {transcript_id} not found")

        logger.info(f"Processing transcript {transcript_id} for feature extraction")

        # Extract features
        features = self.extract_features(transcript.text)

        # Create or update linguistic features
        result = await session.execute(
            select(LinguisticFeatures).where(
                LinguisticFeatures.transcript_id == transcript_id
            )
        )
        linguistic_features = result.scalar_one_or_none()

        if linguistic_features:
            # Update existing
            for key, value in features.items():
                if hasattr(linguistic_features, key):
                    setattr(linguistic_features, key, value)
            linguistic_features.features_json = features
        else:
            # Create new
            linguistic_features = LinguisticFeatures(
                transcript_id=transcript_id,
                student_id=transcript.student_id,
                empathy_markers=features["empathy_markers"],
                problem_solving_language=features["problem_solving_language"],
                perseverance_indicators=features["perseverance_indicators"],
                social_processes=features["social_processes"],
                cognitive_processes=features["cognitive_processes"],
                positive_sentiment=features["positive_sentiment"],
                negative_sentiment=features["negative_sentiment"],
                avg_sentence_length=features["avg_sentence_length"],
                syntactic_complexity=features["syntactic_complexity"],
                features_json=features,
            )
            session.add(linguistic_features)

        await session.commit()
        await session.refresh(linguistic_features)

        logger.info(f"Saved linguistic features for transcript {transcript_id}")
        return linguistic_features


class BehavioralFeatureExtractor:
    """Extract behavioral features from game telemetry data."""

    def __init__(self):
        """Initialize the behavioral feature extractor."""
        logger.info("Initialized BehavioralFeatureExtractor")

    def extract_features(self, telemetry_events: List[GameTelemetry]) -> Dict[str, Any]:
        """
        Extract behavioral features from game telemetry events.

        Args:
            telemetry_events: List of game telemetry events

        Returns:
            Dictionary containing extracted behavioral features
        """
        if not telemetry_events:
            logger.warning("No telemetry events provided for feature extraction")
            return self._get_empty_features()

        # Calculate metrics
        features = {
            "task_completion_rate": self._calculate_task_completion_rate(
                telemetry_events
            ),
            "time_efficiency": self._calculate_time_efficiency(telemetry_events),
            "retry_count": self._count_retries(telemetry_events),
            "recovery_rate": self._calculate_recovery_rate(telemetry_events),
            "distraction_resistance": self._calculate_distraction_resistance(
                telemetry_events
            ),
            "focus_duration": self._calculate_focus_duration(telemetry_events),
            "collaboration_indicators": self._count_collaboration_indicators(
                telemetry_events
            ),
            "leadership_indicators": self._count_leadership_indicators(
                telemetry_events
            ),
            "event_count": len(telemetry_events),
        }

        logger.debug(
            f"Extracted {len(features)} behavioral features from {len(telemetry_events)} events"
        )
        return features

    def _calculate_task_completion_rate(self, events: List[GameTelemetry]) -> float:
        """Calculate percentage of tasks completed."""
        completion_events = [e for e in events if e.event_type == "task_completed"]
        attempt_events = [
            e for e in events if e.event_type in ("task_started", "task_completed")
        ]

        if not attempt_events:
            return 0.0

        return len(completion_events) / len(attempt_events)

    def _calculate_time_efficiency(self, events: List[GameTelemetry]) -> float:
        """Calculate time efficiency (faster completion = higher score)."""
        completion_events = [
            e
            for e in events
            if e.event_type == "task_completed" and e.event_data.get("time_taken_ms")
        ]

        if not completion_events:
            return 0.0

        avg_time = sum(
            e.event_data.get("time_taken_ms", 0) for e in completion_events
        ) / len(completion_events)

        # Normalize: assume 5000ms is baseline, faster is better
        # Score ranges from 0 to 1, where 1 is very efficient
        baseline = 5000
        efficiency = max(0, min(1, baseline / max(avg_time, 1)))
        return efficiency

    def _count_retries(self, events: List[GameTelemetry]) -> int:
        """Count retry attempts."""
        retry_events = [
            e for e in events if e.event_type == "retry" or e.event_data.get("is_retry")
        ]
        return len(retry_events)

    def _calculate_recovery_rate(self, events: List[GameTelemetry]) -> float:
        """Calculate success rate after failures."""
        failure_events = [e for e in events if e.event_type == "task_failed"]
        retry_success_events = [
            e
            for e in events
            if e.event_type == "task_completed" and e.event_data.get("after_retry")
        ]

        if not failure_events:
            return 1.0  # No failures = perfect recovery

        return len(retry_success_events) / len(failure_events)

    def _calculate_distraction_resistance(self, events: List[GameTelemetry]) -> float:
        """Calculate ability to stay focused (fewer distractions = higher score)."""
        distraction_events = [
            e
            for e in events
            if e.event_type in ("context_switch", "pause", "distraction")
        ]
        total_events = len(events)

        if total_events == 0:
            return 1.0

        # Higher score = fewer distractions
        distraction_rate = len(distraction_events) / total_events
        return max(0, 1 - distraction_rate)

    def _calculate_focus_duration(self, events: List[GameTelemetry]) -> float:
        """Calculate average focus duration in seconds."""
        focus_events = [
            e
            for e in events
            if e.event_type == "focus_period" and e.event_data.get("duration_seconds")
        ]

        if not focus_events:
            return 0.0

        total_duration = sum(
            e.event_data.get("duration_seconds", 0) for e in focus_events
        )
        return total_duration / len(focus_events)

    def _count_collaboration_indicators(self, events: List[GameTelemetry]) -> int:
        """Count collaboration indicators."""
        collaboration_events = [
            e
            for e in events
            if e.event_type in ("share_resource", "help_peer", "team_decision")
        ]
        return len(collaboration_events)

    def _count_leadership_indicators(self, events: List[GameTelemetry]) -> int:
        """Count leadership indicators."""
        leadership_events = [
            e
            for e in events
            if e.event_type in ("delegate_task", "lead_discussion", "make_decision")
        ]
        return len(leadership_events)

    def _get_empty_features(self) -> Dict[str, Any]:
        """Return empty feature dictionary."""
        return {
            "task_completion_rate": 0.0,
            "time_efficiency": 0.0,
            "retry_count": 0,
            "recovery_rate": 0.0,
            "distraction_resistance": 1.0,
            "focus_duration": 0.0,
            "collaboration_indicators": 0,
            "leadership_indicators": 0,
            "event_count": 0,
        }

    async def process_game_session(
        self, session: AsyncSession, game_session_id: str
    ) -> BehavioralFeatures:
        """
        Process a game session and extract behavioral features.

        Args:
            session: Database session
            game_session_id: ID of the game session to process

        Returns:
            BehavioralFeatures object with extracted features

        Raises:
            ValueError: If game session not found
        """
        # Fetch game session
        result = await session.execute(
            select(GameSession).where(GameSession.id == game_session_id)
        )
        game_session = result.scalar_one_or_none()

        if not game_session:
            raise ValueError(f"GameSession {game_session_id} not found")

        # Fetch telemetry events for this session
        result = await session.execute(
            select(GameTelemetry)
            .where(GameTelemetry.session_id == game_session_id)
            .order_by(GameTelemetry.timestamp)
        )
        telemetry_events = result.scalars().all()

        logger.info(
            f"Processing {len(telemetry_events)} telemetry events for session {game_session_id}"
        )

        # Extract features
        features = self.extract_features(list(telemetry_events))

        # Create or update behavioral features
        result = await session.execute(
            select(BehavioralFeatures).where(
                BehavioralFeatures.session_id == game_session_id
            )
        )
        behavioral_features = result.scalar_one_or_none()

        if behavioral_features:
            # Update existing
            for key, value in features.items():
                if hasattr(behavioral_features, key):
                    setattr(behavioral_features, key, value)
            behavioral_features.features_json = features
        else:
            # Create new
            behavioral_features = BehavioralFeatures(
                student_id=game_session.student_id,
                session_id=game_session_id,
                task_completion_rate=features["task_completion_rate"],
                time_efficiency=features["time_efficiency"],
                retry_count=features["retry_count"],
                recovery_rate=features["recovery_rate"],
                distraction_resistance=features["distraction_resistance"],
                focus_duration=features["focus_duration"],
                collaboration_indicators=features["collaboration_indicators"],
                leadership_indicators=features["leadership_indicators"],
                features_json=features,
            )
            session.add(behavioral_features)

        await session.commit()
        await session.refresh(behavioral_features)

        logger.info(f"Saved behavioral features for session {game_session_id}")
        return behavioral_features
