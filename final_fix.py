#!/usr/bin/env python3
"""
FINAL FIX: Ensure admin user exists in apartment_platform.db and update config
"""
import sqlite3
from werkzeug.security import generate_password_hash
import os

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'

print("="*60)
print("FINAL DATABASE FIX")
print("="*60)

# Step 1: Verify database exists
if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
    exit(1)

print(f"\n✓ Database exists: {db_path}")
print(f"  Size: {os.path.getsize(db_path)} bytes")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Step 2: Check total users
cursor.execute("SELECT COUNT(*) FROM users")
total = cursor.fetchone()[0]
print(f"\n✓ Total users in database: {total}")

# Step 3: Delete any wrong admin users
cursor.execute("DELETE FROM users WHERE email IN ('admin@example.com', 'test@admin.com')")
if cursor.rowcount > 0:
    print(f"\n✓ Deleted {cursor.rowcount} incorrect admin users")

# Step 4: Check for correct admin
cursor.execute("SELECT id, email, is_admin, referral_number FROM users WHERE email = 'admin@apartmentshare.com'")
admin = cursor.fetchone()

if admin:
    admin_id, email, is_admin, ref_num = admin
    print(f"\n✓ Admin user exists:")
    print(f"  ID: {admin_id}")
    print(f"  Email: {email}")
    print(f"  Is Admin: {bool(is_admin)}")
    print(f"  Referral Number: {ref_num}")
    
    # Update password and ensure fields are correct
    password_hash = generate_password_hash('admin123')
    cursor.execute("""
        UPDATE users 
        SET password_hash = ?, is_admin = 1, referral_number = COALESCE(referral_number, 'IPI000001')
        WHERE id = ?
    """, (password_hash, admin_id))
    print(f"\n✓ Admin password and settings updated")
else:
    print(f"\n⚠️  Admin user not found. Creating new admin...")
    password_hash = generate_password_hash('admin123')
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, wallet_balance, rewards_balance, is_admin, referral_number, date_joined)
        VALUES ('Admin', 'admin@apartmentshare.com', ?, 0.0, 0.0, 1, 'IPI000001', datetime('now'))
    """, (password_hash,))
    print(f"✓ Admin user created")

conn.commit()

# Step 5: Verify admin can login
cursor.execute("SELECT id, email, password_hash FROM users WHERE email = 'admin@apartmentshare.com'")
admin_check = cursor.fetchone()

if admin_check:
    admin_id, email, pwd_hash = admin_check
    from werkzeug.security import check_password_hash
    if check_password_hash(pwd_hash, 'admin123'):
        print(f"\n✅ VERIFICATION PASSED!")
        print(f"   Admin login will work:")
        print(f"   Email: admin@apartmentshare.com")
        print(f"   Password: admin123")
    else:
        print(f"\n❌ Password verification FAILED!")
else:
    print(f"\n❌ Admin user still not found!")

conn.close()

print("\n" + "="*60)
print("FIX COMPLETE - Restart the Flask app now")
print("="*60)
