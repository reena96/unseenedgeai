# Teacher Dashboard Capability

## Purpose

The Teacher Dashboard provides educators with intuitive, evidence-based insights into student skill development. It displays skill assessments, historical trends, supporting evidence, and actionable recommendations for all 7 non-academic skills.

## Requirements

### Requirement: Authentication and Authorization

The system SHALL ensure teachers can only access data for their assigned students.

#### Scenario: Teacher login
- **GIVEN** a teacher navigates to the dashboard
- **WHEN** they enter valid credentials
- **THEN** they are authenticated via OAuth 2.0 + JWT
- **AND** their assigned classrooms and students are loaded
- **AND** they are redirected to the class overview page

#### Scenario: Authorization enforcement
- **GIVEN** a teacher is authenticated
- **WHEN** they attempt to view student data
- **THEN** the system verifies the student is in one of their classrooms
- **AND** access is denied if the student is not theirs
- **AND** unauthorized access is logged for audit

#### Scenario: Session management
- **GIVEN** a teacher is logged in
- **WHEN** 60 minutes of inactivity pass
- **THEN** the session expires
- **AND** they are redirected to login
- **AND** in-progress work is preserved in browser storage

### Requirement: Class Overview (Heatmap)

The system SHALL display a visual heatmap of skill levels for all students in a classroom.

#### Scenario: Heatmap visualization
- **GIVEN** a teacher selects a classroom
- **WHEN** the class overview loads
- **THEN** a grid is displayed with students (rows) × skills (columns)
- **AND** each cell is color-coded:
  - Green (0.75-1.00): Proficient
  - Yellow (0.50-0.74): Developing
  - Red (0.00-0.49): Emerging
  - Gray: No data available
- **AND** cells show the numeric score on hover

#### Scenario: Sorting and filtering
- **GIVEN** the class heatmap is displayed
- **WHEN** a teacher clicks a column header
- **THEN** students are sorted by that skill (high to low or low to high)
- **AND** sort direction is indicated visually
- **AND** sorting persists during the session

#### Scenario: Skill-based filtering
- **GIVEN** the class heatmap
- **WHEN** a teacher selects "Show only students needing support"
- **THEN** only students with any skill <0.50 are displayed
- **AND** count of filtered students is shown
- **AND** filter can be cleared to show all students

#### Scenario: Real-time updates
- **GIVEN** the heatmap is displayed
- **WHEN** new assessments are generated (nightly batch)
- **THEN** the heatmap auto-refreshes the next time the page loads
- **AND** a notification banner indicates "New data available"
- **AND** teacher can click to refresh immediately

### Requirement: Student Detail View

The system SHALL provide in-depth skill profiles for individual students.

#### Scenario: Student profile navigation
- **GIVEN** a teacher is viewing the class heatmap
- **WHEN** they click on a student's name
- **THEN** the student detail page loads
- **AND** all 7 skill scores are displayed with confidence bands
- **AND** most recent assessment period is shown

#### Scenario: Skill score display
- **GIVEN** the student detail view
- **WHEN** displaying skill scores
- **THEN** each skill shows:
  - Score (0-1) as a progress bar with color coding
  - Confidence level (0-1) as a visual indicator
  - Score level label ("Emerging", "Developing", "Proficient")
  - Last updated date
- **AND** skills are sortable by score or alphabetically

#### Scenario: Confidence visualization
- **GIVEN** a skill with confidence 0.65
- **WHEN** displaying the score
- **THEN** confidence is shown as a badge or icon
- **AND** tooltip explains: "Based on transcript, game, and teacher data"
- **AND** low confidence (<0.70) includes a note suggesting more data collection

### Requirement: Historical Trends

The system SHALL display skill development over time with trend analysis.

#### Scenario: Trend chart display
- **GIVEN** a student has multiple assessments over 8+ weeks
- **WHEN** viewing their skill detail
- **THEN** a line chart shows score progression over time
- **AND** x-axis is assessment periods (weeks)
- **AND** y-axis is skill score (0-1)
- **AND** trend line is smooth (not jagged)

#### Scenario: Trend direction indicator
- **GIVEN** historical skill data
- **WHEN** calculating trend
- **THEN** the system computes slope (linear regression)
- **AND** displays visual indicator:
  - ↑ Improving (positive slope >0.05)
  - → Stable (slope between -0.05 and 0.05)
  - ↓ Declining (negative slope <-0.05)
