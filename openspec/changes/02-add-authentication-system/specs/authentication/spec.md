# Authentication Capability Delta

## MODIFIED Requirements

### Requirement: User Authentication

The system SHALL authenticate users via email/password with secure token management and account protection.

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

### Requirement: Token Management

The system SHALL use JWT tokens for stateless authentication with refresh token rotation.

#### Scenario: Access token structure
- **GIVEN** a user successfully logs in
- **WHEN** an access token is generated
- **THEN** token includes claims: sub, email, role, school_id, exp, iat
- **AND** token is signed with HS256 algorithm using secret key from Secret Manager

#### Scenario: Token refresh
- **GIVEN** a user's access token is about to expire
- **WHEN** the client sends a refresh request with valid refresh token
- **THEN** a new access token is generated
- **AND** refresh token is rotated (new refresh token issued)
- **AND** old refresh token is invalidated
- **AND** user remains logged in seamlessly

#### Scenario: Token revocation
- **GIVEN** a user logs out
- **WHEN** the logout request is processed
- **THEN** the refresh token is revoked (added to Redis blacklist)
- **AND** access token remains valid until natural expiration
- **AND** logout event is logged

### Requirement: Password Management

The system SHALL enforce strong password policies and support secure password reset.

#### Scenario: Password requirements
- **GIVEN** a user is setting or changing their password
- **WHEN** they enter a new password
- **THEN** the system validates: minimum 8 characters, uppercase, lowercase, number, special character
- **AND** password is hashed with bcrypt (cost factor 12)
- **AND** plaintext password is never stored

#### Scenario: Password reset request
- **GIVEN** a user forgot their password
- **WHEN** they click "Forgot Password" and enter email
- **THEN** a secure reset token is generated (expires in 1 hour)
- **AND** reset link is emailed via SendGrid
- **AND** rate limiting prevents abuse (max 3 requests/hour)

#### Scenario: Password reset completion
- **GIVEN** a user clicks the reset link
- **WHEN** they enter a new password
- **THEN** the system validates the reset token
- **AND** new password meets requirements
- **AND** all existing sessions are terminated (security measure)
- **AND** confirmation email is sent

## ADDED Requirements

### Requirement: API Authentication Middleware

The system SHALL validate JWT tokens on all protected API endpoints.

#### Scenario: Authenticated API request
- **GIVEN** a client includes a valid access token in Authorization header
- **WHEN** they make an API request
- **THEN** the token signature is validated
- **AND** token expiration is checked
- **AND** user context is extracted and attached to request
- **AND** request proceeds to handler

#### Scenario: Missing or invalid token
- **GIVEN** a client makes a request without a token or with invalid token
- **WHEN** the API middleware processes the request
- **THEN** the request is rejected with 401 Unauthorized
- **AND** response includes WWW-Authenticate header
- **AND** error indicates "Authentication required" or "Invalid token"

### Requirement: Rate Limiting

The system SHALL implement rate limiting to prevent brute force attacks.

#### Scenario: Rate limit enforcement
- **GIVEN** a user or IP address makes repeated login attempts
- **WHEN** they exceed 5 attempts in a 15-minute window
- **THEN** subsequent attempts are rejected with 429 Too Many Requests
- **AND** error message indicates "Too many login attempts. Please try again later."
- **AND** rate limit resets after 15 minutes

#### Scenario: Rate limit tracking
- **GIVEN** login attempts are tracked per IP address
- **WHEN** an attempt is made
- **THEN** the counter is stored in Redis with 15-minute TTL
- **AND** counter is incremented on each attempt
- **AND** successful login resets the counter
