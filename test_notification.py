#!/usr/bin/env python3
"""
Test FCM Push Notification Script with detailed debugging
"""
import os
import json

print("=" * 60)
print("FCM Notification Debug Test")
print("=" * 60)

# Check the config file path
from config import Config
print(f"\n[CONFIG] FIREBASE_SERVICE_ACCOUNT = {Config.FIREBASE_SERVICE_ACCOUNT}")

# Check if file exists
file_path = Config.FIREBASE_SERVICE_ACCOUNT
print(f"[FILE] Exists: {os.path.exists(file_path)}")

if os.path.exists(file_path):
    print(f"[FILE] Size: {os.path.getsize(file_path)} bytes")
    with open(file_path, 'r') as f:
        data = json.load(f)
        print(f"[FILE] project_id: {data.get('project_id')}")
        print(f"[FILE] client_email: {data.get('client_email')}")
        print(f"[FILE] has private_key: {'private_key' in data}")

# Now test with Flask app context
from run import app
from app.models import Driver

with app.app_context():
    # Try to initialize Firebase directly
    print("\n[FIREBASE] Attempting to initialize...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, messaging
        
        # Check if already initialized
        try:
            existing_app = firebase_admin.get_app()
            print(f"[FIREBASE] Already initialized: {existing_app.name}")
            # Delete and reinitialize
            firebase_admin.delete_app(existing_app)
            print("[FIREBASE] Deleted existing app")
        except ValueError:
            print("[FIREBASE] No existing app")
        
        # Initialize fresh
        cred = credentials.Certificate(file_path)
        firebase_app = firebase_admin.initialize_app(cred)
        print(f"[FIREBASE] Initialized successfully: {firebase_app.name}")
        print(f"[FIREBASE] Project ID: {firebase_app.project_id}")
        
        # Get driver
        driver = Driver.query.first()
        print(f"\n[DRIVER] Name: {driver.name}")
        print(f"[DRIVER] FCM Token: {driver.fcm_token[:50] if driver.fcm_token else 'None'}...")
        
        if not driver.fcm_token:
            print("\n[ERROR] No FCM token!")
            exit()
        
        # Try sending
        print("\n[SEND] Creating message...")
        message = messaging.Message(
            notification=messaging.Notification(
                title="Test",
                body="Test notification"
            ),
            token=driver.fcm_token,
        )
        
        print("[SEND] Sending...")
        response = messaging.send(message)
        print(f"[SEND] SUCCESS! Response: {response}")
        
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
