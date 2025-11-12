# Implementation Tasks: GPT-4 Reasoning Generation

## 1. OpenAI API Integration
- [ ] 1.1 Store OpenAI API key in Secret Manager
- [ ] 1.2 Create OpenAI client with proper authentication
- [ ] 1.3 Implement retry logic for API failures
- [ ] 1.4 Add timeout handling (max 30s per request)
- [ ] 1.5 Test connectivity and basic completion

## 2. Reasoning Prompt Engineering
- [ ] 2.1 Create base prompt template for reasoning generation
- [ ] 2.2 Develop skill-specific prompt variations:
  - [ ] 2.2.1 Empathy reasoning prompts
  - [ ] 2.2.2 Adaptability reasoning prompts
  - [ ] 2.2.3 Problem-Solving reasoning prompts
  - [ ] 2.2.4 Self-Regulation reasoning prompts
  - [ ] 2.2.5 Resilience reasoning prompts
  - [ ] 2.2.6 Communication reasoning prompts
  - [ ] 2.2.7 Collaboration reasoning prompts
- [ ] 2.3 Include evidence snippets in prompts
- [ ] 2.4 Include key feature metrics in prompts
- [ ] 2.5 Specify tone: growth-oriented, asset-based, actionable
- [ ] 2.6 Specify length: 2-3 sentences
- [ ] 2.7 Test prompts with GPT-4 and refine based on output quality

## 3. Reasoning Service
- [ ] 3.1 Create ReasoningService class
- [ ] 3.2 Implement reasoning generation method:
  - [ ] 3.2.1 Build prompt from template
  - [ ] 3.2.2 Insert student name, skill, score
  - [ ] 3.2.3 Insert evidence snippets (top 3)
  - [ ] 3.2.4 Insert key feature metrics
  - [ ] 3.2.5 Call OpenAI ChatCompletion API (gpt-4)
  - [ ] 3.2.6 Set temperature=0.3 for consistency
  - [ ] 3.2.7 Set max_tokens=150
  - [ ] 3.2.8 Extract reasoning text from response
  - [ ] 3.2.9 Validate output length and tone
- [ ] 3.3 Add error handling for API failures
- [ ] 3.4 Test with sample assessments

## 4. Reasoning Worker
- [ ] 4.1 Create Cloud Tasks handler for reasoning jobs
- [ ] 4.2 Implement reasoning generation workflow:
  - [ ] 4.2.1 Query assessments needing reasoning (after fusion)
  - [ ] 4.2.2 For each assessment:
    - Retrieve evidence items
    - Retrieve feature importance
    - Generate reasoning via GPT-4
    - Store in reasoning_explanations table
    - Track API cost
  - [ ] 4.2.3 Handle rate limiting (20 requests/minute)
  - [ ] 4.2.4 Log generation time and costs
- [ ] 4.3 Add retry logic (max 3 retries)
- [ ] 4.4 Test worker with 50+ assessments

## 5. Reasoning Storage
- [ ] 5.1 Store reasoning in reasoning_explanations table
  - [ ] 5.1.1 Link to skill_assessments
  - [ ] 5.1.2 Store reasoning_text
  - [ ] 5.1.3 Store generated_by (gpt4 or template)
  - [ ] 5.1.4 Store generation_cost
  - [ ] 5.1.5 Store generated_at timestamp
- [ ] 5.2 Create unique constraint (one reasoning per assessment)
- [ ] 5.3 Test storage and retrieval

## 6. Reasoning Caching
- [ ] 6.1 Hash evidence + features to create cache key
- [ ] 6.2 Check Redis cache before calling GPT-4
- [ ] 6.3 Store generated reasoning in cache (TTL: 7 days)
- [ ] 6.4 Measure cache hit rate (target >50% over time)
- [ ] 6.5 Invalidate cache when assessment is regenerated

## 7. Cost Tracking and Management
- [ ] 7.1 Track tokens used per request
- [ ] 7.2 Calculate cost per reasoning (approx $0.03-0.05)
- [ ] 7.3 Store generation_cost in database
- [ ] 7.4 Create daily cost report
- [ ] 7.5 Set up budget alerts (>$100/day)
- [ ] 7.6 Implement cost ceiling (pause if exceeded)

## 8. Quality Validation
- [ ] 8.1 Check reasoning length (50-200 words)
- [ ] 8.2 Validate tone (no negative language, focus on growth)
- [ ] 8.3 Check for hallucinations (must reference provided evidence)
- [ ] 8.4 Flag low-quality reasoning for review
- [ ] 8.5 Sample 10% for manual quality review

## 9. Fallback Template System
- [ ] 9.1 Create template-based reasoning for each skill × score level
  - [ ] 9.1.1 7 skills × 3 levels (emerging, developing, proficient) = 21 templates
- [ ] 9.2 Implement template selection logic
- [ ] 9.3 Use templates as fallback if GPT-4 fails
- [ ] 9.4 Allow configuration to prefer templates (cost saving mode)
- [ ] 9.5 Test template quality against GPT-4 quality

## 10. Reasoning API Endpoints
- [ ] 10.1 GET /api/v1/reasoning/{assessment_id}
  - [ ] 10.1.1 Return reasoning text
  - [ ] 10.1.2 Include generation method (gpt4 or template)
  - [ ] 10.1.3 Include generated_at timestamp
- [ ] 10.2 POST /api/v1/reasoning/regenerate/{assessment_id}
  - [ ] 10.2.1 Force regeneration of reasoning
  - [ ] 10.2.2 Useful if teacher finds reasoning unhelpful
  - [ ] 10.2.3 Invalidate cache
- [ ] 10.3 Add reasoning to GET /api/v1/skills/{student_id} response

## 11. Prompt Iteration and Improvement
- [ ] 11.1 Collect teacher feedback on reasoning quality
- [ ] 11.2 Analyze low-rated reasoning for patterns
- [ ] 11.3 Iterate on prompts to improve quality
- [ ] 11.4 A/B test prompt variations
- [ ] 11.5 Document best practices for prompt engineering

## 12. Testing
- [ ] 12.1 Unit tests for prompt building
- [ ] 12.2 Integration tests with OpenAI API (use mock for cost)
- [ ] 12.3 Test with diverse assessment scenarios (low/medium/high scores)
- [ ] 12.4 Validate reasoning quality manually (sample 20 reasoning texts)
- [ ] 12.5 Test caching logic
- [ ] 12.6 Test fallback to templates
- [ ] 12.7 Test cost tracking

## 13. Monitoring
- [ ] 13.1 Track reasoning generation success rate
- [ ] 13.2 Monitor API latency (target <10s per reasoning)
- [ ] 13.3 Monitor daily API costs
- [ ] 13.4 Alert on generation failures (>5%)
- [ ] 13.5 Track cache hit rate

## 14. Documentation
- [ ] 14.1 Document reasoning API endpoints
- [ ] 14.2 Document prompt templates and engineering approach
- [ ] 14.3 Document cost management strategy
- [ ] 14.4 Create guide for improving reasoning quality
- [ ] 14.5 Document fallback template system

## 15. Deployment
- [ ] 15.1 Deploy reasoning service to Cloud Run
- [ ] 15.2 Configure OpenAI API key from Secret Manager
- [ ] 15.3 Test reasoning generation in staging
- [ ] 15.4 Monitor production reasoning quality
- [ ] 15.5 Track API costs in production
