#!/usr/bin/env python3
"""
Create test referral usage data for admin dashboard
"""
import sys
import os
sys.path.insert(0, '/Users/ibrahimfakhry/Desktop/last/ipi')

from app import create_app
from app.models import db, User, ReferralUsage, Apartment, Car
from datetime import datetime, timedelta
import random

app = create_app('development')

with app.app_context():
    print("Creating test referral usage data...\n")
    
    # Get users (excluding admin)
    users = User.query.filter(User.is_admin == False).all()
    apartments = Apartment.query.all()
    cars = Car.query.all()
    
    if len(users) < 2:
        print("❌ Need at least 2 non-admin users. Please run seed_data.py first")
        exit(1)
    
    # Clear existing referral usages
    ReferralUsage.query.delete()
    db.session.commit()
    
    # Create sample referral usages
    referrals_created = 0
    
    # Ahmed (user 1) refers Fatima (user 2) for apartment
    if len(users) >= 2 and len(apartments) > 0:
        referral1 = ReferralUsage(
            referrer_user_id=users[0].id,  # Ahmed
            referee_user_id=users[1].id,   # Fatima
            asset_type='apartment',
            asset_id=apartments[0].id,
            investment_amount=500000,
            shares_purchased=5,
            date_used=datetime.utcnow() - timedelta(days=5)
        )
        db.session.add(referral1)
        referrals_created += 1
        print(f"✓ {users[0].name} referred {users[1].name} for apartment")
    
    # Fatima refers Ahmed for a car
    if len(users) >= 2 and len(cars) > 0:
        referral2 = ReferralUsage(
            referrer_user_id=users[1].id,  # Fatima
            referee_user_id=users[0].id,   # Ahmed
            asset_type='car',
            asset_id=cars[0].id,
            investment_amount=450000,
            shares_purchased=10,
            date_used=datetime.utcnow() - timedelta(days=3)
        )
        db.session.add(referral2)
        referrals_created += 1
        print(f"✓ {users[1].name} referred {users[0].name} for car")
    
    # Ahmed refers Mahmoud for another apartment
    if len(users) >= 3 and len(apartments) > 1:
        referral3 = ReferralUsage(
            referrer_user_id=users[0].id,  # Ahmed
            referee_user_id=users[2].id,   # Mahmoud
            asset_type='apartment',
            asset_id=apartments[1].id,
            investment_amount=200000,
            shares_purchased=2,
            date_used=datetime.utcnow() - timedelta(days=1)
        )
        db.session.add(referral3)
        referrals_created += 1
        print(f"✓ {users[0].name} referred {users[2].name} for apartment")
    
    # Add more random referrals
    if len(users) >= 3 and len(apartments) > 2:
        referral4 = ReferralUsage(
            referrer_user_id=users[1].id,
            referee_user_id=users[2].id,
            asset_type='apartment',
            asset_id=apartments[2].id,
            investment_amount=800000,
            shares_purchased=8,
            date_used=datetime.utcnow() - timedelta(hours=12)
        )
        db.session.add(referral4)
        referrals_created += 1
        print(f"✓ {users[1].name} referred {users[2].name} for apartment")
    
    db.session.commit()
    
    print(f"\n✅ Created {referrals_created} test referral usages")
    print("\nNow you can view them at: http://127.0.0.1:5001/admin/referrals-analytics")
