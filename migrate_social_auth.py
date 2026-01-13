"""
Database Migration: Add Social Authentication Fields to User Model
Adds auth_provider, provider_user_id, and provider_email columns
"""
import sqlite3
import os

def migrate():
    """Run migration to add social auth fields"""
    
    # Path to database
    db_path = os.path.join(os.path.dirname(__file__), 'apartment_platform.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    print(f"🔄 Starting database migration for social authentication...")
    print(f"📂 Database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'auth_provider' in columns:
            print("✅ Migration already completed. Columns exist.")
            conn.close()
            return
        
        print("\n📝 Adding new columns to users table...")
        
        # Add auth_provider column
        print("   → Adding auth_provider...")
        cursor.execute(
            "ALTER TABLE users ADD COLUMN auth_provider VARCHAR(20) DEFAULT 'email'"
        )
        
        # Add provider_user_id column
        print("   → Adding provider_user_id...")
        cursor.execute(
            "ALTER TABLE users ADD COLUMN provider_user_id VARCHAR(255)"
        )
        
        # Add provider_email column
        print("   → Adding provider_email...")
        cursor.execute(
            "ALTER TABLE users ADD COLUMN provider_email VARCHAR(255)"
        )
        
        # Create indexes
        print("\n📝 Creating indexes...")
        try:
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_auth_provider ON users(auth_provider)"
            )
            print("   → Created idx_users_auth_provider")
            
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_provider_user_id ON users(provider_user_id)"
            )
            print("   → Created idx_users_provider_user_id")
            
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_provider_lookup ON users(auth_provider, provider_user_id)"
            )
            print("   → Created idx_provider_lookup")
            
        except Exception as e:
            print(f"⚠️  Index creation warning: {e}")
        
        conn.commit()
        
        print("\n✅ Migration completed successfully!")
        print("\n📊 Verifying migration...")
        
        # Verify columns exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        required_columns = ['auth_provider', 'provider_user_id', 'provider_email']
        for col in required_columns:
            if col in columns:
                print(f"   ✓ {col} column added")
            else:
                print(f"   ✗ {col} column MISSING")
        
        # Check existing users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\n👥 Total users in database: {user_count}")
        
        if user_count > 0:
            print("   All existing users have auth_provider='email' by default")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
