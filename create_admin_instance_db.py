"""
Create admin in instance/app.db (the database Flask is actually using)
"""
import sqlite3
from werkzeug.security import generate_password_hash

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/instance/app.db'
admin_email = 'admin@apartmentshare.com'
admin_password = 'admin123'
password_hash = generate_password_hash(admin_password)

print(f"=== Creating Admin in instance/app.db ===\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if admin exists
cursor.execute("SELECT id, name FROM users WHERE email = ?", (admin_email,))
admin = cursor.fetchone()

if admin:
    print(f"✓ Admin exists (ID: {admin[0]}). Updating password...")
    cursor.execute("UPDATE users SET password_hash = ?, is_admin = 1 WHERE email = ?", 
                  (password_hash, admin_email))
else:
    print(f"Creating new admin user...")
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, wallet_balance, rewards_balance, is_admin, referral_number, date_joined)
        VALUES (?, ?, ?, 0.0, 0.0, 1, 'IPI000001', datetime('now'))
    """, ('Admin', admin_email, password_hash))

conn.commit()
conn.close()

print(f"\n✅ Admin ready in instance/app.db!")
print(f"📧 Email: {admin_email}")
print(f"🔑 Password: {admin_password}")