- **AND** statistical significance (p-value) is calculated

#### Scenario: Multi-skill comparison
- **GIVEN** a student's historical data
- **WHEN** teacher selects "Compare all skills"
- **THEN** all 7 skills are plotted on the same chart
- **AND** each skill has a different color
- **AND** legend is displayed
- **AND** chart is interactive (hover for values)

### Requirement: Evidence Viewer

The system SHALL display supporting evidence for each skill assessment with source attribution.

#### Scenario: Evidence list display
- **GIVEN** a skill assessment with 5 evidence items
- **WHEN** teacher views evidence
- **THEN** all 5 items are displayed in a list
- **AND** each item shows:
  - Source type (transcript, game, teacher rubric) with icon
  - Evidence text or description
  - Timestamp or date
  - Relevance score (if available)
- **AND** evidence is sorted by relevance (high to low)

#### Scenario: Transcript evidence with context
- **GIVEN** evidence from a classroom transcript
- **WHEN** displaying the evidence
- **THEN** the system shows:
  - Main evidence text (highlighted)
  - Context before (1-2 sentences)
  - Context after (1-2 sentences)
  - Timestamp in classroom recording
- **AND** teacher can click to view full transcript segment

#### Scenario: Game evidence display
- **GIVEN** evidence from game telemetry
- **WHEN** displaying the evidence
- **THEN** the system shows:
  - Mission name (e.g., "Understanding Perspectives")
  - Behavior description (e.g., "Chose empathetic dialogue option")
  - Game timestamp
- **AND** teacher can view full game session summary

#### Scenario: Teacher rubric evidence
- **GIVEN** evidence from teacher's own rubric assessment
- **WHEN** displaying the evidence
- **THEN** the system shows:
  - Rubric score (1-4)
  - Teacher's qualitative feedback
  - Assessment date
- **AND** teacher can edit or update their rubric entry

#### Scenario: Evidence expansion
- **GIVEN** a collapsed evidence item
- **WHEN** teacher clicks "Show more"
- **THEN** full context and metadata are revealed
- **AND** teacher can collapse it again

### Requirement: AI-Generated Reasoning

The system SHALL display clear, growth-oriented explanations for skill assessments.

#### Scenario: Reasoning display
- **GIVEN** a skill assessment with GPT-4 generated reasoning
- **WHEN** displaying to teacher
- **THEN** reasoning text (2-3 sentences) is shown
- **AND** text is formatted for readability
- **AND** reasoning cites specific evidence
- **AND** language is growth-oriented and asset-based

#### Scenario: Reasoning for different score levels
- **GIVEN** a proficient skill (score ≥0.75)
- **WHEN** displaying reasoning
- **THEN** reasoning celebrates strengths
- **AND** provides specific examples from evidence
- **GIVEN** a developing skill (0.50-0.74)
- **THEN** reasoning acknowledges progress and identifies growth areas
- **GIVEN** an emerging skill (<0.50)
- **THEN** reasoning focuses on incremental gains and next steps

#### Scenario: Reasoning transparency
- **GIVEN** GPT-4 generated reasoning
- **WHEN** teacher hovers over or clicks info icon
- **THEN** a tooltip explains: "Generated by AI based on classroom data"
- **AND** teacher understands this is AI-assisted, not purely human judgment

### Requirement: Intervention Alerts

The system SHALL proactively flag students who may need additional support.

#### Scenario: Low skill alert
- **GIVEN** a student has 2+ skills with score <0.50
- **WHEN** teacher views class overview
- **THEN** student row is flagged with an alert icon
- **AND** clicking the alert shows which skills need attention
- **AND** suggested interventions are provided

#### Scenario: Declining trend alert
- **GIVEN** a student's skill drops >0.20 points over 4 weeks
- **WHEN** viewing student detail
- **THEN** a warning banner is displayed
- **AND** banner includes: "Resilience has declined significantly"
- **AND** teacher can dismiss or acknowledge the alert

#### Scenario: Stagnant progress alert
- **GIVEN** a student shows no improvement (<0.05 change) over 8 weeks
- **WHEN** reviewing the student
- **THEN** a note indicates "Limited growth in Adaptability"
- **AND** teacher can mark as "monitoring" or "intervention planned"

