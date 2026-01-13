#!/usr/bin/env python3
"""
Script to check FCM tokens for all drivers
Run: python3 check_fcm.py
"""
from app.models import Driver
from run import app

with app.app_context():
    drivers = Driver.query.all()

    if not drivers:
        print("No drivers found in database")
    else:
        print("=" * 60)
        print("FCM Token Status for All Drivers")
        print("=" * 60)

        for d in drivers:
            print(f"\nDriver: {d.name}")
            print(f"  ID: {d.id}")
            print(f"  Driver Number: {d.driver_number}")
            print(f"  Phone: {d.phone}")
            print(f"  Is Verified: {d.is_verified}")
            print(f"  Is Approved: {d.is_approved}")

            if d.fcm_token:
                print(f"  FCM Token: {d.fcm_token[:60]}...")
                print(f"  Token Length: {len(d.fcm_token)}")
            else:
                print(f"  FCM Token: NOT SET")

            print(f"  Token Updated At: {d.fcm_token_updated_at}")
            print("-" * 40)

        print(f"\nTotal Drivers: {len(drivers)}")
        with_token = sum(1 for d in drivers if d.fcm_token)
        print(f"Drivers with FCM Token: {with_token}")
        print(f"Drivers without FCM Token: {len(drivers) - with_token}")
