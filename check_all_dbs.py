#!/usr/bin/env python3
"""
Check all database files and see which one has the admin user
"""
import sqlite3
import os

db_files = [
    '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db',
    '/Users/ibrahimfakhry/Desktop/last/ipi/instance/app.db',
    '/Users/ibrahimfakhry/Desktop/last/ipi/app.db',
]

print("=" * 60)
print("CHECKING ALL DATABASE FILES")
print("=" * 60)

for db_path in db_files:
    print(f"\n📁 {db_path}")
    
    if not os.path.exists(db_path):
        print("  ❌ File does not exist")
        continue
    
    print(f"  ✓ Exists ({os.path.getsize(db_path)} bytes)")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for users
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        print(f"  Total users: {total}")
        
        # Check for admin
        cursor.execute("SELECT id, email, is_admin FROM users WHERE email LIKE '%gmail%' OR email LIKE '%admin%' OR is_admin = 1")
        admins = cursor.fetchall()
        
        if admins:
            for admin_id, email, is_admin in admins:
                print(f"  Admin found: {email} (ID: {admin_id}, IsAdmin: {bool(is_admin)})")
        else:
            print("  No admin users found")
        
        conn.close()
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 60)
