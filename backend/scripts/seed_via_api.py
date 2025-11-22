"""
Seed sample data via API endpoints (no direct database access needed).

This creates sample students and assessments by calling the FastAPI endpoints.
"""

import requests
import random
from datetime import datetime, timedelta
from typing import List, Dict

API_BASE_URL = "http://localhost:8080/api/v1"

# Sample data (same as before)
FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
    "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
    "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Michael",
    "Emily", "Daniel", "Elizabeth", "Matthew", "Sofia", "Jackson", "Avery",
    "Sebastian", "Ella", "David", "Scarlett", "Joseph", "Grace", "Samuel",
    "Chloe", "John", "Victoria", "Owen", "Riley", "Dylan", "Aria", "Luke",
    "Lily", "Gabriel", "Aubrey", "Anthony", "Zoey", "Isaac"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts"
]

SKILLS = [
    "empathy",
    "adaptability",
    "problem_solving",
    "self_regulation",
    "resilience",
    "communication",
    "collaboration"
]

EVIDENCE_TEMPLATES = {
    "empathy": [
        "Student showed understanding when classmate was upset. Offered support.",
        "Demonstrated active listening during discussion. Asked thoughtful questions.",
        "Helped new student feel welcome. Introduced them to classmates.",
    ],
    "adaptability": [
        "Quickly adjusted approach when initial strategy didn't work.",
        "Remained calm when schedule changed unexpectedly.",
        "Modified group role when teammate was absent.",
    ],
    "problem_solving": [
        "Broke down complex problem into smaller steps systematically.",
        "Generated multiple solutions and evaluated each one.",
        "Used trial and error effectively, documenting results.",
    ],
    "self_regulation": [
        "Took deep breath when frustrated. Returned with fresh perspective.",
        "Managed time well during test. Prioritized effectively.",
        "Stayed focused during independent work despite distractions.",
    ],
    "resilience": [
        "Persisted through challenging assignment after initial setback.",
        "Bounced back from disappointing grade with study plan.",
        "Maintained positive attitude when project didn't work as expected.",
    ],
    "communication": [
        "Explained reasoning clearly with specific examples.",
        "Listened actively and paraphrased to confirm understanding.",
        "Presented ideas in organized, understandable way.",
    ],
    "collaboration": [
        "Worked cooperatively with diverse team members.",
        "Shared leadership responsibilities in group project.",
        "Helped resolve conflict between teammates constructively.",
    ]
}


def create_student(first_name: str, last_name: str, grade: int, class_name: str) -> Dict:
    """Create a student via API."""
    student_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": f"{first_name.lower()}.{last_name.lower()}@school.edu",
        "grade_level": grade,
        "student_id_external": f"STU{random.randint(1000, 9999)}",
        "is_active": True
    }

    try:
        response = requests.post(f"{API_BASE_URL}/students", json=student_data)
        response.raise_for_status()
        print(f"✅ Created student: {first_name} {last_name} (Grade {grade})")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create student {first_name} {last_name}: {e}")
        return None


def generate_skill_scores() -> Dict[str, float]:
    """Generate realistic skill scores."""
    base_level = random.uniform(0.4, 0.9)
    scores = {}
    for skill in SKILLS:
        # Add variation around base level
        score = base_level + random.uniform(-0.15, 0.15)
        scores[skill] = max(0.2, min(1.0, score))
    return scores


def generate_evidence(skill: str, score: float) -> str:
    """Generate evidence text."""
    templates = EVIDENCE_TEMPLATES.get(skill, ["Demonstrated skill in class."])
    if score >= 0.8:
        prefix = "Strong evidence: "
    elif score >= 0.6:
        prefix = "Good evidence: "
    else:
        prefix = "Some evidence: "
    return prefix + random.choice(templates)


def create_assessment(student_id: str, days_ago: int) -> bool:
    """Create an assessment for a student."""
    skill_scores = generate_skill_scores()
    assessment_date = datetime.now() - timedelta(days=days_ago)

    # Create evidence for each skill
    evidence = {}
    for skill in SKILLS:
        evidence[skill] = {
            "transcript": generate_evidence(skill, skill_scores[skill]),
            "confidence": round(random.uniform(0.7, 0.95), 2),
            "context": f"Observed during {random.choice(['group work', 'discussion', 'project'])}"
        }

    assessment_data = {
        "student_id": student_id,
        "assessment_date": assessment_date.isoformat(),
        "skill_scores": skill_scores,
        "evidence": evidence,
        "overall_score": sum(skill_scores.values()) / len(skill_scores),
        "metadata": {
            "assessment_type": random.choice(["observation", "project", "discussion"]),
            "duration_minutes": random.randint(20, 45)
        }
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/assessments/{student_id}",
            json=assessment_data
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Failed to create assessment: {e}")
        return False


def seed_data():
    """Seed the database with sample data via API."""
    print("🌱 Seeding database via API...")
    print(f"   API URL: {API_BASE_URL}")

    # Test connection
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        print("✅ API connection successful\n")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure the FastAPI server is running on port 8080")
        return

    # Create students
    print("Creating 20 students...")
    students_created = []

    for i in range(20):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        grade = random.randint(6, 12)
        class_name = f"Class {grade}{random.choice(['A', 'B', 'C'])}"

        student = create_student(first_name, last_name, grade, class_name)
        if student:
            students_created.append(student)

    print(f"\n📊 Created {len(students_created)} students")

    # Create assessments
    print("\nCreating assessments...")
    total_assessments = 0

    for student in students_created:
        student_id = student.get('id')
        num_assessments = random.randint(3, 7)

        print(f"  Creating {num_assessments} assessments for {student.get('first_name')} {student.get('last_name')}...")

        for j in range(num_assessments):
            days_ago = int((120 / num_assessments) * j)
            if create_assessment(student_id, days_ago):
                total_assessments += 1

    print(f"\n✨ Seeding complete!")
    print(f"   • {len(students_created)} students")
    print(f"   • {total_assessments} assessments")
    print(f"   • Average {total_assessments / len(students_created):.1f} assessments per student")
    print("\nDashboards:")
    print("  • Teacher Dashboard: http://localhost:8501")
    print("  • Admin Dashboard: http://localhost:8502")
    print("  • Student Portal: http://localhost:8503")


if __name__ == "__main__":
    seed_data()
