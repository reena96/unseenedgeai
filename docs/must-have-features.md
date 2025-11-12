# Must-Have Features (P0 - Critical)

**Project:** Flourish Schools Middle School Non-Academic Skills Measurement Engine
**Date:** November 10, 2025

## Core Requirements

These are the absolute must-have features for the initial release. All P0 requirements must be met for the product to be viable.

### 1. Quantitative Skill Inference
**Requirement:** The system must quantitatively infer a student's non-academic skill levels from classroom conversation transcripts and project deliverables.

**Skills in Scope:**
- Empathy
- Adaptability

**Input Data:**
- Classroom conversation transcripts (full-day transcripts)
- Project deliverables (student work samples)

**Output:**
- Quantitative skill level scores/ratings for each student
- Continuous assessment over time (4-12 week periods)

### 2. Explainable Assessments
**Requirement:** The system must provide justifying evidence and reasoning for each inference.

**Explainability Components:**
- Specific utterances or text passages that support the assessment
- Reasoning explaining how the evidence relates to the skill
- Transparent methodology that educators can understand and trust

### 3. Cloud Deployment
**Requirement:** The system must support cloud deployment for scalability and accessibility.

**Cloud Requirements:**
- Scalable infrastructure (AWS preferred but not mandatory)
- Accessible to multiple schools/districts
- Secure data handling and storage
- Compliance with educational data protection regulations

### 4. High-Performance Parallel Processing
**Requirement:** The system must handle high-performance parallel processing of full days of classroom conversation transcripts and project deliverables.

**Performance Requirements:**
- Process full-day classroom transcripts (6-8 hours of conversation)
- Handle multiple students concurrently
- Support multiple classrooms/schools simultaneously
- Efficient processing pipeline for large-scale data

## Success Metrics

These metrics define success for the must-have features:

1. **Initial Accuracy:** Initial ratings are acceptable to teachers (convergent validity with human judgment)
2. **Longitudinal Tracking:** Detection of statistically significant skill improvement over 4-12 week periods

## Validation and Measurement Methodology

### Ground Truth Establishment
**Requirement:** Human-coded assessments must serve as ground truth for model training and validation.

**Validation Components:**
- Expert coders trained on validated rubrics (e.g., adapted Empathic Communication Coding System)
- Inter-Rater Reliability (IRR) using Krippendorff's Alpha
  - Minimum acceptable: α ≥ 0.70
  - Preferred target: α ≥ 0.80
- Stratified sample of anonymized middle school transcripts

### Four-Phase Validation Process

**Phase 1: Data Preparation**
- Collect and segment stratified sample of classroom transcripts
- Segment into individual utterances for fine-grained analysis

**Phase 2: Human Coding (Ground Truth)**
- Train expert coders on validated rubrics
- Conduct IRR check to ensure consistency (α ≥ 0.80)
- Generate human-coded skill scores as gold standard

**Phase 3: Automated Feature Extraction**
- Process same text through NLP pipelines (LIWC, Coh-Metrix)
- Extract linguistic features (lexical, semantic, structural)
- Generate LLM-derived contextual embeddings

**Phase 4: Empirical Validation**
- Bivariate correlation analysis: Test feature-to-score relationships
- Multiple regression analysis: Identify optimal feature combinations
- Validate convergent validity with human judgment

## Technical Constraints

- **Language:** Python
- **Data Privacy:** Must comply with educational data protection regulations
- **Security:** Data privacy and secure handling are non-negotiable
- **Scalability:** Must scale from pilot (single school) to district-wide deployment
