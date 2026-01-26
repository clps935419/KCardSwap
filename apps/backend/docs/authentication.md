# Authentication Flow Documentation

**Version**: 1.1  
**Phase**: Phase 3.1 - Google OAuth with PKCE Support  
**Last Updated**: 2025-12-17

## Overview

The KCardSwap authentication system uses Google OAuth 2.0 for user authentication and JSON Web Tokens (JWT) for session management. 

**Two OAuth flows are supported:**
1. **Authorization Code Flow with PKCE** (Recommended for Expo/Mobile apps)
2. **Implicit Flow with ID Token** (Legacy/Web support)

This document describes both authentication flows, token structure, and security considerations.

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐         ┌──────────────┐
│   Client    │         │     Kong     │         │   Backend   │         │    Google    │
│  (Mobile)   │         │   Gateway    │         │     API     │         │    OAuth     │
└──────┬──────┘         └──────┬───────┘         └──────┬──────┘         └──────┬───────┘
       │                       │                        │                       │
       │ 1. Get Google Token   │                        │                       │
       ├──────────────────────────────────────────────────────────────────────>│
       │                       │                        │                       │
       │<─────────────────────────────────────────────────────────────────────┤
       │                       │       Google ID Token   │                       │
       │                       │                        │                       │
       │ 2. Login with Google  │                        │                       │
       ├──────────────────────>│                        │                       │
       │   (Google ID Token)   │ 3. Forward Request     │                       │
       │                       ├───────────────────────>│                       │
       │                       │                        │ 4. Verify Google Token│
       │                       │                        ├──────────────────────>│
       │                       │                        │<──────────────────────┤
       │                       │                        │   Valid User Info     │
       │                       │                        │                       │
       │                       │                        │ 5. Create/Get User    │
       │                       │                        │    Generate JWT       │
       │                       │                        │                       │
       │                       │ 6. Return Tokens       │                       │
       │<──────────────────────┤<───────────────────────┤                       │
       │   Access + Refresh    │                        │                       │
```

## Authentication Flows

### Flow 1: Authorization Code Flow with PKCE (Recommended for Expo/Mobile)

This is the **recommended and most secure** flow for Expo AuthSession and mobile applications.

#### Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐         ┌──────────────┐
│   Client    │         │     Kong     │         │   Backend   │         │    Google    │
│ (Expo App)  │         │   Gateway    │         │     API     │         │    OAuth     │
└──────┬──────┘         └──────┬───────┘         └──────┬──────┘         └──────┬───────┘
       │                       │                        │                       │
       │ 1. Start Auth (PKCE)  │                        │                       │
       ├──────────────────────────────────────────────────────────────────────>│
       │   code_challenge      │                        │                       │
       │                       │                        │                       │
       │<─────────────────────────────────────────────────────────────────────┤
       │                       │   Authorization Code   │                       │
       │                       │                        │                       │
       │ 2. Send code + verifier│                       │                       │
       ├──────────────────────>│                        │                       │
       │                       │ 3. Forward Request     │                       │
       │                       ├───────────────────────>│                       │
       │                       │                        │ 4. Exchange Code      │
       │                       │                        │    + code_verifier    │
       │                       │                        ├──────────────────────>│
       │                       │                        │<──────────────────────┤
       │                       │                        │   ID Token            │
       │                       │                        │                       │
       │                       │                        │ 5. Verify ID Token    │
       │                       │                        │    Create/Get User    │
       │                       │                        │    Generate JWT       │
       │                       │                        │                       │
       │                       │ 6. Return Tokens       │                       │
       │<──────────────────────┤<───────────────────────┤                       │
       │   Access + Refresh    │                        │                       │
```

#### Step 1: Client Starts OAuth with PKCE (Client-Side)

Mobile app uses Expo AuthSession to start OAuth flow:
- Generates `code_verifier` (random 43-128 character string)
- Generates `code_challenge` from verifier
- Redirects user to Google with challenge

