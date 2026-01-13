"""
Authentication routes
Handles user registration, login, and logout
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from app.models import db, User, EmailVerification
from app.utils.email_service import generate_otp, send_otp_email
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page - Step 1: Collect info and send OTP"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('user/register.html')
        
        if password != confirm_password:
            flash('كلمات المرور غير متطابقة', 'error')
            return render_template('user/register.html')
        
        if len(password) < 6:
            flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
            return render_template('user/register.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return render_template('user/register.html')
        
        # Generate OTP
        otp_code = generate_otp()
        
        # Delete any existing OTP for this email
        EmailVerification.query.filter_by(email=email).delete()
        
        # Hash password for temporary storage
        from werkzeug.security import generate_password_hash
        temp_password_hash = generate_password_hash(password)
        
        # Store OTP in database
        email_verification = EmailVerification(
            email=email,
            otp_code=otp_code,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            temp_name=name,
            temp_password_hash=temp_password_hash,
            temp_phone=phone
        )
        db.session.add(email_verification)
        db.session.commit()
        
        # Send OTP email
        try:
            send_otp_email(email, otp_code, name)
            
            # Store email in session for verification page
            session['pending_email'] = email
            
            flash('تم إرسال رمز التحقق إلى بريدك الإلكتروني', 'success')
            return redirect(url_for('auth.verify_email'))
        except Exception as e:
            flash('حدث خطأ أثناء إرسال البريد الإلكتروني. يرجى المحاولة مرة أخرى', 'error')
            print(f"Email error: {str(e)}")
            return render_template('user/register.html')
    
    return render_template('user/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user_views.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('البريد الإلكتروني وكلمة المرور مطلوبان', 'error')
            return render_template('user/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        # DEBUG: Log user details
        if user:
            print(f"DEBUG: User found - ID:{user.id}, Email:{user.email}, HasHash:{user.password_hash is not None}")
            if user.password_hash:
                print(f"DEBUG: Password hash length: {len(user.password_hash)}")
                print(f"DEBUG: Testing password '{password}'")
                password_check_result = user.check_password(password)
                print(f"DEBUG: Password check result: {password_check_result}")
        else:
            print(f"DEBUG: No user found with email: {email}")
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user_views.dashboard'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('user/login.html')


@bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Step 2: Verify OTP and create account"""
    pending_email = session.get('pending_email')
    
    if not pending_email:
        flash('الرجاء التسجيل أولاً', 'error')
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        
        if not otp_code:
            flash('الرجاء إدخال رمز التحقق', 'error')
            return render_template('user/verify_email.html', email=pending_email)
        
        # Find OTP record
        email_verification = EmailVerification.query.filter_by(
            email=pending_email,
            otp_code=otp_code,
            is_verified=False
        ).first()
        
        if not email_verification:
            flash('رمز التحقق غير صحيح', 'error')
            return render_template('user/verify_email.html', email=pending_email)
        
        # Check if expired
        if email_verification.expires_at < datetime.utcnow():
            flash('انتهت صلاحية رمز التحقق. الرجاء طلب رمز جديد', 'error')
            return render_template('user/verify_email.html', email=pending_email)
        
        # Create user
        user = User(
            name=email_verification.temp_name,
            email=pending_email,
            phone=email_verification.temp_phone,
            wallet_balance=0.0,
            email_verified=True
        )
        user.password_hash = email_verification.temp_password_hash
        
        # Mark OTP as verified
        email_verification.is_verified = True
        
        db.session.add(user)
        db.session.commit()
        
        # Clear session
        session.pop('pending_email', None)
        
        # Auto-login the user
        login_user(user, remember=True)
        
        flash('مرحباً بك! تم إنشاء حسابك بنجاح', 'success')
        return redirect(url_for('user_views.dashboard'))
    
    return render_template('user/verify_email.html', email=pending_email)


@bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP for web registration"""
    pending_email = session.get('pending_email')
    
    if not pending_email:
        flash('الرجاء التسجيل أولاً', 'error')
        return redirect(url_for('auth.register'))
    
    # Find existing OTP record
    email_verification = EmailVerification.query.filter_by(
        email=pending_email,
        is_verified=False
    ).first()
    
    if not email_verification:
        flash('الرجاء التسجيل مرة أخرى', 'error')
        return redirect(url_for('auth.register'))
    
    # Generate new OTP
    new_otp = generate_otp()
    email_verification.otp_code = new_otp
    email_verification.expires_at = datetime.utcnow() + timedelta(minutes=10)
    email_verification.created_at = datetime.utcnow()
    db.session.commit()
    
    # Send new OTP
    try:
        user_name = email_verification.temp_name or 'المستخدم'
        send_otp_email(pending_email, new_otp, user_name)
        flash('تم إرسال رمز تحقق جديد إلى بريدك الإلكتروني', 'success')
    except Exception as e:
        flash('حدث خطأ أثناء إرسال البريد الإلكتروني', 'error')
        print(f"Email error: {str(e)}")
    
    return redirect(url_for('auth.verify_email'))


@bp.route('/logout')
def logout():
    """Logout current user"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('main.index'))


@bp.route('/google/callback', methods=['POST'])
def google_callback():
    """Handle Google Sign-In callback for web users"""
    from app.auth_providers import verify_google_token
    from flask import jsonify
    
    try:
        data = request.get_json()
        
        if not data or not data.get('credential'):
            return jsonify({
                'success': False,
                'message': 'بيانات غير صالحة'
            }), 400
        
        # Verify Google token
        user_info = verify_google_token(data['credential'])
        
        if not user_info:
            return jsonify({
                'success': False,
                'message': 'فشل التحقق من حساب Google'
            }), 401
        
        # Extract user information
        google_user_id = user_info['user_id']
        email = user_info['email']
        name = user_info['name']
        
        # Check if user exists with Google auth
        user = User.query.filter_by(
            auth_provider='google',
            provider_user_id=google_user_id
        ).first()
        
        if not user:
            # Check if email exists with different auth method (account linking)
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Link existing account to Google
                user.link_social_account('google', google_user_id, email)
                db.session.commit()
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
                db.session.commit()
        
        # Log in the user using Flask-Login
        login_user(user, remember=True)
        
        # Determine redirect URL
        redirect_url = url_for('user_views.dashboard') if not user.is_admin else url_for('admin.dashboard')
        
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'redirect_url': redirect_url
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء تسجيل الدخول',
            'error': str(e)
        }), 500
