#!/usr/bin/env python3
"""
Create fresh database with correct admin user
"""
import os
import sys
sys.path.insert(0, '/Users/ibrahimfakhry/Desktop/last/ipi')

# Set environment to prevent any override
os.environ.pop('ADMIN_EMAIL', None)
os.environ.pop('ADMIN_PASSWORD', None)

from app import create_app
from app.models import db, User

# Create app in development mode
app = create_app('development')

with app.app_context():
    print("Creating fresh database...")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Create all tables
    db.create_all()
    print("✓ All tables created")
    
    # Delete any existing admin users
    User.query.filter_by(is_admin=True).delete()
    db.session.commit()
    
    # Create admin with correct credentials
    admin = User(
        name='Admin',
        email='amsprog2022@gmail.com',
        is_admin=True,
        referral_number='IPI000001'
    )
    admin.set_password('Zo2lot@123')
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"\n✅ Admin user created!")
    print(f"  Email: {admin.email}")
    print(f"  Password: Zo2lot@123")
    print(f"  Referral Number: {admin.referral_number}")
    
    # Verify
    test = User.query.filter_by(email='amsprog2022@gmail.com').first()
    if test and test.check_password('Zo2lot@123'):
        print("\n✅ VERIFICATION PASSED - Login will work!")
    else:
        print("\n❌ Verification failed")
