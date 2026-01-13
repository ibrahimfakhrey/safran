#!/usr/bin/env python3
"""
Test automatic monthly payout system
Simulates investment approval and tests payout distribution
"""
import sys
sys.path.insert(0, '/Users/ibrahimfakhry/Desktop/last/ipi')

from app import create_app
from app.models import db, Share, CarShare
from app.utils.auto_payouts import process_automatic_payouts
from datetime import datetime, timedelta

app = create_app('development')

with app.app_context():
    print("=== Testing Automatic Monthly Payout System ===\n")
    
    # Get all shares
    shares = Share.query.all()
    car_shares = CarShare.query.all()
    
    print(f"Total Apartment Shares: {len(shares)}")
    print(f"Total Car Shares: {len(car_shares)}\n")
    
    if not shares and not car_shares:
        print("❌ No shares found! Please approve some investments first.")
        exit(1)
    
    # Show current share status
    print("📊 Current Share Status:")
    print("-" * 80)
    
    for share in shares[:5]:  # Show first 5
        approval_date = share.purchase_date
        last_payout = share.last_auto_payout_date
        
        print(f"  Share #{share.id}:")
        print(f"    User: {share.investor.name}")
        print(f"    Asset: {share.apartment.title}")
        print(f"    Approval Date: {approval_date.strftime('%Y-%m-%d') if approval_date else 'Unknown'}")
        print(f"    Last Payout: {last_payout.strftime('%Y-%m-%d') if last_payout else 'Never'}")
        print(f"    Wallet: {share.investor.wallet_balance:,.2f} EGP")
        print()
    
    # Run automatic payout
    print("\n🔄 Running automatic payout process...")
    print("=" * 80)
    
    result = process_automatic_payouts()
    
    print("\n📈 Results:")
    print(f"  ✅ Success: {result['success']}")
    print(f"  📦 Shares Processed: {result['shares_processed']}")
    print(f"  💰 Total Distributed: {result['total_distributed']:,.2f} EGP")
    
    if result['errors']:
        print(f"  ⚠️  Errors: {len(result['errors'])}")
        for error in result['errors'][:3]:
            print(f"      - {error}")
    
    print("\n" + "=" * 80)
    print("✅ Test completed!")
    
    # Show updated wallet balances
    print("\n💰 Updated Wallet Balances:")
    for share in shares[:5]:
        print(f"  {share.investor.name}: {share.investor.wallet_balance:,.2f} EGP")
