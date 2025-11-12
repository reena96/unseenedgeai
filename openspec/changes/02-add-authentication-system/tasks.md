# Implementation Tasks: Authentication System

## 1. Database Schema Implementation
- [ ] 1.1 Create teachers table with authentication fields
- [ ] 1.2 Create refresh_tokens table for session management
- [ ] 1.3 Create password_reset_tokens table
- [ ] 1.4 Create audit_logs table for compliance
- [ ] 1.5 Add indexes for performance (email, token hashes, user_id)
- [ ] 1.6 Write Alembic migration scripts
- [ ] 1.7 Test migrations in local environment
- [ ] 1.8 Apply migrations to Cloud SQL instance

## 2. Password Management
- [ ] 2.1 Implement password hashing with bcrypt (cost factor 12)
- [ ] 2.2 Create password validation function (8+ chars, complexity requirements)
- [ ] 2.3 Implement password verification against hash
- [ ] 2.4 Write unit tests for password functions
- [ ] 2.5 Add password strength meter to frontend (future)

## 3. JWT Token Management
- [ ] 3.1 Create JWT token generation function
  - [ ] 3.1.1 Include claims: sub, email, role, school_id, exp, iat
  - [ ] 3.1.2 Sign with HS256 algorithm
  - [ ] 3.1.3 Set access token expiry (60 minutes)
  - [ ] 3.1.4 Set refresh token expiry (7 days)
- [ ] 3.2 Create token validation middleware
  - [ ] 3.2.1 Verify signature
  - [ ] 3.2.2 Check expiration
  - [ ] 3.2.3 Extract user context
  - [ ] 3.2.4 Handle malformed tokens
- [ ] 3.3 Implement refresh token rotation logic
- [ ] 3.4 Create token blacklist in Redis
- [ ] 3.5 Write unit tests for token operations

## 4. Authentication API Endpoints
- [ ] 4.1 POST /api/v1/auth/login
  - [ ] 4.1.1 Validate request body (email, password)
  - [ ] 4.1.2 Verify credentials against database
  - [ ] 4.1.3 Check account lockout status
  - [ ] 4.1.4 Generate access and refresh tokens
  - [ ] 4.1.5 Create session record
  - [ ] 4.1.6 Log successful login event
  - [ ] 4.1.7 Return tokens and user info
  - [ ] 4.1.8 Handle failed login (increment counter, lock after 5 attempts)
- [ ] 4.2 POST /api/v1/auth/refresh
  - [ ] 4.2.1 Validate refresh token
  - [ ] 4.2.2 Check if token is revoked
  - [ ] 4.2.3 Generate new access token
  - [ ] 4.2.4 Rotate refresh token
  - [ ] 4.2.5 Invalidate old refresh token
- [ ] 4.3 POST /api/v1/auth/logout
  - [ ] 4.3.1 Validate current user session
  - [ ] 4.3.2 Revoke refresh token
  - [ ] 4.3.3 Mark session as ended
  - [ ] 4.3.4 Log logout event
- [ ] 4.4 GET /api/v1/auth/me
  - [ ] 4.4.1 Extract user from JWT
  - [ ] 4.4.2 Fetch user details from database
  - [ ] 4.4.3 Return user profile
- [ ] 4.5 Write integration tests for all endpoints

## 5. Password Reset Workflow
- [ ] 5.1 POST /api/v1/auth/password/reset-request
  - [ ] 5.1.1 Validate email format
  - [ ] 5.1.2 Check rate limiting (max 3 requests/hour)
  - [ ] 5.1.3 Generate secure reset token
  - [ ] 5.1.4 Store token in database (expires in 1 hour)
  - [ ] 5.1.5 Send reset email with link
  - [ ] 5.1.6 Return generic success message (prevent user enumeration)
- [ ] 5.2 POST /api/v1/auth/password/reset
  - [ ] 5.2.1 Validate reset token
  - [ ] 5.2.2 Check token expiration
  - [ ] 5.2.3 Validate new password requirements
  - [ ] 5.2.4 Hash and update password
  - [ ] 5.2.5 Invalidate reset token
  - [ ] 5.2.6 Terminate all existing sessions (security measure)
  - [ ] 5.2.7 Send confirmation email
