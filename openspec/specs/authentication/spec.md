# Authentication Capability

## Purpose

The Authentication capability manages user identity, access control, and session management for teachers, administrators, and students. It ensures secure access to the MASS system with role-based permissions and compliance with educational data privacy regulations.

## Requirements

### Requirement: User Registration and Onboarding

The system SHALL support user registration with role-based access.

#### Scenario: School administrator registration
- **GIVEN** a new school is onboarding to MASS
- **WHEN** the school administrator registers
- **THEN** an account is created with "admin" role
- **AND** admin can create teacher accounts for their school
- **AND** admin can configure school settings
- **AND** email verification is required before access

#### Scenario: Teacher account creation by admin
- **GIVEN** a school admin is logged in
- **WHEN** they create a teacher account
- **THEN** teacher receives an email invitation with secure token
- **AND** teacher sets their own password on first login
- **AND** teacher is associated with the school
- **AND** teacher has "teacher" role with appropriate permissions

#### Scenario: Student account creation
- **GIVEN** a teacher imports student roster (CSV or SIS integration)
- **WHEN** student accounts are created
- **THEN** each student gets unique credentials
- **AND** students under 13 are flagged for COPPA compliance
- **AND** parental consent workflow is initiated if needed
- **AND** students have "student" role with limited permissions

### Requirement: User Authentication

The system SHALL authenticate users via email/password with secure token management.

#### Scenario: Successful login
- **GIVEN** a teacher enters valid email and password
- **WHEN** they submit the login form
- **THEN** credentials are verified against database (bcrypt hash)
- **AND** a JWT access token is generated (expires in 60 minutes)
- **AND** a refresh token is generated (expires in 7 days)
- **AND** tokens are returned to the client
- **AND** login event is logged for audit

#### Scenario: Failed login (invalid credentials)
- **GIVEN** a user enters incorrect password
- **WHEN** they attempt to login
- **THEN** authentication fails with generic error "Invalid credentials"
- **AND** failed attempt is logged with IP address
- **AND** account is locked after 5 failed attempts in 15 minutes
- **AND** user receives lockout notification via email

#### Scenario: Account lockout
- **GIVEN** an account has been locked due to failed attempts
- **WHEN** user tries to login
- **THEN** login is denied with message "Account locked. Check email for unlock instructions."
- **AND** user can unlock via email link or after 30 minutes
- **AND** admin can manually unlock the account

#### Scenario: Multi-factor authentication (Future)
- **GIVEN** MFA is enabled for the user (Phase 2 feature)
- **WHEN** they login with valid credentials
- **THEN** an OTP is sent via email or SMS
- **AND** user must enter OTP within 10 minutes
- **AND** access is granted only after OTP verification

### Requirement: Token Management

The system SHALL use JWT tokens for stateless authentication.

#### Scenario: Access token structure
- **GIVEN** a user successfully logs in
- **WHEN** an access token is generated
- **THEN** token includes claims:
  - `sub`: user_id (UUID)
  - `email`: user email
  - `role`: user role (admin, teacher, student)
  - `school_id`: associated school UUID
  - `exp`: expiration timestamp (60 minutes from issue)
  - `iat`: issued at timestamp
- **AND** token is signed with HS256 algorithm using secret key

#### Scenario: Token refresh
- **GIVEN** a user's access token is about to expire
- **WHEN** the client sends a refresh request with valid refresh token
- **THEN** a new access token is generated
- **AND** refresh token is rotated (new refresh token issued)
- **AND** old refresh token is invalidated
- **AND** user remains logged in seamlessly

#### Scenario: Token expiration
- **GIVEN** an access token has expired
- **WHEN** a user makes an API request
- **THEN** the request is rejected with 401 Unauthorized
- **AND** response includes error code "TOKEN_EXPIRED"
- **AND** client automatically attempts token refresh

#### Scenario: Token revocation
- **GIVEN** a user logs out
- **WHEN** the logout request is processed
- **THEN** the refresh token is revoked (added to blacklist)
- **AND** access token remains valid until natural expiration
- **AND** logout event is logged

### Requirement: Role-Based Access Control (RBAC)

The system SHALL enforce permissions based on user roles.

#### Scenario: Teacher permissions
- **GIVEN** a teacher is authenticated
- **WHEN** they access resources
- **THEN** they can:
  - View students in their assigned classrooms
  - Upload classroom audio for their classes
  - View skill assessments for their students
  - Submit teacher rubrics for their students
  - Export data for their classes
