# CI/CD Pipeline and Monitoring Setup

This document describes the CI/CD pipeline and monitoring infrastructure for the MASS platform.

## Overview

The MASS platform uses GitHub Actions for continuous integration and deployment, with Google Cloud Run for hosting, and Google Cloud Monitoring for observability.

## Components

### 1. GitHub Actions Workflows

#### Backend CI/CD (`backend-ci-cd.yml`)
- **Triggers**: Push/PR to `main` or `develop` branches
- **Jobs**:
  - **Test**: Runs pytest with PostgreSQL service
  - **Lint**: Runs Black, Flake8, and MyPy
  - **Build**: Creates Docker image and pushes to GCR
  - **Deploy Staging**: Deploys to staging environment (develop branch)
  - **Deploy Production**: Blue-green deployment to production (main branch)
  - **Rollback**: Automatic rollback on deployment failures

#### Frontend CI/CD (`frontend-ci-cd.yml`)
- **Triggers**: Push/PR to `main` or `develop` affecting frontend files
- **Jobs**:
  - **Test**: Runs npm test and linter
  - **Build**: Creates optimized production build
  - **Build Docker**: Creates nginx-based Docker image
  - **Deploy Staging/Production**: Deploys to Cloud Run

#### Monitoring (`monitoring.yml`)
- **Triggers**: Scheduled (every 15 minutes) or manual
- **Jobs**:
  - **Health Check**: Verifies backend and frontend availability
  - **Performance Check**: Monitors API response times
  - **Cost Monitoring**: Tracks resource usage

### 2. Deployment Strategy

#### Blue-Green Deployment (Production)
1. Deploy new version with `--tag blue` and `--no-traffic`
2. Run health checks on blue version
3. Switch 100% traffic to blue version
4. Automatic rollback if health checks fail

#### Staging Deployment
- Direct deployment from develop branch
- Runs smoke tests post-deployment
- Lower resource allocation than production

### 3. Monitoring Infrastructure

#### Google Cloud Monitoring Dashboard
Location: `infrastructure/monitoring/dashboard.json`

**Metrics Tracked**:
- API request rate (requests/sec)
- API response latency (p95)
- Error rate (errors/sec)
- CPU utilization (%)
- Memory utilization (%)
- Active instance count
- Recent error logs

#### Alert Policies
Location: `infrastructure/monitoring/alert-policies.yml`

**Alerts**:
1. **High API Error Rate**: > 5 errors/min for 5 minutes
2. **High API Latency**: p95 > 1 second for 5 minutes
3. **High CPU**: > 90% for 5 minutes
4. **High Memory**: > 85% for 5 minutes
5. **Service Unavailable**: > 10 5xx errors/min for 3 minutes
6. **Database Connection Failures**: > 1 error/min for 3 minutes
7. **Cost Budget Alert**: > 80% of monthly budget

#### Notification Channels
- Email: engineering@unseenedgeai.com
- Slack: #alerts channel
- PagerDuty: On-call engineer (critical alerts only)

### 4. Uptime Monitoring
- **Backend API**: Health check every 5 minutes
- **Frontend**: Availability check every 5 minutes
- **Target**: 95%+ uptime

## Setup Instructions

### Prerequisites
1. Google Cloud Project with billing enabled
2. GitHub repository with Actions enabled
3. Service account with required permissions

### 1. Configure GitHub Secrets

Add these secrets to your GitHub repository:

```
GCP_PROJECT_ID=your-project-id
GCP_SA_KEY=<service-account-json-key>
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
PAGERDUTY_SERVICE_KEY=your-pagerduty-key
```

### 2. Deploy Monitoring Infrastructure

```bash
cd infrastructure/monitoring

# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export PAGERDUTY_SERVICE_KEY="your-key"

# Deploy
./deploy-monitoring.sh
```

### 3. Verify Workflows

```bash
# Trigger a test deployment
git checkout develop
git commit --allow-empty -m "Test CI/CD pipeline"
git push origin develop

# Check GitHub Actions tab for workflow status
```

### 4. View Monitoring Dashboard

1. Navigate to: https://console.cloud.google.com/monitoring/dashboards
2. Find "MASS Platform Dashboard"
3. Monitor metrics in real-time

## Deployment Flow

### Feature Development
```
feature-branch → develop (staging) → main (production)
```

