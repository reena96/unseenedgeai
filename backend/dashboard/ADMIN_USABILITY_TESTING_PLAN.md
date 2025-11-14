# Administrator Dashboard Usability Testing Plan

## Overview
This document outlines the usability testing plan for the UnseenEdge AI Administrator Dashboard to validate that administrators can effectively use the dashboard to gain insights into school-wide skill development and identify groups needing support.

## Testing Objectives
1. Validate that administrators can navigate the dashboard intuitively
2. Verify that administrators find the analytics actionable
3. Confirm that key insights (trends, equity gaps, alerts) are easily discoverable
4. Assess dashboard performance with realistic data volumes
5. Identify pain points and areas for improvement

## Target Participants
- **Number**: 2-3 school administrators
- **Roles**: Principals, Assistant Principals, or District Administrators
- **Experience**: Varied comfort levels with data dashboards (beginner to advanced)
- **Context**: Administrators responsible for school-wide or district-wide student outcomes

## Test Environment
- **Dashboard Version**: Admin Dashboard v1.0 (Streamlit)
- **Data**: Sample dataset with 100+ students across grades 6-12
- **Access**: Remote testing via screen share or in-person observation
- **Duration**: 45-60 minutes per session

## Testing Materials

### Pre-Test Materials
- Welcome email with testing schedule and Zoom link
- Brief overview of UnseenEdge AI (1-page summary)
- Login credentials (admin/admin123)
- Consent form for recording and note-taking

### Post-Test Materials
- System Usability Scale (SUS) questionnaire
- Custom satisfaction survey
- Follow-up interview questions

## Test Scenarios

### Scenario 1: Getting Oriented (5 minutes)
**Task**: Login and explore the dashboard homepage
**Success Criteria**:
- Successfully logs in within 1 minute
- Identifies the main navigation options
- Understands the purpose of each page

**Observation Points**:
- Does the user understand what each navigation option offers?
- Is the dashboard layout intuitive?
- Are the metrics on the overview page meaningful?

---

### Scenario 2: Identifying School-Wide Trends (10 minutes)
**Task**: Find which skills are strongest/weakest across the school
**Success Criteria**:
- Navigates to School Overview within 30 seconds
- Correctly identifies top 2 and bottom 2 skills
- Understands what the score percentages represent

**Observation Points**:
- Can the user easily interpret the skill distribution chart?
- Do the visualizations clearly communicate insights?
- Does the user notice the alert system?

**Follow-up Questions**:
- "What do these scores tell you about your school?"
- "Would you take any action based on this data?"

---

### Scenario 3: Exploring Trends Over Time (10 minutes)
**Task**: Examine how skills have changed over the past 12 weeks
**Success Criteria**:
- Navigates to "Trends & Progress" page
- Selects different time periods (4-week, 12-week, semester)
- Interprets whether skills are improving or declining

**Observation Points**:
- Is the trend data visualization clear?
- Can the user understand the direction of change?
- Does the user notice whether data is historical or simulated?

**Follow-up Questions**:
- "Which skills show the most growth?"
- "Does this match your expectations for your school?"
- "Would you share this data with your staff? Why or why not?"

---

### Scenario 4: Identifying Equity Gaps (15 minutes)
**Task**: Determine if there are disparities across demographic groups
**Success Criteria**:
- Navigates to "Equity Analysis" page
- Analyzes data by gender, ethnicity, and grade level
- Identifies any significant gaps (>15% difference)

**Observation Points**:
- Is the equity analysis visualization easy to understand?
- Can the user identify actionable insights?
- Does the user understand the statistical significance?

**Follow-up Questions**:
- "Do you see any concerning patterns?"
- "What would you do with this information?"
- "Is the data granular enough for decision-making?"

---

### Scenario 5: Drilling Down to Specific Groups (10 minutes)
**Task**: Find which classrooms or students in Grade 7 need support in Empathy
**Success Criteria**:
- Navigates to "Grade/Class Heatmaps" page
- Uses filters to isolate Grade 7
- Identifies low-performing cells in the heatmap
- Drills down to view individual student data

**Observation Points**:
- Can the user effectively use filters?
- Is the heatmap color coding intuitive (red=low, green=high)?
- Does the drill-down navigation work smoothly?

**Follow-up Questions**:
- "Was it easy to find specific groups?"
- "Would you use this feature regularly? Why or why not?"

