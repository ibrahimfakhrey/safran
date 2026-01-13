#!/usr/bin/env python3
"""
Generate referral numbers for users who don't have them
"""
import sys
import os
sys.path.insert(0, '/Users/ibrahimfakhry/Desktop/last/ipi')

from app import create_app
from app.models import db, User

app = create_app('development')

with app.app_context():
    print("Generating referral numbers for users without them...\n")
    
    # Get all users without referral numbers
    users_without_refs = User.query.filter(
        (User.referral_number == None) | (User.referral_number == '')
    ).all()
    
    if not users_without_refs:
        print("✅ All users already have referral numbers!")
    else:
        for user in users_without_refs:
            # Generate referral number: IPI + 6-digit user ID
            user.referral_number = f"IPI{str(user.id).zfill(6)}"
            print(f"✓ Generated {user.referral_number} for {user.name} ({user.email})")
        
        db.session.commit()
        print(f"\n✅ Generated {len(users_without_refs)} referral numbers")
    
    # Show all users with their referral numbers
    print("\n📋 All Users:")
    all_users = User.query.all()
    for user in all_users:
        print(f"  - {user.name}: {user.referral_number} ({user.email})")