- [ ] 5.3 POST /api/v1/auth/password/change
  - [ ] 5.3.1 Verify current password
  - [ ] 5.3.2 Validate new password
  - [ ] 5.3.3 Ensure new password differs from current
  - [ ] 5.3.4 Update password hash
  - [ ] 5.3.5 Keep current session active
- [ ] 5.4 Integrate with email service (SendGrid)
- [ ] 5.5 Test full reset workflow

## 6. Role-Based Access Control (RBAC)
- [ ] 6.1 Define role permissions:
  - [ ] 6.1.1 Teacher: classroom data, own students, rubric submission
  - [ ] 6.1.2 Admin: school-wide data, teacher management, settings
  - [ ] 6.1.3 Student: own data, game access
- [ ] 6.2 Create permission decorators for routes
  - [ ] 6.2.1 @require_role("teacher")
  - [ ] 6.2.2 @require_role("admin")
  - [ ] 6.2.3 @require_permission("view_student_data")
- [ ] 6.3 Implement school-level data isolation
- [ ] 6.4 Add permission checks in data queries
- [ ] 6.5 Write unit tests for permission enforcement
- [ ] 6.6 Test cross-school access denial

## 7. Session Management
- [ ] 7.1 Create session record on login
- [ ] 7.2 Track device info and IP address
- [ ] 7.3 Support concurrent sessions (multiple devices)
- [ ] 7.4 Implement session listing endpoint (GET /api/v1/auth/sessions)
- [ ] 7.5 Implement session termination endpoint (DELETE /api/v1/auth/sessions/{id})
- [ ] 7.6 Add session timeout logic
- [ ] 7.7 Clean up expired sessions (scheduled job)

## 8. Audit Logging
- [ ] 8.1 Log all login attempts (success and failure)
- [ ] 8.2 Log permission denials
- [ ] 8.3 Log password changes and resets
- [ ] 8.4 Log account lockouts
- [ ] 8.5 Log data access (student records)
- [ ] 8.6 Create audit log query API for admins
- [ ] 8.7 Set up log retention policy (keep for 2 years)
- [ ] 8.8 Test log ingestion and querying

## 9. Security Hardening
- [ ] 9.1 Implement rate limiting (5 attempts per 15 min per IP)
- [ ] 9.2 Add account lockout after failed attempts
- [ ] 9.3 Configure HTTPS-only (TLS 1.3)
- [ ] 9.4 Set secure cookie attributes (HttpOnly, Secure, SameSite)
- [ ] 9.5 Add CSRF protection
- [ ] 9.6 Implement password breach detection (HaveIBeenPwned API - future)
- [ ] 9.7 Configure security headers (HSTS, X-Frame-Options, CSP)
- [ ] 9.8 Run security scan with OWASP ZAP

## 10. COPPA Compliance
- [ ] 10.1 Add student age tracking in database
- [ ] 10.2 Flag students under 13 for parental consent
- [ ] 10.3 Create parental consent workflow
- [ ] 10.4 Store consent status and timestamp
- [ ] 10.5 Block data collection for non-consented students
- [ ] 10.6 Implement consent revocation and data deletion
- [ ] 10.7 Test consent enforcement

## 11. Testing
- [ ] 11.1 Unit tests for password hashing and validation
- [ ] 11.2 Unit tests for JWT generation and validation
- [ ] 11.3 Integration tests for login flow
- [ ] 11.4 Integration tests for token refresh
- [ ] 11.5 Integration tests for password reset
- [ ] 11.6 Security tests for brute force protection
- [ ] 11.7 Security tests for token tampering
- [ ] 11.8 RBAC tests for permission enforcement
- [ ] 11.9 Load testing (100 concurrent logins)
- [ ] 11.10 Achieve >90% code coverage

## 12. Documentation
- [ ] 12.1 Document all API endpoints (OpenAPI/Swagger)
- [ ] 12.2 Create authentication flow diagrams
- [ ] 12.3 Write developer guide for adding protected endpoints
- [ ] 12.4 Document RBAC permission model
- [ ] 12.5 Create troubleshooting guide for auth issues
- [ ] 12.6 Write security best practices guide

## 13. Deployment
- [ ] 13.1 Deploy authentication service to Cloud Run
- [ ] 13.2 Configure environment variables and secrets
- [ ] 13.3 Test in staging environment
- [ ] 13.4 Run smoke tests on production
- [ ] 13.5 Monitor error rates and latency
- [ ] 13.6 Set up alerts for authentication failures
