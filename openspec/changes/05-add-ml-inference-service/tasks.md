# Implementation Tasks: ML Inference Service

## 1. Model Packaging and Deployment
- [ ] 1.1 Export Phase 0 XGBoost models to .pkl files (7 skills)
- [ ] 1.2 Export feature scalers (StandardScaler for each skill)
- [ ] 1.3 Create model version metadata (training date, performance metrics)
- [ ] 1.4 Upload models to Cloud Storage bucket (mass-production-ml-models)
- [ ] 1.5 Implement model versioning scheme (v1.0.0, v1.0.1, etc.)
- [ ] 1.6 Create model registry for tracking deployed versions

## 2. Skill Inference Service
- [ ] 2.1 Create SkillInferenceService class
  - [ ] 2.1.1 Load all 7 XGBoost models from Cloud Storage
  - [ ] 2.1.2 Load corresponding scalers
  - [ ] 2.1.3 Cache models in memory for performance
  - [ ] 2.1.4 Implement model reload on version updates
- [ ] 2.2 Create feature vector preparation
  - [ ] 2.2.1 Define feature order for each skill
  - [ ] 2.2.2 Convert feature dict to numpy array
  - [ ] 2.2.3 Handle missing features (use defaults or imputation)
  - [ ] 2.2.4 Apply feature scaling
- [ ] 2.3 Implement prediction method
  - [ ] 2.3.1 Run model.predict_proba() for probability scores
  - [ ] 2.3.2 Extract probability of "high skill" class
  - [ ] 2.3.3 Clip score to 0-1 range
  - [ ] 2.3.4 Calculate confidence based on prediction margin
- [ ] 2.4 Extract feature importance
  - [ ] 2.4.1 Get model.feature_importances_
  - [ ] 2.4.2 Map to feature names
  - [ ] 2.4.3 Return top 5 most important features
- [ ] 2.5 Test inference with sample feature vectors

## 3. Inference API Endpoints
- [ ] 3.1 POST /api/v1/skills/infer endpoint
  - [ ] 3.1.1 Accept skill name and feature dict
  - [ ] 3.1.2 Validate skill is one of 7 supported skills
  - [ ] 3.1.3 Validate features are present
  - [ ] 3.1.4 Run inference
  - [ ] 3.1.5 Return score, confidence, feature_importance
- [ ] 3.2 POST /api/v1/skills/infer/batch endpoint
  - [ ] 3.2.1 Accept array of (student_id, skill, features)
  - [ ] 3.2.2 Run batch inference (vectorized)
  - [ ] 3.2.3 Return array of results
  - [ ] 3.2.4 Handle partial failures gracefully
- [ ] 3.3 GET /api/v1/skills/models endpoint
  - [ ] 3.3.1 List available model versions
  - [ ] 3.3.2 Show current deployed version per skill
  - [ ] 3.3.3 Show model metadata (accuracy, training date)

## 4. Batch Inference Worker
- [ ] 4.1 Create Cloud Tasks handler for batch inference jobs
- [ ] 4.2 Implement nightly batch inference:
  - [ ] 4.2.1 Query all students with new features (linguistic + behavioral)
  - [ ] 4.2.2 Run inference for all 7 skills per student
  - [ ] 4.2.3 Store results in skill_assessments table (pre-fusion)
  - [ ] 4.2.4 Log processing time and throughput
- [ ] 4.3 Add incremental inference (only for students with new data)
- [ ] 4.4 Test worker with 100+ students

## 5. Model Performance Monitoring
- [ ] 5.1 Track inference latency per skill
- [ ] 5.2 Monitor prediction distribution (detect drift)
- [ ] 5.3 Compare predictions against teacher ratings (validation)
- [ ] 5.4 Calculate correlation (r) between predictions and ground truth
- [ ] 5.5 Alert if correlation drops below 0.50
- [ ] 5.6 Create model performance dashboard

## 6. A/B Testing Framework
- [ ] 6.1 Implement model variant selection logic
- [ ] 6.2 Support traffic splitting (90% v1, 10% v2)
- [ ] 6.3 Track metrics per model version
- [ ] 6.4 Implement gradual rollout (canary deployment)
- [ ] 6.5 Add rollback capability

## 7. Caching
- [ ] 7.1 Cache inference results in Redis
  - [ ] 7.1.1 Key: (student_id, skill, feature_hash)
  - [ ] 7.1.2 TTL: 24 hours
  - [ ] 7.1.3 Invalidate on new features
- [ ] 7.2 Cache loaded models in memory
- [ ] 7.3 Measure cache hit rate (target >80%)

## 8. Error Handling
- [ ] 8.1 Handle missing features gracefully
- [ ] 8.2 Handle model loading failures
- [ ] 8.3 Handle prediction errors (invalid input)
- [ ] 8.4 Retry failed inferences (up to 3 times)
- [ ] 8.5 Log all errors for debugging

## 9. Testing
- [ ] 9.1 Unit tests for feature preparation
- [ ] 9.2 Unit tests for inference logic
- [ ] 9.3 Integration tests with real model files
- [ ] 9.4 Validate predictions match expected ranges (0-1)
- [ ] 9.5 Test batch inference with 1000 students
- [ ] 9.6 Performance test (target: <30s per student for 7 skills)
- [ ] 9.7 Validate feature importance extraction

## 10. Model Retraining Pipeline (Future)
- [ ] 10.1 Document retraining process
- [ ] 10.2 Create training data export script
- [ ] 10.3 Create model training notebook
- [ ] 10.4 Create model evaluation report template
- [ ] 10.5 Document model deployment checklist

## 11. Documentation
- [ ] 11.1 Document inference API endpoints
- [ ] 11.2 Document feature vector format for each skill
- [ ] 11.3 Document model performance metrics
- [ ] 11.4 Create model versioning guide
- [ ] 11.5 Create troubleshooting guide for inference issues

## 12. Deployment
- [ ] 12.1 Deploy inference service to Cloud Run
- [ ] 12.2 Upload model files to Cloud Storage
- [ ] 12.3 Test inference in staging
- [ ] 12.4 Run smoke tests with sample students
- [ ] 12.5 Monitor production inference latency
