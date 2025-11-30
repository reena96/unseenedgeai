#!/usr/bin/env python3
"""Generate sample API response for dashboard skills display."""

import json
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "mass_db",
    "user": "mass_user",
    "password": "mass_password",
}


def get_latest_assessments_for_student(student_id: str) -> dict:
    """Simulate what the API should return for a student's latest assessments."""
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get student info
            cur.execute(
                """
                SELECT id, first_name, last_name, grade_level
                FROM students
                WHERE id = %s
            """,
                (student_id,),
            )
            student = cur.fetchone()

            if not student:
                return {"error": "Student not found"}

            # Get latest assessment for each skill
            cur.execute(
                """
                WITH latest_assessments AS (
                    SELECT
                        sa.*,
                        ROW_NUMBER() OVER (
                            PARTITION BY sa.skill_type
                            ORDER BY sa.created_at DESC
                        ) as rn
                    FROM skill_assessments sa
                    WHERE sa.student_id = %s
                )
                SELECT
                    id,
                    skill_type,
                    score,
                    confidence,
                    reasoning,
                    recommendations,
                    created_at,
                    updated_at
                FROM latest_assessments
                WHERE rn = 1
                ORDER BY skill_type
            """,
                (student_id,),
            )
            assessments = cur.fetchall()

            # Get evidence for each assessment
            assessment_responses = []
            for assessment in assessments:
                cur.execute(
                    """
                    SELECT
                        id,
                        evidence_type,
                        source,
                        content,
                        relevance_score
                    FROM evidence
                    WHERE assessment_id = %s
                    ORDER BY relevance_score DESC
                """,
                    (assessment["id"],),
                )
                evidence = cur.fetchall()

                assessment_responses.append(
                    {
                        "id": assessment["id"],
                        "student_id": student_id,
                        "skill_type": assessment["skill_type"],
                        "score": float(assessment["score"]),
                        "confidence": float(assessment["confidence"]),
                        "reasoning": assessment["reasoning"],
                        "recommendations": assessment["recommendations"],
                        "evidence": [
                            {
                                "id": e["id"],
                                "evidence_type": e["evidence_type"],
                                "source": e["source"],
                                "content": e["content"],
                                "relevance_score": float(e["relevance_score"]),
                            }
                            for e in evidence
                        ],
                        "created_at": assessment["created_at"].isoformat(),
                        "updated_at": assessment["updated_at"].isoformat(),
                    }
                )

            return {
                "student": {
                    "id": student["id"],
                    "first_name": student["first_name"],
                    "last_name": student["last_name"],
                    "grade_level": student["grade_level"],
                },
                "assessments": assessment_responses,
                "overall_score": (
                    sum(a["score"] for a in assessment_responses)
                    / len(assessment_responses)
                    if assessment_responses
                    else 0
                ),
                "total_skills": len(assessment_responses),
            }

    finally:
        conn.close()


def main():
    """Generate sample API responses."""
    print("\n" + "=" * 100)
    print(" " * 30 + "SAMPLE API RESPONSES FOR DASHBOARD")
    print("=" * 100 + "\n")

    # Get first student
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, first_name, last_name FROM students "
        "WHERE is_active = true ORDER BY first_name LIMIT 1"
    )
    student_id, first_name, last_name = cur.fetchone()
    cur.close()
    conn.close()

    print(f"Student: {first_name} {last_name} (ID: {student_id})\n")

    # Get latest assessments
    response = get_latest_assessments_for_student(student_id)

    print("=" * 100)
    print("EXPECTED API RESPONSE FORMAT")
    print("=" * 100 + "\n")

    # Print formatted JSON
    print(json.dumps(response, indent=2, default=str))

    print("\n" + "=" * 100)
    print("SKILLS SUMMARY")
    print("=" * 100 + "\n")

    if "assessments" in response:
        print(f"Total Skills: {len(response['assessments'])}/7")
        print(f"Overall Score: {response['overall_score']:.3f}")
        print(
            f"\n{'Skill':<20} {'Score':<10} {'Confidence':<12} {'Evidence Count':<15}"
        )
        print("-" * 100)
        for assessment in response["assessments"]:
            print(
                f"{assessment['skill_type']:<20} {assessment['score']:<10.3f} "
                f"{assessment['confidence']:<12.3f} {len(assessment['evidence']):<15}"
            )

    print("\n" + "=" * 100)
    print("FRONTEND INTEGRATION NOTES")
    print("=" * 100 + "\n")

    print("The frontend should:")
    print("1. Make a GET request to: /api/v1/assessments/{student_id}")
    print("2. Parse the response to extract the 7 skills")
    print("3. Display each skill with its score and confidence")
    print("4. Use the skill_type field (lowercase) for display:")
    print("   - EMPATHY → Empathy")
    print("   - ADAPTABILITY → Adaptability")
    print("   - PROBLEM_SOLVING → Problem Solving")
    print("   - SELF_REGULATION → Self Regulation")
    print("   - RESILIENCE → Resilience")
    print("   - COMMUNICATION → Communication")
    print("   - COLLABORATION → Collaboration")
    print("\nAlternatively, to get latest assessments one by one:")
    print("GET /api/v1/assessments/{student_id}/empathy/latest")
    print("GET /api/v1/assessments/{student_id}/adaptability/latest")
    print("... and so on for all 7 skills")

    print("\n" + "=" * 100)
    print(" " * 35 + "END OF REPORT")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()
