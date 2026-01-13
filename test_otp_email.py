"""
Test OTP Email Sending
"""
from app import create_app
from app.utils.email_service import send_otp_email
import random

app = create_app()

with app.app_context():
    # Generate test OTP
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    test_email = "ibrahimfakhreyams@gmail.com"  # Send to yourself for testing
    
    print(f"Sending OTP {otp} to {test_email}...")
    
    try:
        success = send_otp_email(test_email, otp)
        if success:
            print("✅ Email sent successfully!")
            print(f"Check your inbox at: {test_email}")
            print(f"OTP Code: {otp}")
        else:
            print("❌ Failed to send email")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
