"""
Test login directly to see what's happening
"""
import sqlite3
from werkzeug.security import check_password_hash

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'
test_email = 'admin@apartmentshare.com'
test_password = 'admin123'

print(f"=== Testing Login for {test_email} ===\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get user by email (case insensitive search)
cursor.execute("SELECT id, name, email, password_hash, is_admin FROM users WHERE LOWER(email) = LOWER(?)", (test_email,))
user = cursor.fetchone()

if not user:
    print(f"❌ No user found with email: {test_email}")
    
    # Check what emails exist
    cursor.execute("SELECT email FROM users LIMIT 10")
    emails = cursor.fetchall()
    print(f"\nEmails in database:")
    for email in emails:
        print(f"  - {email[0]}")
else:
    user_id, name, email, password_hash, is_admin = user
    print(f"✓ User found:")
    print(f"  ID: {user_id}")
    print(f"  Name: {name}")
    print(f"  Email: {email}")  # Print exact email as stored
    print(f"  Is Admin: {bool(is_admin)}")
    print(f"\nPassword Test:")
    print(f"  Testing password: '{test_password}'")
    
    if check_password_hash(password_hash, test_password):
        print(f"  ✅ Password MATCHES!")
    else:
        print(f"  ❌ Password DOES NOT match!")
        print(f"\n  Trying some variations:")
        for variant in ['Admin123', 'ADMIN123', 'admin', '']:
            if check_password_hash(password_hash, variant):
                print(f"    ✓ Password is actually: '{variant}'")

conn.close()