- **AND** they cannot:
  - View students outside their classrooms
  - Access school-wide administrative settings
  - View other teachers' data

#### Scenario: Admin permissions
- **GIVEN** a school admin is authenticated
- **WHEN** they access resources
- **THEN** they can:
  - All teacher permissions for their school
  - Create/edit/delete teacher accounts
  - View school-wide analytics and reports
  - Configure school settings
  - Manage student rosters
- **AND** they cannot:
  - Access data from other schools
  - Modify system-wide settings

#### Scenario: Student permissions
- **GIVEN** a student is authenticated
- **WHEN** they access resources
- **THEN** they can:
  - Play the Flourish Academy game
  - View their own skill progress (student dashboard - Phase 2)
- **AND** they cannot:
  - View other students' data
  - Access teacher or admin features
  - Modify their own assessments

#### Scenario: Permission enforcement
- **GIVEN** a teacher attempts to access another school's data
- **WHEN** the API validates the request
- **THEN** the request is rejected with 403 Forbidden
- **AND** unauthorized access attempt is logged
- **AND** security team is notified if pattern detected

### Requirement: Session Management

The system SHALL manage user sessions securely.

#### Scenario: Session creation
- **GIVEN** a user logs in successfully
- **WHEN** tokens are issued
- **THEN** a session record is created in the database
- **AND** session includes: user_id, device_info, IP address, login_timestamp
- **AND** session is associated with refresh token

#### Scenario: Session expiration (inactivity)
- **GIVEN** a user has been inactive for 60 minutes
- **WHEN** they attempt to make a request
- **THEN** access token has expired
- **AND** client attempts refresh
- **IF** refresh token is still valid (<7 days)
  - **THEN** new access token is issued
- **IF** refresh token is expired
  - **THEN** user must log in again

#### Scenario: Session termination (logout)
- **GIVEN** a user clicks "Logout"
- **WHEN** the logout request is processed
- **THEN** refresh token is revoked
- **AND** session record is marked as "ended"
- **AND** user is redirected to login page
- **AND** client clears local storage

#### Scenario: Concurrent session handling
- **GIVEN** a user logs in from multiple devices
- **WHEN** each login succeeds
- **THEN** each device gets its own session and refresh token
- **AND** all sessions remain valid concurrently
- **AND** user can view active sessions in account settings
- **AND** user can terminate specific sessions remotely

### Requirement: Password Management

The system SHALL enforce strong password policies and support password reset.

