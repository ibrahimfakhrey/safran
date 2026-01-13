"""
Database Migration Script - Fleet Manager & Driver Location Tracking
Adds:
1. is_fleet_manager field to users table
2. Location tracking fields to drivers table
"""
import sqlite3
import os

def migrate_database():
    """Run migration on database"""

    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        # Try alternative path
        db_path = os.path.join(os.path.dirname(__file__), 'apartment_platform.db')
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path} either")
            return False

    print(f"Migrating database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # ============= USER TABLE - Add is_fleet_manager =============
        print("\n1. Adding is_fleet_manager column to users table...")

        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'is_fleet_manager' not in columns:
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN is_fleet_manager BOOLEAN DEFAULT 0
            """)
            print("   - Added is_fleet_manager column")
        else:
            print("   - is_fleet_manager column already exists")

        # ============= DRIVERS TABLE - Add location tracking fields =============
        print("\n2. Adding location tracking columns to drivers table...")

        cursor.execute("PRAGMA table_info(drivers)")
        columns = [col[1] for col in cursor.fetchall()]

        new_columns = [
            ('current_latitude', 'FLOAT'),
            ('current_longitude', 'FLOAT'),
            ('current_location_updated_at', 'DATETIME'),
            ('is_online', 'BOOLEAN DEFAULT 0'),
            ('last_seen_at', 'DATETIME')
        ]

        for col_name, col_type in new_columns:
            if col_name not in columns:
                cursor.execute(f"""
                    ALTER TABLE drivers
                    ADD COLUMN {col_name} {col_type}
                """)
                print(f"   - Added {col_name} column")
            else:
                print(f"   - {col_name} column already exists")

        # Commit changes
        conn.commit()
        print("\n Migration completed successfully!")

        return True

    except Exception as e:
        print(f"\n Error during migration: {str(e)}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 50)
    print("Fleet Manager & Location Tracking Migration")
    print("=" * 50)
    migrate_database()
