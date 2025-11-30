#!/usr/bin/env python3
"""
Verify data integrity for skill assessments.

Checks:
- All students have assessments
- Score ranges are valid (0-1)
- Confidence ranges are valid (0-1)
- Evidence records are linked properly
- No orphaned evidence records
- Timestamps are consistent

Usage:
    python scripts/verify_data_integrity.py
    python scripts/verify_data_integrity.py --verbose
    python scripts/verify_data_integrity.py --fix-orphans
"""

import asyncio
import argparse
import sys
from pathlib import Path
from sqlalchemy import select, func

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.models.assessment import SkillAssessment, Evidence, SkillType  # noqa: E402
from app.models.student import Student  # noqa: E402


class IntegrityChecker:
    """Check data integrity for assessments."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.issues = []
        self.warnings = []

    def log_issue(self, message: str):
        """Log an integrity issue."""
        self.issues.append(message)
        print(f"✗ ISSUE: {message}")

    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        if self.verbose:
            print(f"⚠ WARNING: {message}")

    def log_info(self, message: str):
        """Log informational message."""
        if self.verbose:
            print(f"ℹ {message}")

    async def check_score_ranges(self, session):
        """Check that all scores are within valid range (0-1)."""
        print("\n1. Checking score ranges...")

        result = await session.execute(
            select(SkillAssessment).where(
                (SkillAssessment.score < 0) | (SkillAssessment.score > 1)
            )
        )
        invalid_scores = result.scalars().all()

        if invalid_scores:
            self.log_issue(
                f"Found {len(invalid_scores)} assessments with invalid scores (outside 0-1 range)"
            )
            for assessment in invalid_scores[:5]:  # Show first 5
                self.log_warning(
                    f"  Assessment {assessment.id}: score={assessment.score}"
                )
        else:
            print("✓ All scores are within valid range (0-1)")

        # Check confidence ranges
        result = await session.execute(
            select(SkillAssessment).where(
                (SkillAssessment.confidence < 0) | (SkillAssessment.confidence > 1)
            )
        )
        invalid_confidence = result.scalars().all()

        if invalid_confidence:
            self.log_issue(
                f"Found {len(invalid_confidence)} assessments with invalid "
                f"confidence (outside 0-1 range)"
            )
            for assessment in invalid_confidence[:5]:
                self.log_warning(
                    f"  Assessment {assessment.id}: confidence={assessment.confidence}"
                )
        else:
            print("✓ All confidence scores are within valid range (0-1)")

    async def check_student_coverage(self, session):
        """Check that all students have assessments."""
        print("\n2. Checking student assessment coverage...")

        # Get all students
        result = await session.execute(select(Student))
        all_students = result.scalars().all()

        # Get students with assessments
        result = await session.execute(
            select(Student.id).join(SkillAssessment).distinct()
        )
        students_with_assessments = set(row[0] for row in result.fetchall())

        students_without = [
            s for s in all_students if s.id not in students_with_assessments
        ]

        if students_without:
            self.log_warning(
                f"Found {len(students_without)} students without any assessments"
            )
            if self.verbose:
                for student in students_without[:10]:  # Show first 10
                    self.log_info(
                        f"  Student {student.id} ({student.first_name} {student.last_name})"
                    )
        else:
            print(f"✓ All {len(all_students)} students have assessments")

        # Check for primary skills coverage
        primary_skills = [
            SkillType.EMPATHY,
            SkillType.PROBLEM_SOLVING,
            SkillType.SELF_REGULATION,
            SkillType.RESILIENCE,
        ]

        incomplete_students = []
        for student in all_students:
            result = await session.execute(
                select(SkillAssessment.skill_type)
                .where(SkillAssessment.student_id == student.id)
                .distinct()
            )
            student_skills = set(row[0] for row in result.fetchall())

            missing_skills = set(primary_skills) - student_skills
            if missing_skills:
                incomplete_students.append((student, [s.value for s in missing_skills]))

        if incomplete_students:
            self.log_warning(
                f"Found {len(incomplete_students)} students missing primary skill assessments"
            )
            if self.verbose:
                for student, missing in incomplete_students[:5]:
                    self.log_info(
                        f"  Student {student.id}: missing {', '.join(missing)}"
                    )
        else:
            print(
                f"✓ All students have all {len(primary_skills)} primary skill assessments"
            )

    async def check_orphaned_evidence(self, session, fix: bool = False):
        """Check for evidence records not linked to assessments."""
        print("\n3. Checking for orphaned evidence...")

        # Find evidence with non-existent assessment IDs
        result = await session.execute(
            select(Evidence)
            .outerjoin(SkillAssessment, Evidence.assessment_id == SkillAssessment.id)
            .where(SkillAssessment.id.is_(None))
        )
        orphaned = result.scalars().all()

        if orphaned:
            self.log_issue(f"Found {len(orphaned)} orphaned evidence records")

            if fix:
                print("  Deleting orphaned evidence...")
                for evidence in orphaned:
                    await session.delete(evidence)
                await session.commit()
                print(f"  ✓ Deleted {len(orphaned)} orphaned evidence records")
            else:
                self.log_info(
                    "  Run with --fix-orphans to automatically delete these records"
                )
        else:
            print("✓ No orphaned evidence records found")

    async def check_evidence_linking(self, session):
        """Check that assessments have proper evidence."""
        print("\n4. Checking evidence linking...")

        # Get assessments without evidence
        result = await session.execute(
            select(SkillAssessment)
            .outerjoin(Evidence)
            .group_by(SkillAssessment.id)
            .having(func.count(Evidence.id) == 0)
        )
        without_evidence = result.scalars().all()

        if without_evidence:
            self.log_warning(
                f"Found {len(without_evidence)} assessments without evidence"
            )
            if self.verbose:
                for assessment in without_evidence[:5]:
                    self.log_info(
                        f"  Assessment {assessment.id} ({assessment.skill_type.value})"
                    )
        else:
            print("✓ All assessments have evidence records")

        # Check evidence counts
        result = await session.execute(
            select(
                SkillAssessment.id,
                SkillAssessment.skill_type,
                func.count(Evidence.id).label("evidence_count"),
            )
            .join(Evidence)
            .group_by(SkillAssessment.id, SkillAssessment.skill_type)
        )
        evidence_counts = result.fetchall()

        low_evidence = [
            (id, skill, count) for id, skill, count in evidence_counts if count < 3
        ]
        high_evidence = [
            (id, skill, count) for id, skill, count in evidence_counts if count > 20
        ]

        if low_evidence:
            self.log_warning(
                f"Found {len(low_evidence)} assessments with fewer than 3 evidence records"
            )
        if high_evidence:
            self.log_warning(
                f"Found {len(high_evidence)} assessments with more than 20 evidence records"
            )

        if not low_evidence and not high_evidence:
            print("✓ Evidence counts are reasonable for all assessments")

    async def check_timestamp_consistency(self, session):
        """Check that timestamps are consistent."""
        print("\n5. Checking timestamp consistency...")

        # Check for future timestamps
        from datetime import datetime

        result = await session.execute(
            select(SkillAssessment).where(
                SkillAssessment.created_at > datetime.utcnow()
            )
        )
        future_timestamps = result.scalars().all()

        if future_timestamps:
            self.log_issue(
                f"Found {len(future_timestamps)} assessments with future timestamps"
            )
            for assessment in future_timestamps[:5]:
                self.log_warning(
                    f"  Assessment {assessment.id}: created_at={assessment.created_at}"
                )
        else:
            print("✓ No future timestamps found")

        # Check for updated_at before created_at
        result = await session.execute(
            select(SkillAssessment).where(
                SkillAssessment.updated_at < SkillAssessment.created_at
            )
        )
        inconsistent_timestamps = result.scalars().all()

        if inconsistent_timestamps:
            self.log_issue(
                f"Found {len(inconsistent_timestamps)} assessments with "
                f"updated_at before created_at"
            )
        else:
            print("✓ All timestamps are consistent")

    async def check_database_stats(self, session):
        """Show database statistics."""
        print("\n6. Database statistics:")

        # Count assessments
        result = await session.execute(select(func.count(SkillAssessment.id)))
        total_assessments = result.scalar()
        print(f"  Total assessments: {total_assessments}")

        # Count by skill type
        result = await session.execute(
            select(SkillAssessment.skill_type, func.count(SkillAssessment.id)).group_by(
                SkillAssessment.skill_type
            )
        )
        for skill_type, count in result.fetchall():
            print(f"    - {skill_type.value}: {count}")

        # Count evidence
        result = await session.execute(select(func.count(Evidence.id)))
        total_evidence = result.scalar()
        print(f"  Total evidence records: {total_evidence}")

        # Count students
        result = await session.execute(select(func.count(Student.id)))
        total_students = result.scalar()
        print(f"  Total students: {total_students}")

        if total_students > 0:
            avg_assessments = total_assessments / total_students
            print(f"  Average assessments per student: {avg_assessments:.1f}")

    async def run_all_checks(self, session, fix_orphans: bool = False):
        """Run all integrity checks."""
        print("=" * 70)
        print("SKILL ASSESSMENT DATA INTEGRITY VERIFICATION")
        print("=" * 70)

        await self.check_database_stats(session)
        await self.check_score_ranges(session)
        await self.check_student_coverage(session)
        await self.check_orphaned_evidence(session, fix=fix_orphans)
        await self.check_evidence_linking(session)
        await self.check_timestamp_consistency(session)

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Issues found: {len(self.issues)}")
        print(f"Warnings: {len(self.warnings)}")

        if self.issues:
            print("\nCritical issues:")
            for issue in self.issues:
                print(f"  ✗ {issue}")

        if self.warnings and self.verbose:
            print("\nWarnings:")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  ⚠ {warning}")

        if not self.issues and not self.warnings:
            print("\n✓ All integrity checks passed! Data is healthy.")

        return len(self.issues) == 0


async def main():
    parser = argparse.ArgumentParser(
        description="Verify data integrity for skill assessments"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    parser.add_argument(
        "--fix-orphans",
        action="store_true",
        help="Automatically delete orphaned evidence records",
    )

    args = parser.parse_args()

    checker = IntegrityChecker(verbose=args.verbose)

    try:
        async with AsyncSessionLocal() as session:
            success = await checker.run_all_checks(
                session, fix_orphans=args.fix_orphans
            )

        if not success:
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error during verification: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
