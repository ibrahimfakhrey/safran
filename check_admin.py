"""
Check admin user details in the database
"""
import sqlite3
from werkzeug.security import check_password_hash

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'
test_password = 'admin123'

print("=== Checking Admin User ===\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all admin users
cursor.execute("SELECT id, name, email, is_admin, password_hash, referral_number FROM users WHERE is_admin = 1")
admins = cursor.fetchall()

if not admins:
    print("❌ No admin users found!")
else:
    for admin in admins:
        admin_id, name, email, is_admin, password_hash, ref_num = admin
        print(f"Admin User Found:")
        print(f"  ID: {admin_id}")
        print(f"  Name: {name}")
        print(f"  Email: {email}")
        print(f"  Is Admin: {bool(is_admin)}")
        print(f"  Referral Number: {ref_num}")
        print(f"  Password Hash: {password_hash[:50]}...")
        
        # Test if password matches
        if check_password_hash(password_hash, test_password):
            print(f"  ✅ Password '{test_password}' is CORRECT!")
        else:
            print(f"  ❌ Password '{test_password}' does NOT match!")
        print()

# Check all users with email containing 'admin'
cursor.execute("SELECT id, name, email, is_admin FROM users WHERE email LIKE '%admin%'")
all_admins = cursor.fetchall()

if len(all_admins) > 1:
    print("⚠️ Multiple admin-related users found:")
    for user in all_admins:
        print(f"  - ID:{user[0]}, Name:{user[1]}, Email:{user[2]}, IsAdmin:{user[3]}")

conn.close()
