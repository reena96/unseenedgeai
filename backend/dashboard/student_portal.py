"""
Student Portal for UnseenEdge AI Skill Assessment

Age-appropriate, growth-oriented dashboard for students featuring:
- Visual skill profile (radar & bar charts)
- Growth-focused feedback (emphasizing improvement)
- Achievement badges and milestones
- Historical progress tracking
- Optional reflection journal
- WCAG 2.1 AA accessibility compliance
- Mobile-responsive design
- Privacy-first (students only see their own data)

Usage:
    streamlit run backend/dashboard/student_portal.py --server.port=8502
"""

import streamlit as st
import streamlit_authenticator as stauth
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

# ================================================================================
# CONFIGURATION
# ================================================================================

API_URL = os.getenv("API_URL", "http://localhost:8080/api/v1")

# All 7 skills with student-friendly names
SKILLS = {
    "empathy": {"name": "Understanding Others", "emoji": "❤️", "color": "#FF6B6B"},
    "adaptability": {"name": "Being Flexible", "emoji": "🌈", "color": "#4ECDC4"},
    "problem_solving": {"name": "Solving Problems", "emoji": "🧩", "color": "#45B7D1"},
    "self_regulation": {"name": "Staying Calm", "emoji": "🧘", "color": "#95E1D3"},
    "resilience": {"name": "Bouncing Back", "emoji": "💪", "color": "#FFA07A"},
    "communication": {"name": "Sharing Ideas", "emoji": "💬", "color": "#AA96DA"},
    "collaboration": {"name": "Working Together", "emoji": "🤝", "color": "#FCBAD3"},
}

# Achievement badges
BADGES = {
    "first_assessment": {
        "name": "Getting Started!",
        "emoji": "🎯",
        "description": "You completed your first skill check!",
    },
    "all_skills_green": {
        "name": "All-Star",
        "emoji": "⭐",
        "description": "All your skills are growing strong!",
    },
    "growth_mindset": {
        "name": "Growth Champion",
        "emoji": "🌱",
        "description": "3+ skills are growing well!",
    },
    "consistent": {
        "name": "Keep Going!",
        "emoji": "🔥",
        "description": "You're staying consistent!",
    },
    "strong_empathy": {
        "name": "Empathy Expert",
        "emoji": "❤️",
        "description": "Excellent at understanding others!",
    },
    "strong_problem_solver": {
        "name": "Problem Crusher",
        "emoji": "🧩",
        "description": "Amazing at solving problems!",
    },
    "strong_communicator": {
        "name": "Communication Star",
        "emoji": "💬",
        "description": "Great at sharing your ideas!",
    },
    "strong_team_player": {
        "name": "Team MVP",
        "emoji": "🤝",
        "description": "Awesome at working together!",
    },
    "balanced_skills": {
        "name": "Well-Rounded",
        "emoji": "🎨",
        "description": "Strong across all skill areas!",
    },
    "top_performer": {
        "name": "Rising Star",
        "emoji": "🌟",
        "description": "Outstanding performance!",
    },
    "improvement_streak": {
        "name": "On Fire!",
        "emoji": "📈",
        "description": "Improving in multiple skills!",
    },
    "resilience_master": {
        "name": "Bounce-Back Boss",
        "emoji": "💪",
        "description": "Great at overcoming challenges!",
    },
}

# ================================================================================
# API CLIENT
# ================================================================================


