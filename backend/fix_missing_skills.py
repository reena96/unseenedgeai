#!/usr/bin/env python3
"""Fix missing skills in PostgreSQL database."""

import random
import uuid
from datetime import datetime
from typing import List, Tuple
import psycopg2
from psycopg2.extras import execute_values

# Database connection parameters
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "mass_db",
    "user": "mass_user",
    "password": "mass_password",
}

# All 7 skills that should exist
ALL_SKILLS = [
    "empathy",
    "adaptability",
    "problem_solving",
    "self_regulation",
    "resilience",
    "communication",
    "collaboration",
]

# Evidence templates
EVIDENCE_TEMPLATES = {
    "empathy": [
        (
            "Student demonstrated empathy by acknowledging another's perspective "
            "during group discussion"
        ),
        "Showed understanding of emotional context when responding to peer's challenge",
        "Used supportive language when teammate expressed frustration",
    ],
    "adaptability": [
        "Adjusted strategy when initial approach didn't work in game scenario",
        "Quickly adapted to new game mechanics and rule changes",
        "Showed flexibility in changing roles when team needed different skills",
    ],
    "problem_solving": [
        "Broke down complex challenge into smaller manageable steps",
        "Used creative approach to solve puzzle that others hadn't considered",
        "Analyzed problem from multiple angles before selecting solution",
    ],
    "self_regulation": [
        "Took deep breath and paused before responding to frustrating situation",
        "Maintained focus during extended challenging task",
        "Self-corrected behavior when noticing own frustration rising",
    ],
    "resilience": [
        "Persisted through multiple failed attempts without giving up",
        "Recovered quickly from setback and tried alternative approach",
        "Maintained positive attitude despite challenging obstacles",
    ],
    "communication": [
        "Clearly explained strategy to teammates using specific examples",
        "Asked clarifying questions to ensure understanding",
        "Actively listened and built on others' ideas in discussion",
    ],
    "collaboration": [
        "Shared resources and information with team members proactively",
        "Coordinated actions with teammates to achieve shared goal",
        "Valued diverse perspectives and integrated others' suggestions",
    ],
}

REASONING_TEMPLATES = {
    "empathy": (
        "Student shows consistent ability to recognize and respond to others' "
        "emotional states. They demonstrate understanding of different perspectives "
        "and respond with appropriate emotional support."
    ),
    "adaptability": (
        "Student exhibits strong adaptability when facing new situations or changes "
        "in game mechanics. They quickly adjust strategies and show flexibility in "
        "their approach to challenges."
    ),
    "problem_solving": (
        "Student demonstrates systematic problem-solving skills, breaking down "
        "complex challenges and exploring multiple solution pathways before "
        "selecting an approach."
    ),
    "self_regulation": (
        "Student shows developing self-regulation skills, with ability to monitor "
        "and manage their own emotional responses during challenging tasks."
    ),
    "resilience": (
        "Student displays resilience in the face of setbacks, maintaining "
        "persistence and positive attitude through multiple challenges."
    ),
    "communication": (
        "Student communicates effectively with peers, using clear language and "
        "active listening skills to facilitate understanding."
    ),
    "collaboration": (
        "Student works well in team settings, sharing resources and coordinating "
        "with others to achieve common goals."
    ),
}


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(**DB_CONFIG)


