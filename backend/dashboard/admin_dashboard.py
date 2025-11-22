"""
Administrator Dashboard for UnseenEdge AI Skill Assessment

School-wide analytics dashboard for administrators with:
- Skill distribution across all students (7 skills)
- Trend analysis over time (4-week, 12-week, semester)
- Equity analysis with demographic breakdowns
- Heatmaps by grade/class
- Longitudinal progress tracking
- Export functionality (PDF, CSV)
- Drill-down navigation with breadcrumbs

Usage:
    streamlit run backend/dashboard/admin_dashboard.py --server.port=8501
"""

import streamlit as st
import streamlit_authenticator as stauth
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
from io import BytesIO
import json

# ================================================================================
# CONFIGURATION
# ================================================================================

API_URL = os.getenv("API_URL", "http://localhost:8080/api/v1")

# All 7 skills
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
    "adaptability": "#4ECDC4",
    "problem_solving": "#45B7D1",
    "self_regulation": "#95E1D3",
    "resilience": "#FFA07A",
    "communication": "#AA96DA",
    "collaboration": "#FCBAD3",
}

# Time period options
TIME_PERIODS = {"4 weeks": 28, "12 weeks": 84, "1 semester": 120, "1 year": 365}

# ================================================================================
# API CLIENT
# ================================================================================


