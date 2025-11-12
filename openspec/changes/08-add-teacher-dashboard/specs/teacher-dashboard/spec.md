# Teacher Dashboard Capability Delta

## ADDED Requirements

### Requirement: Class Overview Heatmap

The system SHALL display a visual heatmap showing all students and their skill scores in a grid format.

#### Scenario: Display class heatmap
- **GIVEN** a teacher views their classroom
- **WHEN** the class overview page loads
- **THEN** a grid is displayed with rows=students, columns=7 skills
- **AND** each cell shows a color-coded score (red <0.5, yellow 0.5-0.75, green >0.75)
- **AND** hovering over a cell shows exact score value
- **AND** clicking a cell navigates to student detail for that skill

#### Scenario: Filter and sort heatmap
- **GIVEN** a heatmap is displayed
- **WHEN** teacher applies filters (skill, score range, time period)
- **THEN** heatmap updates to show only matching data
- **AND** teacher can sort by student name or skill scores
- **AND** filters persist when navigating between pages

### Requirement: Student Detail View

The system SHALL provide detailed skill profiles for individual students.

#### Scenario: View student skill profile
- **GIVEN** a teacher selects a student
- **WHEN** the student detail page loads
- **THEN** all 7 skills are displayed with scores and confidence bars
- **AND** reasoning text is displayed for each skill
- **AND** source breakdown shows transcript, game, teacher contributions
- **AND** historical trend chart shows skill development over time

#### Scenario: Navigate to evidence
- **GIVEN** a teacher is viewing a skill assessment
- **WHEN** they click "View Evidence"
- **THEN** evidence viewer opens with all evidence items
- **AND** evidence is grouped by source type
- **AND** evidence is sorted by relevance score

### Requirement: Evidence Viewer

The system SHALL display supporting evidence for skill assessments with context.

#### Scenario: Display evidence items
- **GIVEN** a teacher opens the evidence viewer for a skill
- **WHEN** evidence items load
- **THEN** each item shows: source type icon, evidence text, timestamp, relevance score
- **AND** items are grouped by source (transcript, game, teacher)
- **AND** teacher can expand context (before/after text)
- **AND** skill-relevant phrases are highlighted

#### Scenario: Timeline view
- **GIVEN** evidence viewer is open
- **WHEN** teacher switches to timeline view
- **THEN** evidence is displayed chronologically
- **AND** timeline shows when evidence was collected
- **AND** teacher can filter by date range

### Requirement: Teacher Rubric Submission

The system SHALL allow teachers to submit rubric assessments for students.

#### Scenario: Submit rubric for student
- **GIVEN** a teacher is reviewing a student
- **WHEN** they click "Submit Rubric"
- **THEN** rubric form displays all 7 skills with 4-point scale
- **AND** each scale level has descriptive anchors
- **AND** teacher can add optional qualitative feedback
- **AND** form validates all skills have scores before submission
- **AND** submission is saved and included in future fusion calculations

### Requirement: Responsive and Accessible Design

The system SHALL be usable on desktop and tablet devices with full accessibility support.

#### Scenario: Desktop usage
- **GIVEN** a teacher accesses the dashboard on a desktop (1920x1080)
- **WHEN** they navigate the interface
- **THEN** all components are fully visible and functional
- **AND** charts and visualizations use available screen space

#### Scenario: Keyboard navigation
- **GIVEN** a teacher uses keyboard only (no mouse)
- **WHEN** they navigate the dashboard
- **THEN** all interactive elements are reachable via Tab key
- **AND** focus indicators are clearly visible
- **AND** Enter/Space activates buttons and links

#### Scenario: Screen reader compatibility
- **GIVEN** a visually impaired teacher uses a screen reader
- **WHEN** they navigate the dashboard
- **THEN** all elements have appropriate ARIA labels
- **AND** images have alt text
- **AND** charts have text alternatives or data tables

### Requirement: Data Export

The system SHALL allow teachers to export student data for record-keeping.

#### Scenario: Export class data
- **GIVEN** a teacher views the class overview
- **WHEN** they click "Export to CSV"
- **THEN** a CSV file is downloaded with all student scores
- **AND** CSV includes: student name, all 7 skill scores, confidence scores
- **AND** export includes timestamp and classroom name