#### Step 2: Exchange Authorization Code for JWT

**Endpoint**: `POST /api/v1/auth/google-callback`

**Request**:
```json
{
  "code": "4/0AY0e-g7...",
  "code_verifier": "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk",
  "redirect_uri": "exp://192.168.1.1:19000" 
}
```

**Response** (Success - 200):
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com"
  },
  "error": null
}
```

**Response** (Error - 401):
```json
{
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid authorization code or code_verifier. Token exchange failed."
  }
}
```

#### Backend Processing:
1. Receive authorization code + code_verifier from client
2. Exchange code + verifier + client_secret with Google token endpoint
   - **Important**: Backend still uses client_secret when exchanging with Google
   - PKCE protects the mobile app (no secret stored there)
   - Backend-to-Google communication uses both PKCE and client_secret for maximum security
3. Receive ID token from Google
4. Verify ID token with Google's servers
5. Extract user information (google_id, email, name, picture)
6. Check if user exists in database by google_id
7. If new user:
   - Create User entity
   - Create default Profile entity
8. Generate JWT tokens:
   - Access Token (15 minutes expiry)
   - Refresh Token (7 days expiry)
9. Store refresh token in database
10. Return tokens to client

**Security Benefits:**
- No client secret required on mobile device (stored only on backend)
- Code verifier prevents authorization code interception
- Backend still uses client_secret for Google API communication
- More secure than implicit flow
- Recommended by OAuth 2.0 best practices

**PKCE + Client Secret:**
- Mobile app: Uses PKCE (code_verifier) - no secret exposure
- Backend: Uses both PKCE (code_verifier) AND client_secret
- This provides defense-in-depth security

---

### Flow 2: Admin Login with Email/Password

This flow is for **administrator authentication only** using email and password credentials.

#### Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Admin     │         │     Kong     │         │   Backend   │
│   Client    │         │   Gateway    │         │     API     │
└──────┬──────┘         └──────┬───────┘         └──────┬──────┘
       │                       │                        │
       │ 1. Admin Login        │                        │
       ├──────────────────────>│                        │
       │  (email + password)   │ 2. Forward Request     │
       │                       ├───────────────────────>│
       │                       │                        │
       │                       │                        │ 3. Verify Email
       │                       │                        │    Verify Password
       │                       │                        │    Check Admin Role
       │                       │                        │    Generate JWT
       │                       │                        │
       │                       │ 4. Return Tokens       │
       │<──────────────────────┤<───────────────────────┤
       │   Access + Refresh    │                        │
```

**Endpoint**: `POST /api/v1/auth/admin-login`

**Request**:
```json
{
  "email": "admin@example.com",
  "password": "SecurePassword123"
}
```