1. **Feature Branch**: Developer creates feature branch
2. **Pull Request**: Opens PR to develop
3. **CI Checks**: Automated tests and linting run
4. **Merge to Develop**: Deploys to staging automatically
5. **QA/Testing**: Manual testing on staging
6. **Merge to Main**: Deploys to production with blue-green strategy

## Environment Configuration

### Staging Environment
- **Backend URL**: `https://mass-api-staging-*.run.app`
- **Frontend URL**: `https://mass-frontend-staging-*.run.app`
- **Database**: Cloud SQL (staging instance)
- **Resources**: 2GB RAM, 2 CPU, 1-10 instances

### Production Environment
- **Backend URL**: `https://mass-api-*.run.app`
- **Frontend URL**: `https://mass-frontend-*.run.app`
- **Database**: Cloud SQL (production instance)
- **Resources**: 4GB RAM, 4 CPU, 2-100 instances

## Monitoring Best Practices

### 1. Regular Dashboard Reviews
- Check dashboard daily for anomalies
- Review weekly trends
- Adjust alert thresholds based on actual patterns

### 2. Alert Response
- **Critical**: Respond within 15 minutes
- **Error**: Respond within 1 hour
- **Warning**: Review within 24 hours

### 3. Incident Management
1. Acknowledge alert in PagerDuty/Slack
2. Check monitoring dashboard for context
3. Review recent deployments (GitHub Actions)
4. Check Cloud Logging for detailed errors
5. Rollback if needed
6. Create post-mortem document

### 4. Performance Optimization
- Monitor p95 latency trends
- Optimize queries if latency increases
- Scale instances if CPU/memory consistently high
- Review Cloud Profiler for bottlenecks

## Cost Management

### Current Estimates (Monthly)
- Cloud Run (Backend): $50-200
- Cloud Run (Frontend): $20-50
- Cloud SQL: $100-300
- Cloud Storage: $10-30
- Cloud Monitoring: $5-20
- **Total**: ~$185-600/month

### Cost Optimization
1. Use minimum instances = 1 for staging
2. Enable request-based autoscaling
3. Set maximum instance limits
4. Use Cloud Storage lifecycle policies
5. Monitor with budget alerts (80% threshold)

## Rollback Procedures

### Automatic Rollback
- Triggered by failed health checks during deployment
- Reverts to previous stable revision
- Notifications sent to all channels

### Manual Rollback
```bash
# List revisions
gcloud run revisions list --service mass-api --region us-central1

# Rollback to specific revision
gcloud run services update-traffic mass-api \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

## Troubleshooting

### Deployment Failures
1. Check GitHub Actions logs
2. Verify GCP service account permissions
3. Check Cloud Run error logs
4. Verify Docker image builds successfully

### Monitoring Alerts Not Firing
1. Verify alert policies are enabled
2. Check notification channels are configured
3. Verify metric filters are correct
4. Test with manual threshold triggers

### High Costs
1. Check Cloud Run instance counts
2. Review Cloud SQL connection pooling
3. Check for memory leaks (increasing memory usage)
4. Optimize database queries
5. Review Cloud Storage usage

## Security Considerations

### Secrets Management
- All secrets stored in GitHub Secrets
- Service account keys rotated every 90 days
- Least-privilege IAM roles

### Network Security
- Cloud Run services behind Cloud Load Balancer
- HTTPS only (automatic TLS)
- VPC connectors for database access
- No public database IPs

### Compliance
- FERPA compliant logging (no PII in logs)
- Audit logs enabled
- 90-day log retention
- Regular security scanning with Cloud Security Scanner

## Maintenance Schedule

### Daily
- Review monitoring dashboard
- Check for new alerts
- Verify backups completed

### Weekly
- Review deployment logs
- Check for dependency updates
- Review cost reports

### Monthly
- Rotate service account keys
- Review and update alert thresholds
- Capacity planning review
- Security patch updates

## Support and Resources

- **CI/CD Issues**: Check GitHub Actions logs
- **Monitoring**: https://console.cloud.google.com/monitoring
- **Logging**: https://console.cloud.google.com/logs
- **Cloud Run**: https://console.cloud.google.com/run
- **Documentation**: /infrastructure/CI-CD-README.md

## Next Steps

- [ ] Set up Terraform for infrastructure as code
- [ ] Implement automated rollback testing
- [ ] Add performance benchmarking to CI
- [ ] Set up log-based metrics for custom alerts
- [ ] Implement canary deployments
- [ ] Add E2E tests to CI pipeline

---

**Last Updated**: November 2025
**Maintained By**: Engineering Team
**Version**: 1.0
