#!/usr/bin/env python3
"""Test script to verify progress chart functionality with real API data"""

import requests
from datetime import datetime

API_URL = "http://localhost:8080/api/v1"
TEST_STUDENT_ID = "427d8809-b729-4ef6-b91e-b7d6c53ee95a"  # Noah from seed data


def test_api_data():
    """Test that API returns assessment data with timestamps"""
    print("=" * 60)
    print("Testing API Endpoint")
    print("=" * 60)

    url = f"{API_URL}/assessments/{TEST_STUDENT_ID}"
    params = {"limit": 100}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        assessments = response.json()

        print(f"\n✅ Successfully fetched {len(assessments)} assessments")

        # Check data structure
        if assessments:
            first = assessments[0]
            print("\n📋 Sample assessment structure:")
            print(f"   - ID: {first.get('id')}")
            print(f"   - Student ID: {first.get('student_id')}")
            print(f"   - Skill Type: {first.get('skill_type')}")
            print(f"   - Score: {first.get('score')}")
            print(f"   - Confidence: {first.get('confidence')}")
            print(f"   - Created At: {first.get('created_at')}")
            print(f"   - Evidence Count: {len(first.get('evidence', []))}")

            # Check timestamp parsing
            created_at = first.get("created_at")
            if isinstance(created_at, str):
                timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                print(f"\n✅ Timestamp parsed successfully: {timestamp}")

            # Group by skill type
            skills = {}
            for a in assessments:
                skill_type = a.get("skill_type")
                if skill_type not in skills:
                    skills[skill_type] = []
                skills[skill_type].append(a)

            print("\n📊 Assessments by skill type:")
            for skill, skill_assessments in sorted(skills.items()):
                print(f"   - {skill}: {len(skill_assessments)} assessments")

            # Check date range
            dates = [a.get("created_at") for a in assessments if a.get("created_at")]
            if dates:
                earliest = min(dates)
                latest = max(dates)
                print("\n📅 Date range:")
                print(f"   - Earliest: {earliest}")
                print(f"   - Latest: {latest}")

            return True
        else:
            print("\n⚠️  No assessments found for student")
            return False

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error fetching data: {e}")
        return False


def test_progress_chart_logic():
    """Test the progress chart data processing logic"""
    print("\n" + "=" * 60)
    print("Testing Progress Chart Logic")
    print("=" * 60)

    # Fetch real data
    url = f"{API_URL}/assessments/{TEST_STUDENT_ID}"
    response = requests.get(url, params={"limit": 100}, timeout=10)
    historical_data = response.json()

    SKILLS = [
        "empathy",
        "adaptability",
        "problem_solving",
        "self_regulation",
        "resilience",
        "communication",
        "collaboration",
    ]

    # Group assessments by skill type and date
    skill_history = {skill: [] for skill in SKILLS}

    for assessment in historical_data:
        skill_type = assessment.get("skill_type")
        created_at = assessment.get("created_at")
        score = assessment.get("score")

        if not all([skill_type, created_at, score is not None]):
            continue

        # Parse timestamp
        if isinstance(created_at, str):
            try:
                timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except ValueError:
                continue
        else:
            timestamp = created_at

        # Store data point
        if skill_type in skill_history:
            skill_history[skill_type].append({"timestamp": timestamp, "score": score})

    # Sort each skill's data by timestamp
    for skill in skill_history:
        skill_history[skill].sort(key=lambda x: x["timestamp"])

    print("\n📈 Processed data for chart:")
    for skill in SKILLS:
        if skill_history[skill]:
            count = len(skill_history[skill])
            scores = [d["score"] for d in skill_history[skill]]
            avg_score = sum(scores) / len(scores)
            print(f"   - {skill}: {count} data points, avg score: {avg_score:.2f}")
        else:
            print(f"   - {skill}: No data")

    # Check if we have data for plotting
    has_data = any(len(skill_history[skill]) > 0 for skill in SKILLS)

    if has_data:
        print("\n✅ Progress chart data processing successful!")
        return True
    else:
        print("\n⚠️  No data available for progress chart")
        return False


if __name__ == "__main__":
    print("\n🧪 Testing Progress Chart Functionality\n")

    api_ok = test_api_data()

    if api_ok:
        chart_ok = test_progress_chart_logic()

        if chart_ok:
            print("\n" + "=" * 60)
            print("✅ All tests passed!")
            print("=" * 60)
            print("\nThe dashboard progress chart should now work with real data.")
            print("You can view it by:")
            print("1. Starting the dashboard: streamlit run dashboard/app_template.py")
            print("2. Logging in (teacher/password123)")
            print("3. Going to 'Progress Tracking' tab")
            print("4. Selecting a student and clicking 'Load Progress'\n")
        else:
            print("\n⚠️  Chart logic test failed")
    else:
        print("\n❌ API test failed - make sure backend is running")
        print("   Start it with: ./scripts/start-api.sh\n")
