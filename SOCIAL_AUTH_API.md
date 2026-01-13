# 📚 API Documentation - Social Authentication

## New Endpoints Added

### Google Sign-In
```
POST /api/v1/auth/google
```

### Apple Sign-In
```
POST /api/v1/auth/apple
```

---

## Google Sign-In API

### Endpoint
```
POST http://your-server:5000/api/v1/auth/google
```

### Request Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjFiZjk...",
  "access_token": "ya29.a0AfH6SMBx..." // Optional
}
```

### Success Response (New User)
**Status Code:** `201 Created`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 15,
      "name": "John Doe",
      "email": "john@gmail.com",
      "wallet_balance": 500000.0,
      "rewards_balance": 0.0,
      "is_admin": false,
      "phone": null,
      "total_invested": 0,
      "monthly_expected_income": 0
    }
  },
  "message": "تم إنشاء الحساب بنجاح"
}
```

### Success Response (Existing User)
**Status Code:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": { /* user object */ }
  },
  "message": "تم تسجيل الدخول بنجاح"
}
```

### Success Response (Account Linked)
**Status Code:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": { /* user object */ }
  },
  "message": "تم ربط الحساب بنجاح"
}
```

### Error Responses

#### Missing Token
**Status Code:** `400 Bad Request`
```json
{
  "success": false,
  "error": {
    "code": "MISSING_FIELDS",
    "message": "id_token مطلوب"
  }
}
```

#### Invalid Token
**Status Code:** `401 Unauthorized`
```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "رمز Google غير صالح"
  }
}
```

#### Server Error
**Status Code:** `500 Internal Server Error`
```json
{
  "success": false,
  "error": {
    "code": "GOOGLE_AUTH_ERROR",
    "message": "حدث خطأ أثناء تسجيل الدخول عبر Google",
    "details": "Error details here"
  }
}
```

---

## Apple Sign-In API

### Endpoint
```
POST http://your-server:5000/api/v1/auth/apple
```

### Request Headers
```
Content-Type: application/json
```

### Request Body (First Sign-In)
```json
{
  "identity_token": "eyJraWQiOiJlWGF1bm1MIiwiYWxnIjoi...",
  "authorization_code": "c1a2b3c4d5e6f7g8h9i0...",
  "user_identifier": "001234.5678abcd.1234",
  "email": "john@privaterelay.appleid.com",
  "given_name": "John",
  "family_name": "Doe"
}
```

### Request Body (Subsequent Sign-Ins)
```json
{
  "identity_token": "eyJraWQiOiJlWGF1bm1MIiwiYWxnIjoi...",
  "user_identifier": "001234.5678abcd.1234"
}
```

> **Note**: Apple only provides email, given_name, and family_name on the FIRST sign-in. After that, only identity_token and user_identifier are available.

### Success Response
Same format as Google Sign-In endpoint.

### Error Responses

#### Missing Token
**Status Code:** `400 Bad Request`
```json
{
  "success": false,
  "error": {
    "code": "MISSING_FIELDS",
    "message": "identity_token مطلوب"
  }
}
```

#### Invalid Token
**Status Code:** `401 Unauthorized`
```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "رمز Apple غير صالح"
  }
}
```

#### User Not Found (Edge Case)
**Status Code:** `404 Not Found`
```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "لا يمكن العثور على الحساب. يرجى المحاولة مرة أخرى"
  }
}
```

---

## Account Linking Logic

### Scenario 1: New Social User
- User signs in with Google/Apple for the first time
- Email doesn't exist in database
- **Action**: Create new user account with `auth_provider='google'` or `'apple'`
- **Response**: 201 Created with message "تم إنشاء الحساب بنجاح"

### Scenario 2: Existing Email User
- User has account with email/password (auth_provider='email')
- User signs in with Google/Apple using same email
- **Action**: Link social account to existing user (update auth_provider and provider_user_id)
- **Response**: 200 OK with message "تم ربط الحساب بنجاح"

### Scenario 3: Returning Social User
- User previously signed in with Google/Apple
- **Action**: Login with existing account
- **Response**: 200 OK with message "تم تسجيل الدخول بنجاح"

---

## Testing Examples

### Using cURL

#### Test Google Endpoint
```bash
curl -X POST http://localhost:5000/api/v1/auth/google \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "YOUR_GOOGLE_ID_TOKEN_HERE"
  }'
```

#### Test Apple Endpoint
```bash
curl -X POST http://localhost:5000/api/v1/auth/apple \
  -H "Content-Type: application/json" \
  -d '{
    "identity_token": "YOUR_APPLE_IDENTITY_TOKEN_HERE",
    "user_identifier": "001234.5678abcd.1234",
    "email": "test@privaterelay.appleid.com",
    "given_name": "Test",
    "family_name": "User"
  }'
```

### Using Postman

1. Set method to `POST`
2. URL: `http://localhost:5000/api/v1/auth/google` (or apple)
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "id_token": "paste_real_token_from_mobile_app_here"
}
```
5. Click Send
6. Check response for access_token and user data

---

## Complete API Endpoints List

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/v1/auth/register` | POST | No | Register with email/password |
| `/api/v1/auth/login` | POST | No | Login with email/password |
| **`/api/v1/auth/google`** | **POST** | **No** | **Sign in with Google** |
| **`/api/v1/auth/apple`** | **POST** | **No** | **Sign in with Apple** |
| `/api/v1/auth/refresh` | POST | Yes (Refresh Token) | Refresh access token |
| `/api/v1/auth/me` | GET | Yes | Get current user info |
| `/api/v1/apartments` | GET | No | List all apartments |
| `/api/v1/apartments/:id` | GET | No | Get apartment details |
| `/api/v1/shares/purchase` | POST | Yes | Purchase apartment shares |
| `/api/v1/shares/my-investments` | GET | Yes | Get user's investments |
| `/api/v1/wallet/balance` | GET | Yes | Get wallet balance |
| `/api/v1/wallet/deposit` | POST | Yes | Deposit to wallet |
| `/api/v1/wallet/withdraw` | POST | Yes | Withdraw from wallet |
| `/api/v1/wallet/transactions` | GET | Yes | Get transaction history |
| `/api/v1/user/dashboard` | GET | Yes | Get dashboard data |
| `/api/v1/user/profile` | PUT | Yes | Update user profile |

---

## Error Codes Reference

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `MISSING_FIELDS` | 400 | Required fields missing from request |
| `INVALID_TOKEN` | 401 | Token verification failed |
| `EXPIRED_TOKEN` | 401 | Token has expired |
| `EMAIL_EXISTS` | 409 | Email already registered |
| `USER_NOT_FOUND` | 404 | User doesn't exist |
| `GOOGLE_AUTH_ERROR` | 500 | Google authentication error |
| `APPLE_AUTH_ERROR` | 500 | Apple authentication error |
| `SERVER_ERROR` | 500 | Internal server error |

---

## Using JWT Tokens

After successful authentication, you receive:
- **access_token**: Use for API requests (expires in 7 days)
- **refresh_token**: Use to get new access token (expires in 30 days)

### Making Authenticated Requests

```bash
curl -X GET http://localhost:5000/api/v1/user/dashboard \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Refreshing Access Token

```bash
curl -X POST http://localhost:5000/api/v1/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN_HERE"
```

---

## Notes

- All responses are in JSON format
- All success responses have `success: true`
- All error responses have `success: false`
- Token verification happens server-side for security
- Email addresses from Apple may be private relay addresses
- Account linking is automatic when emails match
