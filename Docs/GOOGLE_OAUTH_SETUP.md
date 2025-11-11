# Google OAuth Implementation Guide

## Overview
This application now supports Google Sign-In/Register functionality using OAuth 2.0. Users can authenticate using their Google accounts as an alternative to traditional username/password authentication.

## Architecture

### Frontend (Angular)
- Uses `@abacritt/angularx-social-login` library
- Google Sign-In button on login and register pages
- Receives Google ID token and sends it to backend
- Location: `/Frontend/babelUI/src/app/components/Users/`

### Backend (Django)
- Uses `google-auth` library to verify Google tokens
- Two endpoints: `/api/users/google-login/` and `/api/users/google-register/`
- Verifies token authenticity with Google
- Creates or authenticates users
- Returns JWT tokens for session management

## API Endpoints

### `POST /api/users/google-login/`
Authenticates existing users via Google OAuth.

**Request Body:**
```json
{
  "token": "google-id-token-here"
}
```

**Success Response (200):**
```json
{
  "access": "jwt-access-token",
  "refresh": "jwt-refresh-token",
  "user": {
    "user_id": "uuid",
    "username": "username",
    "email": "user@example.com",
    "role": "role-uuid",
    "role_name": "Reader",
    "is_active": true,
    "is_staff": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Error Responses:**
- `400` - Missing or invalid token
- `404` - No account found with this email
- `403` - Account is disabled
- `401` - Invalid Google token

### `POST /api/users/google-register/`
Registers new users via Google OAuth.

**Request Body:**
```json
{
  "token": "google-id-token-here"
}
```

**Success Response (201):**
```json
{
  "access": "jwt-access-token",
  "refresh": "jwt-refresh-token",
  "user": {
    "user_id": "uuid",
    "username": "generated-username",
    "email": "user@example.com",
    "role": "role-uuid",
    "role_name": "Reader",
    "is_active": true,
    "is_staff": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Error Responses:**
- `400` - Missing or invalid token
- `409` - Account already exists (user should login instead)
- `401` - Invalid Google token

## Setup Instructions

### Prerequisites
1. Google Cloud Project with OAuth 2.0 credentials
2. Backend dependencies installed
3. Frontend dependencies installed

### Backend Setup

1. **Install required packages:**
   ```bash
   cd Backend
   source venv/bin/activate
   pip install google-auth google-auth-oauthlib
   ```

2. **Configure environment variables:**
   Add to `/Backend/babelLibrary/.env`:
   ```env
   GOOGLE_CLIENT_ID=your-client-id-here
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```

3. **Verify configuration:**
   ```bash
   cd Backend/babelLibrary
   python manage.py check
   ```

### Frontend Setup

1. **Install required packages:**
   ```bash
   cd Frontend/babelUI
   npm install @abacritt/angularx-social-login
   ```

2. **Update environment files:**
   Already configured in:
   - `/Frontend/babelUI/src/environments/environment.ts`
   - `/Frontend/babelUI/src/environments/environment.prod.ts`

3. **Verify setup:**
   ```bash
   ng serve
   ```

## User Flow

### Login Flow
1. User clicks "Sign in with Google" on login page
2. Google OAuth popup appears
3. User selects their Google account
4. Google returns ID token to frontend
5. Frontend sends token to `/api/users/google-login/`
6. Backend verifies token with Google
7. Backend finds existing user by email
8. Backend returns JWT tokens
9. User is logged in

### Register Flow
1. User clicks "Sign up with Google" on register page
2. Google OAuth popup appears
3. User selects their Google account
4. Google returns ID token to frontend
5. Frontend sends token to `/api/users/google-register/`
6. Backend verifies token with Google
7. Backend creates new user with:
   - Email from Google
   - Auto-generated unique username
   - Default "Reader" role
   - No password (OAuth only)
8. Backend returns JWT tokens
9. User is registered and logged in

## Security Considerations

### Token Verification
- All Google tokens are verified server-side using Google's official library
- Tokens are validated against your Google Client ID
- Expired or invalid tokens are rejected

### User Data
- Only email is required from Google
- Username is auto-generated if not provided
- No password is stored for OAuth users
- Users can still set a password later if desired

### Session Management
- JWT tokens are used for session management (same as regular login)
- Refresh tokens allow for extended sessions
- All standard JWT security applies

## Troubleshooting

### "Invalid Google token" Error
- Check that `GOOGLE_CLIENT_ID` in backend .env matches the one in frontend environment files
- Ensure Google OAuth consent screen is properly configured
- Verify authorized JavaScript origins include your frontend URL

### "No account found" on Login
- User needs to register first using Google Register
- Or register using traditional method with the same email

### "Account already exists" on Register
- User should use Google Login instead
- Account with this email already exists in the system

## Testing

### Local Testing
1. Start backend server: `python manage.py runserver`
2. Start frontend dev server: `ng serve`
3. Navigate to `http://localhost:4200/login`
4. Click "Sign in with Google"
5. Use a test Google account

### Manual API Testing
Using curl or Postman:

```bash
# Get a Google ID token first (from frontend or Google OAuth Playground)
# Then test the endpoint:

curl -X POST http://localhost:8000/api/users/google-register/ \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_GOOGLE_ID_TOKEN_HERE"}'
```

## Google Cloud Console Configuration

### Required Settings
1. **Authorized JavaScript origins:**
   - `http://localhost:4200` (development)
   - `https://yourdomain.com` (production)

2. **OAuth Consent Screen:**
   - App name: Babel
   - User support email
   - Developer contact email
   - Scopes: email, profile

3. **API Enablement:**
   - Google+ API (or Google Identity)

## Further Enhancements

Potential improvements:
- Allow users to link/unlink Google account to existing accounts
- Support multiple OAuth providers (GitHub, Facebook, etc.)
- Add profile picture from Google
- Sync user name from Google account
- Add "Login with Google" to profile page for linking accounts
