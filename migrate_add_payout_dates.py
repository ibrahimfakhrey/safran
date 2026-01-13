#!/usr/bin/env python3
"""
Add last_auto_payout_date columns to shares and car_shares tables
"""
import sys
sys.path.insert(0, '/Users/ibrahimfakhry/Desktop/last/ipi')

from app import create_app
from app.models import db
from sqlalchemy import text

app = create_app('development')

with app.app_context():
    print("Adding last_auto_payout_date columns...")
    
    # Add column to shares table
    try:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE shares ADD COLUMN last_auto_payout_date DATETIME'))
            conn.commit()
        print("✅ Added last_auto_payout_date to shares table")
    except Exception as e:
        if 'duplicate column name' in str(e).lower():
            print("⚠️  shares.last_auto_payout_date already exists")
        else:
            print(f"❌ Error adding to shares: {e}")
    
    # Add column to car_shares table  
    try:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE car_shares ADD COLUMN last_auto_payout_date DATETIME'))
            conn.commit()
        print("✅ Added last_auto_payout_date to car_shares table")
    except Exception as e:
        if 'duplicate column name' in str(e).lower():
            print("⚠️  car_shares.last_auto_payout_date already exists")
        else:
            print(f"❌ Error adding to car_shares: {e}")
    
    print("\n✅ Migration complete!")
