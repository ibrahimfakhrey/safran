"""
Create a test admin user with simple credentials
"""
import sqlite3
from werkzeug.security import generate_password_hash

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'

# Test user credentials
test_email = 'test@admin.com'
test_password = 'test123'
password_hash = generate_password_hash(test_password)

print("=== Creating Test Admin User ===\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if test user already exists
cursor.execute("SELECT id FROM users WHERE email = ?", (test_email,))
existing = cursor.fetchone()

if existing:
    print(f"User {test_email} already exists. Updating password...")
    cursor.execute("UPDATE users SET password_hash = ?, is_admin = 1, referral_number = 'IPI999999' WHERE email = ?", 
                  (password_hash, test_email))
else:
    print(f"Creating new user: {test_email}")
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, wallet_balance, rewards_balance, is_admin, referral_number, date_joined)
        VALUES (?, ?, ?, 0.0, 0.0, 1, 'IPI999999', datetime('now'))
    """, ('Test Admin', test_email, password_hash))

conn.commit()
conn.close()

print(f"\n✅ Test admin user ready!")
print(f"\n📧 Email: {test_email}")
print(f"🔑 Password: {test_password}")
print(f"\nTry logging in with these credentials!")