class AdminAPI:
    """API client for administrator dashboard"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout

    def get_all_students(self) -> List[Dict[str, Any]]:
        """Get all students"""
        try:
            response = requests.get(f"{self.base_url}/students", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching students: {e}")
            return []

    def get_batch_assessments(self, student_ids: List[str]) -> Dict[str, Any]:
        """Get assessments for multiple students"""
        try:
            response = requests.post(
                f"{self.base_url}/infer-batch",
                json={"student_ids": student_ids},
                timeout=self.timeout * 2,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching batch assessments: {e}")
            return {}

    def get_historical_assessments(
        self, student_id: str, skill_type: Optional[str] = None, limit: int = 50
    ) -> List[Dict]:
        """Get historical assessments for a student"""
        try:
            params = {"limit": limit}
            if skill_type:
                params["skill_type"] = skill_type

            response = requests.get(
                f"{self.base_url}/assessments/{student_id}",
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching historical assessments: {e}")
            return []

    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health/detailed", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "unhealthy", "error": str(e)}


# ================================================================================
# DATA PROCESSING
# ================================================================================


def create_assessment_dataframe(
    batch_results: Dict[str, Any], students: List[Dict]
) -> pd.DataFrame:
    """Create a DataFrame from batch assessment results"""
    rows = []

    student_lookup = {s["id"]: s for s in students}

    for result in batch_results.get("results", []):
        if result["status"] == "success":
            student = student_lookup.get(result["student_id"], {})
            base_row = {
                "student_id": result["student_id"],
                "first_name": student.get("first_name", "Unknown"),
                "last_name": student.get("last_name", ""),
                "grade": student.get("grade_level", 0),
                "gender": student.get("gender", "Not specified"),
                "ethnicity": student.get("ethnicity", "Not specified"),
            }

            for skill in result["skills"]:
                row = base_row.copy()
                row["skill"] = skill["skill_type"]
                row["score"] = skill["score"]
                row["confidence"] = skill["confidence"]
                row["reasoning"] = skill.get("reasoning", "No reasoning available")
                row["recommendations"] = skill.get("recommendations", "")
                rows.append(row)

    return pd.DataFrame(rows)


# ================================================================================
# VISUALIZATION FUNCTIONS
# ================================================================================


def create_skill_distribution_bar(df: pd.DataFrame) -> go.Figure:
    """Bar chart showing average score for each skill"""
    skill_avg = df.groupby("skill")["score"].agg(["mean", "std", "count"]).reset_index()
    skill_avg["skill_display"] = skill_avg["skill"].str.replace("_", " ").str.title()

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=skill_avg["skill_display"],
            y=skill_avg["mean"] * 100,
            error_y=dict(type="data", array=skill_avg["std"] * 100, visible=True),
            marker_color=[SKILL_COLORS.get(s, "#95E1D3") for s in skill_avg["skill"]],
            text=[f"{m:.1f}%" for m in skill_avg["mean"] * 100],
            textposition="outside",
        )
    )

    fig.update_layout(
        title="School-Wide Skill Distribution (Average Scores)",
        xaxis_title="Skill",
        yaxis_title="Average Score (%)",
        yaxis=dict(range=[0, 100]),
        height=500,
        showlegend=False,
    )

    return fig


def create_skill_distribution_histogram(df: pd.DataFrame, skill: str) -> go.Figure:
    """Histogram showing distribution of scores for a specific skill"""
    skill_df = df[df["skill"] == skill]

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=skill_df["score"] * 100,
            nbinsx=20,
            marker_color=SKILL_COLORS.get(skill, "#95E1D3"),
            name=skill.replace("_", " ").title(),
        )
    )

    fig.update_layout(
        title=f"{skill.replace('_', ' ').title()} Score Distribution",
        xaxis_title="Score (%)",
        yaxis_title="Number of Students",
        height=400,
        showlegend=False,
    )

    return fig


def create_trend_analysis(
    df: pd.DataFrame,
    period_days: int,
    api: "AdminAPI" = None,
    students: List[Dict] = None,
) -> go.Figure:
    """Line graph showing trends over time using real historical data"""
    fig = go.Figure()

    if api and students and len(students) > 0:
        # Use real historical data
        cutoff_date = datetime.now() - timedelta(days=period_days)

        # Collect historical data for all students
        all_historical = []
        for student in students[:20]:  # Limit to 20 students for performance
            try:
                assessments = api.get_historical_assessments(student["id"], limit=100)
                for assessment in assessments:
                    created_at = pd.to_datetime(assessment["created_at"])
                    if created_at >= cutoff_date:
                        all_historical.append(
                            {
                                "skill": assessment["skill_type"],
                                "score": assessment["score"],
                                "created_at": created_at,
                            }
                        )
            except:
                continue

        if all_historical:
            # Create DataFrame and calculate weekly averages
            hist_df = pd.DataFrame(all_historical)
            hist_df["week"] = hist_df["created_at"].dt.to_period("W").dt.to_timestamp()

            for skill in SKILLS:
                skill_data = hist_df[hist_df["skill"] == skill]
                if len(skill_data) > 0:
                    weekly_avg = skill_data.groupby("week")["score"].mean() * 100

                    fig.add_trace(
                        go.Scatter(
                            x=weekly_avg.index,
                            y=weekly_avg.values,
                            mode="lines+markers",
                            name=skill.replace("_", " ").title(),
                            line=dict(color=SKILL_COLORS.get(skill, "#95E1D3")),
                            marker=dict(size=8),
                        )
                    )

            title_suffix = "Real Data"
        else:
            # Fallback to current snapshot if no historical data
            title_suffix = "Snapshot (No Historical Data)"
            dates = [datetime.now()]
            for skill in SKILLS:
                skill_avg = (
                    df[df["skill"] == skill]["score"].mean()
                    if skill in df["skill"].values
                    else 0.5
                )
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=[skill_avg * 100],
                        mode="markers",
                        name=skill.replace("_", " ").title(),
                        marker=dict(size=12, color=SKILL_COLORS.get(skill, "#95E1D3")),
                    )
                )
    else:
        # Fallback: current data snapshot
        title_suffix = "Current Snapshot"
        dates = [datetime.now()]
        for skill in SKILLS:
            skill_avg = (
                df[df["skill"] == skill]["score"].mean()
                if skill in df["skill"].values
                else 0.5
            )
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=[skill_avg * 100],
                    mode="markers",
                    name=skill.replace("_", " ").title(),
                    marker=dict(size=12, color=SKILL_COLORS.get(skill, "#95E1D3")),
                )
            )

    fig.update_layout(
        title=f"Skill Trends Over {period_days} Days ({title_suffix})",
        xaxis_title="Date",
        yaxis_title="Average Score (%)",
        yaxis=dict(range=[0, 100]),
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def create_equity_analysis(df: pd.DataFrame, demographic_field: str) -> go.Figure:
    """Bar chart showing skill scores by demographic group"""
    equity_df = df.groupby([demographic_field, "skill"])["score"].mean().reset_index()
    equity_df["skill_display"] = equity_df["skill"].str.replace("_", " ").str.title()
    equity_df["score_pct"] = equity_df["score"] * 100

    fig = px.bar(
        equity_df,
        x="skill_display",
        y="score_pct",
        color=demographic_field,
        barmode="group",
        title=f"Equity Analysis by {demographic_field.title()}",
        labels={
            "skill_display": "Skill",
            "score_pct": "Average Score (%)",
            demographic_field: demographic_field.title(),
        },
        height=500,
    )

    fig.update_yaxes(range=[0, 100])

    return fig


def create_grade_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap showing skill levels by grade"""
    heatmap_data = df.pivot_table(
        values="score", index="grade", columns="skill", aggfunc="mean"
    )

    # Reorder columns to match SKILLS order
    heatmap_data = heatmap_data[[s for s in SKILLS if s in heatmap_data.columns]]

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values * 100,
            x=[s.replace("_", " ").title() for s in heatmap_data.columns],
            y=heatmap_data.index,
            colorscale="RdYlGn",
            text=[[f"{val:.1f}%" for val in row] for row in heatmap_data.values * 100],
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="Score (%)"),
            hovertemplate="Grade: %{y}<br>Skill: %{x}<br>Avg Score: %{z:.1f}%<extra></extra>",
        )
    )

    fig.update_layout(
        title="Skill Heatmap by Grade Level",
        xaxis_title="Skill",
        yaxis_title="Grade Level",
        height=400,
    )

    return fig


