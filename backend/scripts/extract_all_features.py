"""
Extract linguistic and behavioral features for all students in the database.

This script processes all transcripts and game sessions and extracts features
needed for ML inference.

Usage:
    python scripts/extract_all_features.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from app.core.config import settings
from app.models.transcript import Transcript
from app.models.game_telemetry import GameSession
from app.services.feature_extraction import (
    LinguisticFeatureExtractor,
    BehavioralFeatureExtractor,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def extract_all_features():
    """Extract features for all transcripts and game sessions."""
    print("🔬 Starting feature extraction for all students...")
    print(
        f"📍 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}"
    )

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # Initialize extractors
            print("\n📚 Initializing NLP models...")
            ling_extractor = LinguisticFeatureExtractor()
            behav_extractor = BehavioralFeatureExtractor()

            # Process transcripts
            print("\n📝 Extracting linguistic features from transcripts...")
            result = await session.execute(select(Transcript))
            transcripts = result.scalars().all()

            print(f"   Found {len(transcripts)} transcripts to process")

            success_count = 0
            error_count = 0

            for i, transcript in enumerate(transcripts, 1):
                try:
                    await ling_extractor.process_transcript(session, transcript.id)
                    success_count += 1
                    print(
                        f"   ✅ [{i}/{len(transcripts)}] Processed transcript {transcript.id[:8]}..."
                    )
                except Exception as e:
                    error_count += 1
                    logger.error(
                        f"   ❌ Failed to process transcript {transcript.id}: {e}"
                    )

            print(
                f"\n   📊 Linguistic features: {success_count} successful, {error_count} failed"
            )

            # Process game sessions
            print("\n🎮 Extracting behavioral features from game sessions...")
            result = await session.execute(select(GameSession))
            game_sessions = result.scalars().all()

            print(f"   Found {len(game_sessions)} game sessions to process")

            success_count = 0
            error_count = 0

            for i, game_session in enumerate(game_sessions, 1):
                try:
                    await behav_extractor.process_game_session(session, game_session.id)
                    success_count += 1
                    print(
                        f"   ✅ [{i}/{len(game_sessions)}] Processed game session {game_session.id[:8]}..."
                    )
                except Exception as e:
                    error_count += 1
                    logger.error(
                        f"   ❌ Failed to process game session {game_session.id}: {e}"
                    )

            print(
                f"\n   📊 Behavioral features: {success_count} successful, {error_count} failed"
            )

            print("\n" + "=" * 60)
            print("✅ Feature extraction completed successfully!")
            print("=" * 60)
            print("\n🚀 Next steps:")
            print("   • Test inference endpoints at http://localhost:8000/api/v1/docs")
            print("   • View student data in the dashboard")

        except Exception as e:
            print(f"\n❌ Error during feature extraction: {e}")
            logger.exception("Full error traceback:")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(extract_all_features())