#### Scenario: Password requirements
- **GIVEN** a user is setting or changing their password
- **WHEN** they enter a new password
- **THEN** the system validates:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character (@, #, $, %, etc.)
- **AND** password is hashed with bcrypt (cost factor 12)
- **AND** plaintext password is never stored

#### Scenario: Password reset request
- **GIVEN** a user forgot their password
- **WHEN** they click "Forgot Password" and enter email
- **THEN** a secure reset token is generated (expires in 1 hour)
- **AND** reset link is emailed to the user
- **AND** old passwords remain valid until reset completes
- **AND** rate limiting prevents abuse (max 3 requests/hour)

#### Scenario: Password reset completion
- **GIVEN** a user clicks the reset link
- **WHEN** they enter a new password
- **THEN** the system validates the reset token
- **AND** new password meets requirements
- **AND** password is hashed and updated
- **AND** reset token is invalidated
- **AND** all existing sessions are terminated (security measure)
- **AND** confirmation email is sent

#### Scenario: Password change (authenticated user)
- **GIVEN** a logged-in user wants to change password
- **WHEN** they submit the change form
- **THEN** the system verifies current password
- **AND** validates new password meets requirements
- **AND** new password is different from current
- **AND** password is updated
- **AND** user remains logged in (current session not terminated)

### Requirement: Audit Logging

The system SHALL log all authentication and authorization events for compliance.

#### Scenario: Login event logging
- **GIVEN** any login attempt (success or failure)
- **WHEN** the attempt occurs
- **THEN** an audit log entry is created with:
  - User ID (if known) or email attempted
  - Timestamp (UTC)
  - IP address
  - User agent (browser/device)
  - Success or failure status
  - Failure reason if applicable
- **AND** log is stored in immutable audit_logs table

#### Scenario: Permission denial logging
- **GIVEN** a user attempts an unauthorized action
- **WHEN** access is denied
- **THEN** an audit log entry is created with:
  - User ID
  - Timestamp
  - Resource attempted (e.g., "/api/v1/students/{id}")
  - Permission required
  - Denial reason
- **AND** patterns of repeated denials trigger security review

#### Scenario: Sensitive action logging
- **GIVEN** a user performs a sensitive action (e.g., data export, account deletion)
- **WHEN** the action completes
- **THEN** a detailed audit log is created
- **AND** log includes full context (what was accessed/modified)
- **AND** administrator can query audit logs for compliance reviews

### Requirement: Data Privacy and Compliance

The system SHALL comply with FERPA, COPPA, and GDPR-K requirements.

#### Scenario: FERPA compliance (access control)
- **GIVEN** student educational records in the system
- **WHEN** any user attempts to access them
- **THEN** access is restricted to:
  - Teachers of the student
  - School administrators
  - The student themselves (with parental consent if under 18)
- **AND** all access is logged for audit trail
- **AND** data cannot be shared with third parties without consent

#### Scenario: COPPA compliance (parental consent)
- **GIVEN** a student is under 13 years old
- **WHEN** they are registered in the system
- **THEN** parental consent is required before data collection
- **AND** consent status is tracked in the database
- **AND** students without consent cannot play the game or have transcripts analyzed
- **AND** consent can be revoked, triggering data deletion

#### Scenario: Right to data deletion
- **GIVEN** a parent or eligible student requests data deletion
- **WHEN** the request is verified
- **THEN** all student data is permanently deleted:
  - Skill assessments
  - Transcript segments
  - Game telemetry
  - Evidence items
  - Teacher rubrics
- **AND** deletion is logged for compliance
- **AND** confirmation is sent to requester
- **AND** deletion completes within 30 days

#### Scenario: Data retention policy
- **GIVEN** a student graduates or leaves the school
- **WHEN** graduation date + 1 year has passed
- **THEN** student data is automatically archived or deleted
- **AND** archived data is encrypted and access-restricted
- **AND** retention policy is configurable per school/district

### Requirement: API Authentication

The system SHALL require authentication for all API endpoints except public ones.

#### Scenario: Authenticated API request
- **GIVEN** a client has a valid access token
- **WHEN** they make an API request
- **THEN** the token is included in Authorization header: `Bearer <token>`
- **AND** the API validates token signature
- **AND** token expiration is checked
- **AND** user and role are extracted from token claims
- **AND** request is processed with user context

#### Scenario: Unauthenticated API request
- **GIVEN** a client makes a request without a token
- **WHEN** the API receives the request
- **THEN** the request is rejected with 401 Unauthorized
- **AND** response includes WWW-Authenticate header
- **AND** error message: "Authentication required"

#### Scenario: Invalid token
- **GIVEN** a client sends a malformed or tampered token
- **WHEN** the API validates the token
- **THEN** validation fails (signature mismatch)
- **AND** request is rejected with 401 Unauthorized
- **AND** error message: "Invalid token"
- **AND** incident is logged as potential security threat

## Non-Functional Requirements

### Security
- **Password hashing:** bcrypt with cost factor 12
- **Token signing:** HS256 with 256-bit secret key
- **Secret storage:** Google Cloud Secret Manager
- **HTTPS only:** All traffic over TLS 1.3
- **Rate limiting:** 5 login attempts per 15 minutes per IP

### Performance
- **Login latency:** <500ms p95
- **Token validation:** <10ms
- **Password hashing:** <200ms (bcrypt is intentionally slow)

### Reliability
- **Uptime:** 99.9% for authentication service
- **Token validation cache:** Redis for fast lookups
- **Database failover:** Automatic for authentication database

### Compliance
- **FERPA:** Access controls enforced, audit logging complete
- **COPPA:** Parental consent workflow for users <13
- **GDPR-K:** Right to access, right to deletion, data minimization

## Dependencies

### External Services
- **Google Cloud Secret Manager:** Store signing keys and secrets
- **Email Service:** SendGrid or similar for password reset and notifications

### Internal Services
- **Database:** PostgreSQL for users, sessions, audit logs
- **Cache:** Redis for token blacklist and validation cache

### Libraries
- **python-jose:** JWT handling
- **passlib:** Password hashing (bcrypt)
- **fastapi-security:** OAuth2 password bearer

## API Endpoints

### POST /api/v1/auth/login
Authenticate user and issue tokens.

**Request:**
```json
{
  "email": "teacher@school.edu",
  "password": "SecureP@ssw0rd"
}
```

**Response:** 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "teacher@school.edu",
    "first_name": "Jane",
    "last_name": "Doe",
    "role": "teacher",
    "school_id": "uuid"
  }
}
```

### POST /api/v1/auth/refresh
Refresh access token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:** 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",  // Rotated
  "expires_in": 3600
}
```

