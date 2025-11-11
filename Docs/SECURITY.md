# Security Guidelines

## Environment Variables & Credentials

### Backend (Django)
All sensitive credentials are stored in `/Backend/babelLibrary/.env` and are **NOT** committed to version control.

**Required environment variables:**
- `SECRET_KEY` - Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - Database credentials
- `GEMINI_API_KEY` - Google Gemini API key
- `GOOGLE_CLIENT_ID` - Google OAuth Client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth Client Secret ⚠️ **NEVER EXPOSE THIS**

**Important:** The `.env` file is ignored by git. Use `.env.example` as a template.

### Frontend (Angular)
The frontend environment files (`/Frontend/babelUI/src/environments/`) contain only **public** configuration.

**Current public values:**
- `googleClientId` - Google OAuth Client ID (safe to be public, required for client-side OAuth)

**Note:** Google OAuth Client IDs are designed to be public and used in client-side applications. The Client Secret should NEVER be in the frontend code.

## Google OAuth Configuration

### What's Public vs. Private:
- ✅ **Public (Frontend):** `GOOGLE_CLIENT_ID` - This is meant to identify your app to Google
- ❌ **Private (Backend):** `GOOGLE_CLIENT_SECRET` - This authenticates your backend server to Google

### Security Flow:
1. Frontend initiates Google Sign-In with the public Client ID
2. Google returns an ID token to the frontend
3. Frontend sends the token to your backend
4. Backend verifies the token with Google using the Client Secret
5. Backend creates/authenticates the user and returns JWT tokens

## Best Practices

1. **Never commit `.env` files** - Always use `.env.example` as a template
2. **Rotate credentials regularly** - Especially if they may have been exposed
3. **Use environment-specific configs** - Different credentials for dev/staging/production
4. **Limit OAuth scopes** - Only request the Google permissions you actually need
5. **Monitor API usage** - Set up alerts for unusual activity

## If Credentials Are Compromised

1. **Immediately rotate** all exposed credentials
2. **Review access logs** for unauthorized activity
3. **Update credentials** in all environments
4. **Notify team members** if applicable

## Google OAuth Setup

To configure Google OAuth for your own instance:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure the consent screen
6. Add authorized JavaScript origins: `http://localhost:4200`, `https://yourdomain.com`
7. Add authorized redirect URIs if needed
8. Copy the Client ID (use in frontend) and Client Secret (use in backend .env)
9. Update both environment files with your credentials