def create_class_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap showing all students and their skill scores (clickable for drill-down)"""
    # Pivot data: students as rows, skills as columns
    heatmap_data = df.pivot_table(
        values="score",
        index=["student_id", "first_name", "last_name", "grade"],
        columns="skill",
        aggfunc="mean",
    )

    # Reorder columns
    heatmap_data = heatmap_data[[s for s in SKILLS if s in heatmap_data.columns]]

    # Create student labels
    student_labels = [
        f"{row['first_name']} {row['last_name']} (G{row['grade']})"
        for _, row in heatmap_data.reset_index().iterrows()
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values * 100,
            x=[s.replace("_", " ").title() for s in heatmap_data.columns],
            y=student_labels,
            colorscale="RdYlGn",
            colorbar=dict(title="Score (%)"),
            hovertemplate="Student: %{y}<br>Skill: %{x}<br>Score: %{z:.1f}%<extra></extra>",
        )
    )

    fig.update_layout(
        title="Student Skill Heatmap (Click to drill down)",
        xaxis_title="Skill",
        yaxis_title="Student",
        height=max(600, len(student_labels) * 25),
    )

    return fig


def create_longitudinal_cohort_graph(
    df: pd.DataFrame, api: "AdminAPI" = None, students: List[Dict] = None
) -> go.Figure:
    """Track cohort progress over time using real historical data"""
    grades = sorted(df["grade"].unique())
    fig = go.Figure()

    if api and students and len(students) > 0:
        # Use real historical data
        for grade in grades:
            grade_students = [s for s in students if s.get("grade_level") == grade][
                :10
            ]  # Limit for performance

            grade_historical = []
            for student in grade_students:
                try:
                    assessments = api.get_historical_assessments(
                        student["id"], limit=50
                    )
                    for assessment in assessments:
                        grade_historical.append(
                            {
                                "score": assessment["score"],
                                "created_at": pd.to_datetime(assessment["created_at"]),
                            }
                        )
                except:
                    continue

            if grade_historical:
                hist_df = pd.DataFrame(grade_historical)
                hist_df["month"] = (
                    hist_df["created_at"].dt.to_period("M").dt.to_timestamp()
                )
                monthly_avg = hist_df.groupby("month")["score"].mean() * 100

                fig.add_trace(
                    go.Scatter(
                        x=monthly_avg.index,
                        y=monthly_avg.values,
                        mode="lines+markers",
                        name=f"Grade {grade} Cohort",
                        marker=dict(size=8),
                    )
                )

        title_suffix = "Real Data" if len(fig.data) > 0 else "No Historical Data"
    else:
        # Fallback: show current snapshot by grade
        title_suffix = "Current Snapshot"
        for grade in grades:
            grade_df = df[df["grade"] == grade]
            avg_score = grade_df["score"].mean() * 100
            fig.add_trace(
                go.Scatter(
                    x=[datetime.now()],
                    y=[avg_score],
                    mode="markers",
                    name=f"Grade {grade} Cohort",
                    marker=dict(size=12),
                )
            )

    fig.update_layout(
        title=f"Cohort Progress Over Time ({title_suffix})",
        xaxis_title="Date",
        yaxis_title="Average Skill Score (%)",
        yaxis=dict(range=[0, 100]),
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


# ================================================================================
# EXPORT FUNCTIONS
# ================================================================================


def export_to_csv(df: pd.DataFrame) -> BytesIO:
    """Export DataFrame to CSV"""
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding="utf-8")
    buffer.seek(0)
    return buffer


def export_to_pdf(df: pd.DataFrame) -> BytesIO:
    """Export summary report to PDF format"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )
        from reportlab.lib import colors
        from reportlab.lib.units import inch

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title = Paragraph(
            "UnseenEdge AI - School-Wide Skill Assessment Report", styles["Title"]
        )
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Generated date
        date_text = Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"],
        )
        story.append(date_text)
        story.append(Spacer(1, 0.3 * inch))

        # Summary Statistics
        summary_header = Paragraph("<b>Summary Statistics</b>", styles["Heading2"])
        story.append(summary_header)
        story.append(Spacer(1, 0.1 * inch))

        summary_data = [
            ["Total Students Assessed", str(df["student_id"].nunique())],
            ["Grade Levels", ", ".join(map(str, sorted(df["grade"].unique())))],
            [
                "Skills Tracked",
                "7 (Empathy, Adaptability, Problem Solving, Self-Regulation, Resilience, Communication, Collaboration)",
            ],
        ]
        summary_table = Table(summary_data, colWidths=[3 * inch, 3 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Skill Averages
        skill_header = Paragraph("<b>Skill Averages</b>", styles["Heading2"])
        story.append(skill_header)
        story.append(Spacer(1, 0.1 * inch))

        skill_avg = (
            df.groupby("skill")["score"].agg(["mean", "std", "count"]).reset_index()
        )
        skill_data = [["Skill", "Average Score", "Std Dev", "N Students"]]
        for _, row in skill_avg.iterrows():
            skill_data.append(
                [
                    row["skill"].replace("_", " ").title(),
                    f"{row['mean']*100:.1f}%",
                    f"±{row['std']*100:.1f}%",
                    str(int(row["count"])),
                ]
            )

        skill_table = Table(
            skill_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch]
        )
        skill_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        story.append(skill_table)
        story.append(Spacer(1, 0.3 * inch))

        # Grade Distribution
        grade_header = Paragraph("<b>Grade Distribution</b>", styles["Heading2"])
        story.append(grade_header)
        story.append(Spacer(1, 0.1 * inch))

        grade_counts = df.groupby("grade")["student_id"].nunique().sort_index()
        grade_data = [["Grade", "Number of Students"]]
        for grade, count in grade_counts.items():
            grade_data.append([f"Grade {grade}", str(count)])

        grade_table = Table(grade_data, colWidths=[3 * inch, 3 * inch])
        grade_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        story.append(grade_table)

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    except ImportError:
        # Fallback if reportlab not installed
        st.warning("PDF export requires reportlab. Install with: pip install reportlab")
        return None


def identify_low_performing_groups(
    df: pd.DataFrame, threshold: float = 0.60
) -> List[Dict[str, Any]]:
    """Identify groups that need support based on skill scores below threshold

    Args:
        df: Assessment dataframe
        threshold: Score threshold (0-1) below which groups are flagged (default 0.60 = 60%)

    Returns:
        List of alerts with group info and recommendations
    """
    alerts = []

    # Check by grade
    grade_stats = (
        df.groupby(["grade", "skill"])["score"].agg(["mean", "count"]).reset_index()
    )
    for _, row in grade_stats.iterrows():
        if row["mean"] < threshold and row["count"] >= 3:  # At least 3 students
            alerts.append(
                {
                    "type": "grade",
                    "severity": "high" if row["mean"] < 0.50 else "medium",
                    "group": f"Grade {row['grade']}",
                    "skill": row["skill"].replace("_", " ").title(),
                    "score": row["mean"],
                    "n_students": int(row["count"]),
                    "recommendation": f"Consider targeted interventions for {row['skill'].replace('_', ' ')} skills in Grade {row['grade']}",
                }
            )

    # Check by demographic groups (if data available)
    for demo_field in ["gender", "ethnicity"]:
        if demo_field in df.columns and df[demo_field].notna().any():
            demo_stats = (
                df.groupby([demo_field, "skill"])["score"]
                .agg(["mean", "count"])
                .reset_index()
            )
            overall_mean = df.groupby("skill")["score"].mean()

            for _, row in demo_stats.iterrows():
                skill_overall = overall_mean.get(row["skill"], 0.70)
                # Flag if 15+ percentage points below average
                if (skill_overall - row["mean"]) > 0.15 and row["count"] >= 5:
                    alerts.append(
                        {
                            "type": demo_field,
                            "severity": "high",
                            "group": row[demo_field],
                            "skill": row["skill"].replace("_", " ").title(),
                            "score": row["mean"],
                            "gap": skill_overall - row["mean"],
                            "n_students": int(row["count"]),
                            "recommendation": f"Equity concern: {row[demo_field]} students show significant gap in {row['skill'].replace('_', ' ')} (gap: {(skill_overall - row['mean'])*100:.1f}%)",
                        }
                    )

    # Sort by severity and gap
    alerts.sort(
        key=lambda x: (x["severity"] == "high", x.get("gap", 1 - x["score"])),
        reverse=True,
    )

    return alerts


def create_summary_report(df: pd.DataFrame) -> str:
    """Create text summary report"""
    report = []
    report.append("=" * 60)
    report.append("UnseenEdge AI - School-Wide Skill Assessment Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 60)
    report.append("")

    # Summary statistics
    report.append("SUMMARY STATISTICS")
    report.append("-" * 60)
    report.append(f"Total Students Assessed: {df['student_id'].nunique()}")
    report.append(f"Grade Levels: {sorted(df['grade'].unique())}")
    report.append("")

    # Skill averages
    report.append("SKILL AVERAGES")
    report.append("-" * 60)
    skill_avg = df.groupby("skill")["score"].agg(["mean", "std", "count"])
    for skill, row in skill_avg.iterrows():
        report.append(
            f"{skill.replace('_', ' ').title():20s}: {row['mean']*100:5.1f}% (±{row['std']*100:4.1f}%) [{int(row['count'])} students]"
        )
    report.append("")

    # Grade distribution
    report.append("GRADE DISTRIBUTION")
    report.append("-" * 60)
    grade_counts = df.groupby("grade")["student_id"].nunique().sort_index()
    for grade, count in grade_counts.items():
        report.append(f"Grade {grade}: {count} students")
    report.append("")

    # Demographic breakdown (if available)
    if "gender" in df.columns and df["gender"].notna().any():
        report.append("GENDER DISTRIBUTION")
        report.append("-" * 60)
        gender_counts = df.groupby("gender")["student_id"].nunique()
        for gender, count in gender_counts.items():
            report.append(f"{gender}: {count} students")
        report.append("")

    if "ethnicity" in df.columns and df["ethnicity"].notna().any():
        report.append("ETHNICITY DISTRIBUTION")
        report.append("-" * 60)
        ethnicity_counts = df.groupby("ethnicity")["student_id"].nunique()
        for ethnicity, count in ethnicity_counts.items():
            report.append(f"{ethnicity}: {count} students")
        report.append("")

    report.append("=" * 60)
    report.append("End of Report")
    report.append("=" * 60)

    return "\n".join(report)


# ================================================================================
# MAIN APP
# ================================================================================


def main():
    """Main application"""

    st.set_page_config(
        page_title="Admin Dashboard - UnseenEdge AI",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
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
        <div style='background-color: #e8f5e9; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #4CAF50;'>
            <h2 style='margin: 0; color: #2E7D32;'>📊 Administrator Dashboard - UnseenEdge AI</h2>
            <p style='margin: 10px 0 0 0; font-size: 16px;'>
                <strong>Demo Credentials:</strong><br>
                👤 Username: <code style='background: white; padding: 4px 8px; border-radius: 4px;'>admin</code><br>
                🔑 Password: <code style='background: white; padding: 4px 8px; border-radius: 4px;'>admin123</code>
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    auth_config = {
        "credentials": {
            "usernames": {
                os.getenv("ADMIN_USER", "admin"): {
                    "name": os.getenv("ADMIN_NAME", "Administrator"),
                    "password": os.getenv("ADMIN_PASSWORD", "admin123"),
                }
            }
        },
        "cookie": {
            "name": "unseenedge_admin_auth",
            "key": os.getenv(
                "ADMIN_COOKIE_KEY", "admin_secret_key_change_in_production"
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
        st.error("❌ Username/password is incorrect")
        st.stop()
    elif authentication_status == None:
        st.warning("⚠️ Please enter your username and password")
        st.stop()

    # Initialize API
    api = AdminAPI(API_URL)

    # ========================================================================
    # HEADER
    # ========================================================================

    st.title("📊 Administrator Dashboard - School-Wide Analytics")
    st.markdown("---")

    # ========================================================================
    # SIDEBAR
    # ========================================================================

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

        st.header("Navigation")
        page = st.radio(
            "Select View:",
            [
                "📊 School Overview",
                "📈 Trends & Progress",
                "⚖️ Equity Analysis",
                "🗺️ Grade/Class Heatmaps",
                "📥 Export Reports",
            ],
        )

        st.markdown("---")

        # Filters
        st.header("Filters")
        filter_grade = st.multiselect(
            "Grade Levels", options=list(range(1, 13)), default=[]
        )
        filter_gender = st.multiselect(
            "Gender", options=["Male", "Female", "Non-binary", "Not specified"]
        )
        filter_ethnicity = st.multiselect(
            "Ethnicity", options=[]
        )  # Populated dynamically

    # ========================================================================
    # LOAD DATA
    # ========================================================================

    if "df" not in st.session_state or st.button("🔄 Refresh Data"):
        with st.spinner("Loading student data..."):
            students = api.get_all_students()

            if not students:
                st.warning("No students found in the system.")
                st.stop()

            # Limit to reasonable batch size for demo
            student_ids = [s["id"] for s in students[:100]]

            with st.spinner(f"Analyzing {len(student_ids)} students..."):
                batch_results = api.get_batch_assessments(student_ids)

            if not batch_results or batch_results.get("successful", 0) == 0:
                st.error("No assessment data available.")
                st.stop()

            st.session_state.df = create_assessment_dataframe(batch_results, students)
            st.session_state.students = students[
                :100
            ]  # Store students for historical queries
            st.success(f"✅ Loaded data for {len(student_ids)} students")

    df = st.session_state.df
    students = st.session_state.get("students", [])

    # Apply filters
    if filter_grade:
        df = df[df["grade"].isin(filter_grade)]
    if filter_gender:
        df = df[df["gender"].isin(filter_gender)]
    if filter_ethnicity:
        df = df[df["ethnicity"].isin(filter_ethnicity)]

    # ========================================================================
    # PAGE CONTENT
    # ========================================================================

    if page == "📊 School Overview":
        st.header("School-Wide Skill Distribution")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Students", df["student_id"].nunique())
        with col2:
            st.metric("Grade Levels", len(df["grade"].unique()))
        with col3:
            st.metric("Avg Score", f"{df['score'].mean()*100:.1f}%")
        with col4:
            st.metric("Skills Tracked", len(SKILLS))

        st.markdown("---")

        # Alert System for Low-Performing Groups
        alerts = identify_low_performing_groups(df)
        if alerts:
            st.warning(f"⚠️ **{len(alerts)} Alert(s) Detected**: Groups needing support")

            with st.expander("📋 View All Alerts", expanded=len(alerts) <= 3):
                for i, alert in enumerate(alerts[:10]):  # Show top 10
                    severity_emoji = "🔴" if alert["severity"] == "high" else "🟡"
                    st.markdown(
                        f"""
                    **{severity_emoji} Alert {i+1}**: {alert['group']} - {alert['skill']}
                    - **Score**: {alert['score']*100:.1f}%
                    - **Students Affected**: {alert['n_students']}
                    - **Recommendation**: {alert['recommendation']}
                    """
                    )
                    st.markdown("---")
        else:
            st.success("✅ No alerts: All groups performing above threshold!")

        st.markdown("---")

        # Overall distribution
        fig = create_skill_distribution_bar(df)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Individual skill distributions
        st.subheader("Skill-Specific Distributions")

        selected_skill = st.selectbox(
            "Select Skill to View Distribution",
            options=SKILLS,
            format_func=lambda x: x.replace("_", " ").title(),
        )

        fig = create_skill_distribution_histogram(df, selected_skill)
        st.plotly_chart(fig, use_container_width=True)

    elif page == "📈 Trends & Progress":
        st.header("Trends & Progress Analysis")

        period = st.selectbox("Select Time Period", options=list(TIME_PERIODS.keys()))
        period_days = TIME_PERIODS[period]

        st.info(f"📌 Showing trend data for the past {period} ({period_days} days)")

        # Trend analysis
        fig = create_trend_analysis(df, period_days, api, students)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Longitudinal cohort tracking
        st.subheader("Cohort Progress (Longitudinal)")
        fig = create_longitudinal_cohort_graph(df, api, students)
        st.plotly_chart(fig, use_container_width=True)

    elif page == "⚖️ Equity Analysis":
        st.header("Equity Analysis")

        st.info(
            "Identify disparities across demographic groups to ensure equitable skill development."
        )

        demographic_field = st.radio(
            "Analyze by:",
            options=["gender", "ethnicity", "grade"],
            format_func=lambda x: x.title(),
        )

        fig = create_equity_analysis(df, demographic_field)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Statistical summary
        st.subheader(f"Statistical Summary by {demographic_field.title()}")

        equity_summary = (
            df.groupby([demographic_field, "skill"])["score"]
            .agg(["mean", "std", "count"])
            .reset_index()
        )
        equity_summary["mean_pct"] = (equity_summary["mean"] * 100).round(1)
        equity_summary["std_pct"] = (equity_summary["std"] * 100).round(1)
        equity_summary["skill"] = (
            equity_summary["skill"].str.replace("_", " ").str.title()
        )

        st.dataframe(
            equity_summary[
                [demographic_field, "skill", "mean_pct", "std_pct", "count"]
            ].rename(
                columns={
                    "mean_pct": "Avg Score (%)",
                    "std_pct": "Std Dev (%)",
                    "count": "N Students",
                }
            ),
            use_container_width=True,
        )

    elif page == "🗺️ Grade/Class Heatmaps":
        st.header("Heatmaps - Skill Levels by Grade/Class")

        tab1, tab2 = st.tabs(["📊 By Grade Level", "👥 By Student"])

        with tab1:
            st.subheader("Skill Heatmap by Grade Level")
            fig = create_grade_heatmap(df)
            st.plotly_chart(fig, use_container_width=True)

            st.info(
                "💡 Green = High scores, Yellow = Medium, Red = Low. Click cells for details."
            )

        with tab2:
            st.subheader("Student-Level Heatmap")
            st.info(
                "💡 This heatmap shows individual students. Click on a row to drill down to student details."
            )

            fig = create_class_heatmap(df)
            st.plotly_chart(fig, use_container_width=True)

            # Drill-down capability
            st.markdown("---")
            st.subheader("Drill-Down: Select Student")

            students_list = df[
                ["student_id", "first_name", "last_name", "grade"]
            ].drop_duplicates()
            selected_student = st.selectbox(
                "Choose a student to view details:",
                options=students_list["student_id"].tolist(),
                format_func=lambda x: f"{students_list[students_list['student_id']==x]['first_name'].values[0]} {students_list[students_list['student_id']==x]['last_name'].values[0]} (Grade {students_list[students_list['student_id']==x]['grade'].values[0]})",
            )

            if selected_student:
                student_df = df[df["student_id"] == selected_student]
                student_info = students_list[
                    students_list["student_id"] == selected_student
                ].iloc[0]

                st.markdown(
                    f"### {student_info['first_name']} {student_info['last_name']} - Grade {student_info['grade']}"
                )

                # Student skill radar chart
                student_skills = student_df.groupby("skill")["score"].mean()

                fig = go.Figure()
                fig.add_trace(
                    go.Scatterpolar(
                        r=student_skills.values * 100,
                        theta=[
                            s.replace("_", " ").title() for s in student_skills.index
                        ],
                        fill="toself",
                        name="Skills",
                    )
                )
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False,
                    height=400,
                )
                st.plotly_chart(fig, use_container_width=True)

                # Detailed scores table with reasoning
                st.subheader("Skill Scores & Analysis")

                # Show scores table
                st.dataframe(
                    student_df[["skill", "score", "confidence"]].rename(
                        columns={
                            "skill": "Skill",
                            "score": "Score",
                            "confidence": "Confidence",
                        }
                    ),
                    use_container_width=True,
                )

                # Show reasoning for each skill assessment
                st.subheader("Assessment Reasoning")
                st.info("💡 Detailed AI-generated reasoning for each skill assessment")

                for _, row in student_df.iterrows():
                    with st.expander(
                        f"📊 {row['skill'].replace('_', ' ').title()} - Score: {row['score']*100:.1f}%"
                    ):
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.markdown("**AI Reasoning:**")
                            reasoning = row.get("reasoning", "No reasoning available")
                            if reasoning and reasoning != "No reasoning available":
                                st.markdown(reasoning)
                            else:
                                st.warning(
                                    "Reasoning not yet generated for this assessment"
                                )

                        with col2:
                            st.metric("Score", f"{row['score']*100:.0f}%")
                            st.metric("Confidence", f"{row['confidence']*100:.0f}%")

                        # Show recommendations if available
                        recommendations = row.get("recommendations", "")
                        if recommendations:
                            st.markdown("**Recommendations:**")
                            st.markdown(recommendations)

    elif page == "📥 Export Reports":
        st.header("Export Reports")

        st.info("Generate and download reports in various formats.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("📄 CSV Export")
            st.write("Export raw assessment data as CSV for further analysis.")

            csv_buffer = export_to_csv(df)
            st.download_button(
                label="📥 Download CSV",
                data=csv_buffer,
                file_name=f"skill_assessments_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

        with col2:
            st.subheader("📊 Summary Report (Text)")
            st.write("Generate a text summary report with key statistics.")

            summary_report = create_summary_report(df)
            st.download_button(
                label="📥 Download TXT Report",
                data=summary_report,
                file_name=f"summary_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
            )

        with col3:
            st.subheader("📑 PDF Report")
            st.write("Generate a professional PDF report with tables and statistics.")

            if st.button("🔄 Generate PDF"):
                with st.spinner("Generating PDF report..."):
                    pdf_buffer = export_to_pdf(df)

                if pdf_buffer:
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_buffer,
                        file_name=f"skill_assessment_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                    )
                    st.success("✅ PDF generated successfully!")
                else:
                    st.error(
                        "❌ PDF generation failed. Install reportlab: pip install reportlab"
                    )

        st.markdown("---")

        # Preview
        st.subheader("Report Preview")
        st.text(summary_report)

    # ========================================================================
    # FOOTER
    # ========================================================================

    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center'>
        <p>📊 <strong>UnseenEdge AI Administrator Dashboard</strong></p>
        <p>School-Wide Analytics & Equity Analysis</p>
        <p style='color: gray; font-size: 12px'>Version 1.0 | 2025-11-14</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
