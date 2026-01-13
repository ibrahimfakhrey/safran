"""
Social Authentication Providers
Token verification utilities for Google and Apple Sign-In
"""
import json
import jwt
import requests
from datetime import datetime, timedelta
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from flask import current_app
from functools import lru_cache


# ==================== Google Sign-In ====================

def verify_google_token(token_string):
    """
    Verify Google ID token and extract user information
    Supports both iOS and Android client IDs
    
    Args:
        token_string (str): Google ID token from client
    
    Returns:
        dict: User info with keys: user_id, email, name, verified_email
        None: If verification fails
    """
    try:
        # Get all possible client IDs (iOS, Android, and default)
        client_ids = [
            current_app.config.get('GOOGLE_CLIENT_ID'),
            current_app.config.get('GOOGLE_CLIENT_ID_IOS'),
            current_app.config.get('GOOGLE_CLIENT_ID_ANDROID')
        ]
        # Remove None values and duplicates
        client_ids = list(set(filter(None, client_ids)))
        
        if not client_ids:
            print("⚠️  Google Client ID not configured")
            return None
        
        # Try to verify with each client ID
        idinfo = None
        for client_id in client_ids:
            try:
                # Verify the token with Google
                idinfo = id_token.verify_oauth2_token(
                    token_string, 
                    google_requests.Request(), 
                    client_id
                )
                print(f"✅ Google token verified with client ID: {client_id[:30]}...")
                break  # Successfully verified
            except ValueError:
                # Try next client ID
                continue
        
        if not idinfo:
            print(f"❌ Token verification failed with all client IDs")
            return None
        
        # Verify the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            print(f"⚠️  Invalid issuer: {idinfo['iss']}")
            return None
        
        # Token is valid, return user info
        return {
            'user_id': idinfo['sub'],  # Google user ID (unique)
            'email': idinfo.get('email', ''),
            'name': idinfo.get('name', ''),
            'verified_email': idinfo.get('email_verified', False)
        }
        
    except ValueError as e:
        # Invalid token
        print(f"❌ Google token verification failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error verifying Google token: {e}")
        return None


# ==================== Apple Sign-In ====================

@lru_cache(maxsize=1)
def get_apple_public_keys():
    """
    Fetch Apple's public keys for token verification
    Cached to avoid repeated API calls
    
    Returns:
        list: Apple's public keys
    """
    try:
        response = requests.get('https://appleid.apple.com/auth/keys', timeout=10)
        response.raise_for_status()
        return response.json()['keys']
    except Exception as e:
        print(f"❌ Failed to fetch Apple public keys: {e}")
        return []


def verify_apple_token(token_string):
    """
    Verify Apple identity token and extract user information
    
    Args:
        token_string (str): Apple identity token from client
    
    Returns:
        dict: User info with keys: user_id, email
        None: If verification fails
    """
    try:
        client_id = current_app.config.get('APPLE_CLIENT_ID')
        
        if not client_id:
            print("❌ VERIFY_APPLE_TOKEN: Apple Client ID not configured in config.py")
            return None
        
        print(f"✅ VERIFY_APPLE_TOKEN: Using APPLE_CLIENT_ID = {client_id}")
        
        # Get Apple's public keys
        keys = get_apple_public_keys()
        if not keys:
            print("❌ VERIFY_APPLE_TOKEN: Could not retrieve Apple public keys from https://appleid.apple.com/auth/keys")
            return None
        
        print(f"✅ VERIFY_APPLE_TOKEN: Retrieved {len(keys)} public keys from Apple")
        
        # Decode the header to get the key ID
        header = jwt.get_unverified_header(token_string)
        kid = header.get('kid')
        
        if not kid:
            print("❌ VERIFY_APPLE_TOKEN: Token missing 'kid' in header")
            return None
        
        print(f"✅ VERIFY_APPLE_TOKEN: Token has kid = {kid}")
        
        # Find the matching public key
        key = next((k for k in keys if k['kid'] == kid), None)
        if not key:
            print(f"❌ VERIFY_APPLE_TOKEN: No matching key found for kid: {kid}")
            print(f"   Available kids: {[k['kid'] for k in keys]}")
            return None
        
        print(f"✅ VERIFY_APPLE_TOKEN: Found matching public key")
        
        # Convert JWK to PEM format for PyJWT
        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(json.dumps(key))
        
        # Verify and decode the token
        print(f"🔐 VERIFY_APPLE_TOKEN: Attempting to verify token with audience={client_id}")
        decoded = jwt.decode(
            token_string,
            public_key,
            algorithms=['RS256'],
            audience=client_id,
            issuer='https://appleid.apple.com'
        )
        
        print(f"✅ VERIFY_APPLE_TOKEN: Token verified successfully!")
        print(f"   User ID: {decoded['sub']}")
        print(f"   Email: {decoded.get('email', 'Not provided')}")
        
        # Check expiration
        exp = decoded.get('exp')
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            print("❌ VERIFY_APPLE_TOKEN: Apple token has expired")
            return None
        
        # Return user info
        return {
            'user_id': decoded['sub'],  # Apple user identifier (unique)
            'email': decoded.get('email', ''),  # May be private relay email
        }
        
    except jwt.ExpiredSignatureError:
        print("❌ VERIFY_APPLE_TOKEN: Apple token has expired (ExpiredSignatureError)")
        return None
    except jwt.InvalidTokenError as e:
        print(f"❌ VERIFY_APPLE_TOKEN: Invalid Apple token - {type(e).__name__}: {e}")
        return None
    except Exception as e:
        print(f"❌ VERIFY_APPLE_TOKEN: Unexpected error - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


# ==================== Helper Functions ====================

def clear_apple_keys_cache():
    """Clear the cached Apple public keys (useful for testing)"""
    get_apple_public_keys.cache_clear()
    print("✅ Apple keys cache cleared")


def validate_social_auth_config():
    """
    Validate that social authentication configuration is set up correctly
    
    Returns:
        dict: Configuration status for each provider
    """
    google_configured = bool(current_app.config.get('GOOGLE_CLIENT_ID'))
    apple_configured = bool(
        current_app.config.get('APPLE_CLIENT_ID') and
        current_app.config.get('APPLE_TEAM_ID') and
        current_app.config.get('APPLE_KEY_ID')
    )
    
    return {
        'google': {
            'configured': google_configured,
            'client_id': current_app.config.get('GOOGLE_CLIENT_ID', '')[:20] + '...' if google_configured else 'Not set'
        },
        'apple': {
            'configured': apple_configured,
            'client_id': current_app.config.get('APPLE_CLIENT_ID', 'Not set')
        }
    }
