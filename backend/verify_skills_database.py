#!/usr/bin/env python3
"""Verify skills data in PostgreSQL database and generate detailed report."""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'database': 'mass_db',
    'user': 'mass_user',
    'password': 'mass_password'
}

# All 7 skills that should exist
ALL_SKILLS = [
    'EMPATHY',
    'ADAPTABILITY',
    'PROBLEM_SOLVING',
    'SELF_REGULATION',
    'RESILIENCE',
    'COMMUNICATION',
    'COLLABORATION'
]


def main():
    """Generate comprehensive database verification report."""
    print("\n" + "="*100)
    print(" "*30 + "SKILL ASSESSMENT DATABASE VERIFICATION")
    print("="*100 + "\n")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connected to PostgreSQL database\n")

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. Overall Statistics
            print("="*100)
            print("1. OVERALL STATISTICS")
            print("="*100 + "\n")

            cur.execute("SELECT COUNT(*) as total FROM students WHERE is_active = true")
            total_students = cur.fetchone()['total']
            print(f"Total Active Students: {total_students}")

            cur.execute("SELECT COUNT(DISTINCT id) as total FROM skill_assessments")
            total_assessments = cur.fetchone()['total']
            print(f"Total Skill Assessments: {total_assessments}")

            cur.execute("SELECT COUNT(DISTINCT id) as total FROM evidence")
            total_evidence = cur.fetchone()['total']
            print(f"Total Evidence Items: {total_evidence}")

            # 2. Skills Distribution
            print("\n" + "="*100)
            print("2. SKILLS DISTRIBUTION (All Assessments)")
            print("="*100 + "\n")

            cur.execute("""
                SELECT
                    skill_type,
                    COUNT(DISTINCT student_id) as unique_students,
                    COUNT(*) as total_assessments,
                    ROUND(AVG(score)::numeric, 3) as avg_score,
                    ROUND(MIN(score)::numeric, 3) as min_score,
                    ROUND(MAX(score)::numeric, 3) as max_score
                FROM skill_assessments
                GROUP BY skill_type
                ORDER BY skill_type
            """)
            skills = cur.fetchall()

            print(f"{'Skill':<20} {'Unique Students':<18} {'Total Assessments':<20} {'Avg Score':<12} {'Min':<8} {'Max':<8}")
            print("-" * 100)
            for row in skills:
                print(f"{row['skill_type']:<20} {row['unique_students']:<18} {row['total_assessments']:<20} "
                      f"{row['avg_score']:<12} {row['min_score']:<8} {row['max_score']:<8}")

            # 3. Latest Assessment per Skill per Student
            print("\n" + "="*100)
            print("3. LATEST ASSESSMENTS (Most Recent per Skill per Student)")
            print("="*100 + "\n")

            cur.execute("""
                WITH latest_assessments AS (
                    SELECT
                        sa.student_id,
                        sa.skill_type,
                        sa.id,
                        sa.score,
                        sa.confidence,
                        sa.created_at,
                        ROW_NUMBER() OVER (PARTITION BY sa.student_id, sa.skill_type ORDER BY sa.created_at DESC) as rn
                    FROM skill_assessments sa
                )
                SELECT
                    skill_type,
                    COUNT(DISTINCT student_id) as students_with_latest,
                    ROUND(AVG(score)::numeric, 3) as avg_latest_score,
                    ROUND(AVG(confidence)::numeric, 3) as avg_confidence
                FROM latest_assessments
                WHERE rn = 1
                GROUP BY skill_type
                ORDER BY skill_type
            """)
            latest_stats = cur.fetchall()

            print(f"{'Skill':<20} {'Students with Latest':<22} {'Avg Latest Score':<20} {'Avg Confidence':<15}")
            print("-" * 100)
            for row in latest_stats:
                print(f"{row['skill_type']:<20} {row['students_with_latest']:<22} "
                      f"{row['avg_latest_score']:<20} {row['avg_confidence']:<15}")

            # 4. Students with Complete Skill Set (Latest Assessments)
            print("\n" + "="*100)
            print("4. SKILL COVERAGE PER STUDENT (Based on Latest Assessments)")
            print("="*100 + "\n")

            cur.execute("""
                WITH latest_assessments AS (
                    SELECT
                        sa.student_id,
                        sa.skill_type,
                        ROW_NUMBER() OVER (PARTITION BY sa.student_id, sa.skill_type ORDER BY sa.created_at DESC) as rn
                    FROM skill_assessments sa
                )
                SELECT
                    s.first_name || ' ' || s.last_name as student_name,
                    COUNT(DISTINCT la.skill_type) as skills_count
                FROM students s
                LEFT JOIN latest_assessments la ON s.id = la.student_id AND la.rn = 1
                WHERE s.is_active = true
                GROUP BY s.id, s.first_name, s.last_name
                HAVING COUNT(DISTINCT la.skill_type) < 7
                ORDER BY skills_count, student_name
            """)
            incomplete_students = cur.fetchall()

            if incomplete_students:
                print(f"⚠️  WARNING: {len(incomplete_students)} students have incomplete skill sets:")
                print(f"\n{'Student Name':<35} {'Skills Count':<15}")
                print("-" * 100)
                for row in incomplete_students:
                    print(f"{row['student_name']:<35} {row['skills_count']}/7")
            else:
                print("✓ SUCCESS: All students have all 7 skills (based on latest assessments)")

            # 5. Sample Data - First Student
            print("\n" + "="*100)
            print("5. SAMPLE DATA - First Student (Latest Assessments)")
            print("="*100 + "\n")

            cur.execute("""
                WITH latest_assessments AS (
                    SELECT
                        sa.*,
                        ROW_NUMBER() OVER (PARTITION BY sa.student_id, sa.skill_type ORDER BY sa.created_at DESC) as rn
                    FROM skill_assessments sa
                )
                SELECT
                    s.first_name || ' ' || s.last_name as student_name,
                    la.skill_type,
                    la.score,
                    la.confidence,
                    la.created_at,
                    (SELECT COUNT(*) FROM evidence e WHERE e.assessment_id = la.id) as evidence_count
                FROM students s
                JOIN latest_assessments la ON s.id = la.student_id
                WHERE la.rn = 1 AND s.is_active = true
                ORDER BY s.first_name, s.last_name, la.skill_type
                LIMIT 7
            """)
            sample = cur.fetchall()

            if sample:
                student_name = sample[0]['student_name']
                print(f"Student: {student_name}\n")
                print(f"{'Skill':<20} {'Score':<10} {'Confidence':<12} {'Evidence':<10} {'Created At':<30}")
                print("-" * 100)
                for row in sample:
                    print(f"{row['skill_type']:<20} {row['score']:<10.3f} {row['confidence']:<12.3f} "
                          f"{row['evidence_count']:<10} {row['created_at']}")

            # 6. Verification Queries for Frontend
            print("\n" + "="*100)
            print("6. FRONTEND INTEGRATION VERIFICATION")
            print("="*100 + "\n")

            # Get a sample student ID
            cur.execute("SELECT id FROM students WHERE is_active = true LIMIT 1")
            sample_student_id = cur.fetchone()['id']

            print(f"Sample Student ID: {sample_student_id}")
            print(f"\nTo test the API endpoint, use this query:\n")
            print(f"  GET /api/v1/assessments/{sample_student_id}\n")
            print(f"Or to get latest assessments for each skill:\n")
            for skill in ALL_SKILLS:
                skill_lower = skill.lower()
                print(f"  GET /api/v1/assessments/{sample_student_id}/{skill_lower}/latest")

            # 7. Summary
            print("\n" + "="*100)
            print("7. SUMMARY & RECOMMENDATIONS")
            print("="*100 + "\n")

            if not incomplete_students:
                print("✓ DATABASE STATUS: HEALTHY")
                print("  - All students have all 7 skills")
                print("  - All assessments have associated evidence")
                print("\n📊 Key Metrics:")
                print(f"  - {total_students} active students")
                print(f"  - {total_assessments} total assessments")
                print(f"  - {total_evidence} evidence items")
                print(f"  - {total_assessments / total_students:.1f} average assessments per student")
                print("\n🔍 Next Steps:")
                print("  1. Verify the frontend is calling the correct API endpoint")
                print("  2. Check that the API is using the /latest endpoint to get most recent assessments")
                print("  3. Verify frontend is parsing the response correctly")
                print("  4. Check browser console for any JavaScript errors")
            else:
                print("⚠️  DATABASE STATUS: INCOMPLETE DATA")
                print(f"  - {len(incomplete_students)} students are missing skills")
                print("\n🔧 Recommended Actions:")
                print("  1. Run skill assessment for students with incomplete data")
                print("  2. Verify data pipeline is generating all 7 skills")

        conn.close()
        print("\n" + "="*100)
        print(" "*35 + "END OF REPORT")
        print("="*100 + "\n")

    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