### Requirement: Teacher Rubric Input

The system SHALL allow teachers to submit their own skill assessments via rubrics.

#### Scenario: Rubric assessment form
- **GIVEN** a teacher is viewing a student profile
- **WHEN** they click "Add Teacher Assessment"
- **THEN** a rubric form is displayed for each skill
- **AND** each skill has a 1-4 scale with behavioral anchors:
  - 1: Emerging (needs significant support)
  - 2: Developing (progressing with support)
  - 3: Proficient (meets expectations)
  - 4: Advanced (exceeds expectations)
- **AND** teacher can add qualitative feedback (optional, text field)

#### Scenario: Rubric submission
- **GIVEN** a teacher completes the rubric form
- **WHEN** they submit
- **THEN** rubric scores are saved to the database
- **AND** assessment date is recorded
- **AND** teacher receives confirmation
- **AND** rubric data is included in next fusion cycle

#### Scenario: Bulk rubric entry
- **GIVEN** a teacher wants to assess all students in a class
- **WHEN** they select "Bulk Rubric Entry"
- **THEN** a spreadsheet-like interface is displayed
- **AND** teacher can enter scores for all students × 7 skills
- **AND** form validates all required fields before submission
- **AND** progress is auto-saved every 2 minutes

### Requirement: Data Export

The system SHALL enable teachers to export assessment data for reporting.

#### Scenario: Class report export (CSV)
- **GIVEN** a teacher is viewing class overview
- **WHEN** they click "Export to CSV"
- **THEN** a CSV file is generated with:
  - Student names (or IDs if anonymized)
  - All 7 skill scores
  - Confidence levels
  - Assessment period
- **AND** file downloads immediately
- **AND** filename includes class name and date

#### Scenario: Individual student report (PDF)
- **GIVEN** a teacher is viewing a student detail page
- **WHEN** they click "Generate PDF Report"
- **THEN** a formatted PDF is created with:
  - Student name and demographic info
  - All 7 skill scores with visualizations
  - Historical trend charts
  - Top 3 evidence items per skill
  - AI-generated reasoning
- **AND** PDF is suitable for parent-teacher conferences

#### Scenario: Longitudinal report
- **GIVEN** a teacher selects date range (e.g., full semester)
- **WHEN** exporting longitudinal data
- **THEN** CSV includes all assessment periods in range
- **AND** one row per student per period
- **AND** trend analysis summary is included

### Requirement: Dashboard Performance

The system SHALL load quickly and respond to user interactions smoothly.

#### Scenario: Initial page load
- **GIVEN** a teacher navigates to the dashboard
- **WHEN** the page loads
- **THEN** class overview appears within 2 seconds
- **AND** heatmap data is fetched asynchronously
- **AND** loading skeletons are shown during fetch

#### Scenario: Student detail load
- **GIVEN** a teacher clicks on a student
- **WHEN** the detail page loads
- **THEN** basic info appears within 1 second
- **AND** charts and evidence load progressively
- **AND** page is interactive while data loads

#### Scenario: Large classroom handling
- **GIVEN** a classroom with 35 students
- **WHEN** displaying the heatmap
- **THEN** all data loads within 3 seconds
- **AND** scrolling is smooth (60 fps)
- **AND** no UI lag when sorting/filtering

### Requirement: Responsive Design

The system SHALL be usable on desktop, tablet, and mobile devices.

#### Scenario: Desktop view (≥1024px)
- **GIVEN** a teacher on a desktop computer
- **WHEN** viewing the dashboard
- **THEN** heatmap displays full 7-column grid
- **AND** all controls are visible
- **AND** charts are large and readable

#### Scenario: Tablet view (768-1023px)
- **GIVEN** a teacher on a tablet
- **WHEN** viewing the dashboard
- **THEN** heatmap adapts to smaller width
- **AND** skills may be displayed 2-3 per row
- **AND** touch interactions work smoothly

#### Scenario: Mobile view (<768px)
- **GIVEN** a teacher on a smartphone
- **WHEN** viewing the dashboard
- **THEN** heatmap switches to list view (no grid)
- **AND** student cards stack vertically
- **AND** navigation is via hamburger menu

### Requirement: Accessibility (WCAG 2.1 Level AA)

The system SHALL be accessible to users with disabilities.

