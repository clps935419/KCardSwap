# Identity Module API Documentation

**Module**: Identity  
**Phase**: Phase 3.1 - Google OAuth with PKCE  
**Version**: 1.1  
**Last Updated**: 2025-12-17

## Overview

The Identity module provides authentication and user profile management functionality. It includes:
- Google OAuth 2.0 authentication with two flows:
  - **Authorization Code Flow with PKCE** (Recommended for Expo/Mobile)
  - **Implicit Flow with ID Token** (Legacy/Web support)
- JWT token management (access + refresh tokens)
- User profile CRUD operations
- Privacy settings management

## Base URL

```
http://localhost:8000/api/v1  (Development)
https://api.kcardswap.com/api/v1  (Production)
```

## Authentication

All endpoints except `/auth/*` require Bearer authentication:

```
Authorization: Bearer {access_token}
```

---

## Endpoints Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/auth/google-callback` | No | **[Recommended]** Login with Google OAuth (PKCE) |
| POST | `/auth/google-login` | No | Login with Google OAuth (ID Token) |
| POST | `/auth/refresh` | No | Refresh access token |
| GET | `/profile/me` | Yes | Get user profile |
| PUT | `/profile/me` | Yes | Update user profile |

---

## Authentication Endpoints

### POST /auth/google-callback (Recommended for Expo/Mobile)

Authenticate user with Google OAuth using Authorization Code Flow with PKCE. This is the **recommended and most secure** method for Expo AuthSession and mobile apps.

**Request Body**:
```json
{
  "code": "string",                    // Required: Authorization code from Google
  "code_verifier": "string",           // Required: PKCE code verifier (43-128 chars)
  "redirect_uri": "string | null"      // Optional: Redirect URI (must match auth request)
}
```

**Success Response (200)**:
```json
{
  "data": {
    "access_token": "string",      // JWT access token (15 min expiry)
    "refresh_token": "string",     // JWT refresh token (7 days expiry)
    "token_type": "bearer",
    "expires_in": 900,             // Access token expiry in seconds
    "user_id": "uuid",             // User's unique identifier
    "email": "string"              // User's email address
  },
  "error": null
}
```

**Error Responses**:
- **401 Unauthorized**: Invalid authorization code or code_verifier
- **422 Unprocessable Entity**: Token exchange with Google failed

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/google-callback \
  -H "Content-Type: application/json" \
  -d '{
    "code": "4/0AY0e-g7...",
    "code_verifier": "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk",
    "redirect_uri": "exp://192.168.1.1:19000"
  }'
```

**Flow Overview**:
1. Mobile app starts OAuth with PKCE (generates code_verifier + code_challenge)
2. User authenticates with Google and app receives authorization code
3. App sends code + code_verifier to this endpoint
4. Backend exchanges code with Google to get ID token
5. Backend verifies ID token and creates/retrieves user
6. Backend returns JWT tokens

---

### POST /auth/google-login (Legacy/Web Support)

Authenticate user with Google OAuth and receive JWT tokens.

**Request Body**:
```json
{
  "google_token": "string"  // Required: Google ID token from Google Sign-In
}
```

**Success Response (200)**:
```json
{
  "data": {
    "access_token": "string",      // JWT access token (15 min expiry)
    "refresh_token": "string",     // JWT refresh token (7 days expiry)
    "token_type": "bearer",
    "expires_in": 900,             // Access token expiry in seconds
    "user_id": "uuid",             // User's unique identifier
    "email": "string"              // User's email address
  },
  "error": null
}
```

**Error Responses**:
- **401 Unauthorized**: Invalid Google token

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/google-login \
  -H "Content-Type: application/json" \
  -d '{"google_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."}'
```

---

### POST /auth/refresh

Refresh access token using refresh token.

**Request Body**:
```json
{
  "refresh_token": "string"  // Required: Refresh token from login
}
```

**Success Response (200)**:
```json
{
  "data": {
    "access_token": "string",      // New JWT access token
    "refresh_token": "string",     // New JWT refresh token
    "token_type": "bearer",
    "expires_in": 900,
    "user_id": "uuid",
    "email": "string"
  },
  "error": null
}
```

**Error Responses**:
- **401 Unauthorized**: Invalid or expired refresh token

---

## Profile Endpoints

### GET /profile/me

Get the authenticated user's profile information.

**Authentication**: Required (Bearer token)

**Success Response (200)**:
```json
{
  "data": {
    "user_id": "uuid",
    "nickname": "string | null",
    "avatar_url": "string | null",
    "bio": "string | null",
    "region": "string | null",
    "preferences": {},
    "privacy_flags": {
      "nearby_visible": true,
      "show_online": true,
      "allow_stranger_chat": true
    },
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "error": null
}
```

**Error Responses**:
- **401 Unauthorized**: Invalid or expired token
- **404 Not Found**: Profile not found

---

### PUT /profile/me

Update the authenticated user's profile information.

**Authentication**: Required (Bearer token)

**Request Body** (all fields optional):
```json
{
  "nickname": "string | null",
  "avatar_url": "string | null",
  "bio": "string | null",
  "region": "string | null",
  "preferences": {},
  "privacy_flags": {
    "nearby_visible": boolean,
    "show_online": boolean,
    "allow_stranger_chat": boolean
  }
}
```

**Success Response (200)**:
Same as GET /profile/me

**Error Responses**:
- **400 Validation Error**: Invalid request format
- **401 Unauthorized**: Invalid or expired token

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

---

## Related Documentation

- [Authentication Flow](../authentication.md)
- [Database Architecture](../database-architecture.md)
