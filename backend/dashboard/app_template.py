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
import yaml
from yaml.loader import SafeLoader

# ================================================================================
# CONFIGURATION
# ================================================================================

# Backend API URL (configured via environment variable)
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

# Skill configuration
SKILLS = ["empathy", "problem_solving", "self_regulation", "resilience"]
SKILL_COLORS = {
    "empathy": "#FF6B6B",
    "problem_solving": "#4ECDC4",
    "self_regulation": "#45B7D1",
    "resilience": "#FFA07A"
}

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.75,
    "medium": 0.50,
    "low": 0.0
}

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
            response = requests.get(
                f"{self.base_url}/students",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching students: {e}")
            return []

    def get_student_assessment(self, student_id: str) -> Dict[str, Any]:
        """Get skill assessment for a specific student"""
        try:
            response = requests.post(
                f"{self.base_url}/infer/{student_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching assessment: {e}")
            return {}

    def get_batch_assessments(self, student_ids: List[str]) -> Dict[str, Any]:
        """Get assessments for multiple students"""
        try:
            response = requests.post(
                f"{self.base_url}/infer/batch",
                json={"student_ids": student_ids},
                timeout=self.timeout * 2  # Batch operations get more time
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
                timeout=5  # Health check should be fast
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

    # Determine color based on score
    if score >= 0.75:
        color = "green"
    elif score >= 0.50:
        color = "yellow"
    else:
        color = "red"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score * 100,  # Convert to percentage
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': skill_name.replace("_", " ").title()},
        delta={'reference': 50},  # Reference point (average)
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': SKILL_COLORS.get(skill_name, "blue")},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "gray"},
                {'range': [75, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': confidence * 100
            }
        }
    ))

    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


def create_skills_radar_chart(assessment: Dict[str, Any]) -> go.Figure:
    """Create a radar chart showing all skills"""

    skills_data = {skill['skill_type']: skill['score'] * 100
                   for skill in assessment.get('skills', [])}

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=list(skills_data.values()),
        theta=[s.replace("_", " ").title() for s in skills_data.keys()],
        fill='toself',
        name='Skills'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        height=400
    )

    return fig


def create_progress_chart(student_id: str, historical_data: List[Dict]) -> go.Figure:
    """Create a line chart showing skill progress over time"""

    # This is a placeholder - you'll need to implement historical data storage
    # For now, generate sample data for demonstration

    dates = [datetime.now() - timedelta(days=x*7) for x in range(10, 0, -1)]

    fig = go.Figure()

    for skill in SKILLS:
        # Sample data - replace with actual historical data
        scores = [0.5 + (i * 0.02) for i in range(10)]

        fig.add_trace(go.Scatter(
            x=dates,
            y=scores,
            mode='lines+markers',
            name=skill.replace("_", " ").title(),
            line=dict(color=SKILL_COLORS[skill])
        ))

    fig.update_layout(
        title="Skill Progress Over Time",
        xaxis_title="Date",
        yaxis_title="Skill Score",
        yaxis=dict(range=[0, 1]),
        height=400
    )

    return fig


