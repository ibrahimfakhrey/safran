"""
Check admin user in the database
"""
import sqlite3

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'

print("=== Checking Admin User in Database ===\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check for admin users
cursor.execute("SELECT id, name, email, is_admin, referral_number, password_hash FROM users WHERE email LIKE '%admin%' OR is_admin = 1")
admins = cursor.fetchall()

if admins:
    print(f"Found {len(admins)} admin user(s):\n")
    for admin_id, name, email, is_admin, ref_num, pwd_hash in admins:
        print(f"ID: {admin_id}")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Is Admin: {bool(is_admin)}")
        print(f"Referral Number: {ref_num}")
        print(f"Password Hash: {pwd_hash[:50] if pwd_hash else 'NULL'}...")
        
        # Test password
        from werkzeug.security import check_password_hash
        if pwd_hash:
            test_result = check_password_hash(pwd_hash, 'admin123')
            print(f"Password 'admin123' works: {test_result}")
        print()
else:
    print("❌ No admin users found!")
    
    # Show all users
    cursor.execute("SELECT id, name, email, is_admin FROM users LIMIT 10")
    all_users = cursor.fetchall()
    print(f"\nShowing first 10 users:")
    for user in all_users:
        print(f"  ID:{user[0]}, Name:{user[1]}, Email:{user[2]}, IsAdmin:{user[3]}")

conn.close()
