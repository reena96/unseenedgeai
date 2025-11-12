# Change: Evidence Fusion Service Implementation

## Why
Combine skill scores from multiple sources (transcripts, game, teacher rubrics) using learned weights to produce final, high-confidence skill assessments. This multi-source fusion approach leverages the strengths of each data source and provides more accurate assessments than any single source alone.

## What Changes
- Multi-source score fusion algorithm with skill-specific weights
- Confidence calculation based on source agreement
- Evidence extraction from transcripts, game events, and teacher notes
- Relevance scoring for evidence items
- Evidence ranking and selection (top 3-5 per skill)
- Fusion worker for async processing
- API endpoints for fused assessments and evidence retrieval
- Evidence storage with source attribution
- Agreement analysis between sources

## Impact
- Affected specs: evidence-fusion
- Affected code: New fusion service, evidence extraction, API endpoints
- Database: Updates to skill_assessments table, new evidence_items table
- Infrastructure: Cloud Tasks for fusion jobs
