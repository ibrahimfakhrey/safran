"""
Quick fix: Delete the wrong admin user and restart app
"""
import sqlite3

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'

print("=== Fixing Admin User ===\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Delete admin@example.com if it exists
cursor.execute("DELETE FROM users WHERE email = 'admin@example.com'")
deleted = cursor.rowcount

if deleted > 0:
    print(f"✓ Deleted {deleted} users with email admin@example.com")
else:
    print("  No users with admin@example.com found")

# Verify correct admin exists
cursor.execute("SELECT id, email, is_admin FROM users WHERE email = 'admin@apartmentshare.com'")
admin = cursor.fetchone()

if admin:
    print(f"✓ Correct admin exists: {admin[1]} (ID: {admin[0]})")
    # Update to ensure it's admin
    cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (admin[0],))
else:
    print("❌ admin@apartmentshare.com not found!")
    from werkzeug.security import generate_password_hash
    password_hash = generate_password_hash('admin123')
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, wallet_balance, rewards_balance, is_admin, referral_number, date_joined)
        VALUES (?, ?, ?, 0.0, 0.0, 1, 'IPI000001', datetime('now'))
    """, ('Admin', 'admin@apartmentshare.com', password_hash))
    print("✓ Created admin@apartmentshare.com")

conn.commit()
conn.close()

print("\n✅ Fixed! Now restart the Flask app.")
