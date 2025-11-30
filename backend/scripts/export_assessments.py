#!/usr/bin/env python3
"""
Export skill assessments to JSON backup file.

Usage:
    python scripts/export_assessments.py --output data/exports/assessments_backup.json
    python scripts/export_assessments.py --student-id <uuid> --output backups/student_assessments.json
    python scripts/export_assessments.py --skill-type empathy --output backups/empathy_assessments.json
    python scripts/export_assessments.py --start-date 2024-01-01 --end-date 2024-12-31
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.assessment import SkillAssessment, Evidence, SkillType


def serialize_assessment(assessment: SkillAssessment) -> dict:
    """Convert assessment to JSON-serializable dict."""
    return {
        "id": assessment.id,
        "student_id": assessment.student_id,
        "skill_type": assessment.skill_type.value,
        "score": assessment.score,
        "confidence": assessment.confidence,
        "reasoning": assessment.reasoning,
        "recommendations": assessment.recommendations,
        "feature_importance": assessment.feature_importance,
        "created_at": assessment.created_at.isoformat(),
        "updated_at": assessment.updated_at.isoformat(),
        "evidence": [
            {
                "id": e.id,
                "assessment_id": e.assessment_id,
                "evidence_type": e.evidence_type.value,
                "source": e.source,
                "content": e.content,
                "relevance_score": e.relevance_score,
                "created_at": e.created_at.isoformat(),
                "updated_at": e.updated_at.isoformat(),
            }
            for e in assessment.evidence
        ],
    }


async def export_assessments(
    output_path: str,
    student_id: Optional[str] = None,
    skill_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> int:
    """
    Export assessments to JSON file.

    Args:
        output_path: Path to output JSON file
        student_id: Optional filter by student ID
        skill_type: Optional filter by skill type
        start_date: Optional start date (ISO format)
        end_date: Optional end date (ISO format)

    Returns:
        Number of assessments exported
    """
    async with AsyncSessionLocal() as session:
        # Build query
        query = select(SkillAssessment).options(
            selectinload(SkillAssessment.evidence)
        )

        # Apply filters
        if student_id:
            query = query.where(SkillAssessment.student_id == student_id)

        if skill_type:
            try:
                skill_enum = SkillType(skill_type)
                query = query.where(SkillAssessment.skill_type == skill_enum)
            except ValueError:
                print(f"Error: Invalid skill type '{skill_type}'")
                print(f"Valid types: {[s.value for s in SkillType]}")
                return 0

        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.where(SkillAssessment.created_at >= start_dt)

        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.where(SkillAssessment.created_at <= end_dt)

        # Order by creation date
        query = query.order_by(SkillAssessment.created_at)

        # Execute query
        result = await session.execute(query)
        assessments = result.scalars().all()

        # Serialize to JSON
        data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "export_filters": {
                "student_id": student_id,
                "skill_type": skill_type,
                "start_date": start_date,
                "end_date": end_date,
            },
            "total_assessments": len(assessments),
            "assessments": [serialize_assessment(a) for a in assessments],
        }

        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return len(assessments)


async def main():
    parser = argparse.ArgumentParser(
        description="Export skill assessments to JSON backup file"
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output JSON file path (e.g., data/exports/assessments_backup.json)",
    )
    parser.add_argument(
        "--student-id",
        help="Filter by student ID (UUID)",
    )
    parser.add_argument(
        "--skill-type",
        help=f"Filter by skill type ({', '.join([s.value for s in SkillType])})",
    )
    parser.add_argument(
        "--start-date",
        help="Filter by start date (ISO format: YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end-date",
        help="Filter by end date (ISO format: YYYY-MM-DD)",
    )

    args = parser.parse_args()

    print("Starting assessment export...")
    print(f"Output file: {args.output}")

    if args.student_id:
        print(f"Filtering by student: {args.student_id}")
    if args.skill_type:
        print(f"Filtering by skill: {args.skill_type}")
    if args.start_date:
        print(f"Start date: {args.start_date}")
    if args.end_date:
        print(f"End date: {args.end_date}")

    try:
        count = await export_assessments(
            output_path=args.output,
            student_id=args.student_id,
            skill_type=args.skill_type,
            start_date=args.start_date,
            end_date=args.end_date,
        )

        print(f"\n✓ Successfully exported {count} assessments")
        print(f"✓ Saved to: {args.output}")

    except Exception as e:
        print(f"\n✗ Error during export: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
