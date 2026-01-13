"""
Script to reset admin password and ensure admin user exists
"""
import os
import sys
from app import create_app
from app.models import db, User

def reset_admin_password():
    print("=== Resetting Admin Password ===\n")
    
    # Initialize app context
    app = create_app('production')
    
    with app.app_context():
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@apartmentshare.com')
        admin_password = app.config.get('ADMIN_PASSWORD', 'admin123')
        
        print(f"Target Admin Email: {admin_email}")
        print(f"Target Password: {admin_password}")
        
        # Check if admin exists
        admin = User.query.filter_by(email=admin_email).first()
        
        if admin:
            print(f"✓ Found admin user: {admin.name} (ID: {admin.id})")
            # Reset password
            admin.set_password(admin_password)
            # Ensure is_admin is True
            admin.is_admin = True
            
            # Ensure referral number exists
            if not admin.referral_number:
                admin.generate_referral_number()
                print(f"✓ Generated referral number: {admin.referral_number}")
            
            db.session.commit()
            print("✅ Password reset successfully!")
            
        else:
            print("⚠️ Admin user not found. Creating new admin user...")
            admin = User(
                name='Admin',
                email=admin_email,
                is_admin=True,
                referral_number='IPI000001'
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created successfully!")

        # Verify login works (simulate)
        if admin.check_password(admin_password):
            print("\n✓ Verification: Password check PASSED")
        else:
            print("\n❌ Verification: Password check FAILED")

if __name__ == '__main__':
    # Add current directory to path
    sys.path.append(os.getcwd())
    reset_admin_password()