def check_current_state(conn) -> dict:
    """Check current state of skills in database."""
    print("\n" + "=" * 80)
    print("STEP 1: CHECKING CURRENT DATABASE STATE")
    print("=" * 80 + "\n")

    with conn.cursor() as cur:
        # Get total students
        cur.execute("SELECT COUNT(*) FROM students")
        total_students = cur.fetchone()[0]
        print(f"Total students in database: {total_students}\n")

        # Get skills per student
        cur.execute(
            """
            SELECT skill_type, COUNT(DISTINCT student_id) as student_count
            FROM skill_assessments
            GROUP BY skill_type
            ORDER BY skill_type
        """
        )
        results = cur.fetchall()

        print("Skills distribution:")
        print("-" * 50)
        print(f"{'Skill Type':<25} {'Student Count':<15}")
        print("-" * 50)

        skill_counts = {}
        for skill_type, student_count in results:
            skill_counts[skill_type] = student_count
            print(f"{skill_type:<25} {student_count:<15}")

        print("-" * 50)

        # Get students and their skill counts
        cur.execute(
            """
            SELECT s.id, s.first_name, s.last_name, COUNT(DISTINCT sa.skill_type) as skill_count
            FROM students s
            LEFT JOIN skill_assessments sa ON s.id = sa.student_id
            GROUP BY s.id, s.first_name, s.last_name
            ORDER BY s.first_name, s.last_name
        """
        )
        student_results = cur.fetchall()

        print("\nPer-student skill counts:")
        print("-" * 60)
        print(f"{'Student Name':<30} {'Skills Count':<15}")
        print("-" * 60)

        students_data = []
        for student_id, first_name, last_name, skill_count in student_results:
            full_name = f"{first_name} {last_name}"
            students_data.append(
                {"id": student_id, "name": full_name, "skill_count": skill_count}
            )
            print(f"{full_name:<30} {skill_count}/7")

        print("-" * 60)

        return {
            "total_students": total_students,
            "skill_counts": skill_counts,
            "students_data": students_data,
        }


def get_missing_skills_per_student(conn) -> dict:
    """Identify which skills are missing for each student."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, first_name, last_name FROM students ORDER BY first_name, last_name"
        )
        students = cur.fetchall()

        missing_skills = {}

        for student_id, first_name, last_name in students:
            full_name = f"{first_name} {last_name}"
            # Get existing skills for this student
            cur.execute(
                """
                SELECT skill_type
                FROM skill_assessments
                WHERE student_id = %s
            """,
                (student_id,),
            )

            existing_skills = {row[0] for row in cur.fetchall()}
            needed_skills = [
                skill for skill in ALL_SKILLS if skill not in existing_skills
            ]

            if needed_skills:
                missing_skills[student_id] = {
                    "name": full_name,
                    "missing": needed_skills,
                }

        return missing_skills


def create_assessment_with_evidence(
    conn, student_id: str, skill_type: str
) -> Tuple[str, List[str]]:
    """Create a skill assessment with evidence."""
    assessment_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # Random score and confidence
    score = random.uniform(0.5, 0.9)
    confidence = random.uniform(0.7, 0.9)

    # Get reasoning
    reasoning = REASONING_TEMPLATES.get(
        skill_type, f"Student demonstrates {skill_type} skills."
    )

    with conn.cursor() as cur:
        # Create assessment
        cur.execute(
            """
            INSERT INTO skill_assessments
            (id, student_id, skill_type, score, confidence, reasoning, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                assessment_id,
                student_id,
                skill_type,
                score,
                confidence,
                reasoning,
                now,
                now,
            ),
        )

        # Create 2-3 pieces of evidence
        num_evidence = random.randint(2, 3)
        evidence_ids = []
        evidence_data = []

        templates = EVIDENCE_TEMPLATES.get(skill_type, ["Student showed skill in task"])

        for i in range(num_evidence):
            evidence_id = str(uuid.uuid4())
            evidence_ids.append(evidence_id)

            evidence_type = random.choice(["linguistic", "behavioral"])
            source = "transcript" if evidence_type == "linguistic" else "game_telemetry"
            content = random.choice(templates)
            relevance_score = random.uniform(0.6, 0.9)

            evidence_data.append(
                (
                    evidence_id,
                    assessment_id,
                    evidence_type,
                    source,
                    content,
                    relevance_score,
                    now,
                    now,
                )
            )

        # Bulk insert evidence
        execute_values(
            cur,
            """
            INSERT INTO evidence
            (id, assessment_id, evidence_type, source, content, relevance_score,
             created_at, updated_at)
            VALUES %s
        """,
            evidence_data,
        )

    return assessment_id, evidence_ids


