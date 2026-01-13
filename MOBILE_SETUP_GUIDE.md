# 📱 Mobile App Setup Guide - Social Authentication
## What YOU Need to Do Before Backend Works

This guide explains exactly what you need to do on the mobile app side (Flutter) to make Google and Apple Sign-In work.

---

## 🔴 STEP 1: Get Google OAuth Credentials

### 1.1 Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Create a new project OR select your existing IPI project
3. Project name: "IPI Real Estate" (or whatever you prefer)

### 1.2 Enable Google Sign-In API
1. Go to "APIs & Services" → "Library"
2. Search for "Google Sign-In API"
3. Click "Enable"

### 1.3 Create OAuth 2.0 Credentials

#### For Android App:
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Select "Android"
4. Package name: `com.ipi.realestate` (or your actual package name)
5. Get SHA-1 certificate fingerprint:
   ```bash
   # In your Flutter project directory:
   cd android
   ./gradlew signingReport
   # Copy the SHA-1 from the output
   ```
6. Paste SHA-1 fingerprint
7. Click "Create"
8. **SAVE THE CLIENT ID** - you'll need this for Flutter

#### For iOS App:
1. Click "Create Credentials" → "OAuth 2.0 Client ID" again
2. Select "iOS"
3. Bundle ID: `com.ipi.realestate` (or your actual bundle ID)
4. App Store ID: (leave empty for now if not published)
5. Click "Create"
6. **SAVE THE CLIENT ID** - you'll need this for Flutter

#### For Backend Server:
1. Click "Create Credentials" → "OAuth 2.0 Client ID" again
2. Select "Web application"
3. Name: "IPI Backend Server"
4. Authorized redirect URIs: (leave empty for token verification)
5. Click "Create"
6. **SAVE BOTH**:
   - **Client ID** - send this to me for backend
   - **Client Secret** - send this to me for backend

### 1.4 What to Send Me
After completing above:
```
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxx
```

---

## 🍎 STEP 2: Get Apple Sign-In Credentials

### 2.1 Apple Developer Account Required
- You MUST have an Apple Developer account ($99/year)
- Visit: https://developer.apple.com/

### 2.2 Register App ID
1. Go to "Certificates, Identifiers & Profiles"
2. Click "Identifiers" → "+" button
3. Select "App IDs" → Continue
4. Description: "IPI Real Estate"
5. Bundle ID: `com.ipi.realestate` (must match your iOS app)
6. Scroll down and CHECK "Sign In with Apple"
7. Click "Continue" → "Register"

### 2.3 Create Services ID (for backend communication)
1. Click "Identifiers" → "+" button
2. Select "Services IDs" → Continue
3. Description: "IPI Sign In Service"
4. Identifier: `com.ipi.realestate.signin` (different from app bundle ID)
5. CHECK "Sign In with Apple"
6. Click "Configure" next to Sign In with Apple
7. Primary App ID: Select your app ID from step 2.2
8. Web Domain: Your backend domain (e.g., `api.ipi-realestate.com`)
   - If testing locally, you can use: `localhost`
9. Return URLs: `https://your-domain.com/api/v1/auth/apple/callback`
   - For local testing: `http://localhost:5000/api/v1/auth/apple/callback`
10. Click "Save" → "Continue" → "Register"

### 2.4 Create Key for Server Communication
1. Go to "Keys" → "+" button
2. Key Name: "IPI Sign In Key"
3. CHECK "Sign In with Apple"
4. Click "Configure" next to Sign In with Apple
5. Primary App ID: Select your app ID
6. Click "Save" → "Continue" → "Register"
7. **DOWNLOAD THE KEY FILE** (.p8 file) - you can only download ONCE!
8. Note the Key ID shown (e.g., ABC123XYZ)

### 2.5 Find Your Team ID
1. Go to "Membership" in Apple Developer portal
2. Find "Team ID" (e.g., X7HF123ABC)
3. Copy it

### 2.6 What to Send Me
After completing above:
```
APPLE_CLIENT_ID=com.ipi.realestate.signin
APPLE_TEAM_ID=X7HF123ABC
APPLE_KEY_ID=ABC123XYZ
APPLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
[paste entire content of .p8 file here]
-----END PRIVATE KEY-----
```

---

## 📲 STEP 3: Update Your Flutter App

### 3.1 Add Dependencies to pubspec.yaml
```yaml
dependencies:
  google_sign_in: ^6.1.5
  sign_in_with_apple: ^5.0.0
  http: ^1.1.0  # For API calls
```

Run:
```bash
flutter pub get
```

### 3.2 Android Configuration

Edit `android/app/build.gradle`:
```gradle
android {
    defaultConfig {
        minSdkVersion 21  // Google Sign-In requires minimum 21
    }
}
```

### 3.3 iOS Configuration

Edit `ios/Runner/Info.plist`, add:
```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleTypeRole</key>
        <string>Editor</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <!-- Replace with your REVERSED Client ID -->
            <string>com.googleusercontent.apps.YOUR-CLIENT-ID</string>
        </array>
    </dict>
</array>
```