### POST /api/v1/auth/logout
Terminate session and revoke refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:** 200 OK
```json
{
  "message": "Logged out successfully"
}
```

### POST /api/v1/auth/password/reset-request
Request password reset.

**Request:**
```json
{
  "email": "teacher@school.edu"
}
```

**Response:** 200 OK
```json
{
  "message": "If an account exists, a reset email has been sent"
}
```

### POST /api/v1/auth/password/reset
Complete password reset.

**Request:**
```json
{
  "reset_token": "secure-token-from-email",
  "new_password": "NewSecureP@ssw0rd"
}
```

**Response:** 200 OK
```json
{
  "message": "Password reset successfully"
}
```

### POST /api/v1/auth/password/change
Change password (authenticated user).

**Request:**
```json
{
  "current_password": "OldP@ssw0rd",
  "new_password": "NewSecureP@ssw0rd"
}
```

**Response:** 200 OK
```json
{
  "message": "Password changed successfully"
}
```

### GET /api/v1/auth/me
Get current user info (requires authentication).

**Response:** 200 OK
```json
{
  "id": "uuid",
  "email": "teacher@school.edu",
  "first_name": "Jane",
  "last_name": "Doe",
  "role": "teacher",
  "school_id": "uuid",
  "school_name": "Lincoln Middle School"
}
```

## Data Models

### teachers Table (extends users)
```sql
CREATE TABLE teachers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'teacher',  -- teacher, admin
    email_verified BOOLEAN DEFAULT FALSE,
    account_locked BOOLEAN DEFAULT FALSE,
    failed_login_attempts INTEGER DEFAULT 0,
    last_failed_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_teachers_email ON teachers(email);
CREATE INDEX idx_teachers_school ON teachers(school_id);
```

### refresh_tokens Table
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES teachers(id),
    token_hash VARCHAR(255) NOT NULL,  -- Hashed for security
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP,
    device_info JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);
```

### password_reset_tokens Table
```sql
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES teachers(id),
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reset_tokens_hash ON password_reset_tokens(token_hash);
```

### audit_logs Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,  -- NULL for failed logins with unknown user
    action VARCHAR(100) NOT NULL,  -- login_success, login_failed, permission_denied, etc.
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
```

## Error Codes

- `AUTH_001`: Invalid credentials
- `AUTH_002`: Account locked
- `AUTH_003`: Token expired
- `AUTH_004`: Invalid token
- `AUTH_005`: Refresh token revoked
- `AUTH_006`: Password does not meet requirements
- `AUTH_007`: Reset token expired or invalid
- `AUTH_008`: Email already registered
- `AUTH_009`: Permission denied
- `AUTH_010`: Session not found

## Monitoring and Metrics

### Key Metrics
- **Login success rate:** Target >95%
- **Login latency p95:** <500ms
- **Failed login rate:** Monitor for attacks
- **Token refresh rate:** Track for session health
- **Account lockouts per day:** Alert if spike

### Alerts
- Failed login rate >10% in 15 minutes (potential attack)
- Account lockout rate >5% of users (investigate)
- Token validation errors >5% (check secret rotation)
- Authentication service downtime
- Unusual access patterns (e.g., 100 requests/min from single IP)

## Testing Strategy

### Unit Tests
- Password hashing and verification
- JWT token generation and validation
- Permission checking logic
- Rate limiting enforcement

### Integration Tests
- Full login flow: credentials → tokens → API access
- Token refresh cycle
- Password reset workflow
- Role-based access control enforcement

### Security Tests
- Brute force attack simulation (verify account lockout)
- Token tampering detection
- SQL injection attempts on login
- XSS attempts in email fields

### Compliance Tests
- FERPA: Verify teachers can't access other schools' data
- COPPA: Verify parental consent enforcement for <13
- Data deletion: Verify complete removal of student data

## Future Enhancements (Out of Scope for Phase 1)

- **Multi-Factor Authentication (MFA):** Email/SMS OTP
- **Single Sign-On (SSO):** SAML, OAuth2 with Google/Microsoft
- **Biometric Authentication:** For student game access (mobile)
- **Passwordless Login:** Magic links via email
- **Advanced Threat Detection:** ML-based anomaly detection
- **Session Analytics:** Track user behavior for UX insights
- **Federated Identity:** District-level identity providers
