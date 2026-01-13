#!/usr/bin/env python3
"""Test script to check if app starts correctly"""
import sys
import traceback

try:
    print("Importing create_app...")
    from app import create_app
    
    print("Creating app instance...")
    app = create_app('development')
    
    print("SUCCESS: App created successfully!")
    print(f"Registered blueprints: {[bp.name for bp in app.blueprints.values()]}")
    
    print("\nStarting server on http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
    
except ImportError as e:
    print(f"\nIMPORT ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)
