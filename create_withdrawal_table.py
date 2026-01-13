#!/usr/bin/env python3
"""
Create withdrawal_requests table
"""
import sys
import os
sys.path.insert(0, '/Users/ibrahimfakhry/Desktop/last/ipi')

from app import create_app
from app.models import db

app = create_app('development')

with app.app_context():
    print("Creating withdrawal_requests table...")
    
    # Create all tables (will only create new ones)
    db.create_all()
    
    print("✅ withdrawal_requests table created successfully!")
    
    # Verify table exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'withdrawal_requests' in tables:
        print("\n✓ Table 'withdrawal_requests' exists in database")
        
        # Show columns
        columns = inspector.get_columns('withdrawal_requests')
        print("\nColumns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        print("\n❌ Table 'withdrawal_requests' NOT found!")