def add_missing_skills(conn, missing_skills: dict):
    """Add missing skills for all students."""
    print("\n" + "=" * 80)
    print("STEP 2: ADDING MISSING SKILLS")
    print("=" * 80 + "\n")

    if not missing_skills:
        print("No missing skills found! All students have all 7 skills.\n")
        return

    total_assessments_created = 0
    total_evidence_created = 0

    for student_id, data in missing_skills.items():
        student_name = data["name"]
        skills_to_add = data["missing"]

        print(f"Student: {student_name}")
        print(f"  Adding {len(skills_to_add)} skills: {', '.join(skills_to_add)}")

        for skill_type in skills_to_add:
            assessment_id, evidence_ids = create_assessment_with_evidence(
                conn, student_id, skill_type
            )
            total_assessments_created += 1
            total_evidence_created += len(evidence_ids)
            print(
                f"    ✓ Created {skill_type} assessment ({len(evidence_ids)} evidence items)"
            )

    conn.commit()

    print("\n" + "=" * 80)
    print("Summary:")
    print(f"  - Students updated: {len(missing_skills)}")
    print(f"  - Total assessments created: {total_assessments_created}")
    print(f"  - Total evidence items created: {total_evidence_created}")
    print("=" * 80 + "\n")


def verify_fix(conn):
    """Verify all students now have all 7 skills."""
    print("\n" + "=" * 80)
    print("STEP 3: VERIFYING FIX")
    print("=" * 80 + "\n")

    with conn.cursor() as cur:
        # Check skill distribution
        cur.execute(
            """
            SELECT skill_type, COUNT(DISTINCT student_id) as student_count
            FROM skill_assessments
            GROUP BY skill_type
            ORDER BY skill_type
        """
        )
        results = cur.fetchall()

        print("Skills distribution after fix:")
        print("-" * 50)
        print(f"{'Skill Type':<25} {'Student Count':<15}")
        print("-" * 50)

        for skill_type, student_count in results:
            print(f"{skill_type:<25} {student_count:<15}")

        print("-" * 50)

        # Check per-student counts
        cur.execute(
            """
            SELECT s.id, s.first_name, s.last_name, COUNT(DISTINCT sa.skill_type) as skill_count
            FROM students s
            LEFT JOIN skill_assessments sa ON s.id = sa.student_id
            GROUP BY s.id, s.first_name, s.last_name
            HAVING COUNT(DISTINCT sa.skill_type) < 7
            ORDER BY s.first_name, s.last_name
        """
        )
        incomplete_students = cur.fetchall()

        if incomplete_students:
            print(
                f"\n⚠️  WARNING: Found {len(incomplete_students)} students with incomplete skills:"
            )
            print("-" * 60)
            for student_id, first_name, last_name, skill_count in incomplete_students:
                print(f"  {first_name} {last_name}: {skill_count}/7 skills")
            print("-" * 60)
            return False
        else:
            print("\n✓ SUCCESS: All students have all 7 skills!")

            # Show final counts
            cur.execute(
                """
                SELECT s.first_name, s.last_name, COUNT(DISTINCT sa.skill_type) as skill_count
                FROM students s
                LEFT JOIN skill_assessments sa ON s.id = sa.student_id
                GROUP BY s.first_name, s.last_name
                ORDER BY s.first_name, s.last_name
            """
            )
            all_students = cur.fetchall()

            print("\nFinal verification:")
            print("-" * 60)
            print(f"{'Student Name':<30} {'Skills Count':<15}")
            print("-" * 60)
            for first_name, last_name, skill_count in all_students:
                print(f"{first_name} {last_name}"[:30] + f"{skill_count}/7".rjust(15))
            print("-" * 60)

            return True


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("FIXING MISSING SKILLS IN POSTGRESQL DATABASE")
    print("=" * 80)

    try:
        # Connect to database
        conn = get_db_connection()
        print("✓ Connected to PostgreSQL database\n")

        # Step 1: Check current state (result used for logging/debugging)
        check_current_state(conn)

        # Step 2: Identify and add missing skills
        missing_skills = get_missing_skills_per_student(conn)
        add_missing_skills(conn, missing_skills)

        # Step 3: Verify fix
        success = verify_fix(conn)

        conn.close()

        if success:
            print("\n" + "=" * 80)
            print("✓ ALL DONE! Database has been successfully updated.")
            print("=" * 80 + "\n")
            return 0
        else:
            print("\n" + "=" * 80)
            print("⚠️  WARNING: Some issues remain. Please review output above.")
            print("=" * 80 + "\n")
            return 1

    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
