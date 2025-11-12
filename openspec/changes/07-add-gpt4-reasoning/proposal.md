# Change: GPT-4 Reasoning Generation

## Why
Generate human-readable, growth-oriented explanations for each skill assessment using OpenAI GPT-4. These AI-generated reasoning texts help teachers understand WHY a student received a particular score and provide actionable insights, making the assessments more trustworthy and pedagogically valuable than numeric scores alone.

## What Changes
- OpenAI GPT-4 API integration
- Reasoning prompt templates for all 7 skills
- Context preparation from evidence and features
- Async reasoning generation via Cloud Tasks
- Reasoning caching to avoid redundant API calls
- Cost tracking and budget management
- Tone and language quality validation
- Reasoning storage in database
- API endpoints for reasoning retrieval
- Fallback to templates if GPT-4 fails

## Impact
- Affected specs: evidence-fusion (reasoning is part of assessment delivery)
- Affected code: New reasoning service, prompt engineering, API integration
- Database: New reasoning_explanations table
- Infrastructure: OpenAI API key in Secret Manager, cost monitoring
