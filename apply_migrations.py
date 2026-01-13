"""
Apply schema migrations to apartment_platform.db
Adds: referral_number column and referral_usages table
"""
import sqlite3
from werkzeug.security import generate_password_hash

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'

print("=" * 60)
print("APPLYING SCHEMA MIGRATIONS TO apartment_platform.db")
print("=" * 60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n[Step 1] Checking current schema...")

# Check users table
cursor.execute("PRAGMA table_info(users)")
user_columns = [col[1] for col in cursor.fetchall()]
print(f"  Users table has {len(user_columns)} columns")

# Check if referral_number exists
if 'referral_number' not in user_columns:
    print("\n[Step 2] Adding referral_number column to users table...")
    cursor.execute("ALTER TABLE users ADD COLUMN referral_number VARCHAR(20)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_referral_number ON users(referral_number)")
    print("  ✅ Column added successfully")
else:
    print("\n[Step 2] ✓ referral_number column already exists")

# Check if referral_usages table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='referral_usages'")
table_exists = cursor.fetchone() is not None

if not table_exists:
    print("\n[Step 3] Creating referral_usages table...")
    cursor.execute("""
        CREATE TABLE referral_usages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_user_id INTEGER NOT NULL,
            referee_user_id INTEGER NOT NULL,
            asset_type VARCHAR(20) NOT NULL,
            asset_id INTEGER NOT NULL,
            investment_amount FLOAT NOT NULL,
            shares_purchased INTEGER NOT NULL,
            date_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (referrer_user_id) REFERENCES users(id),
            FOREIGN KEY (referee_user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_referral_usages_referrer ON referral_usages(referrer_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_referral_usages_referee ON referral_usages(referee_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_referral_usages_date ON referral_usages(date_used)")
    print("  ✅ Table created successfully")
else:
    print("\n[Step 3] ✓ referral_usages table already exists")

# Generate referral numbers for users who don't have one
print("\n[Step 4] Generating referral numbers for users...")
cursor.execute("SELECT id, name, email FROM users WHERE referral_number IS NULL OR referral_number = ''")
users_without_ref = cursor.fetchall()

if users_without_ref:
    print(f"  Found {len(users_without_ref)} users without referral numbers")
    for user_id, name, email in users_without_ref:
        ref_num = f"IPI{str(user_id).zfill(6)}"
        cursor.execute("UPDATE users SET referral_number = ? WHERE id = ?", (ref_num, user_id))
        print(f"    - User #{user_id} ({name}): {ref_num}")
    print(f"  ✅ Generated {len(users_without_ref)} referral numbers")
else:
    print("  ✓ All users already have referral numbers")

# Ensure admin user exists with correct password
print("\n[Step 5] Ensuring admin user exists...")
cursor.execute("SELECT id, email, is_admin FROM users WHERE email = 'admin@apartmentshare.com'")
admin = cursor.fetchone()

if admin:
    admin_id, email, is_admin = admin
    print(f"  ✓ Admin user found (ID: {admin_id})")
    # Update password and ensure is_admin is true
    password_hash = generate_password_hash('admin123')
    cursor.execute("UPDATE users SET password_hash = ?, is_admin = 1 WHERE id = ?", (password_hash, admin_id))
    print("  ✅ Admin password updated to: admin123")
else:
    print("  Creating admin user...")
    password_hash = generate_password_hash('admin123')
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, wallet_balance, rewards_balance, is_admin, referral_number, date_joined)
        VALUES (?, ?, ?, 0.0, 0.0, 1, 'IPI000001', datetime('now'))
    """, ('Admin', 'admin@apartmentshare.com', password_hash))
    print("  ✅ Admin user created")

# Commit all changes
conn.commit()

# Show summary
print("\n[Summary] Database statistics:")
cursor.execute("SELECT COUNT(*) FROM users")
total_users = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM users WHERE referral_number IS NOT NULL")
users_with_ref = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM referral_usages")
total_usages = cursor.fetchone()[0]

print(f"  Total users: {total_users}")
print(f"  Users with referral numbers: {users_with_ref}")
print(f"  Referral usage records: {total_usages}")

conn.close()

print("\n" + "=" * 60)
print("✅ MIGRATION COMPLETE!")
print("=" * 60)
print("\nYour database is now ready with the new referral system!")
print("Admin login: admin@apartmentshare.com / admin123")
