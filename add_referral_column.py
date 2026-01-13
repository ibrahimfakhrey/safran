"""
Manual database migration to add referral_number column
"""
import sqlite3
import os

# Database path
db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/instance/app.db'

if os.path.exists(db_path):
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'referral_number' not in columns:
        print("Adding referral_number column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN referral_number VARCHAR(20)")
        cursor.execute("CREATE index idx_users_referral_number ON users (referral_number)")
        conn.commit()
        print("✓ Column added successfully")
    else:
        print("✓ Column already exists")
    
    # Create referral_usages table
    print("\nCreating referral_usages table...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referral_usages (
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_referral_usages_referrer ON referral_usages (referrer_user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_referral_usages_referee ON referral_usages (referee_user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_referral_usages_date ON referral_usages (date_used)")
        conn.commit()
        print("✓ Table created successfully")
    except Exception as e:
        print(f"Note: {e}")
    
    conn.close()
    print("\n✅ Database migration complete!")
else:
    print(f"❌ Database not found at {db_path}")
