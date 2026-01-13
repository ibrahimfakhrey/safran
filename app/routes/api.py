"""
REST API Blueprint for Mobile App
Provides JWT-authenticated endpoints for Flutter mobile application
Version: v1
Language: Arabic
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app.models import db, User, Apartment, Share, Transaction, ApartmentImage, Car, CarShare, InvestmentRequest, ReferralTree, CarInvestmentRequest, CarReferralTree, EmailVerification
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
import random

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


# ==================== Helper Functions ====================

def success_response(data=None, message="نجح", status=200):
    """Standard success response format"""
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status


def error_response(message="حدث خطأ", code="ERROR", details=None, status=400):
    """Standard error response format"""
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
    if details:
        response["error"]["details"] = details
    return jsonify(response), status


def serialize_user(user):
    """Convert User object to dictionary"""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "wallet_balance": user.wallet_balance,
        "rewards_balance": user.rewards_balance,
        "is_admin": user.is_admin,
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "phone": user.phone,
        "total_invested": user.get_total_invested(),
        "monthly_expected_income": user.get_monthly_expected_income()
    }


def serialize_apartment(apartment, include_images=False):
    """Convert Apartment object to dictionary"""
    data = {
        "id": apartment.id,
        "title": apartment.title,
        "description": apartment.description,
        "image": apartment.image,
        "total_price": apartment.total_price,
        "total_shares": apartment.total_shares,
        "shares_available": apartment.shares_available,
        "shares_sold": apartment.shares_sold,
        "share_price": apartment.share_price,
        "monthly_rent": apartment.monthly_rent,
        "location": apartment.location,
        "is_closed": apartment.is_closed,
        "status": apartment.status,
        "completion_percentage": apartment.completion_percentage,
        "investors_count": apartment.investors_count,
        "date_created": apartment.date_created.isoformat() if apartment.date_created else None,
        "last_payout_date": apartment.last_payout_date.isoformat() if apartment.last_payout_date else None
    }
    
    if include_images:
        data["images"] = apartment.images
    
    return data


def serialize_transaction(transaction):
    """Convert Transaction object to dictionary"""
    return {
        "id": transaction.id,
        "amount": transaction.amount,
        "transaction_type": transaction.transaction_type,
        "type_arabic": transaction.type_arabic,
        "date": transaction.date.isoformat() if transaction.date else None,
        "description": transaction.description
    }


def serialize_share(share):
    """Convert Share object to dictionary"""
    return {
        "id": share.id,
        "apartment_id": share.apartment_id,
        "num_shares": 1,
        "share_price": share.share_price,
        "purchase_date": share.purchase_date.isoformat() if share.purchase_date else None
    }


def serialize_withdrawal_request(request):
    """Convert WithdrawalRequest object to dictionary"""
    return {
        "id": request.id,
        "user_id": request.user_id,
        "amount": request.amount,
        "payment_method": request.payment_method,
        "payment_method_arabic": request.payment_method_arabic,
        "account_details": request.account_details,
        "status": request.status,
        "status_arabic": request.status_arabic,
        "admin_notes": request.admin_notes,
        "proof_image": request.proof_image if request.proof_image else None,
        "request_date": request.request_date.isoformat() if request.request_date else None,
        "processed_date": request.processed_date.isoformat() if request.processed_date else None,
        "processed_by": request.processed_by
    }


# ==================== Authentication Endpoints ====================

@api_bp.route('/auth/send-otp', methods=['POST'])
def send_otp():
    """
    Send OTP to email for verification
    POST /api/v1/auth/send-otp
    Body: {
        "name": "أحمد محمد",
        "email": "ahmed@example.com",
        "password": "password123",
        "phone": "01234567890" (optional)
    }
    """
    try:
        from app.utils.email_service import send_otp_email, generate_otp
        from flask import current_app
        
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            return error_response(
                message="البريد الإلكتروني والاسم وكلمة المرور مطلوبة",
                code="MISSING_FIELDS"
            )
        
        email = data['email'].lower().strip()
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return error_response(
                message="البريد الإلكتروني مستخدم بالفعل",
                code="EMAIL_EXISTS",
                status=409
            )
        
        # Delete any existing unverified OTP for this email
        EmailVerification.query.filter_by(email=email, is_verified=False).delete()
        
        # Generate 6-digit OTP
        otp_code = generate_otp(6)
        
        # Create expiry time (10 minutes from now)
        expiry_time = datetime.utcnow() + timedelta(
            minutes=current_app.config.get('OTP_EXPIRY_MINUTES', 10)
        )
        
        # Hash password for temporary storage
        temp_password_hash = generate_password_hash(data['password'])
        
        # Create email verification record
        verification = EmailVerification(
            email=email,
            otp_code=otp_code,
            expires_at=expiry_time,
            temp_name=data['name'],
            temp_password_hash=temp_password_hash,
            temp_phone=data.get('phone')
        )
        
        db.session.add(verification)
        db.session.commit()
        
        # Send OTP email
        email_sent = send_otp_email(email, otp_code, data['name'])
        
        if not email_sent:
            return error_response(
                message="فشل إرسال رمز التحقق. يرجى المحاولة مرة أخرى",
                code="EMAIL_SEND_FAILED",
                status=500
            )
        
        return success_response(
            data={
                "email": email,
                "expires_in_minutes": current_app.config.get('OTP_EXPIRY_MINUTES', 10)
            },
            message="تم إرسال رمز التحقق إلى بريدك الإلكتروني",
            status=200
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء إرسال رمز التحقق",
            code="OTP_SEND_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp():
    """
    Verify OTP and complete registration
    POST /api/v1/auth/verify-otp
    Body: {
        "email": "ahmed@example.com",
        "otp": "123456"
    }
    """
    try:
        from app.utils.email_service import send_welcome_email
        
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('otp'):
            return error_response(
                message="البريد الإلكتروني ورمز التحقق مطلوبان",
                code="MISSING_FIELDS"
            )
        
        email = data['email'].lower().strip()
        otp_code = data['otp'].strip()
        
        # Find verification record
        verification = EmailVerification.query.filter_by(
            email=email,
            is_verified=False
        ).order_by(EmailVerification.created_at.desc()).first()
        
        if not verification:
            return error_response(
                message="لم يتم العثور على رمز تحقق لهذا البريد الإلكتروني",
                code="OTP_NOT_FOUND",
                status=404
            )
        
        # Check if OTP is valid
        if not verification.is_valid():
            return error_response(
                message="رمز التحقق منتهي الصلاحية أو تم استخدامه. يرجى طلب رمز جديد",
                code="OTP_EXPIRED"
            )
        
        # Check if too many attempts
        if verification.attempts >= 5:
            return error_response(
                message="تم تجاوز عدد المحاولات المسموحة. يرجى طلب رمز جديد",
                code="TOO_MANY_ATTEMPTS"
            )
        
        # Increment attempts
        verification.attempts += 1
        db.session.commit()
        
        # Verify OTP
        if verification.otp_code != otp_code:
            return error_response(
                message=f"رمز التحقق غير صحيح. المحاولات المتبقية: {5 - verification.attempts}",
                code="INVALID_OTP"
            )
        
        # Check if user already exists (double check)
        if User.query.filter_by(email=email).first():
            return error_response(
                message="البريد الإلكتروني مستخدم بالفعل",
                code="EMAIL_EXISTS",
                status=409
            )
        
        # Create new user
        user = User(
            name=verification.temp_name,
            email=email,
            phone=verification.temp_phone,
            password_hash=verification.temp_password_hash,
            email_verified=True,
            wallet_balance=0.0
        )
        
        # Generate referral number
        db.session.add(user)
        db.session.flush()  # Get user ID
        user.generate_referral_number()
        
        # Mark verification as completed
        verification.is_verified = True
        
        db.session.commit()
        
        # Send welcome email (async, don't wait)
        try:
            send_welcome_email(email, user.name)
        except:
            pass  # Don't fail registration if welcome email fails
        
        # Create JWT tokens
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=30))
        
        # Send welcome notification
        from app.utils.notification_service import send_push_notification, NotificationTemplates
        if user.fcm_token:  # Only send if user has FCM token
            notification = NotificationTemplates.welcome(user.name)
            send_push_notification(
                user_id=user.id,
                title=notification["title"],
                body=notification["body"],
                data=notification.get("data")
            )
        
        return success_response(
            data={
                "user": serialize_user(user),
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            message="تم تفعيل حسابك بنجاح! مرحباً بك في i pillars i",
            status=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء التحقق من الرمز",
            code="VERIFICATION_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/resend-otp', methods=['POST'])
def resend_otp():
    """
    Resend OTP to email
    POST /api/v1/auth/resend-otp
    Body: {
        "email": "ahmed@example.com"
    }
    """
    try:
        from app.utils.email_service import send_otp_email, generate_otp
        from flask import current_app
        
        data = request.get_json()
        
        if not data or not data.get('email'):
            return error_response(
                message="البريد الإلكتروني مطلوب",
                code="MISSING_EMAIL"
            )
        
        email = data['email'].lower().strip()
        
        # Find latest unverified verification record
        verification = EmailVerification.query.filter_by(
            email=email,
            is_verified=False
        ).order_by(EmailVerification.created_at.desc()).first()
        
        if not verification:
            return error_response(
                message="لم يتم العثور على طلب تسجيل لهذا البريد الإلكتروني",
                code="NO_PENDING_REGISTRATION",
                status=404
            )
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return error_response(
                message="البريد الإلكتروني مستخدم بالفعل",
                code="EMAIL_EXISTS",
                status=409
            )
        
        # Generate new OTP
        otp_code = generate_otp(6)
        expiry_time = datetime.utcnow() + timedelta(
            minutes=current_app.config.get('OTP_EXPIRY_MINUTES', 10)
        )
        
        # Update verification record
        verification.otp_code = otp_code
        verification.expires_at = expiry_time
        verification.attempts = 0  # Reset attempts
        verification.created_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send OTP email
        email_sent = send_otp_email(email, otp_code, verification.temp_name)
        
        if not email_sent:
            return error_response(
                message="فشل إرسال رمز التحقق. يرجى المحاولة مرة أخرى",
                code="EMAIL_SEND_FAILED",
                status=500
            )
        
        return success_response(
            data={
                "email": email,
                "expires_in_minutes": current_app.config.get('OTP_EXPIRY_MINUTES', 10)
            },
            message="تم إعادة إرسال رمز التحقق بنجاح"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء إعادة إرسال الرمز",
            code="RESEND_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/register', methods=['POST'])
def register():
    """
    User registration (Legacy endpoint for backward compatibility)
    POST /api/v1/auth/register
    Body: {
        "name": "Ahmed Ali",
        "email": "ahmed@example.com",
        "password": "password123",
        "phone": "1234567890" (optional)
    }
    
    Note: For new apps, use /auth/send-otp and /auth/verify-otp for email verification
    """
    try:
        data = request.get_json()
        
        # Validation
        if not data or not data.get('name') or not data.get('email') or not data.get('password'):
            return error_response(
                message="الاسم والبريد الإلكتروني وكلمة المرور مطلوبة",
                code="MISSING_FIELDS"
            )
        
        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            return error_response(
                message="البريد الإلكتروني مستخدم بالفعل",
                code="EMAIL_EXISTS",
                status=409
            )
        
        # Create new user
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            wallet_balance=0.0,
            email_verified=True  # Auto-verify for legacy endpoint
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=30))
        
        return success_response(
            data={
                "user": serialize_user(user),
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            message="تم إنشاء الحساب بنجاح",
            status=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء إنشاء الحساب",
            code="REGISTRATION_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    User login
    POST /api/v1/auth/login
    Body: {
        "email": "ahmed@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return error_response(
                message="البريد الإلكتروني وكلمة المرور مطلوبة",
                code="MISSING_CREDENTIALS"
            )
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return error_response(
                message="البريد الإلكتروني أو كلمة المرور غير صحيحة",
                code="INVALID_CREDENTIALS",
                status=401
            )
        
        # Create JWT tokens
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=30))
        
        return success_response(
            data={
                "user": serialize_user(user),
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            message="تم تسجيل الدخول بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء تسجيل الدخول",
            code="LOGIN_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user info
    GET /api/v1/auth/me
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        return success_response(
            data={"user": serialize_user(user)},
            message="تم جلب بيانات المستخدم بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب البيانات",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    POST /api/v1/auth/refresh
    Headers: Authorization: Bearer <refresh_token>
    """
    try:
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(days=7))
        
        return success_response(
            data={"access_token": access_token},
            message="تم تحديث الرمز بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء تحديث الرمز",
            code="REFRESH_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/google', methods=['POST'])
def google_sign_in():
    """
    Authenticate user with Google Sign-In
    POST /api/v1/auth/google
    Body: {
        "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6...",
        "access_token": "ya29.a0AfH6SMBx..." (optional)
    }
    """
    try:
        from app.auth_providers import verify_google_token
        
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('id_token'):
            return error_response(
                message="id_token مطلوب",
                code="MISSING_FIELDS"
            )
        
        # Verify token with Google
        user_info = verify_google_token(data['id_token'])
        
        if not user_info:
            return error_response(
                message="رمز Google غير صالح",
                code="INVALID_TOKEN",
                status=401
            )
        
        # Extract user information
        google_user_id = user_info['user_id']
        email = user_info['email']
        name = user_info['name']
        
        # Check if user exists with Google auth
        user = User.query.filter_by(
            auth_provider='google',
            provider_user_id=google_user_id
        ).first()
        
        is_new_user = False
        
        if not user:
            # Check if email exists with different auth method (potential account linking)
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Link existing account to Google
                user.link_social_account('google', google_user_id, email)
                message = "تم ربط الحساب بنجاح"
            else:
                # Create new user
                user = User(
                    name=name,
                    email=email,
                    auth_provider='google',
                    provider_user_id=google_user_id,
                    provider_email=email,
                    wallet_balance=0.0  # Start with zero balance
                )
                db.session.add(user)
                is_new_user = True
                message = "تم إنشاء الحساب بنجاح"
        else:
            message = "تم تسجيل الدخول بنجاح"
        
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=30))
        
        return success_response(
            data={
                "user": serialize_user(user),
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            message=message,
            status=201 if is_new_user else 200
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء تسجيل الدخول عبر Google",
            code="GOOGLE_AUTH_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/apple', methods=['POST'])
def apple_sign_in():
    """
    Authenticate user with Apple Sign-In
    POST /api/v1/auth/apple
    Body: {
        "identity_token": "eyJraWQiOiJlWGF1bm1MIiwiYWxnIjoi...",
        "authorization_code": "c1a2b3c4d5e6f7g8h9i0..." (optional),
        "user_identifier": "001234.5678abcd.1234",
        "email": "john@privaterelay.appleid.com" (only first sign-in),
        "given_name": "John" (only first sign-in),
        "family_name": "Doe" (only first sign-in)
    }
    """
    try:
        from app.auth_providers import verify_apple_token
        from flask import current_app
        import jwt as pyjwt
        
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('identity_token'):
            return error_response(
                message="identity_token مطلوب",
                code="MISSING_FIELDS"
            )
        
        identity_token = data.get('identity_token')
        
        # 🔍 DEBUG: Decode token WITHOUT verification to see what's inside
        try:
            unverified = pyjwt.decode(identity_token, options={"verify_signature": False})
            print("=" * 80)
            print("🔍 APPLE TOKEN DEBUG INFO:")
            print(f"📋 All Token Claims: {unverified}")
            print(f"👤 Subject (sub): {unverified.get('sub')}")
            print(f"📧 Email: {unverified.get('email', 'Not provided')}")
            print(f"🎯 Audience (aud): {unverified.get('aud')}")
            print(f"✅ Expected Audience: {current_app.config.get('APPLE_CLIENT_ID')}")
            print(f"🏢 Issuer (iss): {unverified.get('iss')}")
            print(f"⏰ Expiration (exp): {unverified.get('exp')}")
            print(f"🔑 Key ID from header: {pyjwt.get_unverified_header(identity_token).get('kid')}")
            
            # Compare audience
            actual_aud = unverified.get('aud')
            expected_aud = current_app.config.get('APPLE_CLIENT_ID')
            if actual_aud != expected_aud:
                print(f"⚠️  WARNING: Audience mismatch!")
                print(f"   Actual:   '{actual_aud}'")
                print(f"   Expected: '{expected_aud}'")
            else:
                print(f"✅ Audience matches!")
            print("=" * 80)
        except Exception as e:
            print(f"❌ DEBUG: Failed to decode token for debugging: {e}")
        
        # Verify token with Apple
        user_info = verify_apple_token(identity_token)
        
        if not user_info:
            print("❌ verify_apple_token() returned None - Token verification failed!")
            return error_response(
                message="رمز Apple غير صالح",
                code="INVALID_TOKEN",
                status=401
            )
        
        # Extract user information
        apple_user_id = user_info['user_id']
        
        # Email and name are only provided on first sign-in
        email = data.get('email') or user_info.get('email') or ''
        given_name = data.get('given_name', '')
        family_name = data.get('family_name', '')
        name = f"{given_name} {family_name}".strip() or "Apple User"
        
        # Check if user exists with Apple auth
        user = User.query.filter_by(
            auth_provider='apple',
            provider_user_id=apple_user_id
        ).first()
        
        is_new_user = False
        
        if not user:
            # For returning users, email might not be provided
            if email:
                # Check if email exists with different auth method
                user = User.query.filter_by(email=email).first()
                
                if user:
                    # Link existing account to Apple
                    user.link_social_account('apple', apple_user_id, email)
                    message = "تم ربط الحساب بنجاح"
                else:
                    # Create new user
                    user = User(
                        name=name,
                        email=email,
                        auth_provider='apple',
                        provider_user_id=apple_user_id,
                        provider_email=email,
                        wallet_balance=0.0  # Start with zero balance
                    )
                    db.session.add(user)
                    is_new_user = True
                    message = "تم إنشاء الحساب بنجاح"
            else:
                # No email provided and user not found - this shouldn't happen
                return error_response(
                    message="لا يمكن العثور على الحساب. يرجى المحاولة مرة أخرى",
                    code="USER_NOT_FOUND",
                    status=404
                )
        else:
            message = "تم تسجيل الدخول بنجاح"
        
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=30))
        
        return success_response(
            data={
                "user": serialize_user(user),
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            message=message,
            status=201 if is_new_user else 200
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء تسجيل الدخول عبر Apple",
            code="APPLE_AUTH_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/auth/delete-account', methods=['POST'])
@jwt_required()
def delete_account():
    """
    Delete user account permanently
    POST /api/v1/auth/delete-account
    Headers: Authorization: Bearer <token>
    Body: {
        "password": "user_password"
    }
    
    ⚠️ WARNING: This action is irreversible!
    All user data will be permanently deleted including:
    - Profile information
    - Wallet balance
    - Investment shares
    - Transaction history
    - Investment requests
    - Referral data
    """
    try:
        from app.models import WithdrawalRequest, ReferralTree, ReferralUsage, CarShare, CarReferralTree
        
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        data = request.get_json()
        
        # For email/password users, require password confirmation
        if user.auth_provider == 'email' or user.password_hash:
            if not data or not data.get('password'):
                return error_response(
                    message="كلمة المرور مطلوبة لتأكيد حذف الحساب",
                    code="PASSWORD_REQUIRED"
                )
            
            if not user.check_password(data['password']):
                return error_response(
                    message="كلمة المرور غير صحيحة",
                    code="INVALID_PASSWORD",
                    status=401
                )
        
        # Check for pending withdrawal requests
        pending_withdrawals = WithdrawalRequest.query.filter_by(
            user_id=user.id,
            status='pending'
        ).count()
        
        if pending_withdrawals > 0:
            return error_response(
                message="لا يمكن حذف الحساب - لديك طلبات سحب معلقة. يرجى إلغاءها أولاً.",
                code="PENDING_WITHDRAWALS",
                details={"pending_count": pending_withdrawals}
            )
        
        # Store user email for confirmation message
        user_email = user.email
        
        # Delete related records that don't have cascade delete
        # Delete withdrawal requests (non-pending ones)
        WithdrawalRequest.query.filter_by(user_id=user.id).delete()
        
        # Delete referral tree entries
        ReferralTree.query.filter_by(user_id=user.id).delete()
        ReferralTree.query.filter_by(referred_by_user_id=user.id).update({'referred_by_user_id': None})
        
        # Delete car referral tree entries
        CarReferralTree.query.filter_by(user_id=user.id).delete()
        CarReferralTree.query.filter_by(referred_by_user_id=user.id).update({'referred_by_user_id': None})
        
        # Delete referral usage records
        ReferralUsage.query.filter_by(referrer_user_id=user.id).delete()
        ReferralUsage.query.filter_by(referee_user_id=user.id).delete()
        
        # Delete car shares (cascade should handle this, but being explicit)
        CarShare.query.filter_by(user_id=user.id).delete()
        
        # Delete the user (cascades will handle shares, transactions, investment_requests)
        db.session.delete(user)
        db.session.commit()
        
        return success_response(
            data={"deleted_email": user_email},
            message="تم حذف الحساب بنجاح. نأسف لرؤيتك تغادر!"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء حذف الحساب",
            code="DELETE_ACCOUNT_ERROR",
            details=str(e),
            status=500
        )


# ==================== Apartment Endpoints ====================

@api_bp.route('/apartments', methods=['GET'])
def get_apartments():
    """
    Get list of apartments with optional filters
    GET /api/v1/apartments?status=available&location=القاهرة&page=1&per_page=10
    """
    try:
        # Get query parameters
        status = request.args.get('status')  # 'available', 'closed', 'new'
        location = request.args.get('location')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query
        query = Apartment.query
        
        # Apply filters
        if status == 'available':
            query = query.filter(Apartment.is_closed == False, Apartment.shares_available > 0)
        elif status == 'closed':
            query = query.filter(Apartment.is_closed == True)
        elif status == 'new':
            query = query.filter(Apartment.shares_available == Apartment.total_shares)
        
        if location:
            query = query.filter(Apartment.location.contains(location))
        
        # Paginate
        pagination = query.order_by(Apartment.date_created.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        apartments = [serialize_apartment(apt, include_images=True) for apt in pagination.items]
        
        return success_response(
            data={
                "apartments": apartments,
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "total_pages": pagination.pages
            },
            message="تم جلب العقارات بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب العقارات",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/apartments/<int:apartment_id>', methods=['GET'])
def get_apartment_details(apartment_id):
    """
    Get apartment details by ID
    GET /api/v1/apartments/1
    """
    try:
        apartment = Apartment.query.get(apartment_id)
        
        if not apartment:
            return error_response(
                message="العقار غير موجود",
                code="APARTMENT_NOT_FOUND",
                status=404
            )
        
        return success_response(
            data={"apartment": serialize_apartment(apartment, include_images=True)},
            message="تم جلب تفاصيل العقار بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب التفاصيل",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


# ==================== Investment/Shares Endpoints ====================

@api_bp.route('/shares/purchase', methods=['POST'])
@jwt_required()
def purchase_shares():
    """
    Purchase shares in an apartment
    POST /api/v1/shares/purchase
    Headers: Authorization: Bearer <token>
    Body: {
        "apartment_id": 1,
        "num_shares": 5
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        data = request.get_json()
        
        if not data or not data.get('apartment_id') or not data.get('num_shares'):
            return error_response(
                message="معرف العقار وعدد الحصص مطلوبة",
                code="MISSING_FIELDS"
            )
        
        apartment_id = data['apartment_id']
        num_shares = data['num_shares']
        
        # Validate num_shares
        if num_shares <= 0:
            return error_response(
                message="عدد الحصص يجب أن يكون أكبر من صفر",
                code="INVALID_SHARES"
            )
        
        # Get apartment
        apartment = Apartment.query.get(apartment_id)
        
        if not apartment:
            return error_response(
                message="العقار غير موجود",
                code="APARTMENT_NOT_FOUND",
                status=404
            )
        
        # Attempt purchase
        success, message = apartment.purchase_shares(user, num_shares)
        
        if not success:
            return error_response(
                message=message,
                code="PURCHASE_FAILED"
            )
        
        db.session.commit()
        
        return success_response(
            data={
                "new_balance": user.wallet_balance,
                "shares_purchased": num_shares,
                "total_cost": apartment.share_price * num_shares,
                "apartment": serialize_apartment(apartment)
            },
            message="تم شراء الحصص بنجاح"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء شراء الحصص",
            code="PURCHASE_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/shares/my-investments', methods=['GET'])
@jwt_required()
def get_my_investments():
    """
    Get user's investment portfolio
    GET /api/v1/shares/my-investments
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        # Get all shares grouped by apartment
        shares_by_apartment = {}
        for share in user.shares:
            apt_id = share.apartment_id
            if apt_id not in shares_by_apartment:
                shares_by_apartment[apt_id] = {
                    "apartment": serialize_apartment(share.apartment),
                    "shares_owned": 0,
                    "total_invested": 0,
                    "monthly_income": 0
                }
            shares_by_apartment[apt_id]["shares_owned"] += 1
            shares_by_apartment[apt_id]["total_invested"] += share.share_price
            if share.apartment:
                shares_by_apartment[apt_id]["monthly_income"] += share.apartment.monthly_rent / share.apartment.total_shares
        
        investments = list(shares_by_apartment.values())
        
        return success_response(
            data={
                "investments": investments,
                "total_invested": user.get_total_invested(),
                "monthly_expected_income": user.get_monthly_expected_income(),
                "total_apartments": len(investments)
            },
            message="تم جلب الاستثمارات بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب الاستثمارات",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


# ==================== Wallet Endpoints ====================

@api_bp.route('/wallet/balance', methods=['GET'])
@jwt_required()
def get_wallet_balance():
    """
    Get user's wallet balance
    GET /api/v1/wallet/balance
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        return success_response(
            data={
                "wallet_balance": user.wallet_balance,
                "rewards_balance": user.rewards_balance,
                "total_balance": user.wallet_balance + user.rewards_balance
            },
            message="تم جلب الرصيد بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب الرصيد",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/wallet/withdrawal-request', methods=['POST'])
@jwt_required()
def submit_withdrawal_request():
    """
    Submit withdrawal request
    POST /api/v1/wallet/withdrawal-request
    Headers: Authorization: Bearer <token>
    Body: {
        "amount": 500,
        "payment_method": "instapay",  // instapay, wallet, company
        "account_details": "01234567890"  // optional for company
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        # Check if user already has a pending request
        from app.models import WithdrawalRequest
        pending = WithdrawalRequest.query.filter_by(
            user_id=user.id,
            status='pending'
        ).first()
        
        if pending:
            return error_response(
                message="لديك طلب سحب قيد المراجعة بالفعل. لا يمكن تقديم طلب جديد.",
                code="PENDING_REQUEST_EXISTS"
            )
        
        data = request.get_json()
        
        if not data or not data.get('amount') or not data.get('payment_method'):
            return error_response(
                message="المبلغ وطريقة الدفع مطلوبة",
                code="MISSING_FIELDS"
            )
        
        amount = float(data['amount'])
        payment_method = data['payment_method']
        account_details = data.get('account_details', '').strip()
        
        # Validation
        if amount < 100:
            return error_response(
                message="الحد الأدنى للسحب هو 100 جنيه",
                code="INVALID_AMOUNT"
            )
        
        if amount > user.wallet_balance:
            return error_response(
                message="رصيد المحفظة غير كافي",
                code="INSUFFICIENT_BALANCE",
                details={
                    "required": amount,
                    "available": user.wallet_balance
                }
            )
        
        if payment_method not in ['instapay', 'wallet', 'company']:
            return error_response(
                message="طريقة الدفع غير صالحة",
                code="INVALID_PAYMENT_METHOD"
            )
        
        if not account_details and payment_method != 'company':
            return error_response(
                message="يرجى إدخال تفاصيل الحساب",
                code="MISSING_ACCOUNT_DETAILS"
            )
        
        # Create withdrawal request
        new_request = WithdrawalRequest(
            user_id=user.id,
            amount=amount,
            payment_method=payment_method,
            account_details=account_details if payment_method != 'company' else 'استلام من الشركة',
            status='pending'
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        return success_response(
            data={
                "request": serialize_withdrawal_request(new_request),
                "message": f"تم تقديم طلب سحب {amount:,.0f} جنيه. سيتم مراجعته من قبل الإدارة."
            },
            message="تم تقديم طلب السحب بنجاح",
            status=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء تقديم الطلب",
            code="REQUEST_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/wallet/withdrawal-requests', methods=['GET'])
@jwt_required()
def get_withdrawal_requests():
    """
    Get user's withdrawal request history
    GET /api/v1/wallet/withdrawal-requests?page=1&per_page=20
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        from app.models import WithdrawalRequest
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Paginate requests
        pagination = WithdrawalRequest.query.filter_by(user_id=user.id)\
            .order_by(WithdrawalRequest.request_date.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        requests = [serialize_withdrawal_request(req) for req in pagination.items]
        
        return success_response(
            data={
                "requests": requests,
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "total_pages": pagination.pages
            },
            message="تم جلب طلبات السحب بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب الطلبات",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/wallet/pending-request', methods=['GET'])
@jwt_required()
def get_pending_withdrawal_request():
    """
    Get current pending withdrawal request
    GET /api/v1/wallet/pending-request
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        from app.models import WithdrawalRequest
        pending_request = WithdrawalRequest.query.filter_by(
            user_id=user.id,
            status='pending'
        ).first()
        
        return success_response(
            data={
                "pending_request": serialize_withdrawal_request(pending_request) if pending_request else None
            },
            message="تم جلب الطلب المعلق بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب الطلب",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/wallet/cancel-request/<int:request_id>', methods=['POST'])
@jwt_required()
def cancel_withdrawal_request(request_id):
    """
    Cancel pending withdrawal request
    POST /api/v1/wallet/cancel-request/<id>
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        from app.models import WithdrawalRequest
        from datetime import datetime
        
        withdrawal_request = WithdrawalRequest.query.get(request_id)
        
        if not withdrawal_request:
            return error_response(
                message="الطلب غير موجود",
                code="REQUEST_NOT_FOUND",
                status=404
            )
        
        # Check ownership
        if withdrawal_request.user_id != user.id:
            return error_response(
                message="غير مصرح لك بإلغاء هذا الطلب",
                code="UNAUTHORIZED",
                status=403
            )
        
        # Can only cancel pending requests
        if withdrawal_request.status != 'pending':
            return error_response(
                message="لا يمكن إلغاء هذا الطلب",
                code="CANNOT_CANCEL"
            )
        
        withdrawal_request.status = 'cancelled'
        withdrawal_request.processed_date = datetime.utcnow()
        db.session.commit()
        
        return success_response(
            data={
                "request": serialize_withdrawal_request(withdrawal_request)
            },
            message="تم إلغاء طلب السحب بنجاح"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء إلغاء الطلب",
            code="CANCEL_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/wallet/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """
    Get user's transaction history
    GET /api/v1/wallet/transactions?page=1&per_page=20
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Paginate transactions
        pagination = user.transactions.order_by(Transaction.date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        transactions = [serialize_transaction(t) for t in pagination.items]
        
        return success_response(
            data={
                "transactions": transactions,
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "total_pages": pagination.pages
            },
            message="تم جلب المعاملات بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب المعاملات",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )


# ==================== User Dashboard Endpoint ====================

@api_bp.route('/user/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """
    Get user dashboard data
    GET /api/v1/user/dashboard
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        # Get recent transactions
        recent_transactions = [
            serialize_transaction(t) 
            for t in user.transactions.order_by(Transaction.date.desc()).limit(5).all()
        ]
        
        # Count apartments invested in
        apartments_count = db.session.query(db.func.count(db.func.distinct(Share.apartment_id)))\
            .filter(Share.user_id == user.id).scalar() or 0
        
        return success_response(
            data={
                "user": serialize_user(user),
                "wallet_balance": user.wallet_balance,
                "rewards_balance": user.rewards_balance,
                "total_invested": user.get_total_invested(),
                "monthly_expected_income": user.get_monthly_expected_income(),
                "apartments_count": apartments_count,
                "total_shares": user.shares.count(),
                "recent_transactions": recent_transactions
            },
            message="تم جلب بيانات لوحة التحكم بنجاح"
        )
        
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب البيانات",
            code="FETCH_ERROR",
            details=str(e),
            status=500
        )

@api_bp.route('/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update user profile
    PUT /api/v1/user/profile
    Headers: Authorization: Bearer <token>
    Body: {
        "name": "أحمد محمد الجديد",
        "phone": "01234567890"
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        data = request.get_json()
        
        # Update fields if provided
        if data.get('name'):
            user.name = data['name']
        if data.get('phone'):
            user.phone = data['phone']
        
        db.session.commit()
        
        return success_response(
            data={"user": serialize_user(user)},
            message="تم تحديث الملف الشخصي بنجاح"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء التحديث",
            code="UPDATE_ERROR",
            details=str(e),
            status=500
        )


@api_bp.route('/user/update-fcm-token', methods=['POST'])
@jwt_required()
def update_fcm_token():
    """
    Update user's FCM token for push notifications
    POST /api/v1/user/update-fcm-token
    Headers: Authorization: Bearer <token>
    Body: {
        "fcm_token": "device_token_here"
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(
                message="المستخدم غير موجود",
                code="USER_NOT_FOUND",
                status=404
            )
        
        data = request.get_json()
        
        if not data or not data.get('fcm_token'):
            return error_response(
                message="FCM token مطلوب",
                code="MISSING_TOKEN"
            )
        
        # Update FCM token
        user.fcm_token = data['fcm_token']
        db.session.commit()
        
        return success_response(
            data={"fcm_token_updated": True},
            message="تم تحديث رمز الإشعارات بنجاح"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء تحديث الرمز",
            code="TOKEN_UPDATE_ERROR",
            details=str(e),
            status=500
        )


# ==================== Car Endpoints ====================

def serialize_car(car):
    """Convert Car object to dictionary"""
    return {
        "id": car.id,
        "title": car.title,
        "description": car.description,
        "image": car.image,
        "total_price": car.total_price,
        "total_shares": car.total_shares,
        "shares_available": car.shares_available,
        "shares_sold": car.shares_sold,
        "share_price": car.share_price,
        "monthly_rent": car.monthly_rent,
        "location": car.location,
        "is_closed": car.is_closed,
        "status": car.status,
        "completion_percentage": car.completion_percentage,
        "investors_count": car.investors_count,
        "brand": car.brand,
        "model": car.model,
        "year": car.year,
        "date_created": car.date_created.isoformat() if car.date_created else None
    }

@api_bp.route('/cars', methods=['GET'])
def get_cars():
    """
    Get list of cars
    GET /api/v1/cars
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Car.query.order_by(Car.date_created.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        cars = [serialize_car(car) for car in pagination.items]
        
        return success_response(
            data={
                "cars": cars,
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "total_pages": pagination.pages
            },
            message="تم جلب السيارات بنجاح"
        )
    except Exception as e:
        return error_response(message="حدث خطأ أثناء جلب السيارات", details=str(e), status=500)

@api_bp.route('/cars/<int:car_id>', methods=['GET'])
def get_car_details(car_id):
    """Get car details"""
    try:
        car = Car.query.get(car_id)
        if not car:
            return error_response(message="السيارة غير موجودة", status=404)
        return success_response(data={"car": serialize_car(car)}, message="تم جلب تفاصيل السيارة بنجاح")
    except Exception as e:
        return error_response(message="حدث خطأ", details=str(e), status=500)

@api_bp.route('/shares/purchase-car', methods=['POST'])
@jwt_required()
def purchase_car_shares_fake():
    """
    FAKE endpoint for purchasing car shares (for testing only)
    POST /api/v1/shares/purchase-car
    Headers: Authorization: Bearer <token>
    Body: {
        "car_id": 1,
        "num_shares": 5
    }
    
    Returns fake success response without any database operations.
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('car_id') or not data.get('num_shares'):
            return error_response(message="البيانات ناقصة")
        
        num_shares = data['num_shares']
        
        # Return fake success response
        return success_response(
            message=f"تم شراء {num_shares} حصة بنجاح"
        )
    except Exception as e:
        return error_response(message="حدث خطأ أثناء الشراء", details=str(e), status=500)


@api_bp.route('/cars/purchase', methods=['POST'])
@jwt_required()
def purchase_car_shares():
    """Purchase shares in a car"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        data = request.get_json()
        
        if not data or not data.get('car_id') or not data.get('num_shares'):
            return error_response(message="البيانات ناقصة")
            
        car = Car.query.get(data['car_id'])
        if not car:
            return error_response(message="السيارة غير موجودة", status=404)
            
        success, msg = car.purchase_shares(user, data['num_shares'])
        if not success:
            return error_response(message=msg)
            
        db.session.commit()
        return success_response(
            data={
                "new_balance": user.wallet_balance,
                "shares_purchased": data['num_shares'],
                "car": serialize_car(car)
            },
            message="تم شراء حصص السيارة بنجاح"
        )
    except Exception as e:
        db.session.rollback()
        return error_response(message="حدث خطأ أثناء الشراء", details=str(e), status=500)

@api_bp.route('/cars/my-investments', methods=['GET'])
@jwt_required()
def get_my_car_investments():
    """Get user's car investments"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        # Group shares by car
        shares_by_car = {}
        for share in user.car_shares:
            car_id = share.car_id
            if car_id not in shares_by_car:
                shares_by_car[car_id] = {
                    "car": serialize_car(share.car),
                    "shares_owned": 0,
                    "total_invested": 0,
                    "monthly_income": 0
                }
            shares_by_car[car_id]["shares_owned"] += 1
            shares_by_car[car_id]["total_invested"] += share.share_price
            if share.car:
                shares_by_car[car_id]["monthly_income"] += share.car.monthly_rent / share.car.total_shares

        return success_response(
            data={"investments": list(shares_by_car.values())},
            message="تم جلب استثمارات السيارات بنجاح"
        )
    except Exception as e:
        return error_response(message="حدث خطأ", details=str(e), status=500)


# ==================== Admin Endpoints ====================

@api_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or not user.is_admin:
            return error_response(
                message='غير مصرح لك بالوصول',
                code='UNAUTHORIZED',
                status=403
            )
        
        total_users = User.query.count()
        total_apartments = Apartment.query.count()
        total_cars = Car.query.count()
        pending_requests = InvestmentRequest.query.filter_by(status='pending').count()
        approved_requests = InvestmentRequest.query.filter_by(status='approved').count()
        total_investments = Share.query.count()
        
        total_apartment_value = db.session.query(db.func.sum(Apartment.total_price)).scalar() or 0
        total_car_value = db.session.query(db.func.sum(Car.total_price)).scalar() or 0
        
        return success_response(
            data={
                'total_users': total_users,
                'total_apartments': total_apartments,
                'total_cars': total_cars,
                'pending_requests': pending_requests,
                'approved_requests': approved_requests,
                'total_investments': total_investments,
                'total_platform_value': total_apartment_value + total_car_value
            },
            message='تم جلب الإحصائيات بنجاح'
        )
    except Exception as e:
        return error_response(message='حدث خطأ أثناء جلب الإحصائيات', details=str(e), status=500)


@api_bp.route('/admin/investment-requests', methods=['GET'])
@jwt_required()
def get_investment_requests():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or not user.is_admin:
            return error_response(message='غير مصرح لك بالوصول', code='UNAUTHORIZED', status=403)
        
        status_filter = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = InvestmentRequest.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        query = query.order_by(InvestmentRequest.date_submitted.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        requests_list = []
        for req in pagination.items:
            requests_list.append({
                'id': req.id,
                'user_id': req.user_id,
                'user_name': req.user.name,
                'user_email': req.user.email,
                'apartment_id': req.apartment_id,
                'apartment_title': req.apartment.title if req.apartment else None,
                'shares_requested': req.shares_requested,
                'total_amount': req.total_amount,
                'status': req.status,
                'status_arabic': req.status_arabic,
                'full_name': req.full_name,
                'phone': req.phone,
                'national_id': req.national_id,
                'date_submitted': req.date_submitted.isoformat() if req.date_submitted else None,
                'admin_notes': req.admin_notes
            })
        
        return success_response(
            data={
                'requests': requests_list,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'total_pages': pagination.pages
            },
            message='تم جلب الطلبات بنجاح'
        )
    except Exception as e:
        return error_response(message='حدث خطأ أثناء جلب الطلبات', details=str(e), status=500)


@api_bp.route('/admin/investment-requests/<int:request_id>/action', methods=['POST'])
@jwt_required()
def admin_request_action(request_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or not user.is_admin:
            return error_response(message='غير مصرح لك بالوصول', code='UNAUTHORIZED', status=403)
        
        data = request.get_json()
        action = data.get('action')
        admin_notes = data.get('admin_notes', '')
        
        if action not in ['approve', 'reject']:
            return error_response(message='الإجراء غير صحيح', code='INVALID_ACTION')
        
        inv_request = InvestmentRequest.query.get(request_id)
        if not inv_request:
            return error_response(message='الطلب غير موجود', status=404)
        
        if action == 'approve':
            inv_request.status = 'approved'
            apartment = inv_request.apartment
            investor = inv_request.user
            
            for _ in range(inv_request.shares_requested):
                share = Share(
                    user_id=investor.id,
                    apartment_id=apartment.id,
                    share_price=apartment.share_price
                )
                db.session.add(share)
            
            apartment.shares_available -= inv_request.shares_requested
            if apartment.shares_available == 0:
                apartment.is_closed = True
        else:
            inv_request.status = 'rejected'
        
        inv_request.admin_notes = admin_notes
        inv_request.date_reviewed = datetime.utcnow()
        inv_request.reviewed_by = user.id
        
        db.session.commit()
        
        return success_response(
            data={'request': {
                'id': inv_request.id,
                'status': inv_request.status,
                'status_arabic': inv_request.status_arabic
            }},
            message=f'تم {inv_request.status_arabic} الطلب بنجاح'
        )
    except Exception as e:
        db.session.rollback()
        return error_response(message='حدث خطأ أثناء معالجة الطلب', details=str(e), status=500)


# ==================== KYC & Investment Request Endpoints ====================

@api_bp.route('/user/kyc', methods=['POST'])
@jwt_required()
def submit_kyc():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return error_response(message='المستخدم غير موجود', status=404)
        
        data = request.get_json()
        
        user.phone = data.get('phone', user.phone)
        user.national_id = data.get('national_id', user.national_id)
        user.address = data.get('address', user.address)
        user.date_of_birth = data.get('date_of_birth', user.date_of_birth)
        user.nationality = data.get('nationality', user.nationality)
        user.occupation = data.get('occupation', user.occupation)
        
        db.session.commit()
        
        return success_response(
            data={
                'kyc_completed': all([user.phone, user.national_id, user.address, 
                                     user.date_of_birth, user.nationality, user.occupation])
            },
            message='تم تحديث معلومات KYC بنجاح'
        )
    except Exception as e:
        db.session.rollback()
        return error_response(message='حدث خطأ أثناء تحديث المعلومات', details=str(e), status=500)


@api_bp.route('/investments/request', methods=['POST'])
@jwt_required()
def create_investment_request():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        # Check if request is multipart/form-data
        if not request.files and not request.form:
             return error_response(message='يجب إرسال البيانات بصيغة multipart/form-data', code='INVALID_CONTENT_TYPE')

        data = request.form
        files = request.files
        
        required_fields = ['apartment_id', 'shares_requested', 'full_name', 'phone', 
                          'national_id', 'address', 'date_of_birth', 'nationality', 'occupation']
        
        for field in required_fields:
            if not data.get(field):
                return error_response(message=f'الحقل {field} مطلوب', code='MISSING_FIELDS')
        
        # Validate files
        required_files = ['id_document_front', 'id_document_back', 'proof_of_address']
        for file_field in required_files:
            if file_field not in files or files[file_field].filename == '':
                 return error_response(message=f'الملف {file_field} مطلوب', code='MISSING_FILES')

        apartment = Apartment.query.get(data['apartment_id'])
        if not apartment:
            return error_response(message='الشقة غير موجودة', status=404)
        
        shares_requested = int(data['shares_requested'])
        if apartment.shares_available < shares_requested:
            return error_response(message='عدد الحصص المطلوبة غير متاح', code='INSUFFICIENT_SHARES')
        
        referred_by_user_id = None
        if data.get('referred_by_code'):
            referral = ReferralTree.query.filter_by(
                referral_code=data['referred_by_code'],
                apartment_id=apartment.id
            ).first()
            if referral:
                referred_by_user_id = referral.user_id
        
        # Save files
        from flask import current_app
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        front_file = files['id_document_front']
        front_filename = secure_filename(f"{timestamp}_front_{user.id}_{front_file.filename}")
        front_file.save(os.path.join(upload_dir, front_filename))
        
        back_file = files['id_document_back']
        back_filename = secure_filename(f"{timestamp}_back_{user.id}_{back_file.filename}")
        back_file.save(os.path.join(upload_dir, back_filename))
        
        address_file = files['proof_of_address']
        address_filename = secure_filename(f"{timestamp}_address_{user.id}_{address_file.filename}")
        address_file.save(os.path.join(upload_dir, address_filename))

        inv_request = InvestmentRequest(
            user_id=user.id,
            apartment_id=apartment.id,
            shares_requested=shares_requested,
            referred_by_user_id=referred_by_user_id,
            full_name=data['full_name'],
            phone=data['phone'],
            national_id=data['national_id'],
            address=data['address'],
            date_of_birth=data['date_of_birth'],
            nationality=data['nationality'],
            occupation=data['occupation'],
            id_document_front=front_filename,
            id_document_back=back_filename,
            proof_of_address=address_filename,
            status='pending'
        )
        
        db.session.add(inv_request)
        db.session.commit()
        
        return success_response(
            data={
                'request_id': inv_request.id,
                'status': inv_request.status,
                'status_arabic': inv_request.status_arabic,
                'total_amount': inv_request.total_amount
            },
            message='تم إرسال طلب الاستثمار بنجاح'
        )
    except Exception as e:
        db.session.rollback()
        return error_response(message='حدث خطأ أثناء إنشاء الطلب', details=str(e), status=500)


@api_bp.route('/investments/requests', methods=['GET'])
@jwt_required()
def get_user_investment_requests():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        requests = InvestmentRequest.query.filter_by(user_id=user.id).order_by(InvestmentRequest.date_submitted.desc()).all()
        
        requests_list = []
        for req in requests:
            requests_list.append({
                'id': req.id,
                'apartment_id': req.apartment_id,
                'apartment_title': req.apartment.title if req.apartment else None,
                'shares_requested': req.shares_requested,
                'total_amount': req.total_amount,
                'status': req.status,
                'status_arabic': req.status_arabic,
                'date_submitted': req.date_submitted.isoformat() if req.date_submitted else None,
                'admin_notes': req.admin_notes if req.status in ['rejected', 'documents_missing'] else None
            })
        
        return success_response(
            data={'requests': requests_list},
            message='تم جلب طلبات الاستثمار بنجاح'
        )
    except Exception as e:
        return error_response(message='حدث خطأ', details=str(e), status=500)


# ==================== Car Investment Request Endpoints ====================

@api_bp.route('/cars/investment-request', methods=['POST'])
@jwt_required()
def create_car_investment_request():
    """
    Create a new car investment request with KYC documents.
    
    Requires multipart/form-data with:
    - car_id: int (required)
    - shares_requested: int (required)
    - full_name: string (required)
    - phone: string (required)
    - national_id: string (required)
    - address: string (required)
    - date_of_birth: string (required) - format: YYYY-MM-DD
    - nationality: string (required)
    - occupation: string (required)
    - referred_by_code: string (optional) - referral code
    - id_document_front: file (required) - front of ID document
    - id_document_back: file (required) - back of ID document
    - proof_of_address: file (required) - proof of address document
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        # Check if request is multipart/form-data
        if not request.files and not request.form:
            return error_response(message='يجب إرسال البيانات بصيغة multipart/form-data', code='INVALID_CONTENT_TYPE')

        data = request.form
        files = request.files
        
        # Validate required fields
        required_fields = ['car_id', 'shares_requested', 'full_name', 'phone', 
                          'national_id', 'address', 'date_of_birth', 'nationality', 'occupation']
        
        for field in required_fields:
            if not data.get(field):
                return error_response(message=f'الحقل {field} مطلوب', code='MISSING_FIELDS')
        
        # Validate files
        required_files = ['id_document_front', 'id_document_back', 'proof_of_address']
        for file_field in required_files:
            if file_field not in files or files[file_field].filename == '':
                return error_response(message=f'الملف {file_field} مطلوب', code='MISSING_FILES')

        # Validate car exists
        car = Car.query.get(data['car_id'])
        if not car:
            return error_response(message='السيارة غير موجودة', code='CAR_NOT_FOUND', status=404)
        
        # Validate shares availability
        shares_requested = int(data['shares_requested'])
        if shares_requested <= 0:
            return error_response(message='عدد الحصص يجب أن يكون أكبر من صفر', code='INVALID_SHARES')
        
        if car.shares_available < shares_requested:
            return error_response(
                message=f'عدد الحصص المطلوبة ({shares_requested}) غير متاح. المتاح: {car.shares_available}',
                code='INSUFFICIENT_SHARES'
            )
        
        # Check for existing pending request
        existing_request = CarInvestmentRequest.query.filter_by(
            user_id=user.id,
            car_id=car.id,
            status='pending'
        ).first()
        
        if existing_request:
            return error_response(
                message='لديك طلب استثمار قيد الانتظار لهذه السيارة',
                code='DUPLICATE_REQUEST'
            )
        
        # Handle referral code
        referred_by_user_id = None
        if data.get('referred_by_code'):
            referral = CarReferralTree.query.filter_by(
                referral_code=data['referred_by_code'],
                car_id=car.id
            ).first()
            if referral:
                referred_by_user_id = referral.user_id
        
        # Save uploaded files
        from flask import current_app
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save ID front
        front_file = files['id_document_front']
        front_filename = secure_filename(f"car_{timestamp}_front_{user.id}_{front_file.filename}")
        front_file.save(os.path.join(upload_dir, front_filename))
        
        # Save ID back
        back_file = files['id_document_back']
        back_filename = secure_filename(f"car_{timestamp}_back_{user.id}_{back_file.filename}")
        back_file.save(os.path.join(upload_dir, back_filename))
        
        # Save proof of address
        address_file = files['proof_of_address']
        address_filename = secure_filename(f"car_{timestamp}_address_{user.id}_{address_file.filename}")
        address_file.save(os.path.join(upload_dir, address_filename))

        # Create car investment request
        car_inv_request = CarInvestmentRequest(
            user_id=user.id,
            car_id=car.id,
            shares_requested=shares_requested,
            referred_by_user_id=referred_by_user_id,
            full_name=data['full_name'],
            phone=data['phone'],
            national_id=data['national_id'],
            address=data['address'],
            date_of_birth=data['date_of_birth'],
            nationality=data['nationality'],
            occupation=data['occupation'],
            id_document_front=front_filename,
            id_document_back=back_filename,
            proof_of_address=address_filename,
            status='pending'
        )
        
        db.session.add(car_inv_request)
        db.session.commit()
        
        return success_response(
            data={
                'request_id': car_inv_request.id,
                'car_id': car_inv_request.car_id,
                'car_title': car.title,
                'shares_requested': car_inv_request.shares_requested,
                'total_amount': car_inv_request.total_amount,
                'status': car_inv_request.status,
                'status_arabic': car_inv_request.status_arabic,
                'date_submitted': car_inv_request.date_submitted.isoformat()
            },
            message='تم إرسال طلب الاستثمار في السيارة بنجاح',
            status=201
        )
    except ValueError as e:
        db.session.rollback()
        return error_response(message='قيمة غير صالحة للحقول الرقمية', code='INVALID_VALUE', details=str(e))
    except Exception as e:
        db.session.rollback()
        return error_response(message='حدث خطأ أثناء إنشاء الطلب', code='SERVER_ERROR', details=str(e), status=500)


@api_bp.route('/cars/investment-requests', methods=['GET'])
@jwt_required()
def get_user_car_investment_requests():
    """
    Get all car investment requests for the authenticated user.
    
    Query Parameters:
    - status: string (optional) - filter by status: pending, under_review, approved, rejected, documents_missing
    
    Returns list of car investment requests with details.
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        query = CarInvestmentRequest.query.filter_by(user_id=user.id)
        
        # Optional status filter
        status_filter = request.args.get('status')
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        requests = query.order_by(CarInvestmentRequest.date_submitted.desc()).all()
        
        requests_list = []
        for req in requests:
            requests_list.append({
                'id': req.id,
                'car_id': req.car_id,
                'car_title': req.car.title if req.car else None,
                'car_image': req.car.image if req.car else None,
                'shares_requested': req.shares_requested,
                'total_amount': req.total_amount,
                'status': req.status,
                'status_arabic': req.status_arabic,
                'date_submitted': req.date_submitted.isoformat() if req.date_submitted else None,
                'date_reviewed': req.date_reviewed.isoformat() if req.date_reviewed else None,
                'admin_notes': req.admin_notes if req.status in ['rejected', 'documents_missing'] else None,
                'missing_documents': req.missing_documents if req.status == 'documents_missing' else None,
                'contract_pdf': req.contract_pdf if req.status == 'approved' else None
            })
        
        return success_response(
            data={'requests': requests_list},
            message='تم جلب طلبات استثمار السيارات بنجاح'
        )
    except Exception as e:
        return error_response(message='حدث خطأ', code='SERVER_ERROR', details=str(e), status=500)


@api_bp.route('/cars/investment-requests/<int:request_id>', methods=['GET'])
@jwt_required()
def get_car_investment_request_detail(request_id):
    """
    Get detailed information about a specific car investment request.
    
    Path Parameters:
    - request_id: int (required) - ID of the investment request
    
    Returns full details of the investment request including KYC data.
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        inv_request = CarInvestmentRequest.query.filter_by(
            id=request_id,
            user_id=user.id
        ).first()
        
        if not inv_request:
            return error_response(
                message='طلب الاستثمار غير موجود',
                code='REQUEST_NOT_FOUND',
                status=404
            )
        
        return success_response(
            data={
                'id': inv_request.id,
                'car_id': inv_request.car_id,
                'car_title': inv_request.car.title if inv_request.car else None,
                'car_image': inv_request.car.image if inv_request.car else None,
                'car_location': inv_request.car.location if inv_request.car else None,
                'shares_requested': inv_request.shares_requested,
                'share_price': inv_request.car.share_price if inv_request.car else None,
                'total_amount': inv_request.total_amount,
                'monthly_income': (inv_request.car.monthly_rent / inv_request.car.total_shares) * inv_request.shares_requested if inv_request.car else 0,
                'status': inv_request.status,
                'status_arabic': inv_request.status_arabic,
                'date_submitted': inv_request.date_submitted.isoformat() if inv_request.date_submitted else None,
                'date_reviewed': inv_request.date_reviewed.isoformat() if inv_request.date_reviewed else None,
                'admin_notes': inv_request.admin_notes,
                'missing_documents': inv_request.missing_documents,
                'contract_pdf': inv_request.contract_pdf,
                'kyc_data': {
                    'full_name': inv_request.full_name,
                    'phone': inv_request.phone,
                    'national_id': inv_request.national_id,
                    'address': inv_request.address,
                    'date_of_birth': inv_request.date_of_birth,
                    'nationality': inv_request.nationality,
                    'occupation': inv_request.occupation
                }
            },
            message='تم جلب تفاصيل طلب الاستثمار بنجاح'
        )
    except Exception as e:
        return error_response(message='حدث خطأ', code='SERVER_ERROR', details=str(e), status=500)