---

### Scenario 6: Exporting Data for Reporting (5 minutes)
**Task**: Export a summary report for a school board meeting
**Success Criteria**:
- Navigates to "Export Reports" page
- Successfully downloads CSV and PDF reports
- Understands the difference between export formats

**Observation Points**:
- Is the export process straightforward?
- Are the export options clearly labeled?
- Does the user understand what data is included?

**Follow-up Questions**:
- "Would you feel confident presenting this report?"
- "Is any critical information missing?"

---

## Data Collection Methods

### Quantitative Metrics
1. **Task Success Rate**: % of tasks completed successfully
2. **Time on Task**: Average time to complete each scenario
3. **Error Rate**: Number of navigation errors or misinterpretations
4. **System Usability Scale (SUS) Score**: Target ≥ 75 (Good usability)
5. **Net Promoter Score (NPS)**: Would recommend to peers?

### Qualitative Data
1. **Think-Aloud Protocol**: Participants verbalize thoughts during tasks
2. **Screen Recordings**: Capture all interactions
3. **Observer Notes**: Document hesitations, confusion, delight
4. **Post-Test Interview**: Open-ended questions about experience
5. **Survey Comments**: Free-text feedback on strengths/weaknesses

## Success Criteria

### Must-Have Benchmarks
- ✅ **75%+ task success rate** across all scenarios
- ✅ **75%+ SUS score** (Good usability)
- ✅ **75%+ of participants** find insights actionable
- ✅ **Zero critical errors** (data misinterpretation, system crashes)
- ✅ **All participants** can export a report successfully

### Nice-to-Have Benchmarks
- ⭐ **85%+ SUS score** (Excellent usability)
- ⭐ **90%+ task success rate**
- ⭐ **Positive NPS** (>0, ideally +50)
- ⭐ **<2 minutes** average time for common tasks

## Interview Questions

### Pre-Test
1. "How do you currently track student skill development?"
2. "What data do you wish you had access to?"
3. "How comfortable are you with data dashboards?"

### Post-Test
1. "What was your first impression of the dashboard?"
2. "Which feature did you find most valuable? Least valuable?"
3. "Did anything confuse or frustrate you?"
4. "What information is missing that you'd want to see?"
5. "Would you use this dashboard in your daily work? How?"
6. "On a scale of 1-10, how likely are you to recommend this to other administrators?"

## Timeline

| Phase | Activities | Duration |
|-------|-----------|----------|
| **Planning** | Recruit participants, prepare materials | Week 1 |
| **Pilot Test** | Run 1 pilot session, refine scenarios | Week 2 |
| **Testing** | Conduct 2-3 usability sessions | Week 2-3 |
| **Analysis** | Review recordings, compile metrics | Week 3 |
| **Reporting** | Document findings, prioritize fixes | Week 4 |
| **Iteration** | Implement high-priority improvements | Week 5-6 |

## Deliverables

1. **Usability Test Report** (PDF)
   - Executive summary
   - Task success rates and time on task
   - SUS scores and interpretation
   - Key findings and recommendations
   - Participant quotes

2. **Prioritized Improvement List** (Excel/Notion)
   - Critical issues (P0): Must fix before launch
   - High-priority (P1): Fix in next sprint
   - Medium-priority (P2): Fix in 2-3 months
   - Low-priority (P3): Nice-to-haves

3. **Video Highlights Reel** (3-5 minutes)
   - Positive moments (delight, aha moments)
   - Pain points (confusion, frustration)
   - Actionable clips for design team

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| Participants don't show up | Over-recruit by 20%, send reminders |
| Technical issues during testing | Test all tech 24hrs before, have backup plan |
| Participants aren't representative | Screen participants carefully, ensure diversity |
| Data is not realistic | Use seed data that mirrors real school demographics |
| Participants are too polite | Emphasize that honest feedback helps improve the tool |

## Follow-Up Actions

### After Each Session
- Debrief with observer team
- Note immediate critical issues
- Update test script if needed

### After All Sessions
- Compile all metrics and themes
- Create prioritized bug/enhancement list
- Share findings with development team
- Schedule iteration planning meeting

## Contact Information

**Research Lead**: [TBD]
**Participant Recruitment**: [TBD]
**Technical Support**: [TBD]

---

**Last Updated**: 2025-11-14
**Version**: 1.0
