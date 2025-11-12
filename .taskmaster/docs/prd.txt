# Middle School Non-Academic Skills Measurement System (MASS)
## Comprehensive Product Requirements Document

**Version:** 2.0 (Final)  
**Organization:** Flourish Schools  
**Project ID:** JnGyV0Xlx2AEiL31nu7J_1761530509243  
**Date:** January 2025  
**Status:** Ready for Implementation

---

## Table of Contents

1. Executive Summary
2. Problem Statement
3. Vision and Goals
4. Target Users and Personas
5. Core Solution Architecture
6. Functional Requirements
7. Non-Functional Requirements
8. User Experience and Design
9. Technical Specifications
10. Game-Based Assessment Component (Flourish Academy)
11. Implementation Roadmap
12. Success Metrics and Evaluation
13. Risk Management
14. Dependencies and Assumptions
15. Out of Scope
16. Appendices

---

## 1. Executive Summary

The Middle School Non-Academic Skills Measurement System (MASS) is a comprehensive, AI-driven platform designed to provide continuous, objective assessment of non-academic skills in middle school students (grades 6-8, ages 11-14). The system addresses a critical gap in educational assessment by combining four evidence layers—baseline cognitive assessment, stealth game-based behavioral measurement, AI-driven analysis of classroom interactions, and teacher rubric evaluation—to create a triangulated, fair, and actionable profile of student development in skills such as empathy, adaptability, resilience, problem-solving, self-regulation, communication, and collaboration.

Unlike traditional self-report surveys that are prone to social desirability bias, MASS provides continuous, unobtrusive measurement that captures authentic student behavior in diverse contexts. The system empowers educators with evidence-based insights for timely interventions, enables administrators to understand school-wide trends and equity patterns, and provides students with actionable feedback on their growth areas.

**Key Innovation:** MASS integrates a sophisticated stealth assessment game (Flourish Academy) with classroom transcript analysis and teacher evaluation, creating a comprehensive ecosystem for non-academic skills measurement that is both rigorous and engaging for students.

**Core Value Proposition:**
- **For Educators:** Objective, continuous assessment without additional workload; evidence-based insights for targeted interventions
- **For Administrators:** Data-driven understanding of school-wide skill development; ability to demonstrate educational outcomes to stakeholders
- **For Students:** Engaging, game-based learning experience with actionable feedback on growth areas
- **For Schools:** Scalable, cloud-based system that integrates with existing school management systems

---

## 2. Problem Statement

### 2.1 The Challenge of Measuring Non-Academic Skills

Middle school educators recognize that non-academic skills—such as empathy, adaptability, resilience, problem-solving, self-regulation, communication, and collaboration—are critical predictors of academic success, career readiness, and life outcomes. However, schools currently lack scalable, objective tools to measure and track these skills effectively.

### 2.2 Limitations of Current Approaches

**Self-Report Surveys:** Traditional social-emotional learning (SEL) surveys rely on student self-assessment, which is vulnerable to social desirability bias. Students tend to respond in ways they believe are socially acceptable rather than honestly reporting their actual skills. Additionally, surveys are typically administered only once or twice per year, providing limited insight into skill development trajectories.

**Teacher Observations:** While teacher observations are valuable, they are inherently subjective and vary significantly between classrooms and schools. Teachers lack standardized frameworks for assessment and have limited time to conduct systematic observations. Moreover, students behave differently in structured versus unstructured environments, and teachers may not observe all relevant contexts.

**Lack of Continuous Measurement:** Current assessment approaches provide only snapshots of student development at specific points in time. Skill development is dynamic and highly context-dependent, requiring continuous measurement to capture growth and identify students needing support.

**No Triangulation of Evidence:** Existing tools typically rely on a single data source (surveys, observations, or work samples). This creates vulnerability to bias and limits the validity of inferences about student skills.

### 2.3 Impact of the Problem

The lack of effective non-academic skills measurement has several negative consequences:

- **Missed Interventions:** Students struggling with empathy, resilience, or self-regulation are not identified early enough for targeted support
- **Inequitable Outcomes:** Without objective measurement, biases in teacher perception may disadvantage certain student populations
- **Limited Accountability:** Schools cannot demonstrate the impact of SEL programs or track school-wide trends in skill development
- **Reduced Student Agency:** Students lack actionable feedback on their non-academic skill development and growth trajectories

---

## 3. Vision and Goals

### 3.1 Vision Statement

To empower middle schools with a comprehensive, objective, and continuous system for measuring non-academic skills that enables timely interventions, demonstrates educational outcomes, and prepares students for real-world success.

### 3.2 Primary Goals

**Goal 1: Provide Continuous, Objective Assessment**  
Develop a system that continuously measures non-academic skills through multiple evidence sources, reducing reliance on subjective teacher judgment and self-report bias.

**Goal 2: Enable Timely Interventions**  
Provide educators with early identification of students struggling with specific non-academic skills, enabling targeted support before problems escalate.

**Goal 3: Demonstrate Educational Outcomes**  
Enable administrators to track school-wide trends in non-academic skill development and demonstrate the impact of SEL initiatives to stakeholders.

**Goal 4: Engage Students in Skill Development**  
Create an engaging, game-based learning experience that motivates students to develop non-academic skills while providing unobtrusive assessment.

### 3.3 Success Metrics