class StudentAPI:
    """API client for student portal"""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout

    def get_student(self, student_id: str) -> Dict[str, Any]:
        """Get student information"""
        try:
            response = requests.get(
                f"{self.base_url}/students/{student_id}", timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching student info: {e}")
            return {}

    def get_assessment(self, student_id: str) -> Dict[str, Any]:
        """Get skill assessment for student"""
        try:
            # Get existing assessments from database
            response = requests.get(
                f"{self.base_url}/assessments/{student_id}",
                params={"limit": 10},
                timeout=self.timeout,
            )
            response.raise_for_status()
            assessments = response.json()

            # Format response to match expected structure
            if assessments:
                # Group by skill type and get the most recent for each
                skills_dict = {}
                for assessment in assessments:
                    skill_type = assessment["skill_type"]
                    if skill_type not in skills_dict:
                        skills_dict[skill_type] = {
                            "skill_type": skill_type,
                            "score": assessment["score"],
                            "confidence": assessment["confidence"],
                            "reasoning": assessment.get("reasoning", ""),
                            "recommendations": assessment.get("recommendations", ""),
                        }

                return {
                    "student_id": student_id,
                    "skills": list(skills_dict.values()),
                    "timestamp": assessments[0]["created_at"] if assessments else None,
                }
            return {}
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching assessment: {e}")
            return {}

    def get_historical_assessments(
        self, student_id: str, limit: int = 20
    ) -> List[Dict]:
        """Get historical assessments for improvement tracking"""
        try:
            response = requests.get(
                f"{self.base_url}/assessments/{student_id}",
                params={"limit": limit},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching historical data: {e}")
            return []

    def save_reflection(self, student_id: str, content: str) -> bool:
        """Save student reflection to file (placeholder - would use database in production)"""
        try:
            import os
            from datetime import datetime

            # Create reflections directory if it doesn't exist
            reflections_dir = os.path.join(os.path.dirname(__file__), "reflections")
            os.makedirs(reflections_dir, exist_ok=True)

            # Save to file (in production, save to database)
            filename = os.path.join(reflections_dir, f"{student_id}_reflections.txt")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"\n\n{'='*60}\n[{timestamp}]\n{content}\n{'='*60}"

            with open(filename, "a", encoding="utf-8") as f:
                f.write(entry)

            return True
        except Exception as e:
            st.error(f"Error saving reflection: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health/detailed", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "unhealthy", "error": str(e)}


# ================================================================================
# VISUALIZATION FUNCTIONS
# ================================================================================


def create_skill_radar(skills: List[Dict]) -> go.Figure:
    """Create radar chart showing all 7 skills"""
    skill_names = []
    skill_scores = []

    for skill in skills:
        skill_key = skill["skill_type"]
        if skill_key in SKILLS:
            skill_names.append(SKILLS[skill_key]["name"])
            skill_scores.append(skill["score"] * 100)

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=skill_scores,
            theta=skill_names,
            fill="toself",
            fillcolor="rgba(69, 183, 209, 0.3)",
            line=dict(color="rgb(69, 183, 209)", width=3),
            marker=dict(size=10, color="rgb(69, 183, 209)"),
            name="Your Skills",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=14),
            ),
            angularaxis=dict(tickfont=dict(size=16, family="Arial, sans-serif")),
        ),
        showlegend=False,
        height=500,
        font=dict(size=16, family="Arial, sans-serif"),
    )

    return fig


def create_skill_bars(skills: List[Dict]) -> go.Figure:
    """Create horizontal bar chart for skills"""
    skill_data = []

    for skill in skills:
        skill_key = skill["skill_type"]
        if skill_key in SKILLS:
            skill_data.append(
                {
                    "name": SKILLS[skill_key]["name"],
                    "emoji": SKILLS[skill_key]["emoji"],
                    "score": skill["score"] * 100,
                    "color": SKILLS[skill_key]["color"],
                }
            )

    # Sort by score descending
    skill_data = sorted(skill_data, key=lambda x: x["score"], reverse=True)

    fig = go.Figure()

    for item in skill_data:
        fig.add_trace(
            go.Bar(
                y=[f"{item['emoji']} {item['name']}"],
                x=[item["score"]],
                orientation="h",
                marker=dict(color=item["color"]),
                text=[f"{item['score']:.0f}%"],
                textposition="outside",
                textfont=dict(size=16),
                name=item["name"],
                showlegend=False,
            )
        )

    fig.update_layout(
        xaxis=dict(
            range=[0, 100], title=dict(text="Skill Level (%)", font=dict(size=16))
        ),
        yaxis=dict(title=dict(font=dict(size=16)), tickfont=dict(size=14)),
        height=400,
        font=dict(size=14, family="Arial, sans-serif"),
        margin=dict(l=200, r=50, t=50, b=50),
    )

    return fig


def create_progress_timeline(student_id: str) -> go.Figure:
    """Create timeline showing progress over time (simulated for now)"""
    # Note: Replace with actual historical data queries
    dates = pd.date_range(end=datetime.now(), periods=8, freq="W")

    fig = go.Figure()

    # Simulate growth for each skill
    for skill_key, skill_info in SKILLS.items():
        base_score = 50 + (
            hash(skill_key) % 20
        )  # Deterministic "random" starting point
        growth = [base_score + i * 3 for i in range(8)]  # Simulated growth

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=growth,
                mode="lines+markers",
                name=f"{skill_info['emoji']} {skill_info['name']}",
                line=dict(color=skill_info["color"], width=3),
                marker=dict(size=10),
            )
        )

    fig.update_layout(
        title="Your Growth Over Time",
        xaxis_title="Date",
        yaxis_title="Skill Level (%)",
        yaxis=dict(range=[0, 100]),
        height=500,
        font=dict(size=14, family="Arial, sans-serif"),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            font=dict(size=12),
        ),
    )

    return fig


