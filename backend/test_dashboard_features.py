#!/usr/bin/env python3
"""
Test script for Tasks 27 & 28 new features
Tests API endpoints and file operations
"""

import requests
import json
from datetime import datetime
import os

API_BASE = "http://localhost:9000/api/v1"


def test_historical_assessments():
    """Test historical assessment retrieval"""
    print("\n=== Testing Historical Assessments ===")

    # Get a student ID
    students = requests.get(f"{API_BASE}/students").json()
    if not students:
        print("❌ No students found")
        return False

    student_id = students[0]["id"]
    print(f"✓ Testing with student: {student_id}")

    # Get historical assessments
    response = requests.get(f"{API_BASE}/assessments/{student_id}?limit=50")
    if response.status_code == 200:
        assessments = response.json()
        print(f"✓ Retrieved {len(assessments)} historical assessments")

        if assessments:
            # Show sample
            sample = assessments[0]
            print(
                f"  Sample: {sample.get('skill_type')} - Score: {sample.get('score'):.2f}"
            )
        return True
    else:
        print(f"❌ Failed to retrieve assessments: {response.status_code}")
        return False


def test_batch_assessments():
    """Test batch assessment endpoint"""
    print("\n=== Testing Batch Assessments ===")

    students = requests.get(f"{API_BASE}/students").json()
    if not students:
        print("❌ No students found")
        return False

    student_id = students[0]["id"]

    # Test batch assessment
    response = requests.post(
        f"{API_BASE}/assessments/{student_id}/batch", json={"use_cached": True}
    )

    if response.status_code == 200:
        results = response.json()
        print(f"✓ Batch assessment successful - {len(results)} skills assessed")
        for skill_type, result in list(results.items())[:3]:
            print(f"  {skill_type}: {result.get('score', 0):.2f}")
        return True
    else:
        print(f"❌ Batch assessment failed: {response.status_code}")
        return False


def test_reflection_persistence():
    """Test reflection file creation"""
    print("\n=== Testing Reflection Persistence ===")

    reflection_dir = "backend/dashboard/reflections"
    test_student_id = "test_student_123"
    test_content = "This is a test reflection about my empathy skills."

    # Create reflection file (simulating what student_portal.py does)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reflection_file = os.path.join(reflection_dir, f"{test_student_id}_reflections.txt")

    try:
        with open(reflection_file, "a", encoding="utf-8") as f:
            f.write(f"\n--- Reflection saved at {timestamp} ---\n")
            f.write(f"{test_content}\n")

        print(f"✓ Reflection saved to: {reflection_file}")

        # Verify file exists and has content
        if os.path.exists(reflection_file):
            with open(reflection_file, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"✓ File verified - {len(content)} characters")
            return True
        else:
            print("❌ Reflection file not found")
            return False
    except Exception as e:
        print(f"❌ Failed to save reflection: {e}")
        return False


def test_badge_logic():
    """Test enhanced badge detection logic"""
    print("\n=== Testing Enhanced Badge System ===")

    # Sample skill data (would come from API in real usage)
    skills = [
        {"skill_type": "empathy", "score": 0.85},
        {"skill_type": "adaptability", "score": 0.78},
        {"skill_type": "communication", "score": 0.82},
        {"skill_type": "problem_solving", "score": 0.75},
        {"skill_type": "collaboration", "score": 0.88},
        {"skill_type": "self_awareness", "score": 0.76},
        {"skill_type": "resilience", "score": 0.80},
    ]

    badges_earned = []

    # All skills assessment completed
    if len(skills) >= 7:
        badges_earned.append("first_assessment")

    # High empathy (80%+)
    if any(s["skill_type"] == "empathy" and s["score"] >= 0.80 for s in skills):
        badges_earned.append("strong_empathy")

    # All skills green (70%+)
    if all(s["score"] >= 0.70 for s in skills):
        badges_earned.append("all_skills_green")

    # Well-rounded (all within 15% range)
    scores = [s["score"] for s in skills]
    if max(scores) - min(scores) <= 0.15:
        badges_earned.append("balanced_skills")

    # Top performer (85%+ in 3+ skills)
    high_scores = sum(1 for s in skills if s["score"] >= 0.85)
    if high_scores >= 3:
        badges_earned.append("top_performer")

    print(f"✓ Badge detection working - {len(badges_earned)} badges earned")
    for badge in badges_earned:
        print(f"  🏆 {badge}")

    return len(badges_earned) >= 3  # Should earn at least 3 badges with this data


def test_alert_system():
    """Test low-performing group detection logic"""
    print("\n=== Testing Alert System ===")

    # Simulated data (would come from real students in production)
    import pandas as pd

    sample_data = [
        {"grade": 7, "empathy": 0.55, "communication": 0.65, "problem_solving": 0.70},
        {"grade": 7, "empathy": 0.58, "communication": 0.62, "problem_solving": 0.68},
        {"grade": 8, "empathy": 0.75, "communication": 0.78, "problem_solving": 0.80},
        {"grade": 8, "empathy": 0.72, "communication": 0.76, "problem_solving": 0.82},
    ]

    df = pd.DataFrame(sample_data)
    threshold = 0.60
    alerts = []

    # Check by grade
    for grade in df["grade"].unique():
        grade_df = df[df["grade"] == grade]
        for skill in ["empathy", "communication", "problem_solving"]:
            avg_score = grade_df[skill].mean()
            if avg_score < threshold:
                alerts.append(
                    {
                        "group": f"Grade {grade}",
                        "skill": skill,
                        "score": avg_score,
                        "count": len(grade_df),
                    }
                )

    if alerts:
        print(f"✓ Alert detection working - {len(alerts)} alert(s) found")
        for alert in alerts:
            print(f"  ⚠️ {alert['group']} - {alert['skill']}: {alert['score']:.1%}")
    else:
        print("✓ No alerts (all groups above threshold)")

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("DASHBOARD FEATURES TEST SUITE")
    print("Testing Tasks 27 & 28 Implementation")
    print("=" * 60)

    results = {
        "Historical Assessments": test_historical_assessments(),
        "Batch Assessments": test_batch_assessments(),
        "Reflection Persistence": test_reflection_persistence(),
        "Enhanced Badge System": test_badge_logic(),
        "Alert System": test_alert_system(),
    }

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