Add Apple Sign-In capability:
1. Open `ios/Runner.xcworkspace` in Xcode
2. Select "Runner" target
3. Go to "Signing & Capabilities"
4. Click "+ Capability"
5. Add "Sign In with Apple"

### 3.4 Flutter Code Example

#### Google Sign-In Button:
```dart
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> signInWithGoogle() async {
  try {
    final GoogleSignIn googleSignIn = GoogleSignIn(
      scopes: ['email', 'profile'],
    );
    
    final GoogleSignInAccount? account = await googleSignIn.signIn();
    if (account == null) return; // User cancelled
    
    final GoogleSignInAuthentication auth = await account.authentication;
    
    // Send to YOUR backend
    final response = await http.post(
      Uri.parse('http://your-server-ip:5000/api/v1/auth/google'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'id_token': auth.idToken,
        'access_token': auth.accessToken,
      }),
    );
    
    final data = jsonDecode(response.body);
    
    if (data['success']) {
      // Save tokens
      String accessToken = data['data']['access_token'];
      String refreshToken = data['data']['refresh_token'];
      
      // Store in secure storage and navigate to home
      print('Login successful: ${data['data']['user']}');
    } else {
      print('Error: ${data['error']['message']}');
    }
  } catch (e) {
    print('Google Sign-In Error: $e');
  }
}
```

#### Apple Sign-In Button:
```dart
import 'package:sign_in_with_apple/sign_in_with_apple.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> signInWithApple() async {
  try {
    final credential = await SignInWithApple.getAppleIDCredential(
      scopes: [
        AppleIDAuthorizationScopes.email,
        AppleIDAuthorizationScopes.fullName,
      ],
    );
    
    // Send to YOUR backend
    final response = await http.post(
      Uri.parse('http://your-server-ip:5000/api/v1/auth/apple'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'identity_token': credential.identityToken,
        'authorization_code': credential.authorizationCode,
        'user_identifier': credential.userIdentifier,
        'email': credential.email,  // May be null after first sign-in
        'given_name': credential.givenName,  // May be null
        'family_name': credential.familyName,  // May be null
      }),
    );
    
    final data = jsonDecode(response.body);
    
    if (data['success']) {
      String accessToken = data['data']['access_token'];
      String refreshToken = data['data']['refresh_token'];
      
      print('Login successful: ${data['data']['user']}');
    } else {
      print('Error: ${data['error']['message']}');
    }
  } catch (e) {
    print('Apple Sign-In Error: $e');
  }
}
```

---

## 🔧 STEP 4: Testing Setup

### Local Testing with Your Phone

#### Option 1: Use ngrok (Easiest)
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 5000

# ngrok will give you a URL like: https://abc123.ngrok.io
# Use this in your Flutter app instead of localhost
```

Replace in Flutter:
```dart
Uri.parse('https://abc123.ngrok.io/api/v1/auth/google')
```

#### Option 2: Use Local Network IP
```bash
# Find your computer's IP on local network
# macOS:
ifconfig | grep "inet "

# Use something like: http://192.168.1.100:5000
```

Replace in Flutter:
```dart
Uri.parse('http://192.168.1.100:5000/api/v1/auth/google')
```

---

## ✅ Checklist - What to Send Me

Once you complete the above steps, send me:

```bash
# Google Credentials
GOOGLE_CLIENT_ID=xxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxxxxxxxxxx

# Apple Credentials
APPLE_CLIENT_ID=com.ipi.realestate.signin
APPLE_TEAM_ID=XXXXXXXXXX
APPLE_KEY_ID=XXXXXXXXXX
APPLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...
...rest of the key...
-----END PRIVATE KEY-----"
```

---

## 🚀 After You Send Me Credentials

1. I will add them to the backend configuration
2. I will finish implementing the endpoints
3. You can test the integration from your Flutter app
4. We'll debug together if needed

---

## ❓ Common Issues & Solutions

### Google Sign-In Not Working
- **Problem**: "Developer Error" or "Sign-In Failed"
- **Solution**: 
  - Make sure SHA-1 is correct (run `./gradlew signingReport` again)
  - Check package name matches exactly
  - Wait 5-10 minutes after creating credentials

### Apple Sign-In Not Working
- **Problem**: "Invalid Client" error
- **Solution**:
  - Verify Bundle ID matches exactly
  - Check Services ID is configured correctly
  - Make sure Sign In with Apple is enabled in Xcode

### Backend Returns 401 Error
- **Problem**: "Invalid Token" error
- **Solution**:
  - Token might be expired (tokens expire quickly)
  - Make sure you're sending both `id_token` and `access_token`
  - Check network request is reaching backend

---

## 📞 Need Help?

If you get stuck on any step, let me know which step and what error you're seeing!

**Most Important**: Send me the credentials once you have them, and I'll complete the backend implementation.