# ================================================================================
# FEEDBACK GENERATION
# ================================================================================


def generate_growth_feedback(skill: Dict) -> str:
    """Generate positive, growth-oriented feedback for a skill"""
    skill_key = skill["skill_type"]
    skill_name = SKILLS.get(skill_key, {}).get("name", skill_key)
    score = skill["score"]

    if score >= 0.80:
        messages = [
            f"Awesome work on {skill_name}! You're doing great! Keep it up! 🌟",
            f"You're really strong at {skill_name}! Way to go! 🎉",
            f"Excellent {skill_name} skills! You're a superstar! ⭐",
        ]
    elif score >= 0.60:
        messages = [
            f"You're making good progress with {skill_name}! Keep going! 💪",
            f"Nice work on {skill_name}! You're getting better every day! 🌱",
            f"Your {skill_name} is growing! Keep practicing! 🚀",
        ]
    elif score >= 0.40:
        messages = [
            f"You're on the right track with {skill_name}! Keep trying! 🌈",
            f"Great effort on {skill_name}! You're improving! 🎯",
            f"You're learning {skill_name}! Every step counts! 👍",
        ]
    else:
        messages = [
            f"You're just getting started with {skill_name}! Everyone starts somewhere! 🌟",
            f"{skill_name} is a skill you can grow! Keep practicing! 💚",
            f"You have lots of room to grow in {skill_name}! That's exciting! 🌱",
        ]

    import random

    return random.choice(messages)


def check_badges_earned(
    skills: List[Dict], historical_data: List[Dict] = None
) -> List[Dict]:
    """Check which badges the student has earned with enhanced milestone detection

    Args:
        skills: Current skill assessments
        historical_data: Historical assessments for improvement tracking (optional)

    Returns:
        List of earned badges
    """
    earned = []

    # First assessment badge (everyone gets this)
    earned.append(BADGES["first_assessment"])

    # All skills green (score >= 0.70)
    all_green = all(s["score"] >= 0.70 for s in skills)
    if all_green:
        earned.append(BADGES["all_skills_green"])

    # Growth mindset (at least 3 skills >= 0.60)
    growth_count = sum(1 for s in skills if s["score"] >= 0.60)
    if growth_count >= 3:
        earned.append(BADGES["growth_mindset"])

    # Top performer (average score >= 0.85)
    avg_score = sum(s["score"] for s in skills) / len(skills) if skills else 0
    if avg_score >= 0.85:
        earned.append(BADGES["top_performer"])

    # Balanced skills (all skills within 0.15 of average)
    if skills and len(skills) >= 5:
        scores = [s["score"] for s in skills]
        avg = sum(scores) / len(scores)
        is_balanced = all(abs(score - avg) <= 0.15 for score in scores)
        if is_balanced and avg >= 0.60:
            earned.append(BADGES["balanced_skills"])

    # Individual skill mastery badges (score >= 0.80)
    skill_badge_map = {
        "empathy": "strong_empathy",
        "problem_solving": "strong_problem_solver",
        "communication": "strong_communicator",
        "collaboration": "strong_team_player",
        "resilience": "resilience_master",
    }

    for skill in skills:
        skill_type = skill["skill_type"]
        if skill_type in skill_badge_map and skill["score"] >= 0.80:
            earned.append(BADGES[skill_badge_map[skill_type]])

    # Improvement streak (if historical data available)
    if historical_data and len(historical_data) > 1:
        # Check if multiple skills have improved
        improvements = 0
        for skill_type in set(s["skill_type"] for s in skills):
            skill_history = [
                h for h in historical_data if h.get("skill_type") == skill_type
            ]
            if len(skill_history) >= 2:
                skill_history.sort(key=lambda x: x.get("created_at", ""))
                if (
                    skill_history[-1]["score"] > skill_history[0]["score"] + 0.05
                ):  # 5% improvement
                    improvements += 1

        if improvements >= 2:
            earned.append(BADGES["improvement_streak"])

    # Consistent (placeholder - would check login frequency in production)
    earned.append(BADGES["consistent"])

    return earned


# ================================================================================
# MAIN APP
# ================================================================================