**Response** (Success - 200):
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "admin@example.com",
    "role": "admin"
  },
  "error": null
}
```

**Response** (Error - 401):
```json
{
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid credentials or not an admin"
  }
}
```

#### Backend Processing:
1. Get user by email from database
2. Verify user has password_hash (not a Google OAuth user)
3. Verify password using secure password hashing (bcrypt)
4. Check if user has admin role (`admin` or `super_admin`)
5. Generate JWT tokens:
   - Access Token (15 minutes expiry)
   - Refresh Token (7 days expiry)
6. Store refresh token in database
7. Return tokens with role information

#### Creating Admin Users

Admin users can be created using provided scripts:

**Method 1: Using init_admin.py (Idempotent)**
```bash
cd apps/backend
poetry run python scripts/init_admin.py --email admin@example.com --password SecurePass123
```

**Method 2: Using create_admin.py (Fail-fast)**
```bash
cd apps/backend
poetry run python scripts/create_admin.py --email admin@example.com --password SecurePass123 --role admin
```

**Method 3: Using Docker**
```bash
docker compose exec backend python scripts/init_admin.py --email admin@example.com --password SecurePass123
```

**Security Considerations:**
- Passwords are hashed using bcrypt before storage
- Minimum password length: 8 characters (recommended in scripts)
- Admin role verification ensures only authorized users can access admin endpoints
- Failed login attempts return generic error message to prevent user enumeration

---

### Flow 3: Implicit Flow with ID Token (Legacy/Web Support)

This flow is **maintained for backward compatibility** and web applications. For new mobile implementations, use Flow 1 (PKCE) instead.

#### Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐         ┌──────────────┐
│   Client    │         │     Kong     │         │   Backend   │         │    Google    │
│  (Mobile)   │         │   Gateway    │         │     API     │         │    OAuth     │
└──────┬──────┘         └──────┬───────┘         └──────┬──────┘         └──────┬───────┘
       │                       │                        │                       │
       │ 1. Get Google Token   │                        │                       │
       ├──────────────────────────────────────────────────────────────────────>│
       │                       │                        │                       │
       │<─────────────────────────────────────────────────────────────────────┤
       │                       │       Google ID Token   │                       │
       │                       │                        │                       │
       │ 2. Login with Google  │                        │                       │
       ├──────────────────────>│                        │                       │
       │   (Google ID Token)   │ 3. Forward Request     │                       │
       │                       ├───────────────────────>│                       │
       │                       │                        │ 4. Verify Google Token│
       │                       │                        ├──────────────────────>│
       │                       │                        │<──────────────────────┤
       │                       │                        │   Valid User Info     │
       │                       │                        │                       │
       │                       │                        │ 5. Create/Get User    │
       │                       │                        │    Generate JWT       │
       │                       │                        │                       │
       │                       │ 6. Return Tokens       │                       │
       │<──────────────────────┤<───────────────────────┤                       │
       │   Access + Refresh    │                        │                       │
```

#### Step 1: Client Gets Google ID Token
- User initiates login via Google OAuth
- Client app receives Google ID Token from Google
- This happens entirely client-side using Google Sign-In SDK

#### Step 2: Exchange Google Token for JWT
**Endpoint**: `POST /api/v1/auth/google-login`

**Request**:
```json
{
  "google_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```

**Response** (Success - 200):
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com"
  },
  "error": null
}
```

**Response** (Error - 401):
```json
{
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid Google token"
  }
}
```

#### Backend Processing:
1. Verify Google ID Token with Google's servers
2. Extract user information (google_id, email, name, picture)
3. Check if user exists in database by google_id
4. If new user:
   - Create User entity
   - Create default Profile entity
5. Generate JWT tokens:
   - Access Token (15 minutes expiry)
   - Refresh Token (7 days expiry)
6. Store refresh token in database
7. Return tokens to client

**Note:** This flow is less secure than PKCE as the ID token is exposed client-side. Use PKCE flow (Flow 1) for mobile apps.

---

### 2. Token Refresh

#### Purpose
- Access tokens expire after 15 minutes for security
- Refresh tokens allow getting new access tokens without re-authentication
- Refresh tokens are single-use (revoked after use)

**Endpoint**: `POST /api/v1/auth/refresh`

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (Success - 200):
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com"
  },
  "error": null
}
```

**Response** (Error - 401):
```json
{
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired refresh token"
  }
}
```

#### Backend Processing:
1. Verify JWT signature and expiration
2. Check if refresh token exists in database and is not revoked
3. Revoke old refresh token (mark as revoked=true)
4. Generate new access and refresh tokens
5. Store new refresh token in database
6. Return new tokens

### 3. Authenticated Requests

#### Using Access Token
All protected endpoints require Bearer authentication:

**Request Header**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example**: Get user profile
```
GET /api/v1/profile/me
Authorization: Bearer {access_token}
```

#### Backend Processing:
1. Extract token from Authorization header
2. Verify JWT signature
3. Check token expiration
4. Extract user_id from token payload
5. Process request with authenticated user context

## JWT Token Structure

