"""
Streamlit Dashboard Template for UnseenEdge AI Skill Assessment

This is a starter template for building a teacher-facing dashboard to view
student skill assessments. Customize as needed for your use case.

Installation:
    pip install streamlit plotly pandas requests

Usage:
    streamlit run dashboard/app_template.py

Features:
    - Student search and selection
    - Skill assessment visualization
    - Evidence viewer
    - Progress tracking over time
    - Batch student comparison

Customization Points:
    - Update API_URL to point to your deployed backend
    - Customize skill colors and thresholds
    - Add authentication (Streamlit supports OAuth)
    - Add export functionality (PDF reports)
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

# Backend API URL (configured via environment variable)
API_URL = os.getenv("API_URL", "http://localhost:8080/api/v1")

# Skill configuration - all 7 skills
SKILLS = [
    "empathy",
    "adaptability",
    "problem_solving",
    "self_regulation",
    "resilience",
    "communication",
    "collaboration",
]
SKILL_COLORS = {
    "empathy": "#FF6B6B",
    "adaptability": "#9B59B6",
    "problem_solving": "#4ECDC4",
    "self_regulation": "#45B7D1",
    "resilience": "#FFA07A",
    "communication": "#2ECC71",
    "collaboration": "#F39C12",
}

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {"high": 0.75, "medium": 0.50, "low": 0.0}

# ================================================================================
# API CLIENT
# ================================================================================


class SkillAssessmentAPI:
    """Client for interacting with the backend API"""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout

    def get_students(self) -> List[Dict[str, Any]]:
        """Get list of all students"""
        try:
            response = requests.get(f"{self.base_url}/students", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching students: {e}")
            return []

    def get_student_assessment(self, student_id: str) -> Dict[str, Any]:
        """Get skill assessment for a specific student"""
        try:
            # Get existing assessments from database
            # Need enough assessments to cover all 7 skill types
            response = requests.get(
                f"{self.base_url}/assessments/{student_id}",
                params={"limit": 100},
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
                            "evidence": assessment.get("evidence", []),
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

    def get_batch_assessments(self, student_ids: List[str]) -> Dict[str, Any]:
        """Get assessments for multiple students"""
        try:
            response = requests.post(
                f"{self.base_url}/infer-batch",
                json={"student_ids": student_ids},
                timeout=self.timeout * 2,  # Batch operations get more time
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching batch assessments: {e}")
            return {}

    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = requests.get(
                f"{self.base_url}/health/detailed",
                timeout=5,  # Health check should be fast
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "unhealthy", "error": str(e)}


# ================================================================================
# CACHED API FUNCTIONS
# ================================================================================


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_students_cached(api_url: str) -> List[Dict[str, Any]]:
    """Get students list with caching."""
    api = SkillAssessmentAPI(api_url)
    return api.get_students()


@st.cache_data(ttl=60)  # Cache for 1 minute
def get_student_assessment_cached(api_url: str, student_id: str) -> Dict[str, Any]:
    """Get student assessment with caching."""
    api = SkillAssessmentAPI(api_url)
    return api.get_student_assessment(student_id)


# ================================================================================
# VISUALIZATION FUNCTIONS
# ================================================================================


def create_skill_gauge(skill_name: str, score: float, confidence: float) -> go.Figure:
    """Create a gauge chart for a single skill"""

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=score * 100,  # Convert to percentage
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": skill_name.replace("_", " ").title()},
            delta={"reference": 50},  # Reference point (average)
            gauge={
                "axis": {"range": [None, 100]},
                "bar": {"color": SKILL_COLORS.get(skill_name, "blue")},
                "steps": [
                    {"range": [0, 50], "color": "lightgray"},
                    {"range": [50, 75], "color": "gray"},
                    {"range": [75, 100], "color": "lightgreen"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": confidence * 100,
                },
            },
        )
    )

    fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))

    return fig


def create_skills_radar_chart(assessment: Dict[str, Any]) -> go.Figure:
    """Create a radar chart showing all skills"""

    skills_data = {
        skill["skill_type"]: skill["score"] * 100
        for skill in assessment.get("skills", [])
    }

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=list(skills_data.values()),
            theta=[s.replace("_", " ").title() for s in skills_data.keys()],
            fill="toself",
            name="Skills",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=400,
    )

    return fig


def create_progress_chart(
    student_id: str, historical_data: List[Dict], date_range_days: int = None
) -> go.Figure:
    """Create a line chart showing skill progress over time

    Args:
        student_id: Student ID for the chart
        historical_data: List of assessment dictionaries from API
        date_range_days: Optional filter for date range (7, 30, 90, or None for all)

    Returns:
        Plotly figure showing skill progress over time
    """

    if not historical_data:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No historical data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(
            title="Skill Progress Over Time",
            xaxis_title="Date",
            yaxis_title="Skill Score",
            height=400,
        )
        return fig

    # Filter by date range if specified
    cutoff_date = None
    if date_range_days:
        from datetime import timezone

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=date_range_days)

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
                # Handle both ISO formats with/without 'Z'
                timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except ValueError:
                continue
        else:
            timestamp = created_at

        # Apply date filter
        if cutoff_date and timestamp < cutoff_date:
            continue

        # Store data point
        if skill_type in skill_history:
            skill_history[skill_type].append({"timestamp": timestamp, "score": score})

    # Sort each skill's data by timestamp
    for skill in skill_history:
        skill_history[skill].sort(key=lambda x: x["timestamp"])

    # Create figure
    fig = go.Figure()

    for skill in SKILLS:
        if skill_history[skill]:
            timestamps = [d["timestamp"] for d in skill_history[skill]]
            scores = [d["score"] for d in skill_history[skill]]

            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=scores,
                    mode="lines+markers",
                    name=skill.replace("_", " ").title(),
                    line=dict(color=SKILL_COLORS[skill]),
                    marker=dict(size=8),
                    hovertemplate=(
                        f"<b>{skill.replace('_', ' ').title()}</b><br>"
                        + "Date: %{x|%Y-%m-%d}<br>"
                        + "Score: %{y:.2f}<br>"
                        + "<extra></extra>"
                    ),
                )
            )

    # Update layout
    title = "Skill Progress Over Time"
    if date_range_days:
        title += f" (Last {date_range_days} Days)"

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Skill Score",
        yaxis=dict(range=[0, 1]),
        height=400,
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def create_class_heatmap(batch_results: Dict[str, Any]) -> go.Figure:
    """Create a heatmap showing all students and their skill scores"""

    # Extract data
    students = []
    skill_scores = {skill: [] for skill in SKILLS}

    for result in batch_results.get("results", []):
        if result["status"] == "success":
            students.append(result["student_id"])
            for skill in result["skills"]:
                skill_scores[skill["skill_type"]].append(skill["score"])

    # Create dataframe
    df = pd.DataFrame(skill_scores, index=students)

    fig = px.imshow(
        df,
        labels=dict(x="Skill", y="Student", color="Score"),
        x=[s.replace("_", " ").title() for s in SKILLS],
        y=students,
        color_continuous_scale="RdYlGn",
        aspect="auto",
    )

    fig.update_layout(height=max(400, len(students) * 30))

    return fig


# ================================================================================
# MAIN APP
# ================================================================================


def main():
    """Main Streamlit application"""

    # Page configuration
    st.set_page_config(
        page_title="UnseenEdge AI - Skill Assessment Dashboard",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ========================================================================
    # AUTHENTICATION
    # ========================================================================

    # Show login banner at the top
    if (
        "authentication_status" not in st.session_state
        or st.session_state.get("authentication_status") is None
    ):
        st.markdown(
            """
        <div style='background-color: #e3f2fd; padding: 20px; \
border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2196F3;'>
            <h2 style='margin: 0; color: #1976D2;'>\