| Metric | Target | Timeline |
| :--- | :--- | :--- |
| **Educator Acceptance** | 80% of teachers rate initial skill assessments as acceptable or better | Week 12 (pilot) |
| **Skill Improvement Detection** | System detects statistically significant skill improvement over 4-12 week periods | Week 16 (pilot) |
| **Teacher Workload** | Reduce SEL assessment workload by 50% | Ongoing |
| **Educator Confidence** | 75% of teachers report increased confidence in skill assessment accuracy | Week 20 (pilot) |
| **Student Engagement** | 85% of students report game is engaging and fun | Week 8 (pilot) |
| **System Uptime** | 99.5% system availability | Ongoing |
| **Data Accuracy** | Transcription accuracy >95%; skill inference validated against teacher ratings (r > 0.70) | Week 24 (pilot) |
| **Equity** | No significant demographic disparities in skill assessments (p > 0.05) | Week 24 (pilot) |

---

## 4. Target Users and Personas

### 4.1 Primary Users

**Persona 1: Ms. Chen, Middle School Teacher**

Ms. Chen teaches 7th-grade English Language Arts to 120 students across five classes. She is passionate about student development but feels overwhelmed by the amount of time required for SEL assessment and feedback. She wants objective data to support her observations and help identify students who need additional support. She is comfortable with technology but prefers tools that don't require significant additional work.

**Key Needs:**
- Objective, data-driven insights into student non-academic skills
- Minimal additional workload for assessment
- Clear, actionable recommendations for interventions
- Evidence to support her observations and justify interventions to parents

**Persona 2: Dr. Patel, School Administrator**

Dr. Patel is the principal of a mid-sized middle school serving 600 students. She is responsible for demonstrating educational outcomes to the district and community. She wants to understand school-wide trends in non-academic skill development and identify areas where additional resources or professional development are needed.

**Key Needs:**
- School-wide data on non-academic skill development
- Ability to track trends over time and compare to district benchmarks
- Equity analysis to identify disparities in skill development
- Reports for stakeholders (district, school board, parents)

**Persona 3: Marcus, 7th-Grade Student**

Marcus is a 12-year-old student who is generally engaged in school but struggles with self-regulation and adaptability. He sometimes gets frustrated when tasks are difficult and has difficulty working with peers who have different perspectives. He enjoys games and interactive learning experiences.

**Key Needs:**
- Engaging, game-based learning experience
- Clear feedback on his strengths and growth areas
- Specific, actionable suggestions for improvement
- Recognition of his progress and achievements

### 4.2 Secondary Users

**School District Administrators:** Need district-level dashboards and reporting for strategic planning and resource allocation.

**Parents:** Receive reports on their child's non-academic skill development and suggestions for home support.

**Counselors and Support Staff:** Use MASS data to identify students needing additional support and to monitor the impact of interventions.

---

## 5. Core Solution Architecture

### 5.1 Four-Layer Evidence Architecture

MASS employs a sophisticated four-layer evidence architecture to triangulate non-academic skills assessment:

#### **Layer 1: Baseline Cognitive and Mindset Assessment**

The system begins with a baseline assessment of students' cognitive reasoning abilities and growth mindset orientation. This layer establishes an initial learner profile and provides context for interpreting subsequent assessments.

