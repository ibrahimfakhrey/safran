"""
Direct SQL script to generate referral numbers for existing users
"""
import sqlite3

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/instance/app.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Generating Referral Numbers ===\n")

# Get all users without referral numbers
cursor.execute("SELECT id, name, email FROM users WHERE referral_number IS NULL OR referral_number = ''")
users = cursor.fetchall()

if not users:
    print("✓ All users already have referral numbers")
else:
    print(f"Found {len(users)} users without referral numbers\n")
    
    for user_id, name, email in users:
        referral_number = f"IPI{str(user_id).zfill(6)}"
        cursor.execute("UPDATE users SET referral_number = ? WHERE id = ?", (referral_number, user_id))
        print(f"User #{user_id} ({name}): {referral_number}")
    
    conn.commit()
    print(f"\n✅ Generated referral numbers for {len(users)} users!")

# Show summary
cursor.execute("SELECT COUNT(*) FROM users")
total_users = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM users WHERE referral_number IS NOT NULL")
with_numbers = cursor.fetchone()[0]

print(f"\nSummary:")
print(f"Total users: {total_users}")
print(f"With referral numbers: {with_numbers}")

conn.close()
