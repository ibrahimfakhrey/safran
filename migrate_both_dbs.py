"""
Add referral_number column to both databases
"""
import sqlite3
import os

databases = [
    '/Users/ibrahimfakhry/Desktop/last/ipi/instance/app.db',
    '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'
]

for db_path in databases:
    if os.path.exists(db_path):
        print(f"\n=== Processing {os.path.basename(db_path)} ===")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'referral_number' not in columns:
            print("Adding referral_number column...")
            cursor.execute("ALTER TABLE users ADD COLUMN referral_number VARCHAR(20)")
            cursor.execute("CREATE index IF NOT EXISTS idx_users_referral_number ON users (referral_number)")
            conn.commit()
            print("✓ Column added")
        else:
            print("✓ Column already exists")
        
        # Generate referral numbers
        cursor.execute("SELECT id, name FROM users WHERE referral_number IS NULL OR referral_number = ''")
        users = cursor.fetchall()
        
        if users:
            print(f"Generating referral numbers for {len(users)} users...")
            for user_id, name in users:
                referral_number = f"IPI{str(user_id).zfill(6)}"
                cursor.execute("UPDATE users SET referral_number = ? WHERE id = ?", (referral_number, user_id))
                print(f"  {name}: {referral_number}")
            conn.commit()
            print("✓ Referral numbers generated")
        else:
            print("✓ All users have referral numbers")
        
        conn.close()
    else:
        print(f"❌ Database not found: {db_path}")

print("\n✅ All databases updated!")