def create_class_heatmap(batch_results: Dict[str, Any]) -> go.Figure:
    """Create a heatmap showing all students and their skill scores"""

    # Extract data
    students = []
    skill_scores = {skill: [] for skill in SKILLS}

    for result in batch_results.get('results', []):
        if result['status'] == 'success':
            students.append(result['student_id'])
            for skill in result['skills']:
                skill_scores[skill['skill_type']].append(skill['score'])

    # Create dataframe
    df = pd.DataFrame(skill_scores, index=students)

    fig = px.imshow(
        df,
        labels=dict(x="Skill", y="Student", color="Score"),
        x=[s.replace("_", " ").title() for s in SKILLS],
        y=students,
        color_continuous_scale="RdYlGn",
        aspect="auto"
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
        initial_sidebar_state="expanded"
    )

    # ========================================================================
    # AUTHENTICATION
    # ========================================================================

    # Load authentication config
    # In production, use hashed passwords from environment variables or secure storage
    auth_config = {
        'credentials': {
            'usernames': {
                os.getenv('DASHBOARD_USER', 'teacher'): {
                    'name': os.getenv('DASHBOARD_NAME', 'Teacher'),
                    'password': os.getenv('DASHBOARD_PASSWORD_HASH', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW')  # Default: 'password123'
                }
            }
        },
        'cookie': {
            'name': 'unseenedge_auth',
            'key': os.getenv('DASHBOARD_COOKIE_KEY', 'unseenedge_secret_key_change_in_production'),
            'expiry_days': 30
        }
    }

    authenticator = stauth.Authenticate(
        auth_config['credentials'],
        auth_config['cookie']['name'],
        auth_config['cookie']['key'],
        auth_config['cookie']['expiry_days']
    )

    # Login widget
    name, authentication_status, username = authenticator.login('Login to UnseenEdge Dashboard', 'main')

    # Handle authentication status
    if authentication_status == False:
        st.error('Username/password is incorrect')
        st.info('Default credentials - Username: teacher, Password: password123')
        st.stop()
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        st.info('Default credentials - Username: teacher, Password: password123')
        st.stop()

    # Initialize API client (only if authenticated)
    api = SkillAssessmentAPI(API_URL)

    # Header
    st.title("🎓 UnseenEdge AI Skill Assessment Dashboard")
    st.markdown("---")

    # Sidebar - User info and logout
    with st.sidebar:
        st.write(f'Welcome *{name}*')
        authenticator.logout('Logout', 'sidebar')
        st.markdown("---")

        st.header("System Status")
        health = api.health_check()

        if health.get('status') == 'healthy':
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            st.json(health)

        st.markdown("---")

        # Navigation
        st.header("Navigation")
        page = st.radio(
            "Select View:",
            ["🔍 Student Search", "📊 Class Overview", "📈 Progress Tracking"]
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
            st.info("💡 **Tip:** Run `python scripts/seed_data.py` to create sample students.")
            return

        # Student selection
        student_options = {s['student_id']: s.get('name', s['student_id']) for s in students}
        selected_student = st.selectbox(
            "Select Student:",
            options=list(student_options.keys()),
            format_func=lambda x: student_options[x]
        )

        if st.button("📊 Get Assessment", type="primary"):
            with st.spinner("Analyzing student data..."):
                assessment = get_student_assessment_cached(API_URL, selected_student)

            if assessment:
                # Display assessment metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Student ID", assessment['student_id'])
                with col2:
                    st.metric("Inference Time", f"{assessment['total_inference_time_ms']}ms")
                with col3:
                    st.metric("Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M"))

                st.markdown("---")

                # Skill gauges
                st.subheader("Skill Scores")
                cols = st.columns(len(SKILLS))

                for idx, skill_data in enumerate(assessment['skills']):
                    with cols[idx]:
                        fig = create_skill_gauge(
                            skill_data['skill_type'],
                            skill_data['score'],
                            skill_data['confidence']
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Confidence badge
                        confidence = skill_data['confidence']
                        if confidence >= CONFIDENCE_THRESHOLDS['high']:
                            st.success(f"High Confidence: {confidence:.2f}")
                        elif confidence >= CONFIDENCE_THRESHOLDS['medium']:
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

                for skill_data in assessment['skills']:
                    with st.expander(f"📋 {skill_data['skill_type'].replace('_', ' ').title()} Evidence"):
                        evidence = skill_data.get('evidence', [])

                        if evidence:
                            for idx, ev in enumerate(evidence[:5], 1):  # Top 5
                                st.markdown(f"**{idx}. {ev.get('source', 'Unknown Source')}** (Relevance: {ev.get('relevance', 0):.2f})")
                                st.write(ev.get('text', 'No text available'))
                                st.markdown("---")
                        else:
                            st.info("No evidence available")

                # GPT-4 Reasoning
                st.subheader("🤖 AI-Generated Insights")

                for skill_data in assessment['skills']:
                    if 'reasoning' in skill_data and skill_data['reasoning']:
                        with st.expander(f"💬 {skill_data['skill_type'].replace('_', ' ').title()} Reasoning"):
                            st.write(skill_data['reasoning'])
                    else:
                        st.info(f"No reasoning available for {skill_data['skill_type']}")

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
            student_ids = [s['student_id'] for s in students[:100]]  # Max 100

            with st.spinner(f"Analyzing {len(student_ids)} students..."):
                batch_results = api.get_batch_assessments(student_ids)

            if batch_results:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Students", batch_results['total_students'])
                with col2:
                    st.metric("Successful", batch_results['successful'])
                with col3:
                    st.metric("Failed", batch_results['failed'])
                with col4:
                    st.metric("Processing Time", f"{batch_results['total_time_ms']/1000:.2f}s")

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

                for result in batch_results['results']:
                    if result['status'] == 'success':
                        for skill in result['skills']:
                            skill_averages[skill['skill_type']].append(skill['score'])

                stats_df = pd.DataFrame({
                    'Skill': [s.replace("_", " ").title() for s in SKILLS],
                    'Average Score': [sum(skill_averages[s])/len(skill_averages[s]) if skill_averages[s] else 0 for s in SKILLS],
                    'Min Score': [min(skill_averages[s]) if skill_averages[s] else 0 for s in SKILLS],
                    'Max Score': [max(skill_averages[s]) if skill_averages[s] else 0 for s in SKILLS]
                })

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

        student_options = {s['student_id']: s.get('name', s['student_id']) for s in students}
        selected_student = st.selectbox(
            "Select Student:",
            options=list(student_options.keys()),
            format_func=lambda x: student_options[x],
            key="progress_student"
        )

        # Placeholder for historical data
        st.info("📊 Historical data tracking coming soon! This will show skill progress over weeks/months.")

        # Sample progress chart (replace with actual historical data)
        progress_fig = create_progress_chart(selected_student, [])
        st.plotly_chart(progress_fig, use_container_width=True)

        st.markdown("---")

        # Next steps
        st.subheader("💡 Recommendations")
        st.write("""
        **To enable progress tracking:**
        1. Store assessment results with timestamps in the database
        2. Query historical assessments for the selected student
        3. Update the `create_progress_chart()` function to use real data
        4. Add date range filters for flexible time periods
        """)


# ================================================================================
# FOOTER
# ================================================================================

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>🎓 <strong>UnseenEdge AI Skill Assessment Dashboard</strong></p>
        <p>Powered by GPT-4o-mini, XGBoost, and Evidence Fusion</p>
        <p style='color: gray; font-size: 12px'>Version 1.0 | 2025-11-13</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