#### Scenario: Keyboard navigation
- **GIVEN** a teacher using keyboard only
- **WHEN** navigating the dashboard
- **THEN** all interactive elements are keyboard accessible
- **AND** focus indicators are clearly visible
- **AND** tab order is logical

#### Scenario: Screen reader support
- **GIVEN** a teacher using a screen reader
- **WHEN** accessing the dashboard
- **THEN** all content has semantic HTML and ARIA labels
- **AND** charts have alt text descriptions
- **AND** heatmap color meanings are announced

#### Scenario: Color contrast
- **GIVEN** heatmap color coding (red/yellow/green)
- **WHEN** displaying scores
- **THEN** all colors meet WCAG AA contrast ratios (4.5:1 for text)
- **AND** colorblind-friendly palette is used
- **AND** score labels supplement color (not color alone)

#### Scenario: Text scaling
- **GIVEN** a teacher increases browser font size to 200%
- **WHEN** viewing the dashboard
- **THEN** all text scales appropriately
- **AND** layout adapts without horizontal scrolling
- **AND** no content is cut off or overlapping

## Non-Functional Requirements

### Performance
- **Initial load:** <2 seconds
- **Student detail load:** <1 second
- **Chart rendering:** <500ms
- **CSV export:** <3 seconds for 100 students

### Usability
- **Learnability:** Teachers can navigate core features within 10 minutes
- **Efficiency:** Access student detail in ≤2 clicks from home
- **Satisfaction:** 80%+ teachers rate dashboard as "helpful" or "very helpful"

### Browser Support
- **Desktop:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile:** iOS Safari 14+, Chrome Android 90+

### Security
- **HTTPS:** All traffic encrypted with TLS 1.3
- **XSS Protection:** Content Security Policy enforced
- **CSRF Protection:** Tokens required for state-changing operations
- **Session timeout:** 60 minutes of inactivity

## Dependencies

### Internal Services
- **Authentication Service:** User login and session management
- **Evidence Fusion Service:** Provides fused skill assessments
- **Skill Inference Service:** Provides source scores
- **Database:** PostgreSQL for all assessment data

### External Libraries
- **React 18.x:** UI framework
- **Chart.js or Recharts:** Data visualization
- **Material-UI or Chakra UI:** Component library
- **React Query:** Server state management and caching
- **Axios:** HTTP client
- **date-fns:** Date formatting

## API Endpoints (Backend)

### GET /api/v1/dashboard/class/{classroom_id}
Get class overview data for heatmap.

**Response:** 200 OK
```json
{
  "classroom_id": "uuid",
  "classroom_name": "Ms. Johnson's 7th Grade",
  "assessment_period": {
    "start": "2024-01-01",
    "end": "2024-01-07"
  },
  "students": [
    {
      "student_id": "uuid",
      "first_name": "Marcus",
      "last_name": "Chen",
      "skills": {
        "empathy": {"score": 0.78, "confidence": 0.85},
        "adaptability": {"score": 0.65, "confidence": 0.72},
        "problem_solving": {"score": 0.82, "confidence": 0.88},
        "self_regulation": {"score": 0.70, "confidence": 0.75},
        "resilience": {"score": 0.75, "confidence": 0.80},
        "communication": {"score": 0.88, "confidence": 0.90},
        "collaboration": {"score": 0.80, "confidence": 0.83}
      },
      "alerts": ["declining_trend_resilience"]
    }
  ]
}
```

### GET /api/v1/dashboard/student/{student_id}
Get detailed student profile.

**Query Params:**
- `include_history`: boolean (default: true)
- `history_weeks`: integer (default: 12)

**Response:** 200 OK
```json
{
  "student_id": "uuid",
  "first_name": "Marcus",
  "last_name": "Chen",
  "grade_level": 7,
  "current_skills": { /* same as class endpoint */ },
  "historical_assessments": [
    {
      "period": {"start": "2024-01-01", "end": "2024-01-07"},
      "skills": { /* scores for each skill */ }
    }
  ],
  "trend_analysis": {
    "empathy": {"direction": "improving", "slope": 0.08, "p_value": 0.03}
  }
}
```

### GET /api/v1/dashboard/evidence/{assessment_id}
Already defined in Evidence Fusion spec.

### GET /api/v1/dashboard/reasoning/{assessment_id}
Already defined in Evidence Fusion spec.

