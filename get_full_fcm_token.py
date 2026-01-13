#!/usr/bin/env python3
"""
Get full FCM token for a driver
Run: python3 get_full_fcm_token.py
"""
from app.models import Driver
from run import app

with app.app_context():
    drivers = Driver.query.all()

    print("=" * 80)
    print("FULL FCM TOKENS")
    print("=" * 80)

    for d in drivers:
        print(f"\nDriver: {d.name} (ID: {d.id})")
        print(f"Driver Number: {d.driver_number}")
        print(f"Phone: {d.phone}")
        print("-" * 80)
        if d.fcm_token:
            print("FCM Token (copy this full token):")
            print(d.fcm_token)
            print(f"\nToken Length: {len(d.fcm_token)} characters")
        else:
            print("FCM Token: NOT SET")
        print("=" * 80)
