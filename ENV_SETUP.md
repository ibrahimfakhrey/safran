# 🔧 Environment Variables Setup

Create a `.env` file in your project root with these credentials.

## Required Environment Variables

```bash
# ==================== Flask Configuration ====================
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# ==================== Google OAuth ====================
# Get these from: https://console.cloud.google.com/
GOOGLE_CLIENT_ID=xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxx

# ==================== Apple Sign-In ====================
# Get these from: https://developer.apple.com/
APPLE_CLIENT_ID=com.ipi.realestate.signin
APPLE_TEAM_ID=XXXXXXXXXX
APPLE_KEY_ID=XXXXXXXXXX
APPLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...
...paste your full private key here...
-----END PRIVATE KEY-----"

# ==================== Database (Optional) ====================
DATABASE_URL=sqlite:///apartment_platform.db

# ==================== Admin Credentials ====================
ADMIN_EMAIL=admin@apartmentshare.com
ADMIN_PASSWORD=change-this-password
```

## How to Get Credentials

### Google OAuth
1. Visit https://console.cloud.google.com/
2. Create a new project or select existing
3. Go to "APIs & Services" → "Credentials"
4. Create "OAuth 2.0 Client ID" for Web application
5. Copy the Client ID and Client Secret

### Apple Sign-In
1. Visit https://developer.apple.com/
2. Go to "Certificates, Identifiers & Profiles"
3. Create App ID and Services ID
4. Create a Key for Sign In with Apple
5. Download the .p8 key file (you can only do this once!)
6. Note your Team ID, Key ID, and Services ID

## Loading Environment Variables

The application automatically loads `.env` using `python-dotenv`.

To manually load in Python:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Security Notes

- ✅ Add `.env` to `.gitignore` to prevent committing secrets
- ✅ Use different secrets for development and production
- ✅ Rotate keys periodically for security
- ✅ Never share your private keys publicly
- ✅ Use environment variables in production hosting platforms

## Production Hosting

### On PythonAnywhere / Heroku / Railway
Set environment variables in the platform's dashboard instead of using `.env` file.

### On Your Own Server
Use a secrets management system or securely stored `.env` file with proper permissions:
```bash
chmod 600 .env  # Only owner can read/write
```

## Validation

To check if your credentials are configured:
```bash
python3 -c "from app import create_app; from app.auth_providers import validate_social_auth_config; app = create_app(); app.app_context().push(); print(validate_social_auth_config())"
```

Expected output:
```json
{
  "google": {
    "configured": true,
    "client_id": "1234567890-abc123..."
  },
  "apple": {
    "configured": true,
    "client_id": "com.ipi.realestate.signin"
  }
}
```