### Access Token Payload
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",  // User ID
  "email": "user@example.com",
  "type": "access",
  "iat": 1700000000,  // Issued at (Unix timestamp)
  "exp": 1700000900   // Expires at (Unix timestamp)
}
```

### Refresh Token Payload
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",  // User ID
  "email": "user@example.com",
  "type": "refresh",
  "iat": 1700000000,  // Issued at (Unix timestamp)
  "exp": 1700604800   // Expires at (Unix timestamp, 7 days later)
}
```

### Token Characteristics
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret Key**: Configured via `JWT_SECRET_KEY` environment variable
- **Access Token Expiry**: 15 minutes (900 seconds)
- **Refresh Token Expiry**: 7 days (604800 seconds)
- **Token Type Verification**: Enforced in backend (access vs refresh)

## Security Considerations

### 1. Token Storage
**Client-Side**:
- Access Token: Can be stored in memory (most secure) or secure storage
- Refresh Token: MUST be stored in secure storage (Keychain/Keystore)
- Never store tokens in localStorage (web) due to XSS risks

### 2. Token Transmission
- Always use HTTPS in production
- Tokens transmitted via Authorization header (Bearer scheme)
- Kong Gateway can be configured to enforce HTTPS

### 3. Token Revocation
- Refresh tokens are single-use and revoked after refresh
- Future: Implement logout endpoint to revoke all user refresh tokens
- Future: Implement token blacklist for emergency revocation

### 4. Google Token Verification
- Backend verifies Google ID token with Google's servers
- Checks token issuer is Google (`accounts.google.com`)
- Validates token signature using Google's public keys
- Ensures token hasn't expired

### 5. Admin Password Security
- Passwords are hashed using bcrypt (adaptive hashing algorithm)
- Password verification uses constant-time comparison to prevent timing attacks
- Minimum password length of 8 characters recommended
- Failed login attempts return generic error messages to prevent user enumeration
- Admin users cannot use Google OAuth (must use email/password)

### 6. Rate Limiting
- Kong Gateway can enforce rate limits on auth endpoints
- Prevents brute force attacks
- Recommended: 10 login attempts per minute per IP

## Error Handling

### Common Error Responses

#### 400 - Validation Error
```json
{
  "data": null,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Invalid request format",
    "details": {
      "google_token": ["Field required"]
    }
  }
}
```

#### 401 - Unauthorized
```json
{
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

#### 403 - Forbidden
```json
{
  "data": null,
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions"
  }
}
```

#### 429 - Rate Limited
```json
{
  "data": null,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests, please try again later"
  }
}
```

## Environment Configuration

### Required Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-min-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=your-redirect-uri
```

### Production Best Practices
1. Use strong JWT secret (minimum 32 characters, random)
2. Rotate JWT secret periodically (requires re-authentication of all users)
3. Use environment-specific Google OAuth credentials
4. Enable SQL_ECHO=false in production
5. Configure Kong Gateway for additional security layer

## Testing Authentication

### Manual Testing with curl

#### 1. Admin Login with Email/Password
```bash
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "SecurePass123"}'
```

#### 2. Login with Google (requires valid Google ID token)
```bash
curl -X POST http://localhost:8000/api/v1/auth/google-login \
  -H "Content-Type: application/json" \
  -d '{"google_token": "YOUR_GOOGLE_ID_TOKEN"}'
```

#### 3. Refresh Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

#### 4. Authenticated Request (Get Profile)
```bash
curl -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Future Enhancements (Phase 4+)

1. **Logout Endpoint**: Revoke all user refresh tokens
2. **Token Blacklist**: Redis-based revocation list for emergency token invalidation
3. **Multi-Device Management**: Track and manage tokens per device
4. **Two-Factor Authentication**: Optional 2FA for enhanced security
5. **Biometric Authentication**: Integrate with device biometrics
6. **Session Management**: View and revoke active sessions

## References

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [Kong JWT Plugin](https://docs.konghq.com/hub/kong-inc/jwt/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
