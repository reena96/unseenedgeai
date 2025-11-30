#!/usr/bin/env python3
"""
Import skill assessments from JSON backup file.

Usage:
    python scripts/import_assessments.py --input data/exports/assessments_backup.json
    python scripts/import_assessments.py --input backups/assessments.json --skip-duplicates
    python scripts/import_assessments.py --input backups/assessments.json --update-duplicates
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Tuple
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.models.assessment import (  # noqa: E402
    SkillAssessment,
    Evidence,
    SkillType,
    EvidenceType,
)


async def import_assessments(
    input_path: str,
    skip_duplicates: bool = False,
    update_duplicates: bool = False,
) -> Tuple[int, int, int]:
    """
    Import assessments from JSON file.

    Args:
        input_path: Path to input JSON file
        skip_duplicates: Skip assessments that already exist (by ID)
        update_duplicates: Update existing assessments with imported data

    Returns:
        Tuple of (imported, skipped, updated) counts
    """
    # Read JSON file
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assessments_data = data.get("assessments", [])
    total = len(assessments_data)

    print(f"Found {total} assessments in backup file")
    print(f"Backup timestamp: {data.get('export_timestamp', 'unknown')}")

    imported = 0
    skipped = 0
    updated = 0
    errors = []

    async with AsyncSessionLocal() as session:
        for idx, assessment_data in enumerate(assessments_data, 1):
            try:
                assessment_id = assessment_data["id"]

                # Check if assessment already exists
                result = await session.execute(
                    select(SkillAssessment)
                    .options(selectinload(SkillAssessment.evidence))
                    .where(SkillAssessment.id == assessment_id)
                )
                existing = result.scalar_one_or_none()

                if existing:
                    if skip_duplicates:
                        skipped += 1
                        if idx % 100 == 0:
                            print(f"Progress: {idx}/{total} (skipped duplicate)")
                        continue
                    elif update_duplicates:
                        # Update existing assessment
                        existing.score = assessment_data["score"]
                        existing.confidence = assessment_data["confidence"]
                        existing.reasoning = assessment_data["reasoning"]
                        existing.recommendations = assessment_data.get(
                            "recommendations"
                        )
                        existing.feature_importance = assessment_data.get(
                            "feature_importance"
                        )

                        # Delete old evidence and import new
                        for old_evidence in existing.evidence:
                            await session.delete(old_evidence)

                        # Add new evidence
                        for evidence_data in assessment_data.get("evidence", []):
                            evidence = Evidence(
                                id=evidence_data["id"],
                                assessment_id=assessment_id,
                                evidence_type=EvidenceType(
                                    evidence_data["evidence_type"]
                                ),
                                source=evidence_data["source"],
                                content=evidence_data["content"],
                                relevance_score=evidence_data["relevance_score"],
                            )
                            session.add(evidence)

                        updated += 1
                        if idx % 100 == 0:
                            print(f"Progress: {idx}/{total} (updated)")
                    else:
                        skipped += 1
                        if idx % 100 == 0:
                            print(
                                f"Progress: {idx}/{total} (duplicate exists, skipping)"
                            )
                        continue
                else:
                    # Create new assessment
                    assessment = SkillAssessment(
                        id=assessment_id,
                        student_id=assessment_data["student_id"],
                        skill_type=SkillType(assessment_data["skill_type"]),
                        score=assessment_data["score"],
                        confidence=assessment_data["confidence"],
                        reasoning=assessment_data["reasoning"],
                        recommendations=assessment_data.get("recommendations"),
                        feature_importance=assessment_data.get("feature_importance"),
                    )

                    # Manually set timestamps if they exist in the backup
                    if "created_at" in assessment_data:
                        assessment.created_at = datetime.fromisoformat(
                            assessment_data["created_at"]
                        )
                    if "updated_at" in assessment_data:
                        assessment.updated_at = datetime.fromisoformat(
                            assessment_data["updated_at"]
                        )

                    session.add(assessment)

                    # Import evidence
                    for evidence_data in assessment_data.get("evidence", []):
                        evidence = Evidence(
                            id=evidence_data["id"],
                            assessment_id=assessment_id,
                            evidence_type=EvidenceType(evidence_data["evidence_type"]),
                            source=evidence_data["source"],
                            content=evidence_data["content"],
                            relevance_score=evidence_data["relevance_score"],
                        )

                        # Manually set timestamps if they exist
                        if "created_at" in evidence_data:
                            evidence.created_at = datetime.fromisoformat(
                                evidence_data["created_at"]
                            )
                        if "updated_at" in evidence_data:
                            evidence.updated_at = datetime.fromisoformat(
                                evidence_data["updated_at"]
                            )

                        session.add(evidence)

                    imported += 1
                    if idx % 100 == 0:
                        print(f"Progress: {idx}/{total} (imported)")

                # Commit every 100 records for better performance
                if idx % 100 == 0:
                    await session.commit()

            except Exception as e:
                errors.append((assessment_data.get("id", "unknown"), str(e)))
                print(f"Error importing assessment {assessment_data.get('id')}: {e}")

        # Final commit
        await session.commit()

    if errors:
        print(f"\n⚠ Encountered {len(errors)} errors during import:")
        for assessment_id, error in errors[:10]:  # Show first 10 errors
            print(f"  - {assessment_id}: {error}")

    return imported, skipped, updated


async def main():
    parser = argparse.ArgumentParser(
        description="Import skill assessments from JSON backup file"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input JSON file path (e.g., data/exports/assessments_backup.json)",
    )
    parser.add_argument(
        "--skip-duplicates",
        action="store_true",
        help="Skip assessments that already exist in database",
    )
    parser.add_argument(
        "--update-duplicates",
        action="store_true",
        help="Update existing assessments with imported data",
    )

    args = parser.parse_args()

    if args.skip_duplicates and args.update_duplicates:
        print(
            "Error: Cannot use both --skip-duplicates and --update-duplicates",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Starting assessment import...")
    print(f"Input file: {args.input}")
    duplicate_mode = (
        "skip"
        if args.skip_duplicates
        else "update" if args.update_duplicates else "error on duplicate"
    )
    print(f"Duplicate handling: {duplicate_mode}")

    try:
        imported, skipped, updated = await import_assessments(
            input_path=args.input,
            skip_duplicates=args.skip_duplicates,
            update_duplicates=args.update_duplicates,
        )

        print("\n✓ Import complete:")
        print(f"  - Imported: {imported}")
        print(f"  - Skipped: {skipped}")
        print(f"  - Updated: {updated}")

    except Exception as e:
        print(f"\n✗ Error during import: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
