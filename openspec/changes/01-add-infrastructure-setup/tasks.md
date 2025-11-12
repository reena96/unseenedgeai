# Implementation Tasks: Infrastructure Setup

## 1. GCP Project Initialization
- [ ] 1.1 Create GCP project `mass-production`
- [ ] 1.2 Enable billing account
- [ ] 1.3 Enable required APIs:
  - [ ] 1.3.1 Cloud Run API
  - [ ] 1.3.2 Cloud SQL Admin API
  - [ ] 1.3.3 Cloud Storage API
  - [ ] 1.3.4 Cloud Tasks API
  - [ ] 1.3.5 Cloud Pub/Sub API
  - [ ] 1.3.6 Cloud Speech-to-Text API
  - [ ] 1.3.7 Secret Manager API
  - [ ] 1.3.8 Cloud Logging API
  - [ ] 1.3.9 Cloud Monitoring API
- [ ] 1.4 Configure default region (us-central1)
- [ ] 1.5 Set up billing alerts and budget caps

## 2. Cloud SQL Database Setup
- [ ] 2.1 Create Cloud SQL instance with PostgreSQL 15
  - [ ] 2.1.1 Instance tier: db-custom-2-7680 (2 vCPU, 7.5GB RAM)
  - [ ] 2.1.2 Enable high availability mode
  - [ ] 2.1.3 Configure automated backups (daily at 3 AM)
  - [ ] 2.1.4 Set maintenance window (Sunday 4 AM)
- [ ] 2.2 Create database `mass_db`
- [ ] 2.3 Install TimescaleDB extension
- [ ] 2.4 Configure connection pooling (PgBouncer)
- [ ] 2.5 Set up database credentials in Secret Manager
- [ ] 2.6 Configure SSL/TLS for connections
- [ ] 2.7 Set up database monitoring and alerting
- [ ] 2.8 Test database connectivity from Cloud Run

## 3. Cloud Storage Configuration
- [ ] 3.1 Create bucket `mass-production-audio-files` for audio recordings
  - [ ] 3.1.1 Set region to us-central1
  - [ ] 3.1.2 Configure lifecycle policy (delete after 30 days)
  - [ ] 3.1.3 Enable versioning for accidental deletion recovery
  - [ ] 3.1.4 Set up CORS for frontend uploads
- [ ] 3.2 Create bucket `mass-production-ml-models` for trained models
  - [ ] 3.2.1 Set region to us-central1
  - [ ] 3.2.2 Enable versioning for model rollback
  - [ ] 3.2.3 Configure IAM permissions for service accounts
- [ ] 3.3 Test file upload and download operations
- [ ] 3.4 Verify lifecycle policies trigger correctly

## 4. Cloud Tasks and Pub/Sub Setup
- [ ] 4.1 Create Cloud Tasks queues:
  - [ ] 4.1.1 `transcription-jobs` queue (max 10 concurrent)
  - [ ] 4.1.2 `inference-jobs` queue (max 20 concurrent)
  - [ ] 4.1.3 Configure retry policies and deadlines
  - [ ] 4.1.4 Set up queue monitoring
- [ ] 4.2 Create Pub/Sub topics:
  - [ ] 4.2.1 `audio-uploaded` topic
  - [ ] 4.2.2 `transcription-completed` topic
  - [ ] 4.2.3 `features-extracted` topic
  - [ ] 4.2.4 `skills-inferred` topic
- [ ] 4.3 Create Pub/Sub subscriptions for each topic
- [ ] 4.4 Configure message retention and acknowledgment deadlines
- [ ] 4.5 Test message publishing and consumption

## 5. Service Accounts and IAM
- [ ] 5.1 Create service account `mass-api@mass-production.iam.gserviceaccount.com`
- [ ] 5.2 Grant required permissions:
  - [ ] 5.2.1 Cloud SQL Client role
  - [ ] 5.2.2 Storage Object Admin role
  - [ ] 5.2.3 Cloud Tasks Enqueuer role
  - [ ] 5.2.4 Pub/Sub Publisher/Subscriber roles
  - [ ] 5.2.5 Secret Manager Secret Accessor role
  - [ ] 5.2.6 Speech-to-Text User role
- [ ] 5.3 Download and securely store service account key
- [ ] 5.4 Configure service account for Cloud Run deployment
- [ ] 5.5 Document IAM roles and permissions

## 6. Secret Manager Configuration
- [ ] 6.1 Store database password
- [ ] 6.2 Store JWT signing secret key (256-bit)
- [ ] 6.3 Store OpenAI API key (for future GPT-4 integration)
- [ ] 6.4 Configure secret access permissions
- [ ] 6.5 Set up secret rotation policies
- [ ] 6.6 Test secret retrieval from application

## 7. Terraform Infrastructure-as-Code
- [ ] 7.1 Create Terraform project structure
- [ ] 7.2 Write Terraform configuration for:
  - [ ] 7.2.1 GCP provider and project setup
  - [ ] 7.2.2 Cloud SQL instance and database
  - [ ] 7.2.3 Cloud Storage buckets
  - [ ] 7.2.4 Cloud Tasks queues
  - [ ] 7.2.5 Pub/Sub topics and subscriptions
  - [ ] 7.2.6 Service accounts and IAM bindings
  - [ ] 7.2.7 Secret Manager secrets
- [ ] 7.3 Initialize Terraform backend (GCS for state storage)
- [ ] 7.4 Run `terraform plan` and review changes
- [ ] 7.5 Apply Terraform configuration
- [ ] 7.6 Verify all resources created correctly
- [ ] 7.7 Document Terraform usage and commands

## 8. Monitoring and Logging
- [ ] 8.1 Enable Cloud Logging for all services
- [ ] 8.2 Set up log sinks for error tracking
- [ ] 8.3 Configure Cloud Monitoring dashboards:
  - [ ] 8.3.1 Database performance metrics
  - [ ] 8.3.2 Cloud Run instance metrics
  - [ ] 8.3.3 Storage usage metrics
  - [ ] 8.3.4 Task queue depth and latency
- [ ] 8.4 Create alerting policies:
  - [ ] 8.4.1 Database connection failures
  - [ ] 8.4.2 High CPU/memory usage
  - [ ] 8.4.3 Storage quota warnings
  - [ ] 8.4.4 Task queue processing delays
- [ ] 8.5 Set up Sentry for error tracking
- [ ] 8.6 Configure alert notification channels (email, Slack)

## 9. CI/CD Pipeline
- [ ] 9.1 Create GitHub Actions workflow for:
  - [ ] 9.1.1 Automated testing on pull requests
  - [ ] 9.1.2 Docker image building
  - [ ] 9.1.3 Image pushing to Google Artifact Registry
  - [ ] 9.1.4 Cloud Run deployment on merge to main
- [ ] 9.2 Configure GitHub secrets for GCP credentials
- [ ] 9.3 Set up deployment environments (staging, production)
- [ ] 9.4 Test full CI/CD pipeline with dummy application
- [ ] 9.5 Document deployment process

## 10. Documentation and Verification
- [ ] 10.1 Create infrastructure architecture diagram
- [ ] 10.2 Document all GCP resource names and configurations
- [ ] 10.3 Write setup guide for local development environment
- [ ] 10.4 Create troubleshooting guide for common issues
- [ ] 10.5 Verify all services are accessible and functional
- [ ] 10.6 Run end-to-end connectivity tests
- [ ] 10.7 Create infrastructure cost estimate and monitoring dashboard
- [ ] 10.8 Hand off infrastructure to development team with walkthrough