### POST /api/v1/rubrics/assessment
Submit teacher rubric assessment.

**Request:**
```json
{
  "student_id": "uuid",
  "teacher_id": "uuid",
  "assessment_date": "2024-01-15",
  "assessments": [
    {
      "skill": "empathy",
      "score": 3,
      "feedback": "Shows good understanding of peers' perspectives"
    },
    {
      "skill": "adaptability",
      "score": 2,
      "feedback": "Struggles with unexpected changes to routine"
    }
  ]
}
```

**Response:** 201 Created
```json
{
  "rubric_ids": ["uuid1", "uuid2"],
  "created_count": 2
}
```

### GET /api/v1/dashboard/export/class/{classroom_id}
Export class data as CSV.

**Query Params:**
- `period_start`: Date
- `period_end`: Date
- `format`: "csv" | "json"

**Response:** 200 OK
```
Content-Type: text/csv
Content-Disposition: attachment; filename="class_7A_skills_2024-01-15.csv"

Student ID,First Name,Last Name,Empathy,Adaptability,Problem Solving,...
uuid1,Marcus,Chen,0.78,0.65,0.82,...
uuid2,Sarah,Lopez,0.85,0.72,0.88,...
```

## UI Components

### ClassHeatmap Component
```tsx
interface ClassHeatmapProps {
  classroomId: string;
  onStudentClick: (studentId: string) => void;
}

// Displays color-coded grid of students × skills
// Supports sorting, filtering, and real-time updates
```

### StudentProfile Component
```tsx
interface StudentProfileProps {
  studentId: string;
  includeHistory?: boolean;
}

// Shows skill scores, confidence, trends, evidence, reasoning
// Expandable sections for detailed views
```

### SkillTrendChart Component
```tsx
interface SkillTrendChartProps {
  studentId: string;
  skills: string[];  // ["empathy", "adaptability"]
  weeks: number;     // historical period
}

// Line chart showing skill progression over time
// Interactive hover for exact values
```

### EvidenceList Component
```tsx
interface EvidenceListProps {
  assessmentId: string;
  maxItems?: number;
}

// Displays evidence items with source icons
// Expandable for full context
// Sorted by relevance
```

## Error Handling

### Error States
- **No data available:** "No assessments yet. Check back after students complete game and transcripts are processed."
- **Loading error:** "Unable to load data. Please refresh or contact support."
- **Unauthorized:** "You don't have permission to view this student."
- **Session expired:** "Your session has expired. Please log in again."

### Graceful Degradation
- If charts fail to load, show data in table format
- If evidence unavailable, show score and confidence only
- If API slow, show cached data with "Last updated" timestamp

## Monitoring and Metrics

### User Metrics
- **Daily active teachers:** Track logins per day
- **Feature usage:** Which pages/features are most used
- **Session duration:** Average time spent on dashboard
- **Export frequency:** How often teachers export data

### Performance Metrics
- **Page load time p95:** Target <2s
- **API latency p95:** Target <500ms
- **Error rate:** Target <1%

### Alerts
- Page load time p95 >3 seconds
- API error rate >5%
- Dashboard unavailable (uptime <99%)

## Testing Strategy

### Unit Tests
- React component rendering
- User interaction handlers (click, sort, filter)
- Data transformation logic
- Chart rendering

### Integration Tests
- Full user flows: login → class overview → student detail → evidence → export
- API integration with real backend
- Form submission (rubric entry)

### Accessibility Tests
- Automated: axe-core, Lighthouse
- Manual: keyboard navigation, screen reader testing
- Color contrast validation

### Usability Tests
- 5 teachers perform task scenarios (find student, view evidence, export data)
- Target: 90%+ task completion rate
- Collect feedback on clarity and usefulness

## Future Enhancements (Out of Scope for Phase 1)

- **Administrator Dashboard:** District-level views, school comparisons
- **Student Dashboard:** Age-appropriate skill summaries and growth visualizations
- **Parent Portal:** View student progress with limited data
- **Intervention Library:** Suggested activities per skill and score level
- **Collaborative Notes:** Teachers share observations about students
- **Real-Time Alerts:** Push notifications for significant changes
- **Custom Views:** Teachers create saved filters and layouts
- **Mobile App:** Native iOS/Android app (currently web-only)