🎓 Welcome to UnseenEdge AI Dashboard</h2>
            <p style='margin: 10px 0 0 0; font-size: 16px;'>
                <strong>Demo Credentials:</strong><br>
                👤 Username: <code style='background: white; \
padding: 4px 8px; border-radius: 4px;'>teacher</code><br>
                🔑 Password: <code style='background: white; \
padding: 4px 8px; border-radius: 4px;'>password123</code>
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Load authentication config
    # In production, use hashed passwords from environment variables or secure storage
    auth_config = {
        "credentials": {
            "usernames": {
                os.getenv("DASHBOARD_USER", "teacher"): {
                    "name": os.getenv("DASHBOARD_NAME", "Teacher"),
                    "password": os.getenv(
                        "DASHBOARD_PASSWORD", "password123"
                    ),  # Plain text, will be auto-hashed
                }
            }
        },
        "cookie": {
            "name": "unseenedge_auth",
            "key": os.getenv(
                "DASHBOARD_COOKIE_KEY", "unseenedge_secret_key_change_in_production"
            ),
            "expiry_days": 30,
        },
    }

    authenticator = stauth.Authenticate(
        credentials=auth_config["credentials"],
        cookie_name=auth_config["cookie"]["name"],
        cookie_key=auth_config["cookie"]["key"],
        cookie_expiry_days=auth_config["cookie"]["expiry_days"],
        auto_hash=True,  # Auto-hash plain text passwords on first run
    )

    # Login widget (v0.4.2+ returns None, use session state instead)
    authenticator.login(location="main")

    # Get authentication details from session state
    name = st.session_state.get("name")
    authentication_status = st.session_state.get("authentication_status")

    # Handle authentication status
    if authentication_status is False:
        st.error("❌ Username/password is incorrect")
        st.stop()
    elif authentication_status is None:
        st.warning("⚠️ Please enter your username and password")
        st.stop()

    # Initialize API client (only if authenticated)
    api = SkillAssessmentAPI(API_URL)

    # Header
    st.title("🎓 UnseenEdge AI Skill Assessment Dashboard")
    st.markdown("---")

    # Sidebar - User info and logout
    with st.sidebar:
        st.write(f"Welcome *{name}*")
        authenticator.logout(button_name="Logout", location="sidebar")
        st.markdown("---")

        st.header("System Status")
        health = api.health_check()

        if health.get("status") == "healthy":
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            st.json(health)

        st.markdown("---")

        # Navigation
        st.header("Navigation")
        page = st.radio(
            "Select View:",
            ["🔍 Student Search", "📊 Class Overview", "📈 Progress Tracking"],
        )

    # ========================================================================
    # PAGE 1: STUDENT SEARCH
    # ========================================================================

    if page == "🔍 Student Search":
        st.header("Student Skill Assessment")

        # Get students (cached)
        students = get_students_cached(API_URL)

        if not students:
            st.warning("No students found. Please add students to the database.")
            st.info(
                "💡 **Tip:** Run `python scripts/seed_data.py` to create sample students."
            )
            return

        # Student selection
        student_options = {
            s["id"]: f"{s.get('first_name', '')} {s.get('last_name', '')}".strip()
            or s["id"]
            for s in students
        }
        selected_student = st.selectbox(
            "Select Student:",
            options=list(student_options.keys()),
            format_func=lambda x: student_options[x],
        )

        if st.button("📊 Get Assessment", type="primary"):
            with st.spinner("Analyzing student data..."):
                assessment = get_student_assessment_cached(API_URL, selected_student)

            if assessment:
                # Display assessment metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Student ID", assessment["student_id"])
                with col2:
                    # Only show inference time if available (from ML inference endpoint)
                    if "total_inference_time_ms" in assessment:
                        st.metric(
                            "Inference Time",
                            f"{assessment['total_inference_time_ms']}ms",
                        )
                    else:
                        # Show assessment timestamp instead
                        timestamp = assessment.get(
                            "timestamp", datetime.now().isoformat()
                        )
                        st.metric(
                            "Assessed At",
                            timestamp[:10] if isinstance(timestamp, str) else "Recent",
                        )
                with col3:
                    st.metric("Current Time", datetime.now().strftime("%Y-%m-%d %H:%M"))

                st.markdown("---")

                # Skill gauges
                st.subheader("Skill Scores")
                skills_data = assessment.get("skills", [])
                num_skills = len(skills_data)
                # Create columns based on actual skills data, max 4 per row
                cols_per_row = min(num_skills, 4)
                cols = st.columns(cols_per_row) if cols_per_row > 0 else []

                for idx, skill_data in enumerate(skills_data):
                    col_idx = idx % cols_per_row if cols_per_row > 0 else 0
                    with cols[col_idx]:
                        fig = create_skill_gauge(
                            skill_data["skill_type"],
                            skill_data["score"],
                            skill_data["confidence"],
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Confidence badge
                        confidence = skill_data["confidence"]
                        if confidence >= CONFIDENCE_THRESHOLDS["high"]:
                            st.success(f"High Confidence: {confidence:.2f}")
                        elif confidence >= CONFIDENCE_THRESHOLDS["medium"]:
                            st.warning(f"Medium Confidence: {confidence:.2f}")
                        else:
                            st.error(f"Low Confidence: {confidence:.2f}")

                st.markdown("---")

                # Radar chart
                st.subheader("Skills Overview")
                radar_fig = create_skills_radar_chart(assessment)
                st.plotly_chart(radar_fig, use_container_width=True)

                st.markdown("---")

                # Evidence details
                st.subheader("Supporting Evidence")

                for skill_data in assessment["skills"]:
                    with st.expander(
                        f"📋 {skill_data['skill_type'].replace('_', ' ').title()} Evidence"
                    ):
                        evidence = skill_data.get("evidence", [])

                        if evidence:
                            for idx, ev in enumerate(evidence[:5], 1):  # Top 5
                                # Handle both API formats (relevance_score/relevance, content/text)
                                relevance = ev.get(
                                    "relevance_score", ev.get("relevance", 0)
                                )
                                source = ev.get("source", "Unknown Source")
                                evidence_type = ev.get("evidence_type", "unknown")
                                content = ev.get(
                                    "content", ev.get("text", "No content available")
                                )

                                st.markdown(
                                    f"**{idx}. {source}** ({evidence_type}) - "
                                    f"Relevance: {relevance:.2f}"
                                )
                                st.write(content)
                                st.markdown("---")
                        else:
                            st.info("No evidence available")

                # GPT-4 Reasoning
                st.subheader("🤖 AI-Generated Insights")

                for skill_data in assessment["skills"]:
                    if "reasoning" in skill_data and skill_data["reasoning"]:
                        with st.expander(
                            f"💬 {skill_data['skill_type'].replace('_', ' ').title()} Reasoning"
                        ):
                            st.write(skill_data["reasoning"])
                    else:
                        st.info(
                            f"No reasoning available for {skill_data['skill_type']}"
                        )

    # ========================================================================
    # PAGE 2: CLASS OVERVIEW
    # ========================================================================

    elif page == "📊 Class Overview":
        st.header("Class-Wide Skill Analysis")

        students = get_students_cached(API_URL)

        if not students:
            st.warning("No students found.")
            return

        st.info(f"Found {len(students)} students")

        if st.button("📊 Analyze All Students", type="primary"):
            student_ids = [s["id"] for s in students[:100]]  # Max 100

            with st.spinner(f"Analyzing {len(student_ids)} students..."):
                batch_results = api.get_batch_assessments(student_ids)

            if batch_results:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Students", batch_results["total_students"])
                with col2:
                    st.metric("Successful", batch_results["successful"])
                with col3:
                    st.metric("Failed", batch_results["failed"])
                with col4:
                    st.metric(
                        "Processing Time", f"{batch_results['total_time_ms']/1000:.2f}s"
                    )

                st.markdown("---")

                # Heatmap
                st.subheader("Class Skill Heatmap")
                heatmap_fig = create_class_heatmap(batch_results)
                st.plotly_chart(heatmap_fig, use_container_width=True)

                st.markdown("---")

                # Class statistics
                st.subheader("Class Statistics")

                # Calculate average scores per skill
                skill_averages = {skill: [] for skill in SKILLS}

                for result in batch_results["results"]:
                    if result["status"] == "success":
                        for skill in result["skills"]:
                            skill_averages[skill["skill_type"]].append(skill["score"])

                stats_df = pd.DataFrame(
                    {
                        "Skill": [s.replace("_", " ").title() for s in SKILLS],
                        "Average Score": [
                            (
                                sum(skill_averages[s]) / len(skill_averages[s])
                                if skill_averages[s]
                                else 0
                            )
                            for s in SKILLS
                        ],
                        "Min Score": [
                            min(skill_averages[s]) if skill_averages[s] else 0
                            for s in SKILLS
                        ],
                        "Max Score": [
                            max(skill_averages[s]) if skill_averages[s] else 0
                            for s in SKILLS
                        ],
                    }
                )

                st.dataframe(stats_df, use_container_width=True)

    # ========================================================================
    # PAGE 3: PROGRESS TRACKING
    # ========================================================================

    elif page == "📈 Progress Tracking":
        st.header("Student Progress Over Time")

        students = get_students_cached(API_URL)

        if not students:
            st.warning("No students found.")
            return

        student_options = {
            s["id"]: f"{s.get('first_name', '')} {s.get('last_name', '')}".strip()
            or s["id"]
            for s in students
        }
        selected_student = st.selectbox(
            "Select Student:",
            options=list(student_options.keys()),
            format_func=lambda x: student_options[x],
            key="progress_student",
        )

        # Date range filter
        col1, col2 = st.columns([3, 1])
        with col1:
            date_range_option = st.selectbox(
                "Time Period:",
                options=["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
                index=0,
                key="date_range",
            )
        with col2:
            load_button = st.button(
                "📈 Load Progress", type="primary", key="load_progress"
            )

        # Map selection to days
        date_range_map = {
            "All Time": None,
            "Last 7 Days": 7,
            "Last 30 Days": 30,
            "Last 90 Days": 90,
        }
        date_range_days = date_range_map[date_range_option]

        if load_button:
            with st.spinner("Loading historical assessment data..."):
                # Fetch all historical assessments for this student
                try:
                    response = requests.get(
                        f"{API_URL}/assessments/{selected_student}",
                        params={"limit": 1000},  # Get comprehensive history
                        timeout=10,
                    )
                    response.raise_for_status()
                    historical_assessments = response.json()

                    # Display metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Assessments", len(historical_assessments))
                    with col2:
                        if historical_assessments:
                            earliest = min(
                                a["created_at"] for a in historical_assessments
                            )
                            earliest_date = (
                                earliest[:10] if isinstance(earliest, str) else "N/A"
                            )
                            st.metric("Data Since", earliest_date)
                    with col3:
                        # Count unique skills assessed
                        unique_skills = len(
                            set(a["skill_type"] for a in historical_assessments)
                        )
                        st.metric("Skills Tracked", f"{unique_skills}/{len(SKILLS)}")

                    st.markdown("---")

                    # Create and display progress chart
                    if historical_assessments:
                        progress_fig = create_progress_chart(
                            selected_student, historical_assessments, date_range_days
                        )
                        st.plotly_chart(progress_fig, use_container_width=True)

                        # Show data summary
                        st.markdown("---")
                        st.subheader("📊 Assessment Summary")

                        # Create summary table
                        summary_data = []
                        for skill in SKILLS:
                            skill_assessments = [
                                a
                                for a in historical_assessments
                                if a["skill_type"] == skill
                            ]

                            if skill_assessments:
                                scores = [a["score"] for a in skill_assessments]
                                latest_score = skill_assessments[0][
                                    "score"
                                ]  # Already sorted desc
                                avg_score = sum(scores) / len(scores)

                                summary_data.append(
                                    {
                                        "Skill": skill.replace("_", " ").title(),
                                        "Total Assessments": len(skill_assessments),
                                        "Latest Score": f"{latest_score:.2f}",
                                        "Average Score": f"{avg_score:.2f}",
                                        "Min Score": f"{min(scores):.2f}",
                                        "Max Score": f"{max(scores):.2f}",
                                    }
                                )

                        if summary_data:
                            summary_df = pd.DataFrame(summary_data)
                            st.dataframe(
                                summary_df, use_container_width=True, hide_index=True
                            )
                        else:
                            st.info(
                                "No assessment data available for the selected time period"
                            )

                    else:
                        st.warning("No historical assessments found for this student")
                        st.info(
                            "💡 **Tip:** Generate assessments first to build up "
                            "historical data for tracking."
                        )

                except requests.exceptions.RequestException as e:
                    st.error(f"Error loading assessment data: {e}")
                    st.info("Make sure the backend API is running at " + API_URL)

        else:
            st.info("👆 Click 'Load Progress' to view historical skill assessments")
            st.markdown(
                """
                **Features:**
                - View skill trends over time
                - Filter by date range (7/30/90 days or all time)
                - Compare progress across all 7 skills
                - See detailed assessment statistics
                """
            )

    # ================================================================================
    # FOOTER
    # ================================================================================

    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center'>
        <p>🎓 <strong>UnseenEdge AI Skill Assessment Dashboard</strong></p>
        <p>Powered by GPT-4o-mini, XGBoost, and Evidence Fusion</p>
        <p style='color: gray; font-size: 12px'>Version 1.0 | 2025-11-13</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
