#!/usr/bin/env python3
"""
Test Google Auth directly to debug the issue
"""
import os
from config import Config

print("=" * 60)
print("Google Auth Debug Test")
print("=" * 60)

file_path = Config.FIREBASE_SERVICE_ACCOUNT
print(f"Service Account: {file_path}")
print(f"File Exists: {os.path.exists(file_path)}")

try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    
    # Load credentials
    print("\n[1] Loading service account credentials...")
    credentials = service_account.Credentials.from_service_account_file(
        file_path,
        scopes=['https://www.googleapis.com/auth/firebase.messaging']
    )
    print(f"    Service Account Email: {credentials.service_account_email}")
    print(f"    Project ID: {credentials.project_id}")
    
    # Try to get an access token
    print("\n[2] Requesting access token...")
    credentials.refresh(Request())
    print(f"    Token obtained: {credentials.token[:50]}...")
    print(f"    Token expiry: {credentials.expiry}")
    print("\n[SUCCESS] Google Auth is working!")
    
    # Now try FCM with this token
    print("\n[3] Testing FCM API directly...")
    import requests
    import json
    
    # Get driver FCM token
    from run import app
    from app.models import Driver
    
    with app.app_context():
        driver = Driver.query.first()
        fcm_token = driver.fcm_token
        print(f"    Driver: {driver.name}")
        print(f"    FCM Token: {fcm_token[:50]}...")
    
    # Send FCM request directly
    url = f"https://fcm.googleapis.com/v1/projects/{credentials.project_id}/messages:send"
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": {
            "token": fcm_token,
            "notification": {
                "title": "Test Direct",
                "body": "Direct FCM API test"
            }
        }
    }
    
    print(f"\n[4] Sending to FCM API...")
    print(f"    URL: {url}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text}")
    
    if response.status_code == 200:
        print("\n[SUCCESS] FCM notification sent!")
    else:
        print(f"\n[FAILED] FCM error: {response.text}")

except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