**Components:**
- Cognitive reasoning tasks assessing problem-solving and analytical thinking
- Growth mindset survey (adapted from Dweck's framework)
- Optional self-regulation and grit self-report measures
- Bias-resistant anchors to reduce social desirability bias

**Output:** Initial learner profile with cognitive baseline and mindset orientation

#### **Layer 2: Stealth Game-Based Behavioral Assessment (Flourish Academy)**

Students engage with an engaging narrative game (Flourish Academy) that measures non-academic skills through gameplay without students being aware they are being assessed. The game captures authentic behavior in simulated scenarios that require problem-solving, planning, self-regulation, empathy, and adaptability.

**Components:**
- Narrative-driven game world with interconnected missions
- Scenarios requiring empathy, adaptability, problem-solving, and self-regulation
- Real-time telemetry logging of all student interactions
- Think-aloud prompts to capture metacognitive processes
- Adaptive difficulty to maintain engagement

**Measured Behaviors:**
- Task sequencing efficiency and planning
- Resource allocation decisions
- Recovery from mistakes and persistence
- Delegation patterns and collaboration
- Distraction resistance and focus maintenance
- Adaptability to unexpected challenges
- Empathetic decision-making in social scenarios

**Output:** Behavioral skill scores with confidence estimates and feature importance

#### **Layer 3: AI-Driven Classroom Assessment**

The system analyzes classroom interactions and project deliverables using natural language processing and machine learning to infer non-academic skills from authentic classroom contexts.

**Data Sources:**
- Classroom conversation transcripts (from audio recording and speech-to-text)
- Group discussion recordings and transcripts
- Project submissions and collaborative work artifacts
- Peer interaction observations

**Analysis Approach:**
- Linguistic feature extraction (empathy markers, problem-solving language, perseverance indicators)
- Behavioral feature extraction (participation patterns, collaboration indicators)
- Contextual analysis (classroom dynamics, peer relationships)

**Measured Skills:**
- Empathy and perspective-taking (from linguistic markers and collaborative behaviors)
- Adaptability (from response to challenges and flexibility in approach)
- Communication effectiveness (from linguistic quality and clarity)
- Collaborative behaviors (from group interaction patterns)
- Emotional tone stability (from sentiment analysis and emotional language)

**Output:** Skill scores with evidence excerpts and temporal trend curves

#### **Layer 4: Teacher Rubric Evaluation**

Teachers provide structured rubric-based assessments of student non-academic skills, grounding AI-driven assessments in human judgment and contextual knowledge.

**Components:**
- Digital rubric interface with clear performance descriptors
- Standards-aligned rubrics for each non-academic skill
- Cross-links with AI insights to support teacher judgment
- Optional qualitative comments for context

**Measured Skills:** Same seven core skills (empathy, adaptability, problem-solving, self-regulation, resilience, communication, collaboration)

**Output:** Teacher ratings (1-4 scale) with qualitative feedback

### 5.2 Evidence Fusion and Skill Inference

MASS combines evidence from all four layers using a multi-source fusion model to produce triangulated skill assessments. The fusion model:

1. **Normalizes scores** from each evidence source to a common 0-1 scale
2. **Weights sources** based on reliability and relevance (e.g., game telemetry weighted higher for problem-solving, classroom transcripts weighted higher for communication)
3. **Calculates confidence** based on agreement between sources and strength of evidence
4. **Generates reasoning** explaining which evidence contributed to each score

**Output:** Comprehensive skill profile with:
- Overall skill scores (0-1 scale)
- Confidence estimates (0-1 scale)
- Evidence excerpts from each source
- Human-readable reasoning
- Temporal trends (if multiple assessments available)
- Specific recommendations for growth

---

## 6. Functional Requirements

### 6.1 P0 Requirements (Must-Have, Critical)

#### P0.1: Quantitative Skill Inference

**Requirement:** The system must quantitatively infer student non-academic skill levels from classroom conversation transcripts and project deliverables.

**Implementation:**
- Speech-to-text pipeline converts classroom audio to transcripts with >95% accuracy
- Linguistic analysis extracts features from transcripts (LIWC categories, syntactic patterns, discourse markers)
- Behavioral analysis extracts features from game telemetry and project submissions
- XGBoost models combine features to produce quantitative skill scores (0-1 scale)
- Models trained on human-coded ground truth data with Krippendorff's Alpha ≥ 0.80

**Acceptance Criteria:**
- Skill scores are numeric (0-1 scale) and interpretable
- Scores correlate with teacher ratings (r ≥ 0.70)
- System handles full-day transcripts (6+ hours of audio) without errors
- Inference latency <30 seconds per student

#### P0.2: Evidence and Reasoning

**Requirement:** The system must provide justifying evidence and reasoning for each skill inference.

**Implementation:**
- Evidence extraction selects representative evidence from three sources (linguistic, behavioral, contextual)
- Evidence includes direct quotes or descriptions with timestamps
- Reasoning generation uses LLM to explain why a student received a particular score
- Confidence scoring indicates reliability of the assessment

**Acceptance Criteria:**
- Every skill score includes 2-3 evidence items with source attribution
- Reasoning is clear, concise (2-3 sentences), and actionable
- Confidence scores accurately reflect reliability of assessments
- Teachers find evidence and reasoning helpful for decision-making

#### P0.3: Cloud Deployment and Scalability

**Requirement:** The system must support cloud deployment for scalability and accessibility.

**Implementation:**
- Deployed on Google Cloud Platform (GCP)
- Cloud Run for API server with auto-scaling (0-100 instances)
- Cloud SQL for PostgreSQL database with high availability
- Cloud Storage for audio files and artifacts
- Managed services eliminate infrastructure management overhead

**Acceptance Criteria:**
- System handles 1,000+ concurrent users without degradation
- Auto-scaling responds to load within 30 seconds
- 99.5% uptime SLA
- Cost scales linearly with usage (~$3.20/student/month)

#### P0.4: High-Performance Parallel Processing

**Requirement:** The system must handle high-performance parallel processing of full-day classroom transcripts and project deliverables.

**Implementation:**
- Celery + Redis for async task queue
- Multiple workers process transcription, linguistic analysis, and skill inference in parallel
- Batch processing for full-day transcripts
- Streaming processing for real-time events
- TimescaleDB for efficient time-series queries

**Acceptance Criteria:**
- Full-day transcript processing (6 hours of audio) completes in <30 minutes for 100 students
- System processes 100 GB/day of data without bottlenecks
- Task queue handles 1000+ concurrent tasks
- No data loss or corruption under high load

### 6.2 P1 Requirements (Should-Have, Important)

#### P1.1: Teacher Dashboard

**Requirement:** The system should offer a dashboard interface for educators to view and track student skill assessments.

**Implementation:**
- React-based web dashboard
- Real-time updates of student skill scores
- Class-level insights and patterns
- Alerts for students needing support
- Evidence and reasoning display for each skill
- Trend visualization over time

**Key Features:**
- Student list with current skill scores
- Detailed student profile with evidence and reasoning
- Class-level skill distribution and trends
- Alerts for significant changes or concerning patterns
- Export functionality for reports

**Acceptance Criteria:**
- Dashboard loads in <2 seconds
- Teachers can view all student data without additional training
- 80% of teachers find dashboard helpful for decision-making
- Mobile-responsive design for accessibility

#### P1.2: School Management System Integration

**Requirement:** The system should integrate with existing school management systems for seamless data exchange.

**Implementation:**
- OneRoster API support for roster synchronization
- Fallback CSV import for schools without API access
- Automated daily roster sync
- Role-based access control based on school system roles
- Data validation and error handling

**Supported Integrations:**
- OneRoster (standard)
- Clever
- ClassLink
- CSV import (fallback)

**Acceptance Criteria:**
- Roster sync completes in <5 minutes
- 99% accuracy in roster synchronization
- Teachers automatically see their students in the system
- Access controls properly enforced

#### P1.3: Administrator Dashboard

**Requirement:** The system should provide school and district-level dashboards for administrators.

**Implementation:**
- High-level skill distribution across school/district
- Trend analysis over time
- Equity analysis (demographic breakdowns)
- Heatmaps and longitudinal graphs
- Export-friendly reports

**Key Features:**
- School-wide skill averages and distributions
- Trends over time (4-week, 12-week, semester)
- Equity analysis by demographic groups
- Identification of schools/grades needing support
- Custom report generation

**Acceptance Criteria:**
- Administrators can view school-wide trends in <5 minutes
- Reports are exportable in PDF and CSV formats
- Equity analysis identifies disparities (if present)
- 75% of administrators find insights actionable

#### P1.4: Role-Based Access Control

**Requirement:** The system should enforce role-based access control to ensure data privacy and security.

**Implementation:**
- Teacher role: Can view own students' data
- Administrator role: Can view school/district-level data
- Counselor role: Can view flagged students and intervention data
- Student role: Can view own profile and progress
- System administrator role: Can manage users and system settings

**Acceptance Criteria:**
- Users can only access data appropriate to their role
- Audit logs track all data access
- No unauthorized access incidents

### 6.3 P2 Requirements (Nice-to-Have, Optional)

#### P2.1: Predictive Analytics

**Requirement:** The system could provide predictive analytics to forecast future skill development trajectories.

**Implementation (Phase 3+):**
- Time-series analysis of skill development
- Forecasting models to predict future skill levels
- Early warning system for students at risk of declining skills
- Intervention effectiveness tracking

**Status:** Foundation present in database schema; feature deferred to Phase 3

#### P2.2: Customizable Reporting

**Requirement:** The system could offer customizable reporting tools for various stakeholders.

**Implementation (Phase 3+):**
- Custom report builder for administrators
- Stakeholder-specific report templates
- Automated report scheduling and distribution
- Data visualization customization

**Status:** Basic reporting included in Phase 3; advanced customization deferred to Phase 4

#### P2.3: Student Reflection and Goal-Setting

**Requirement:** The system could provide tools for students to reflect on their skills and set growth goals.

**Implementation (Phase 3+):**
- Student portal with skill profile visualization
- Reflection prompts based on assessment results
- Goal-setting interface
- Progress tracking toward goals

**Status:** Deferred to Phase 3

---

## 7. Non-Functional Requirements

### 7.1 Performance Requirements

| Requirement | Target | Rationale |
| :--- | :--- | :--- |
| **Transcription Latency** | <5 seconds per minute of audio | Enable near-real-time processing |
| **Skill Inference Latency** | <30 seconds per student | Provide timely insights |
| **Dashboard Query Latency** | <2 seconds | Ensure responsive user experience |
| **API Response Latency** | <500ms (p95) | Support real-time applications |
| **System Throughput** | 1,000 concurrent users | Support school-wide deployment |
| **Data Processing** | 100 GB/day | Handle full-day transcripts for large schools |
| **Task Queue Depth** | <1,000 tasks | Prevent queue overflow |

### 7.2 Security Requirements

**Data Encryption:**
- End-to-end encryption for data in transit (TLS 1.3)
- Encryption at rest for all stored data (AES-256)
- Encrypted backups with separate key management

**Access Control:**
- Role-based access control (RBAC)
- Multi-factor authentication (MFA) for sensitive operations
- Audit logs for all data access
- Regular access reviews and cleanup

**Compliance:**
- FERPA (Family Educational Rights and Privacy Act) compliance
- COPPA (Children's Online Privacy Protection Act) compliance
- GDPR compliance (if applicable)
- SOC 2 Type II certification

**Data Retention and Deletion:**
- Student data retained for duration of enrollment + 1 year
- Audio files deleted after transcription (unless explicitly retained)
- Automatic deletion of data upon student request
- Audit trail of all deletions

### 7.3 Scalability Requirements

**Multi-Tenancy:**
- Support multiple schools and districts
- Isolated data for each tenant
- Separate configuration and customization per tenant

**Horizontal Scaling:**
- Cloud Run auto-scales from 0 to 100 instances
- Database read replicas for scaling queries
- Caching layer (Redis) for frequently accessed data
- CDN for static assets

**Capacity Planning:**
- Support 10,000+ students without major rework
- Linear cost scaling: $3.20/student/month
- Automatic resource provisioning based on demand

### 7.4 Accessibility Requirements

**WCAG 2.1 Compliance:**
- Level AA compliance for all web interfaces
- Keyboard navigation support
- Screen reader compatibility
- Color-blind friendly color schemes
- Adjustable text size and contrast

**Inclusive Design:**
- Support for multiple languages (future)
- Closed captions for video content
- Plain language explanations
- Mobile-responsive design

### 7.5 Reliability and Availability

**Uptime SLA:** 99.5% availability (target: <3.6 hours downtime per month)

**Disaster Recovery:**
- Automated daily backups
- Backup retention: 30 days
- Recovery time objective (RTO): 1 hour
- Recovery point objective (RPO): 1 hour

**Error Handling:**
- Graceful degradation when services fail
- Fallback options for critical features
- Clear error messages for users
- Automatic error reporting and alerting

---

## 8. User Experience and Design

### 8.1 Design Principles

**Principle 1: Growth Mindset Orientation**  
The interface emphasizes growth, learning, and improvement rather than fixed abilities. Language focuses on "developing skills" rather than "measuring deficits."

**Principle 2: Evidence-Based Transparency**  
All assessments include clear evidence and reasoning. Users understand why the system made a particular assessment and can verify or challenge it.

**Principle 3: Actionable Insights**  
Dashboards and reports focus on actionable recommendations rather than just scores. Teachers and students know what to do with the information.

**Principle 4: Minimal Cognitive Load**  
Interfaces are designed to be scannable and intuitive. Information is presented clearly without overwhelming users with data.

**Principle 5: Inclusive and Accessible**  
Design considers users with diverse abilities and backgrounds. Interfaces are accessible to users with visual, hearing, motor, or cognitive disabilities.

### 8.2 Teacher Dashboard Design

**Key Sections:**

1. **Class Overview** - At-a-glance view of class-level skill distribution
2. **Student List** - Sortable/filterable list of students with current skill scores
3. **Student Detail** - Deep dive into individual student with evidence and reasoning
4. **Alerts** - Notifications of students needing support or showing significant changes
5. **Resources** - Links to intervention strategies and professional development

**Key Interactions:**

- Click on student name to view detailed profile
- Click on skill score to see evidence and reasoning
- Filter by skill or concern area
- Export data for reports or further analysis
- View trends over time (4-week, 12-week, semester)

### 8.3 Student Experience (Flourish Academy Game)

**Key Design Elements:**

1. **Engaging Narrative** - Students are part of a meaningful story where their choices matter
2. **Character Development** - Relationships with game characters develop based on student choices
3. **Meaningful Choices** - Decisions have real consequences that affect the game world
4. **Feedback and Growth** - Clear feedback on choices and opportunities to learn and improve
5. **Accessibility** - Multiple difficulty levels, text-to-speech, color-blind friendly

**Game Flow:**

1. **Onboarding** - Character creation, tutorial, meeting mentor character
2. **Missions** - Interconnected missions requiring empathy, problem-solving, adaptability
3. **Relationships** - Develop relationships with NPCs based on choices
4. **Progression** - Unlock new areas and challenges as skills develop
5. **Reflection** - Periodic reflection prompts encourage metacognition

---

## 9. Technical Specifications

### 9.1 Technology Stack

| Layer | Component | Technology | Rationale |
| :--- | :--- | :--- | :--- |
| **Frontend (Game)** | Game Client | Unity (C#) | Industry standard; strong 2D/3D support |
| **Frontend (Web)** | Dashboard | React + TypeScript | Type safety; component reusability |
| **Backend** | API Server | FastAPI (Python) | Modern; excellent for data science |
| **Backend** | Async Tasks | Celery + Redis | Proven; integrates with Python |
| **Backend** | Event Streaming | Kafka | Scalable event ingestion |
| **NLP/ML** | Speech-to-Text | Google Cloud Speech-to-Text | Managed service; high accuracy |
| **NLP/ML** | Linguistic Analysis | Hugging Face Transformers | State-of-the-art; open-source |
| **NLP/ML** | Skill Inference | Scikit-learn + XGBoost | Interpretable; efficient |
| **NLP/ML** | Reasoning | OpenAI GPT-4 API | Best-in-class reasoning |
| **Database** | Relational | PostgreSQL | Mature; reliable |
| **Database** | Time-Series | TimescaleDB | Optimized for time-series |
| **Cache** | In-Memory | Redis | Fast; proven |
| **Cloud** | Infrastructure | Google Cloud Platform | Excellent AI/ML support |
| **Container** | Orchestration | Docker + Cloud Run | Serverless; simple |
| **Monitoring** | Observability | Google Cloud Logging | Integrated with GCP |

### 9.2 API Specification

**Base URL:** `https://api.mass.flourishschools.org/api/v1`

**Authentication:** OAuth 2.0 with JWT tokens

**Key Endpoints:**

```
Authentication
  POST /auth/login
  POST /auth/logout
  POST /auth/refresh-token

Telemetry
  POST /telemetry/events
  POST /telemetry/batch

Audio & Transcripts
  POST /audio/upload
  GET /transcripts/{student_id}

Skills Assessment
  GET /skills/{student_id}
  GET /skills/{student_id}/history
  GET /evidence/{student_id}/{skill}
  GET /reasoning/{student_id}/{skill}

Dashboards
  GET /dashboard/teacher/{teacher_id}
  GET /dashboard/admin/{school_id}
  GET /dashboard/student/{student_id}

Rubric Assessment
  POST /rubric/assessments
  GET /rubric/assessments/{student_id}

School Integration
  POST /integration/sync-roster
  GET /integration/status
```

### 9.3 Data Model

**Core Entities:**

- **Students** - Student profiles with demographic data
- **Teachers** - Teacher profiles and class assignments
- **Schools** - School information and configuration
- **GameTelemetry** - Game events and interactions
- **AudioFiles** - Classroom and interview audio
- **Transcripts** - Speech-to-text output
- **LinguisticFeatures** - Extracted linguistic features
- **BehavioralFeatures** - Aggregated behavioral features
- **SkillAssessments** - Skill scores with evidence and reasoning
- **RubricAssessments** - Teacher rubric evaluations

**Relationships:**

```
Student --teaches--> Teacher
Student --attends--> School
Student --plays--> GameTelemetry
Student --records--> AudioFiles
AudioFiles --transcribed--> Transcripts
Transcripts --analyzed--> LinguisticFeatures
GameTelemetry --aggregated--> BehavioralFeatures
LinguisticFeatures + BehavioralFeatures --inferred--> SkillAssessments
Teacher --evaluates--> RubricAssessments
```

### 9.4 Skill Inference Model

**Input Features:**

*Linguistic Features:*
- Empathy markers (count, frequency)
- Problem-solving language (count, frequency)
- Perseverance indicators (count, frequency)
- Sentiment scores (positive, negative)
- Sentence complexity metrics
- Word embeddings (768-dimensional)

*Behavioral Features:*
- Task completion rate
- Time efficiency
- Retry count and recovery
- Distraction resistance
- Collaboration indicators
- Leadership indicators
- Persistence in face of challenges

**Model Architecture:**

1. Feature normalization (StandardScaler)
2. XGBoost classifier (one per skill)
3. Confidence estimation based on feature agreement
4. Evidence extraction and ranking
5. Reasoning generation via LLM

**Output:**

```json
{
  "skill": "empathy",
  "score": 0.78,
  "confidence": 0.85,
  "evidence": [
    {
      "type": "linguistic",
      "source": "transcript",
      "content": "...",
      "timestamp": "..."
    }
  ],
  "reasoning": "...",
  "feature_importance": {
    "empathy_markers": 0.35,
    "collaboration_indicators": 0.28,
    "positive_sentiment": 0.18,
    "..."
  }
}
```

### 9.5 Infrastructure Architecture

**GCP Components:**

- **Cloud Run** - API server (auto-scaling, serverless)
- **Cloud SQL** - PostgreSQL database (high availability)
- **Cloud Storage** - Audio files and artifacts
- **Cloud Speech-to-Text** - Managed STT service
- **Vertex AI** - ML model serving
- **Cloud Logging** - Application logs
- **Cloud Monitoring** - Metrics and alerting
- **Cloud IAM** - Access control

**Deployment:**

- Docker containers for all services
- Automated CI/CD pipeline (GitHub Actions)
- Blue-green deployments for zero downtime
- Automated rollback on errors

---

## 10. Game-Based Assessment Component (Flourish Academy)

### 10.1 Game Overview

**Flourish Academy** is a narrative-driven game where students play as a new student at an academy for developing non-academic skills. The game features interconnected missions that require empathy, problem-solving, adaptability, and resilience. Students develop relationships with game characters based on their choices, creating emotional investment and motivation.

### 10.2 Game World and Narrative

**Setting:** Flourish Academy, a magical school where students develop non-academic skills

**Characters:**
- **Mentor:** Wise guide who supports the player
- **Classmates:** NPCs with different personalities and challenges
- **Antagonist:** Misunderstanding or conflict that drives the narrative

**Narrative Arc:**
- **Act 1:** Arrival and orientation; building relationships
- **Act 2:** Deepening challenges requiring skill development
- **Act 3:** Climactic challenge requiring integration of all skills
- **Epilogue:** Reflection on growth and impact

### 10.3 Core Missions

**Mission 1: Understanding Perspectives (Empathy)**
- Help a classmate understand a difficult situation
- Choose between selfish and empathetic responses
- Consequences affect relationship and future missions

**Mission 2: Adapt to Change (Adaptability)**
- Unexpected rule changes require flexible thinking
- Multiple solution paths; some more efficient than others
- Distraction elements test focus and persistence

**Mission 3: Solve the Problem (Problem-Solving)**
- Complex problem requiring planning and strategy
- Resource allocation decisions
- Recovery from mistakes

**Mission 4: Work Together (Collaboration)**
- Team-based mission requiring coordination
- Delegation and leadership decisions
- Conflict resolution scenarios

**Mission 5: Overcome Adversity (Resilience)**
- Significant challenge requiring persistence
- Multiple failures before success
- Reflection on growth and learning

### 10.4 Telemetry and Assessment

**Events Logged:**
- Mission start/completion
- Choice made and consequences
- Time spent on tasks
- Mistakes and recovery
- Collaboration indicators
- Distraction events
- Think-aloud responses

**Assessment Approach:**
- Stealth assessment: students unaware they're being assessed
- Behavior-based: inferences from choices and actions
- Context-aware: assessment considers mission difficulty and context
- Adaptive: difficulty adjusts based on performance

### 10.5 Engagement Mechanics

**Motivation Systems:**
- Relationship development with characters
- Achievement badges for milestones
- Progression through game world
- Meaningful choices with real consequences
- Character growth and development

**Accessibility:**
- Multiple difficulty levels
- Text-to-speech for dialogue
- Color-blind friendly palette
- Keyboard and controller support
- Adjustable text size

---

## 11. Implementation Roadmap

### 11.1 Phase 1: Foundation (Weeks 1-8)

**Goal:** Build core infrastructure and basic functionality

**Deliverables:**
- GCP project setup and configuration
- FastAPI server with basic endpoints
- PostgreSQL and TimescaleDB setup
- Game telemetry ingestion pipeline
- Celery task queue
- Basic authentication system
- CI/CD pipeline

**Team:** 4 engineers (3 backend, 1 DevOps)

**Key Milestones:**
- Week 2: GCP infrastructure deployed
- Week 4: API server deployed to Cloud Run
- Week 6: Database and telemetry pipeline working
- Week 8: CI/CD pipeline operational

### 11.2 Phase 2: NLP and Skill Inference (Weeks 9-16)

**Goal:** Implement speech-to-text and skill inference

**Deliverables:**
- Google Cloud STT integration
- Linguistic analysis pipeline
- Behavioral feature extraction
- XGBoost model training and validation
- Evidence extraction system
- Reasoning generation (LLM integration)
- Model monitoring and alerting

**Team:** 4 engineers (2 ML, 1 backend, 1 data scientist)

**Key Milestones:**
- Week 10: STT pipeline working
- Week 12: Linguistic analysis pipeline working
- Week 14: XGBoost models trained and validated
- Week 16: Evidence and reasoning working end-to-end

### 11.3 Phase 3: Dashboards and Integration (Weeks 17-24)

**Goal:** Build user interfaces and integrate with school systems

**Deliverables:**
- Teacher dashboard (React)
- Administrator dashboard (React)
- Student portal (React)
- SIS integration (OneRoster, Clever, ClassLink)
- Role-based access control
- Reporting features
- User management

**Team:** 4 engineers (2 frontend, 1 backend, 1 product)

**Key Milestones:**
- Week 18: Teacher dashboard MVP
- Week 20: Admin dashboard MVP
- Week 22: SIS integration working
- Week 24: Full dashboard suite with reporting

### 11.4 Phase 4: Testing, Optimization, and Launch (Weeks 25-32)

**Goal:** Validate system and prepare for launch

**Deliverables:**
- Comprehensive testing (unit, integration, end-to-end)
- Performance optimization
- Security audit and hardening
- Pilot with 1-2 schools
- Feedback integration
- Launch preparation
- Documentation and training

**Team:** 3 engineers (1 QA, 1 DevOps, 1 backend), 1 product manager

**Key Milestones:**
- Week 26: Test coverage >80%
- Week 28: Pilot schools onboarded
- Week 30: Security audit passed
- Week 32: Launch-ready

### 11.5 Timeline Summary

| Phase | Duration | Team | Status |
| :--- | :--- | :--- | :--- |
| Phase 1: Foundation | 8 weeks | 4 engineers | Weeks 1-8 |
| Phase 2: NLP & Inference | 8 weeks | 4 engineers | Weeks 9-16 |
| Phase 3: Dashboards | 8 weeks | 4 engineers | Weeks 17-24 |
| Phase 4: Testing & Launch | 8 weeks | 3 engineers | Weeks 25-32 |
| **Total** | **32 weeks (8 months)** | **4-6 engineers avg** | **Ready for launch** |

---

## 12. Success Metrics and Evaluation

### 12.1 Product Success Metrics

| Metric | Target | Measurement Method |
| :--- | :--- | :--- |
| **Educator Acceptance** | 80% of teachers rate assessments as acceptable | Post-pilot survey |
| **Skill Improvement Detection** | Detect significant improvement over 4-12 weeks | Statistical analysis of scores |
| **Teacher Workload Reduction** | 50% reduction in SEL assessment time | Time tracking study |
| **Educator Confidence** | 75% report increased confidence in assessments | Post-pilot survey |
| **Student Engagement** | 85% report game is engaging | Student survey |
| **System Uptime** | 99.5% availability | Monitoring dashboard |
| **Data Accuracy** | Transcription >95%; inference r > 0.70 with teacher ratings | Validation study |
| **Equity** | No significant demographic disparities | Statistical analysis |

### 12.2 Validation Framework

**Convergent Validity:** Skill scores correlate with teacher ratings (target: r ≥ 0.70)

**Discriminant Validity:** Skill scores don't correlate with unrelated measures (e.g., empathy shouldn't correlate with math ability)

**Reliability:** Consistent measurement across time and contexts (test-retest r ≥ 0.75)

**Fairness:** No significant disparities by demographic group (p > 0.05)

**Responsiveness:** Detects skill improvement over 4-12 week periods

### 12.3 Evaluation Timeline

| Milestone | Timeline | Evaluation |
| :--- | :--- | :--- |
| **Prototype Validation** | Week 16 | Technical validation of components |
| **Pilot Validation** | Week 28 | Convergent validity, teacher acceptance |
| **Full Validation** | Week 36 | Comprehensive validation study |
| **Year 1 Review** | Month 12 | Longitudinal effectiveness, equity analysis |

---

## 13. Risk Management

### 13.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **Transcription accuracy too low** | Medium | High | Early testing with real classroom audio; manual review fallback |
| **Model performance below target** | Medium | High | Validate models early; rule-based fallback system |
| **Scalability issues** | Low | High | Load testing; use managed services |
| **Data privacy breach** | Low | Critical | Encryption, access controls, security audits |
| **SIS integration fails** | Medium | Medium | Start with CSV import; add API integration later |

### 13.2 Organizational Risks

| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **Teacher skepticism** | High | Medium | Transparency, evidence-based design, gradual rollout |
| **Low adoption** | Medium | High | Professional development, clear value demonstration |
| **Privacy concerns** | Medium | High | Clear privacy policy, parental consent, opt-out option |
| **Resource constraints** | Medium | Medium | Phased implementation, prioritize P0 requirements |

### 13.3 Mitigation Strategies

**For Transcription Accuracy:**
- Test with real classroom audio in Phase 2
- Implement confidence scoring and manual review for low-confidence segments
- Fallback: teachers can manually review transcripts

**For Teacher Skepticism:**
- Transparency: explain how assessments are made
- Evidence-based: show evidence for each assessment
- Gradual rollout: start with one grade level
- Professional development: train teachers on system use

**For Privacy Concerns:**
- Clear privacy policy explaining data collection and use
- Parental consent for classroom recording
- Opt-out option for families
- Regular privacy audits

---

## 14. Dependencies and Assumptions

### 14.1 External Dependencies

**Google Cloud Platform Services:**
- Cloud Run availability and performance
- Cloud SQL reliability
- Cloud Speech-to-Text accuracy
- Vertex AI model serving

**Third-Party APIs:**
- Hugging Face Transformers availability
- OpenAI GPT-4 API availability
- OneRoster API standards

**School Systems:**
- Availability of classroom audio (with proper consent)
- Access to student work samples
- Integration with school management systems

### 14.2 Assumptions

**Technical Assumptions:**
- Classroom audio quality is sufficient for transcription (>90% accuracy)
- Schools have internet connectivity for cloud-based system
- Schools willing to record classroom audio (with proper consent)

**Organizational Assumptions:**
- Educators are willing to adopt new technology
- Schools have staff to manage system implementation
- District leadership supports non-academic skills assessment

**Data Assumptions:**
- Sufficient training data available for model development
- Human-coded ground truth data can be obtained with acceptable inter-rater reliability (α ≥ 0.80)

---

## 15. Out of Scope

### 15.1 Features Not Included in Initial Release

**Predictive Analytics:** Forecasting future skill development trajectories (Phase 3+)

**Advanced Reporting:** Customizable report builder (Phase 3+)

**Student Reflection Tools:** Student goal-setting and reflection interface (Phase 3+)

**Parent Portal:** Parent access to student data (Phase 3+)

**Multi-Language Support:** Support for languages other than English (Phase 4+)

**Mobile App:** Native mobile applications (Phase 4+)

### 15.2 Out of Scope Entirely

- Integration with non-educational platforms
- Academic skill assessment (focus is non-academic skills only)
- Therapeutic or clinical interventions
- Special education IEP management
- Attendance or discipline tracking

---

## 16. Appendices

### Appendix A: Skill Definitions

**Empathy:** The ability to understand and share the feelings of others; recognizing others' perspectives and responding with compassion.

**Adaptability:** The ability to adjust to new conditions, changing circumstances, and unexpected challenges; flexibility in thinking and approach.

**Problem-Solving:** The ability to identify, analyze, and solve problems; breaking complex problems into manageable parts and developing solutions.

**Self-Regulation:** The ability to manage emotions, impulses, and behavior; maintaining focus and control in challenging situations.

**Resilience:** The ability to recover from difficulties; persisting through challenges and learning from failures.

**Communication:** The ability to express ideas clearly and listen effectively; adapting communication style to audience and context.

**Collaboration:** The ability to work effectively with others; contributing to group goals while respecting diverse perspectives.

### Appendix B: LIWC Categories and Linguistic Markers

**Empathy-Related Markers:**
- Social processes: friend, talk, family, interact
- Affiliation: team, together, group, cooperate
- Perspective-taking: understand, imagine, think, believe

**Problem-Solving Markers:**
- Cognitive processes: think, know, consider, analyze
- Insight: realize, understand, see, notice
- Causation: because, cause, reason, why

**Perseverance Markers:**
- Achievement: accomplish, succeed, win, achieve
- Future focus: will, going, plan, prepare
- Positive emotion: good, great, happy, love

### Appendix C: Classroom Transcript Analysis Example

**Raw Transcript:**
> "I think I understand how you feel about this. That must be really frustrating. Let me help you think through this problem. First, we could try this approach, and if that doesn't work, we could try something else. I'm here to support you."

**Extracted Features:**
- Empathy markers: "understand how you feel" (1), "frustrating" (1), "support" (1) = 3
- Problem-solving markers: "think through" (1), "approach" (1), "try" (2) = 4
- Perspective-taking: "understand" (1), "your feel" (1) = 2
- Positive sentiment: "support" (1) = 1

**Skill Inference:**
- Empathy score: 0.85 (high empathy markers + perspective-taking)
- Problem-solving score: 0.72 (good problem-solving language + structured approach)
- Communication score: 0.78 (clear, supportive communication)

### Appendix D: Game Telemetry Example

**Mission: "Help Morgan Understand the Friendship"**

**Events Logged:**
1. Mission started at 10:30 AM
2. Player chose "Listen to Morgan's perspective" (empathetic choice)
3. Player spent 2 minutes reading dialogue
4. Player chose "Suggest talking to friend" (collaborative solution)
5. Player completed mission successfully
6. Player received feedback: "Great empathy! You really understood Morgan's feelings."

**Extracted Features:**
- Empathy indicators: chose empathetic option, spent time understanding
- Collaboration indicators: suggested collaborative solution
- Completion: mission completed successfully
- Time efficiency: reasonable time for mission

**Skill Inference:**
- Empathy score: 0.82
- Collaboration score: 0.75
- Problem-solving score: 0.68

### Appendix E: Evidence Example

**Student:** Marcus Chen, Grade 7

**Skill:** Empathy

**Score:** 0.78

**Confidence:** 0.85

**Evidence:**

1. **Linguistic Evidence** (Classroom Transcript, Jan 15, 10:30 AM)
   - Quote: "I think I understand how you feel about this. That must be really frustrating."
   - Source: Group discussion about peer conflict
   - Relevance: Direct empathy language and perspective-taking

2. **Behavioral Evidence** (Game Telemetry, Jan 14, 2:00 PM)
   - Event: Chose "Listen to Morgan's perspective" in empathy mission
   - Context: Mission requiring understanding of character's feelings
   - Relevance: Demonstrated empathetic decision-making in game

3. **Contextual Evidence** (Teacher Rubric, Jan 12)
   - Teacher Rating: 3/4 for empathy
   - Comment: "Marcus shows good understanding of others' perspectives, especially in group work."
   - Source: Teacher observation and rubric assessment

**Reasoning:**
Marcus demonstrates empathy through both language use (perspective-taking language in classroom discussions) and behavior (empathetic choices in game scenarios). His teacher also rates him as showing good empathy in group work. Confidence is high due to consistent evidence across multiple sources.

**Recommendations:**
Continue to encourage Marcus to practice perspective-taking in group discussions. Consider assigning him a peer mentor role to further develop empathy skills.

---

## Conclusion

The Middle School Non-Academic Skills Measurement System (MASS) represents a comprehensive, evidence-based approach to addressing a critical gap in educational assessment. By combining four evidence layers—baseline cognitive assessment, stealth game-based measurement, AI-driven classroom analysis, and teacher evaluation—MASS provides a triangulated, fair, and actionable assessment of non-academic skills.

The system is designed to be implementable, manageable, and scalable, using proven technologies and pragmatic design principles. With an 8-month development timeline and a team of 6-8 engineers, MASS can be deployed to schools and begin providing value to educators and students.

Success will be measured through educator acceptance, skill improvement detection, reduced teacher workload, increased educator confidence, and validated accuracy of skill assessments. The system is designed to be equitable, accessible, and compliant with all relevant regulations.

MASS has the potential to transform how schools assess and support non-academic skill development, ultimately preparing students for real-world success and demonstrating the impact of educational programs to stakeholders.

---

## Document Control

| Version | Date | Author | Status |
| :--- | :--- | :--- | :--- |
| 1.0 | Original | Flourish Schools | Original Brief |
| 2.0 | January 2025 | Manus AI | Final Comprehensive PRD |

**Approved By:** [To be completed upon review]

**Date Approved:** [To be completed upon review]

---

*This Product Requirements Document is designed to align cross-functional stakeholders and enable independent implementation. It focuses on the "what" and "why" of the product, providing a clear roadmap for development.*
