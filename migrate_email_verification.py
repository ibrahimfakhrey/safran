"""
Database migration script to add email verification support
Adds email_verified column to users table and creates email_verifications table
"""
import sqlite3
import os

# Get database path
db_path = 'instance/app.db'

if not os.path.exists(db_path):
    print("Database not found. Please run the app first to create the database.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Adding Email Verification Support ===\n")

try:
    # Add email_verified column to users table
    print("1. Adding email_verified column to users table...")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0")
        # Set existing users as verified
        cursor.execute("UPDATE users SET email_verified = 1")
        print("   ✓ Added email_verified column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("   ℹ email_verified column already exists")
        else:
            raise
    
    # Create email_verifications table
    print("\n2. Creating email_verifications table...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(120) NOT NULL,
                otp_code VARCHAR(10) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_verified BOOLEAN DEFAULT 0,
                attempts INTEGER DEFAULT 0,
                temp_name VARCHAR(100),
                temp_password_hash VARCHAR(200),
                temp_phone VARCHAR(20)
            )
        """)
        
        # Create index on email
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_email_verifications_email 
            ON email_verifications(email)
        """)
        
        print("   ✓ Created email_verifications table")
    except sqlite3.Error as e:
        print(f"   ⚠ Table may already exist: {e}")
    
    # Commit changes
    conn.commit()
    print("\n✅ Migration completed successfully!")
    print("\nNext steps:")
    print("1. Install Flask-Mail: pip install Flask-Mail")
    print("2. Set email credentials in config.py or environment variables:")
    print("   MAIL_USERNAME=your-email@gmail.com")
    print("   MAIL_PASSWORD=your-app-password")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Migration failed: {e}")
    raise
finally:
    conn.close()
