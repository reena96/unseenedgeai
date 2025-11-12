# Implementation Tasks: Evidence Fusion Service

## 1. Fusion Weights Configuration
- [ ] 1.1 Define skill-specific weights from Phase 0 validation:
  - [ ] 1.1.1 Empathy: transcript 0.35, game 0.40, teacher 0.25
  - [ ] 1.1.2 Adaptability: transcript 0.20, game 0.50, teacher 0.30
  - [ ] 1.1.3 Problem-Solving: transcript 0.30, game 0.45, teacher 0.25
  - [ ] 1.1.4 Self-Regulation: transcript 0.25, game 0.40, teacher 0.35
  - [ ] 1.1.5 Resilience: transcript 0.25, game 0.50, teacher 0.25
  - [ ] 1.1.6 Communication: transcript 0.50, game 0.25, teacher 0.25
  - [ ] 1.1.7 Collaboration: transcript 0.40, game 0.35, teacher 0.25
- [ ] 1.2 Store weights in configuration file
- [ ] 1.3 Support weight updates without code changes

## 2. Evidence Fusion Service
- [ ] 2.1 Create EvidenceFusionService class
- [ ] 2.2 Implement score fusion algorithm:
  - [ ] 2.2.1 Retrieve scores from all sources (transcript, game, teacher)
  - [ ] 2.2.2 Apply skill-specific weights
  - [ ] 2.2.3 Calculate weighted average
  - [ ] 2.2.4 Normalize if sources are missing
  - [ ] 2.2.5 Return fused score (0-1)
- [ ] 2.3 Implement confidence calculation:
  - [ ] 2.3.1 Calculate standard deviation of source scores
  - [ ] 2.3.2 Low std = high agreement = high confidence
  - [ ] 2.3.3 Adjust confidence based on number of sources
  - [ ] 2.3.4 Return confidence (0-1)
- [ ] 2.4 Test fusion with various score combinations

## 3. Evidence Extraction
- [ ] 3.1 Create evidence extractors for each source:
  - [ ] 3.1.1 TranscriptEvidenceExtractor
    - Extract relevant transcript segments
    - Score relevance based on skill patterns
    - Include context (before/after text)
    - Link to timestamps
  - [ ] 3.1.2 GameEvidenceExtractor
    - Extract relevant game choices and events
    - Score relevance based on skill mapping
    - Include mission and choice context
  - [ ] 3.1.3 TeacherEvidenceExtractor
    - Extract teacher rubric feedback
    - Include qualitative notes
    - Link to assessment date
- [ ] 3.2 Implement relevance scoring algorithm
- [ ] 3.3 Rank evidence by relevance (top 3-5 per skill)
- [ ] 3.4 Test extractors with sample data

## 4. Evidence Storage
- [ ] 4.1 Store evidence in evidence_items table
  - [ ] 4.1.1 Link to skill_assessments
  - [ ] 4.1.2 Include source type and source_id
  - [ ] 4.1.3 Store evidence_text and context
  - [ ] 4.1.4 Store relevance_score
  - [ ] 4.1.5 Store timestamp_in_source
- [ ] 4.2 Create indexes for fast retrieval
- [ ] 4.3 Test storage and retrieval

## 5. Fusion Worker
- [ ] 5.1 Create Cloud Tasks handler for fusion jobs
- [ ] 5.2 Implement fusion workflow:
  - [ ] 5.2.1 Query all students needing fusion (new source data)
  - [ ] 5.2.2 For each student and skill:
    - Retrieve transcript-based score
    - Retrieve game-based score
    - Retrieve teacher rubric score
    - Run fusion algorithm
    - Extract evidence from all sources
    - Store fused assessment
  - [ ] 5.2.3 Update skill_assessments with fused scores
  - [ ] 5.2.4 Store evidence items
- [ ] 5.3 Add error handling and retries
- [ ] 5.4 Test worker with 100+ students

## 6. Fusion API Endpoints
- [ ] 6.1 GET /api/v1/skills/{student_id}
  - [ ] 6.1.1 Return fused assessments for all 7 skills
  - [ ] 6.1.2 Include source scores and weights used
  - [ ] 6.1.3 Include confidence scores
  - [ ] 6.1.4 Include assessment period
- [ ] 6.2 GET /api/v1/skills/{student_id}/{skill}
  - [ ] 6.2.1 Return detailed assessment for one skill
  - [ ] 6.2.2 Include evidence items
  - [ ] 6.2.3 Include feature importance
- [ ] 6.3 GET /api/v1/evidence/{assessment_id}
  - [ ] 6.3.1 Return all evidence for an assessment
  - [ ] 6.3.2 Group by source type
  - [ ] 6.3.3 Include relevance scores
  - [ ] 6.3.4 Include full context

## 7. Agreement Analysis
- [ ] 7.1 Calculate correlation between sources
- [ ] 7.2 Identify cases of high disagreement (std dev >0.3)
- [ ] 7.3 Flag assessments needing manual review
- [ ] 7.4 Generate agreement report for validation

## 8. Fusion Visualization (API Support)
- [ ] 8.1 Provide data for source breakdown chart
- [ ] 8.2 Provide data for confidence visualization
- [ ] 8.3 Provide data for evidence timeline

## 9. Testing
- [ ] 9.1 Unit tests for fusion algorithm
- [ ] 9.2 Unit tests for confidence calculation
- [ ] 9.3 Unit tests for evidence extraction
- [ ] 9.4 Integration tests for full fusion pipeline
- [ ] 9.5 Validate fused scores match expected ranges
- [ ] 9.6 Test with missing sources (e.g., no game data yet)
- [ ] 9.7 Test agreement analysis with diverse scenarios

## 10. Monitoring
- [ ] 10.1 Track fusion job completion rate
- [ ] 10.2 Monitor confidence score distribution
- [ ] 10.3 Alert on high disagreement rates (>20% of assessments)
- [ ] 10.4 Track evidence extraction success rate

## 11. Documentation
- [ ] 11.1 Document fusion algorithm and weights
- [ ] 11.2 Document evidence extraction logic
- [ ] 11.3 Document API endpoints for fused assessments
- [ ] 11.4 Create fusion troubleshooting guide

## 12. Deployment
- [ ] 12.1 Deploy fusion service to Cloud Run
- [ ] 12.2 Test fusion with sample students
- [ ] 12.3 Verify evidence extraction works correctly
- [ ] 12.4 Monitor production fusion jobs
