"""
Email service for sending OTP verification emails
Premium HTML/CSS templates in Arabic with brand colors
"""
from flask import current_app
from flask_mail import Mail, Message
import random
import string
from datetime import datetime, timedelta

mail = Mail()


def generate_otp(length=6):
    """Generate a random numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))


def get_otp_email_template(otp_code, user_name):
    """
    Premium Arabic HTML email template for OTP verification
    Uses brand colors: Gold (#D4AF37) and Navy Blue (#0A1128)
    """
    return f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>رمز التحقق - i pillars i</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0A1128 0%, #1e3a5f 100%);
            padding: 20px;
            direction: rtl;
        }}
        
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }}
        
        .header {{
            background: linear-gradient(135deg, #D4AF37 0%, #F4E5A1 100%);
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.3;
        }}
        
        .logo {{
            font-size: 36px;
            font-weight: 900;
            color: #0A1128;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            letter-spacing: 2px;
        }}
        
        .tagline {{
            font-size: 14px;
            color: #0A1128;
            font-weight: 600;
            position: relative;
            z-index: 1;
            opacity: 0.8;
        }}
        
        .content {{
            padding: 50px 40px;
            background: #ffffff;
        }}
        
        .greeting {{
            font-size: 24px;
            color: #0A1128;
            margin-bottom: 20px;
            font-weight: 700;
        }}
        
        .message {{
            font-size: 16px;
            color: #333333;
            line-height: 1.8;
            margin-bottom: 30px;
        }}
        
        .otp-container {{
            background: linear-gradient(135deg, #0A1128 0%, #1e3a5f 100%);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 5px 20px rgba(10, 17, 40, 0.2);
        }}
        
        .otp-label {{
            font-size: 14px;
            color: #D4AF37;
            font-weight: 600;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .otp-code {{
            font-size: 48px;
            font-weight: 900;
            color: #D4AF37;
            letter-spacing: 15px;
            margin: 15px 0;
            text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
            font-family: 'Courier New', monospace;
        }}
        
        .otp-validity {{
            font-size: 13px;
            color: #F4E5A1;
            margin-top: 15px;
        }}
        
        .warning-box {{
            background: #FFF9E6;
            border-right: 4px solid #D4AF37;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
        }}
        
        .warning-title {{
            font-size: 16px;
            color: #D4AF37;
            font-weight: 700;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .warning-text {{
            font-size: 14px;
            color: #666666;
            line-height: 1.6;
        }}
        
        .features {{
            margin: 40px 0;
        }}
        
        .feature-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 20px;
            gap: 15px;
        }}
        
        .feature-icon {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #D4AF37 0%, #F4E5A1 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-size: 20px;
        }}
        
        .feature-text {{
            flex: 1;
        }}
        
        .feature-title {{
            font-size: 16px;
            color: #0A1128;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .feature-description {{
            font-size: 14px;
            color: #666666;
            line-height: 1.5;
        }}
        
        .footer {{
            background: #0A1128;
            padding: 30px 40px;
            text-align: center;
        }}
        
        .footer-text {{
            font-size: 13px;
            color: #F4E5A1;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        
        .footer-links {{
            margin: 20px 0;
        }}
        
        .footer-link {{
            color: #D4AF37;
            text-decoration: none;
            margin: 0 15px;
            font-size: 13px;
            font-weight: 600;
        }}
        
        .footer-link:hover {{
            text-decoration: underline;
        }}
        
        .social-links {{
            margin-top: 20px;
        }}
        
        .social-link {{
            display: inline-block;
            width: 35px;
            height: 35px;
            background: #D4AF37;
            border-radius: 50%;
            margin: 0 5px;
            line-height: 35px;
            text-decoration: none;
            color: #0A1128;
            font-weight: 700;
        }}
        
        .copyright {{
            font-size: 12px;
            color: #888888;
            margin-top: 20px;
        }}
        
        @media only screen and (max-width: 600px) {{
            .content {{
                padding: 30px 20px;
            }}
            
            .otp-code {{
                font-size: 36px;
                letter-spacing: 10px;
            }}
            
            .feature-item {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <div class="logo">i pillars i</div>
            <div class="tagline">منصة الاستثمار العقاري الذكية</div>
        </div>
        
        <!-- Content -->
        <div class="content">
            <div class="greeting">مرحباً {user_name}! 👋</div>
            
            <div class="message">
                شكراً لانضمامك إلى <strong>i pillars i</strong>، منصة الاستثمار العقاري الرائدة. 
                للمتابعة وتفعيل حسابك، يرجى استخدام رمز التحقق أدناه:
            </div>
            
            <!-- OTP Box -->
            <div class="otp-container">
                <div class="otp-label">رمز التحقق الخاص بك</div>
                <div class="otp-code">{otp_code}</div>
                <div class="otp-validity">⏱ صالح لمدة 10 دقائق</div>
            </div>
            
            <!-- Warning -->
            <div class="warning-box">
                <div class="warning-title">
                    🔒 تنبيه أمني
                </div>
                <div class="warning-text">
                    لا تشارك هذا الرمز مع أي شخص. فريق i pillars i لن يطلب منك أبداً مشاركة رمز التحقق.
                    إذا لم تقم بطلب هذا الرمز، يرجى تجاهل هذه الرسالة.
                </div>
            </div>
            
            <!-- Features -->
            <div class="features">
                <div class="feature-item">
                    <div class="feature-icon">🏢</div>
                    <div class="feature-text">
                        <div class="feature-title">استثمر في العقارات</div>
                        <div class="feature-description">امتلك حصصاً في عقارات مختارة بعناية واحصل على دخل شهري ثابت</div>
                    </div>
                </div>
                
                <div class="feature-item">
                    <div class="feature-icon">💰</div>
                    <div class="feature-text">
                        <div class="feature-title">عوائد شهرية مضمونة</div>
                        <div class="feature-description">اربح من إيجارات العقارات كل شهر مباشرة في محفظتك</div>
                    </div>
                </div>
                
                <div class="feature-item">
                    <div class="feature-icon">📱</div>
                    <div class="feature-text">
                        <div class="feature-title">تابع استثماراتك</div>
                        <div class="feature-description">راقب محفظتك وعوائدك في الوقت الفعلي من أي مكان</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div class="footer-text">
                هذه رسالة تلقائية، يرجى عدم الرد عليها.
                <br>
                للدعم الفني، تواصل معنا على support@ipillarsi.com
            </div>
            
            <div class="footer-links">
                <a href="#" class="footer-link">الشروط والأحكام</a>
                <a href="#" class="footer-link">سياسة الخصوصية</a>
                <a href="#" class="footer-link">اتصل بنا</a>
            </div>
            
            <div class="social-links">
                <a href="#" class="social-link">f</a>
                <a href="#" class="social-link">t</a>
                <a href="#" class="social-link">in</a>
                <a href="#" class="social-link">ig</a>
            </div>
            
            <div class="copyright">
                © 2025 i pillars i. جميع الحقوق محفوظة.
            </div>
        </div>
    </div>
</body>
</html>
"""


def send_otp_email(email, otp_code, user_name="المستخدم"):
    """Send OTP verification email"""
    try:
        msg = Message(
            subject="رمز التحقق - i pillars i | Verification Code",
            recipients=[email],
            html=get_otp_email_template(otp_code, user_name)
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {email}: {str(e)}")
        return False


def send_welcome_email(email, user_name):
    """Send welcome email after successful registration"""
    welcome_html = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>مرحباً بك - i pillars i</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0A1128 0%, #1e3a5f 100%);
            padding: 20px;
            direction: rtl;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 20px;
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #D4AF37 0%, #F4E5A1 100%);
            padding: 40px;
            text-align: center;
        }}
        .logo {{
            font-size: 36px;
            font-weight: 900;
            color: #0A1128;
        }}
        .content {{
            padding: 40px;
        }}
        .title {{
            font-size: 28px;
            color: #0A1128;
            margin-bottom: 20px;
            font-weight: 700;
        }}
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #D4AF37 0%, #F4E5A1 100%);
            color: #0A1128;
            padding: 15px 40px;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 700;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">i pillars i</div>
        </div>
        <div class="content">
            <div class="title">🎉 مرحباً بك، {user_name}!</div>
            <p>تم تفعيل حسابك بنجاح. ابدأ رحلتك الاستثمارية الآن!</p>
            <a href="http://127.0.0.1:5000/market" class="btn">استكشف الفرص المتاحة</a>
        </div>
    </div>
</body>
</html>
"""
    
    try:
        msg = Message(
            subject="مرحباً بك في i pillars i 🎉",
            recipients=[email],
            html=welcome_html
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email to {email}: {str(e)}")
        return False
