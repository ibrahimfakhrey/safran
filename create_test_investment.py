#!/usr/bin/env python3
"""
Create test investment for a@a.com from 1 month ago
This simulates an investment approved exactly 1 month ago to test automatic payout
"""
import sys
sys.path.insert(0, '/Users/ibrahimfakhry/Desktop/last/ipi')

from app import create_app
from app.models import db, User, Share, Apartment, InvestmentRequest
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

app = create_app('development')

with app.app_context():
    print("=== Creating Test Investment for a@a.com ===\n")
    
    # Get or create test user
    user = User.query.filter_by(email='a@a.com').first()
    if not user:
        print("❌ User a@a.com not found! Please create it first.")
        exit(1)
    
    print(f"✓ Found user: {user.name} ({user.email})")
    print(f"  Current wallet: {user.wallet_balance:,.2f} EGP\n")
    
    # Get first apartment
    apartment = Apartment.query.first()
    if not apartment:
        print("❌ No apartments found!")
        exit(1)
    
    print(f"✓ Using apartment: {apartment.title}")
    print(f"  Monthly rent: {apartment.monthly_rent:,.2f} EGP")
    print(f"  Total shares: {apartment.total_shares}\n")
    
    # Calculate dates
    approval_date = datetime.utcnow() - relativedelta(months=1)  # Exactly 1 month ago
    print(f"📅 Setting approval date to: {approval_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   (Exactly 1 month ago from now)\n")
    
    # Create investment request (approved)
    request = InvestmentRequest(
        user_id=user.id,
        apartment_id=apartment.id,
        shares_requested=1,
        full_name=user.name,
        phone=user.phone or '01000000000',
        national_id='12345678901234',
        address='Test Address',
        date_of_birth='1990-01-01',
        nationality='Egyptian',
        occupation='Test',
        status='approved',
        date_submitted=approval_date,
        date_reviewed=approval_date,  # Important: This is used for payout calculation
        reviewed_by=1  # Admin user
    )
    db.session.add(request)
    db.session.flush()
    
    # Create share
    share_price = apartment.total_price / apartment.total_shares
    share = Share(
        user_id=user.id,
        apartment_id=apartment.id,
        share_price=share_price,
        date_purchased=approval_date  # Set to 1 month ago
    )
    db.session.add(share)
    
    db.session.commit()
    
    print("✅ Test investment created successfully!\n")
    print("📊 Investment Details:")
    print(f"   User: {user.name}")
    print(f"   Apartment: {apartment.title}")
    print(f"   Shares: 1")
    print(f"   Share Price: {share_price:,.2f} EGP")
    print(f"   Monthly Income: {apartment.monthly_rent / apartment.total_shares:,.2f} EGP")
    print(f"   Approval Date: {approval_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Expected Payout: {apartment.monthly_rent / apartment.total_shares:,.2f} EGP (1 month)")
    print("\n✅ Ready for automatic payout test!")