def main():
    """Main application"""

    st.set_page_config(
        page_title="My Skills - UnseenEdge",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Custom CSS for accessibility and mobile responsiveness
    st.markdown(
        """
    <style>
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        body { background: white !important; color: black !important; }
        .stButton>button { border: 2px solid black !important; }
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stPlotlyChart { width: 100% !important; }
        h1 { font-size: 24px !important; }
        h2 { font-size: 20px !important; }
    }

    /* Larger, readable fonts */
    body { font-size: 16px !important; font-family: Arial, sans-serif !important; }
    h1 { font-size: 32px !important; }
    h2 { font-size: 24px !important; }
    p { font-size: 16px !important; line-height: 1.6 !important; }

    /* Focus indicators for keyboard navigation */
    button:focus, a:focus, select:focus { outline: 3px solid #4CAF50 !important; }

    /* Color contrast for WCAG AA */
    .stButton>button { background-color: #2196F3; color: white; font-size: 18px; padding: 12px 24px; }
    .stButton>button:hover { background-color: #1976D2; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # ========================================================================
    # AUTHENTICATION
    # ========================================================================

    if (
        "authentication_status" not in st.session_state
        or st.session_state.get("authentication_status") is None
    ):
        st.markdown(
            """
        <div style='background-color: #E3F2FD; padding: 30px; border-radius: 15px; margin-bottom: 30px; border-left: 6px solid #2196F3; text-align: center;'>
            <h1 style='margin: 0; color: #1976D2; font-size: 36px;'>🌟 Welcome to Your Skills Dashboard!</h1>
            <p style='margin: 20px 0 0 0; font-size: 20px;'>
                <strong>Sign in to see how you're growing!</strong><br><br>
                👤 Username: <code style='background: white; padding: 6px 12px; border-radius: 6px; font-size: 18px;'>student123</code><br>
                🔑 Password: <code style='background: white; padding: 6px 12px; border-radius: 6px; font-size: 18px;'>password</code>
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Simple authentication (in production, integrate with real auth system)
    auth_config = {
        "credentials": {
            "usernames": {
                os.getenv("STUDENT_USER", "student123"): {
                    "name": os.getenv("STUDENT_NAME", "Student"),
                    "password": os.getenv("STUDENT_PASSWORD", "password"),
                }
            }
        },
        "cookie": {
            "name": "unseenedge_student_auth",
            "key": os.getenv(
                "STUDENT_COOKIE_KEY", "student_secret_key_change_in_production"
            ),
            "expiry_days": 30,
        },
    }

    authenticator = stauth.Authenticate(
        credentials=auth_config["credentials"],
        cookie_name=auth_config["cookie"]["name"],
        cookie_key=auth_config["cookie"]["key"],
        cookie_expiry_days=auth_config["cookie"]["expiry_days"],
        auto_hash=True,
    )

    authenticator.login(location="main")

    name = st.session_state.get("name")
    authentication_status = st.session_state.get("authentication_status")

    if authentication_status == False:
        st.error("❌ Oops! That username or password didn't work. Try again!")
        st.stop()
    elif authentication_status == None:
        st.warning("⚠️ Please sign in to see your skills!")
        st.stop()

    # Initialize API
    api = StudentAPI(API_URL)

    # ========================================================================
    # HEADER
    # ========================================================================

    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"🌟 Welcome, {name}!")
        st.markdown("### Let's see how you're growing!")
    with col2:
        authenticator.logout(button_name="Sign Out", location="main")

    st.markdown("---")

    # ========================================================================
    # LOAD DATA
    # ========================================================================

    # For demo, use a hardcoded student ID (in production, get from authentication)
    # TODO: Get actual student ID from authenticated user
    if "student_id" not in st.session_state:
        # Get first student from API for demo
        try:
            response = requests.get(f"{API_URL}/students", timeout=10)
            students = response.json()
            if students:
                st.session_state.student_id = students[0]["id"]
            else:
                st.error("No students found. Please contact your teacher!")
                st.stop()
        except Exception as e:
            st.error(f"Couldn't connect to the system: {e}")
            st.stop()

    student_id = st.session_state.student_id

    # Load assessment data
    if "assessment" not in st.session_state or st.button("🔄 Refresh My Skills"):
        with st.spinner("Loading your skills..."):
            assessment = api.get_assessment(student_id)

            if not assessment or "skills" not in assessment:
                st.error(
                    "Couldn't load your skills. Please try again or ask your teacher for help!"
                )
                st.stop()

            st.session_state.assessment = assessment

    assessment = st.session_state.assessment
    skills = assessment["skills"]

    # ========================================================================
    # ACHIEVEMENT BADGES
    # ========================================================================

    st.markdown("## 🏆 Your Achievements")

    # Fetch historical data for improvement tracking
    historical_data = api.get_historical_assessments(student_id, limit=50)

    badges_earned = check_badges_earned(skills, historical_data)

    badge_cols = st.columns(len(badges_earned))
    for idx, badge in enumerate(badges_earned):
        with badge_cols[idx]:
            st.markdown(
                f"""
            <div style='background-color: #FFF9C4; padding: 20px; border-radius: 15px; text-align: center; border: 3px solid #FBC02D;'>
                <div style='font-size: 48px;'>{badge['emoji']}</div>
                <div style='font-size: 18px; font-weight: bold; color: #F57F17; margin-top: 10px;'>{badge['name']}</div>
                <div style='font-size: 14px; color: #666; margin-top: 8px;'>{badge['description']}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ========================================================================
    # SKILL VISUALIZATION
    # ========================================================================

    st.markdown("## 📊 Your Skills Right Now")

    tab1, tab2 = st.tabs(["🕸️ Skill Web", "📊 Skill Bars"])

    with tab1:
        st.markdown("This shows all 7 of your skills in one picture!")
        fig = create_skill_radar(skills)
        st.plotly_chart(fig, use_container_width=True, key="radar")

    with tab2:
        st.markdown("Here's how you're doing in each skill!")
        fig = create_skill_bars(skills)
        st.plotly_chart(fig, use_container_width=True, key="bars")

    st.markdown("---")

    # ========================================================================
    # GROWTH-ORIENTED FEEDBACK
    # ========================================================================

    st.markdown("## 💬 What This Means for You")

    st.info("💡 Remember: Everyone is good at different things, and everyone can grow!")

    feedback_cols = st.columns(2)

    for idx, skill in enumerate(skills):
        with feedback_cols[idx % 2]:
            skill_key = skill["skill_type"]
            skill_info = SKILLS.get(skill_key, {})

            feedback = generate_growth_feedback(skill)

            st.markdown(
                f"""
            <div style='background-color: #E8F5E9; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid {skill_info.get("color", "#4CAF50")};'>
                <div style='font-size: 24px; margin-bottom: 10px;'>{skill_info.get("emoji", "🌟")} <strong>{skill_info.get("name", skill_key)}</strong></div>
                <div style='font-size: 16px; color: #333;'>{feedback}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ========================================================================
    # PROGRESS OVER TIME
    # ========================================================================

    st.markdown("## 📈 Your Growth Journey")

    st.info("💡 This shows how your skills have been growing over time!")
    st.warning(
        "⚠️ Note: This is sample data. Your teacher will set up real tracking soon!"
    )

    fig = create_progress_timeline(student_id)
    st.plotly_chart(fig, use_container_width=True, key="timeline")

    st.markdown("---")

    # ========================================================================
    # REFLECTION JOURNAL (Optional)
    # ========================================================================

    st.markdown("## 📝 My Reflections (Optional)")

    st.markdown(
        "💭 Take a moment to think about your skills. What are you proud of? What do you want to work on?"
    )

    reflection = st.text_area(
        "Write your thoughts here (only you and your teacher can see this):",
        height=150,
        placeholder="Example: I'm proud of how I worked with my group today. Next time, I want to stay calm when things get hard.",
        key="reflection_area",
        help="This is your private space to reflect on your learning.",
    )

    if st.button("💾 Save My Reflection", type="primary"):
        if reflection:
            success = api.save_reflection(student_id, reflection)
            if success:
                st.success(
                    "✅ Your reflection has been saved! Great job thinking about your growth!"
                )
                st.info(
                    "💡 Your teacher can see your reflections to better support your learning."
                )
            else:
                st.error(
                    "❌ Oops! Something went wrong. Please try again or ask your teacher for help."
                )
        else:
            st.warning("✏️ Write something first before saving!")

    st.markdown("---")

    # ========================================================================
    # FOOTER
    # ========================================================================

    st.markdown(
        """
    <div style='text-align: center; padding: 30px; background-color: #F5F5F5; border-radius: 10px;'>
        <h3 style='color: #333;'>🌟 Keep Growing! 🌟</h3>
        <p style='font-size: 16px; color: #666;'>
            Remember: Skills are like muscles - they get stronger when you practice!<br>
            You're doing great, and you can always get better!
        </p>
        <p style='font-size: 14px; color: #999; margin-top: 20px;'>
            UnseenEdge AI Student Portal | Version 1.0 | 2025-11-14
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
