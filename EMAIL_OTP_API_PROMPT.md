# Email OTP Verification API - Flutter Integration Guide

## Overview

This document provides complete API specifications for implementing email OTP verification during user registration. The system sends a beautiful premium HTML email in Arabic with a 6-digit OTP code.

---

## Base URL

```
http://127.0.0.1:5000/api/v1
```

For production, replace with your production server URL.

---

## Registration Flow

The new registration process has 3 steps:

1. **Send OTP** → User enters registration details, system sends OTP to email
2. **Verify OTP** → User enters OTP code, account is created
3. **Login** → User is automatically logged in after verification

---

## API Endpoints

### 1. Send OTP for Registration

Initiates registration by sending a 6-digit OTP to the user's email.

**Endpoint:** `POST /auth/send-otp`

**Content-Type:** `application/json`

#### Request Body

```json
{
    "name": "أحمد محمد علي",
    "email": "ahmed@example.com",
    "password": "SecurePass123!",
    "phone": "+201234567890"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | User's full name (Arabic/English) |
| `email` | string | Yes | Valid email address |
| `password` | string | Yes | Password (min 6 characters recommended) |
| `phone` | string | No | Phone number with country code |

#### Success Response (200 OK)

```json
{
    "success": true,
    "message": "تم إرسال رمز التحقق إلى بريدك الإلكتروني",
    "data": {
        "email": "ahmed@example.com",
        "expires_in_minutes": 10
    }
}
```

#### Error Responses

**Missing Fields (400)**
```json
{
    "success": false,
    "error": {
        "code": "MISSING_FIELDS",
        "message": "البريد الإلكتروني والاسم وكلمة المرور مطلوبة"
    }
}
```

**Email Already Exists (409)**
```json
{
    "success": false,
    "error": {
        "code": "EMAIL_EXISTS",
        "message": "البريد الإلكتروني مستخدم بالفعل"
    }
}
```

**Email Send Failed (500)**
```json
{
    "success": false,
    "error": {
        "code": "EMAIL_SEND_FAILED",
        "message": "فشل إرسال رمز التحقق. يرجى المحاولة مرة أخرى"
    }
}
```

---

### 2. Verify OTP and Complete Registration

Verifies the OTP code and creates the user account.

**Endpoint:** `POST /auth/verify-otp`

**Content-Type:** `application/json`

#### Request Body

```json
{
    "email": "ahmed@example.com",
    "otp": "123456"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | The email address used in send-otp |
| `otp` | string | Yes | 6-digit OTP code from email |

#### Success Response (201 Created)

```json
{
    "success": true,
    "message": "تم تفعيل حسابك بنجاح! مرحباً بك في i pillars i",
    "data": {
        "user": {
            "id": 1,
            "name": "أحمد محمد علي",
            "email": "ahmed@example.com",
            "wallet_balance": 0.0,
            "rewards_balance": 0.0,
            "is_admin": false,
            "date_joined": "2025-12-11T12:00:00",
            "phone": "+201234567890",
            "total_invested": 0.0,
            "monthly_expected_income": 0.0
        },
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

#### Error Responses

**Missing Fields (400)**
```json
{
    "success": false,
    "error": {
        "code": "MISSING_FIELDS",
        "message": "البريد الإلكتروني ورمز التحقق مطلوبان"
    }
}
```

**OTP Not Found (404)**
```json
{
    "success": false,
    "error": {
        "code": "OTP_NOT_FOUND",
        "message": "لم يتم العثور على رمز تحقق لهذا البريد الإلكتروني"
    }
}
```

**OTP Expired (400)**
```json
{
    "success": false,
    "error": {
        "code": "OTP_EXPIRED",
        "message": "رمز التحقق منتهي الصلاحية أو تم استخدامه. يرجى طلب رمز جديد"
    }
}
```

**Invalid OTP (400)**
```json
{
    "success": false,
    "error": {
        "code": "INVALID_OTP",
        "message": "رمز التحقق غير صحيح. المحاولات المتبقية: 4"
    }
}
```

**Too Many Attempts (400)**
```json
{
    "success": false,
    "error": {
        "code": "TOO_MANY_ATTEMPTS",
        "message": "تم تجاوز عدد المحاولات المسموحة. يرجى طلب رمز جديد"
    }
}
```

---

### 3. Resend OTP

Resends a new OTP code to the email address.

**Endpoint:** `POST /auth/resend-otp`

**Content-Type:** `application/json`

#### Request Body

```json
{
    "email": "ahmed@example.com"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | The email address used in send-otp |

#### Success Response (200 OK)

```json
{
    "success": true,
    "message": "تم إعادة إرسال رمز التحقق بنجاح",
    "data": {
        "email": "ahmed@example.com",
        "expires_in_minutes": 10
    }
}
```

#### Error Responses

**No Pending Registration (404)**
```json
{
    "success": false,
    "error": {
        "code": "NO_PENDING_REGISTRATION",
        "message": "لم يتم العثور على طلب تسجيل لهذا البريد الإلكتروني"
    }
}
```

---

## Email Template Preview

The OTP email features:
- **Premium Design**: Gradient gold header with navy blue accents
- **Arabic Direction**: Full RTL support
- **Responsive**: Mobile-friendly design
- **Brand Colors**: Gold (#D4AF37) and Navy (#0A1128)
- **Security Warning**: Explains not to share OTP
- **Features Showcase**: Highlights platform benefits
- **Professional Footer**: Social links, support contact, copyright

### Email Content Structure

```
┌─────────────────────────────────────┐
│  🏆 i pillars i                     │
│  منصة الاستثمار العقاري الذكية      │
├─────────────────────────────────────┤
│                                     │
│  مرحباً أحمد! 👋                    │
│                                     │
│  رمز التحقق الخاص بك:               │
│  ┌──────────┐                       │
│  │ 123456 │                       │
│  └──────────┘                       │
│  ⏱ صالح لمدة 10 دقائق              │
│                                     │
│  🔒 تنبيه أمني                      │
│  لا تشارك هذا الرمز مع أي شخص       │
│                                     │
│  Features:                          │
│  🏢 استثمر في العقارات              │
│  💰 عوائد شهرية مضمونة              │
│  📱 تابع استثماراتك                │
│                                     │
└─────────────────────────────────────┘
```

---

## OTP Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| OTP Length | 6 digits | Numeric only (000000-999999) |
| Expiry Time | 10 minutes | After this, OTP is invalid |
| Max Attempts | 5 | After 5 wrong attempts, must request new OTP |
| Cooldown | None | Can resend immediately |

---

## Flutter Implementation Example

### 1. Model Classes

```dart
class OtpResponse {
  final String email;
  final int expiresInMinutes;

  OtpResponse({
    required this.email,
    required this.expiresInMinutes,
  });

  factory OtpResponse.fromJson(Map<String, dynamic> json) {
    return OtpResponse(
      email: json['email'],
      expiresInMinutes: json['expires_in_minutes'],
    );
  }
}

class VerificationResponse {
  final User user;
  final String accessToken;
  final String refreshToken;

  VerificationResponse({
    required this.user,
    required this.accessToken,
    required this.refreshToken,
  });

  factory VerificationResponse.fromJson(Map<String, dynamic> json) {
    return VerificationResponse(
      user: User.fromJson(json['user']),
      accessToken: json['access_token'],
      refreshToken: json['refresh_token'],
    );
  }
}
```

### 2. API Service

```dart
import 'package:dio/dio.dart';

class AuthService {
  final Dio _dio;
  final String baseUrl = 'http://127.0.0.1:5000/api/v1';

  AuthService(this._dio);

  Future<OtpResponse> sendOtp({
    required String name,
    required String email,
    required String password,
    String? phone,
  }) async {
    try {
      final response = await _dio.post(
        '$baseUrl/auth/send-otp',
        data: {
          'name': name,
          'email': email,
          'password': password,
          if (phone != null) 'phone': phone,
        },
      );

      if (response.data['success']) {
        return OtpResponse.fromJson(response.data['data']);
      }
      throw response.data['error']['message'];
    } on DioException catch (e) {
      throw e.response?.data?['error']?['message'] ?? 'حدث خطأ في الاتصال';
    }
  }

  Future<VerificationResponse> verifyOtp({
    required String email,
    required String otp,
  }) async {
    try {
      final response = await _dio.post(
        '$baseUrl/auth/verify-otp',
        data: {
          'email': email,
          'otp': otp,
        },
      );

      if (response.data['success']) {
        return VerificationResponse.fromJson(response.data['data']);
      }
      throw response.data['error']['message'];
    } on DioException catch (e) {
      throw e.response?.data?['error']?['message'] ?? 'حدث خطأ في الاتصال';
    }
  }

  Future<OtpResponse> resendOtp({required String email}) async {
    try {
      final response = await _dio.post(
        '$baseUrl/auth/resend-otp',
        data: {'email': email},
      );

      if (response.data['success']) {
        return OtpResponse.fromJson(response.data['data']);
      }
      throw response.data['error']['message'];
    } on DioException catch (e) {
      throw e.response?.data?['error']?['message'] ?? 'حدث خطأ في الاتصال';
    }
  }
}
```

### 3. Registration Screen

```dart
import 'package:flutter/material.dart';

class RegistrationScreen extends StatefulWidget {
  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _phoneController = TextEditingController();
  bool _isLoading = false;

  Future<void> _sendOtp() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final authService = AuthService(/* dio instance */);
      final response = await authService.sendOtp(
        name: _nameController.text,
        email: _emailController.text,
        password: _passwordController.text,
        phone: _phoneController.text.isNotEmpty ? _phoneController.text : null,
      );

      // Navigate to OTP screen
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => OtpVerificationScreen(
            email: response.email,
            expiresInMinutes: response.expiresInMinutes,
          ),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('إنشاء حساب جديد')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _nameController,
              decoration: InputDecoration(
                labelText: 'الاسم الكامل',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
            ),
            SizedBox(height: 16),
            TextFormField(
              controller: _emailController,
              decoration: InputDecoration(
                labelText: 'البريد الإلكتروني',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.emailAddress,
              validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
            ),
            SizedBox(height: 16),
            TextFormField(
              controller: _passwordController,
              decoration: InputDecoration(
                labelText: 'كلمة المرور',
                border: OutlineInputBorder(),
              ),
              obscureText: true,
              validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
            ),
            SizedBox(height: 16),
            TextFormField(
              controller: _phoneController,
              decoration: InputDecoration(
                labelText: 'رقم الهاتف (اختياري)',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.phone,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isLoading ? null : _sendOtp,
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isLoading
                  ? CircularProgressIndicator()
                  : Text('إرسال رمز التحقق'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### 4. OTP Verification Screen

```dart
import 'package:flutter/material.dart';
import 'package:pin_code_fields/pin_code_fields.dart';
import 'dart:async';

class OtpVerificationScreen extends StatefulWidget {
  final String email;
  final int expiresInMinutes;

  OtpVerificationScreen({
    required this.email,
    required this.expiresInMinutes,
  });

  @override
  State<OtpVerificationScreen> createState() => _OtpVerificationScreenState();
}

class _OtpVerificationScreenState extends State<OtpVerificationScreen> {
  final _otpController = TextEditingController();
  bool _isLoading = false;
  int _secondsRemaining = 0;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _secondsRemaining = widget.expiresInMinutes * 60;
    _startTimer();
  }

  void _startTimer() {
    _timer = Timer.periodic(Duration(seconds: 1), (timer) {
      if (_secondsRemaining > 0) {
        setState(() => _secondsRemaining--);
      } else {
        timer.cancel();
      }
    });
  }

  Future<void> _verifyOtp() async {
    if (_otpController.text.length != 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('يرجى إدخال رمز التحقق المكون من 6 أرقام')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final authService = AuthService(/* dio instance */);
      final response = await authService.verifyOtp(
        email: widget.email,
        otp: _otpController.text,
      );

      // Save tokens and navigate to home
      // await saveTokens(response.accessToken, response.refreshToken);
      Navigator.pushReplacementNamed(context, '/home');
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _resendOtp() async {
    try {
      final authService = AuthService(/* dio instance */);
      await authService.resendOtp(email: widget.email);
      
      setState(() => _secondsRemaining = widget.expiresInMinutes * 60);
      _startTimer();
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('تم إعادة إرسال رمز التحقق')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final minutes = _secondsRemaining ~/ 60;
    final seconds = _secondsRemaining % 60;

    return Scaffold(
      appBar: AppBar(title: Text('التحقق من البريد الإلكتروني')),
      body: Padding(
        padding: EdgeInsets.all(16),
        children: [
          Text(
            'أدخل رمز التحقق',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 8),
          Text(
            'تم إرسال رمز مكون من 6 أرقام إلى ${widget.email}',
            style: TextStyle(color: Colors.grey),
          ),
          SizedBox(height: 32),
          PinCodeTextField(
            length: 6,
            controller: _otpController,
            keyboardType: TextInputType.number,
            onCompleted: (v) => _verifyOtp(),
          ),
          SizedBox(height: 24),
          if (_secondsRemaining > 0)
            Text(
              'ينتهي خلال: $minutes:${seconds.toString().padLeft(2, '0')}',
              style: TextStyle(color: Colors.orange),
            ),
          SizedBox(height: 16),
          ElevatedButton(
            onPressed: _isLoading ? null : _verifyOtp,
            child: _isLoading
                ? CircularProgressIndicator()
                : Text('تحقق'),
          ),
          SizedBox(height: 16),
          TextButton(
            onPressed: _secondsRemaining > 0 ? null : _resendOtp,
            child: Text('إعادة إرسال الرمز'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    _otpController.dispose();
    super.dispose();
  }
}
```

---

## Email Configuration

Before using the OTP system, configure email settings:

### Option 1: Environment Variables (Recommended)

```bash
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-app-password"
```

### Option 2: Config File

Edit `config.py`:

```python
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-app-password'
```

### Gmail App Password Setup

1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate password for "Mail"
5. Use the 16-character password

---

## Testing

1. **Install Dependencies**:
   ```bash
   pip install Flask-Mail
   ```

2. **Run Migration**:
   ```bash
   python migrate_email_verification.py
   ```

3. **Configure Email**:
   Set `MAIL_USERNAME` and `MAIL_PASSWORD` in config or environment

4. **Start Server**:
   ```bash
   python flask_app.py
   ```

5. **Test with Postman/curl**:
   ```bash
   # Send OTP
   curl -X POST http://127.0.0.1:5000/api/v1/auth/send-otp \
     -H "Content-Type: application/json" \
     -d '{"name":"Test User","email":"test@example.com","password":"Test123!"}'
   
   # Check email for OTP, then verify
   curl -X POST http://127.0.0.1:5000/api/v1/auth/verify-otp \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","otp":"123456"}'
   ```

---

## Security Notes

1. **OTP Storage**: Temporary passwords are hashed before storage
2. **Rate Limiting**: Max 5 verification attempts per OTP
3. **Expiry**: OTP expires after 10 minutes
4. **Email Validation**: Validates email format before sending
5. **HTTPS**: Use HTTPS in production to protect OTP in transit
