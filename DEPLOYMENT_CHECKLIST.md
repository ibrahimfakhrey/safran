"""
DEPLOYMENT CHECKLIST FOR OTP EMAIL VERIFICATION
================================================

Before uploading to production server, ensure:

1. ✅ INSTALL FLASK-MAIL ON SERVER
   ------------------------------
   SSH into your server and run:
   pip install Flask-Mail

2. ✅ RUN DATABASE MIGRATION ON SERVER
   -----------------------------------
   After uploading files, run:
   python3 migrate_email_verification.py
   
   This will:
   - Add email_verified column to users table
   - Create email_verifications table
   - Mark existing users as verified

3. ✅ VERIFY CONFIG.PY ON SERVER
   -----------------------------
   Make sure config.py has the correct email credentials:
   
   MAIL_SERVER = 'smtp.gmail.com'
   MAIL_PORT = 587
   MAIL_USE_TLS = True
   MAIL_USERNAME = 'ibrahimfakhreyams@gmail.com'
   MAIL_PASSWORD = 'lzyr svkj mynb gtsa'

4. ✅ TEST EMAIL SENDING ON SERVER
   -------------------------------
   After upload, test with:
   python3 test_otp_email.py
   
   You should receive an email at ibrahimfakhreyams@gmail.com

5. ✅ RESTART FLASK APP
   --------------------
   After migration and testing:
   - If using systemd: sudo systemctl restart your-app
   - If using PythonAnywhere: Reload web app
   - If manual: pkill python; python3 flask_app.py

6. ✅ TEST API ENDPOINTS
   ---------------------
   Test the OTP flow:
   
   curl -X POST https://your-domain.com/api/v1/auth/send-otp \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com"}'

7. ✅ CHECK REQUIREMENTS.TXT
   -------------------------
   Make sure Flask-Mail is in requirements.txt:
   Flask-Mail==0.10.0

FILES TO UPLOAD:
===============
✓ app/__init__.py (updated with Flask-Mail)
✓ app/models.py (added EmailVerification model)
✓ app/routes/api.py (added OTP endpoints)
✓ app/utils/email_service.py (NEW FILE - email template)
✓ config.py (updated email settings)
✓ migrate_email_verification.py (NEW FILE - migration script)
✓ requirements.txt (add Flask-Mail)
✓ EMAIL_OTP_API_PROMPT.md (for Flutter developer)
✓ CAR_INVESTMENT_API_PROMPT.md (for Flutter developer)

ENVIRONMENT VARIABLES (Optional but Recommended):
================================================
For better security, you can set these on your server:

export MAIL_USERNAME="ibrahimfakhreyams@gmail.com"
export MAIL_PASSWORD="lzyr svkj mynb gtsa"

Then config.py will use them automatically.

TESTING CHECKLIST:
==================
After deployment, test:

□ Send OTP to new email
□ Receive email with correct template
□ Verify OTP code works
□ Register new user successfully
□ Existing users can still login
□ Resend OTP functionality works
□ OTP expires after 10 minutes

COMMON ISSUES & SOLUTIONS:
==========================

Issue: Emails not sending
Solution: Check Gmail App Password is correct
         Check MAIL_SERVER, MAIL_PORT settings
         Verify server can connect to smtp.gmail.com:587

Issue: Database error on migration
Solution: Backup database first
         Run migration script again
         Check SQLite version

Issue: OTP endpoint returns 500 error
Solution: Check Flask-Mail is installed
         Check email_verifications table exists
         Check app/__init__.py has mail.init_app(app)

ROLLBACK PLAN:
==============
If something goes wrong:

1. Restore database backup
2. Remove new columns:
   ALTER TABLE users DROP COLUMN email_verified;
3. Remove email_verifications table:
   DROP TABLE email_verifications;
4. Restart app

SUCCESS INDICATORS:
===================
✓ Migration script runs without errors
✓ Test email sends successfully
✓ API endpoints return 200/201 status
✓ Email arrives with correct OTP
✓ OTP verification works
✓ New users can register
✓ Existing users still work

Need help? Email support@ipillarsi.com
