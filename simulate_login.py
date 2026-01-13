"""
Simulate the exact login flow that Flask uses
"""
import sqlite3

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'
test_email = 'admin@apartmentshare.com'
test_password = 'admin123'

print("=== Simulating Flask Login Flow ===\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# This is what Flask does: filter_by(email=email).first()
cursor.execute("SELECT id, name, email, password_hash, is_admin FROM users WHERE email = ?", (test_email,))
user = cursor.fetchone()

print(f"Step 1: Query user by email '{test_email}'")
if user:
    user_id, name, email, password_hash, is_admin = user
    print(f"  ✓ User found: ID={user_id}, Name={name}, Email={email}")
    print(f"  ✓ Is Admin: {bool(is_admin)}")
    print(f"  ✓ Password hash exists: {password_hash is not None}")
    print(f"  ✓ Password hash length: {len(password_hash) if password_hash else 0}")
    
    print(f"\nStep 2: Check password")
    from werkzeug.security import check_password_hash
    
    if password_hash:
        result = check_password_hash(password_hash, test_password)
        print(f"  Password check result: {result}")
        
        if result:
            print(f"\n✅ LOGIN SHOULD SUCCEED!")
        else:
            print(f"\n❌ LOGIN SHOULD FAIL - password doesn't match")
    else:
        print(f"  ❌ No password hash stored!")
else:
    print(f"  ❌ User not found")

# Also check if there are any NULL password_hashes
cursor.execute("SELECT id, name, email FROM users WHERE password_hash IS NULL OR password_hash = ''")
null_users = cursor.fetchall()
if null_users:
    print(f"\n⚠️ Warning: {len(null_users)} users have NULL/empty password_hash:")
    for u in null_users:
        print(f"  - ID:{u[0]}, Name:{u[1]}, Email:{u[2]}")

conn.close()
