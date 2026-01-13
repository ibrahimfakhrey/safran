#!/usr/bin/env python3
"""
Database Migration Script for PythonAnywhere
Run this script to add missing columns/tables to the database.

Usage: python migrate_db.py
"""

import sqlite3
import os
import sys

# Try multiple possible database locations
POSSIBLE_DB_PATHS = [
    # PythonAnywhere paths - app.db
    '/home/amsfiles/ipi/instance/app.db',
    '/home/amsfiles/ipi/app.db',
    '/home/amsfiles/instance/app.db',
    # PythonAnywhere paths - ipi.db
    '/home/amsfiles/ipi/instance/ipi.db',
    '/home/amsfiles/ipi/ipi.db',
    '/home/amsfiles/instance/ipi.db',
    # Local development paths
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'ipi.db'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ipi.db'),
]


def find_database():
    """Find the database file"""
    for path in POSSIBLE_DB_PATHS:
        if os.path.exists(path):
            return path
    return None


def get_existing_columns(cursor, table_name):
    """Get list of existing columns in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def table_exists(cursor, table_name):
    """Check if a table exists"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


def add_column_if_missing(cursor, table_name, column_name, column_type, default=None):
    """Add a column to table if it doesn't exist"""
    existing = get_existing_columns(cursor, table_name)

    if column_name in existing:
        print(f"    [exists] {column_name}")
        return False

    sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
    if default is not None:
        sql += f" DEFAULT {default}"

    cursor.execute(sql)
    print(f"    [ADDED] {column_name}")
    return True


def create_table_if_missing(cursor, table_name, create_sql):
    """Create a table if it doesn't exist"""
    if table_exists(cursor, table_name):
        print(f"  Table '{table_name}' exists")
        return False

    cursor.execute(create_sql)
    print(f"  [CREATED] Table '{table_name}'")
    return True


def migrate():
    """Run all migrations"""
    db_path = find_database()

    if not db_path:
        print("ERROR: Could not find database file!")
        print("Searched in:")
        for path in POSSIBLE_DB_PATHS:
            print(f"  - {path}")
        print("\nPlease specify the correct path by editing POSSIBLE_DB_PATHS in this script.")
        return False

    print(f"Found database at: {db_path}")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # ============================================
        # USERS TABLE
        # ============================================
        print("\n[users table]")
        if table_exists(cursor, 'users'):
            add_column_if_missing(cursor, 'users', 'email_verified', 'BOOLEAN', '0')
            add_column_if_missing(cursor, 'users', 'rewards_balance', 'FLOAT', '0.0')
            add_column_if_missing(cursor, 'users', 'auth_provider', "VARCHAR(20)", "'email'")
            add_column_if_missing(cursor, 'users', 'provider_user_id', 'VARCHAR(255)', 'NULL')
            add_column_if_missing(cursor, 'users', 'provider_email', 'VARCHAR(255)', 'NULL')
            add_column_if_missing(cursor, 'users', 'referral_number', 'VARCHAR(20)', 'NULL')
            add_column_if_missing(cursor, 'users', 'phone', 'VARCHAR(20)', 'NULL')
            add_column_if_missing(cursor, 'users', 'national_id', 'VARCHAR(50)', 'NULL')
            add_column_if_missing(cursor, 'users', 'address', 'TEXT', 'NULL')
            add_column_if_missing(cursor, 'users', 'date_of_birth', 'VARCHAR(20)', 'NULL')
            add_column_if_missing(cursor, 'users', 'nationality', 'VARCHAR(50)', 'NULL')
            add_column_if_missing(cursor, 'users', 'occupation', 'VARCHAR(100)', 'NULL')
            add_column_if_missing(cursor, 'users', 'id_document_path', 'VARCHAR(300)', 'NULL')
            add_column_if_missing(cursor, 'users', 'fcm_token', 'VARCHAR(255)', 'NULL')
        else:
            print("  Table does not exist - will be created by Flask")

        # ============================================
        # SHARES TABLE
        # ============================================
        print("\n[shares table]")
        if table_exists(cursor, 'shares'):
            add_column_if_missing(cursor, 'shares', 'last_auto_payout_date', 'DATETIME', 'NULL')
        else:
            print("  Table does not exist - will be created by Flask")

        # ============================================
        # DRIVERS TABLE
        # ============================================
        print("\n[drivers table]")
        if table_exists(cursor, 'drivers'):
            add_column_if_missing(cursor, 'drivers', 'driver_number', 'VARCHAR(20)', 'NULL')
            add_column_if_missing(cursor, 'drivers', 'password_hash', 'VARCHAR(256)', 'NULL')
            add_column_if_missing(cursor, 'drivers', 'password_plain', 'VARCHAR(100)', 'NULL')
            add_column_if_missing(cursor, 'drivers', 'fcm_token', 'VARCHAR(500)', 'NULL')
            add_column_if_missing(cursor, 'drivers', 'fcm_token_updated_at', 'DATETIME', 'NULL')
            add_column_if_missing(cursor, 'drivers', 'is_verified', 'BOOLEAN', '0')
            add_column_if_missing(cursor, 'drivers', 'photo_filename', 'VARCHAR(300)', 'NULL')
            add_column_if_missing(cursor, 'drivers', 'license_filename', 'VARCHAR(300)', 'NULL')
            add_column_if_missing(cursor, 'drivers', 'rating', 'FLOAT', '0.0')
            add_column_if_missing(cursor, 'drivers', 'completed_missions', 'INTEGER', '0')
            add_column_if_missing(cursor, 'drivers', 'is_approved', 'BOOLEAN', '0')
            add_column_if_missing(cursor, 'drivers', 'email', 'VARCHAR(120)', 'NULL')
            add_column_if_missing(cursor, 'drivers', 'created_at', 'DATETIME', 'NULL')
        else:
            print("  Table does not exist - will be created by Flask")

        # ============================================
        # MISSIONS TABLE
        # ============================================
        print("\n[missions table]")
        if table_exists(cursor, 'missions'):
            # Mission type and source
            add_column_if_missing(cursor, 'missions', 'mission_type', "VARCHAR(20)", "'admin_assigned'")
            add_column_if_missing(cursor, 'missions', 'app_name', 'VARCHAR(50)', 'NULL')
            add_column_if_missing(cursor, 'missions', 'expected_cost', 'FLOAT', 'NULL')

            # Route details
            add_column_if_missing(cursor, 'missions', 'from_location', 'VARCHAR(200)', "''")
            add_column_if_missing(cursor, 'missions', 'to_location', 'VARCHAR(200)', "''")
            add_column_if_missing(cursor, 'missions', 'distance_km', 'FLOAT', '0')

            # Timing
            add_column_if_missing(cursor, 'missions', 'mission_date', 'DATE', 'NULL')
            add_column_if_missing(cursor, 'missions', 'start_time', 'TIME', 'NULL')
            add_column_if_missing(cursor, 'missions', 'end_time', 'TIME', 'NULL')

            # Financial details
            add_column_if_missing(cursor, 'missions', 'total_revenue', 'FLOAT', '0')
            add_column_if_missing(cursor, 'missions', 'fuel_cost', 'FLOAT', '0')
            add_column_if_missing(cursor, 'missions', 'driver_fees', 'FLOAT', '0')
            add_column_if_missing(cursor, 'missions', 'company_profit', 'FLOAT', '0')

            # Status and workflow
            add_column_if_missing(cursor, 'missions', 'status', "VARCHAR(20)", "'pending'")
            add_column_if_missing(cursor, 'missions', 'notes', 'TEXT', 'NULL')

            # Approval workflow
            add_column_if_missing(cursor, 'missions', 'is_approved', 'BOOLEAN', '0')
            add_column_if_missing(cursor, 'missions', 'approved_at', 'DATETIME', 'NULL')
            add_column_if_missing(cursor, 'missions', 'can_start', 'BOOLEAN', '0')

            # Timestamps
            add_column_if_missing(cursor, 'missions', 'created_at', 'DATETIME', 'NULL')
            add_column_if_missing(cursor, 'missions', 'started_at', 'DATETIME', 'NULL')
            add_column_if_missing(cursor, 'missions', 'ended_at', 'DATETIME', 'NULL')
            add_column_if_missing(cursor, 'missions', 'completed_at', 'DATETIME', 'NULL')

            # GPS Location tracking
            add_column_if_missing(cursor, 'missions', 'start_latitude', 'FLOAT', 'NULL')
            add_column_if_missing(cursor, 'missions', 'start_longitude', 'FLOAT', 'NULL')
            add_column_if_missing(cursor, 'missions', 'end_latitude', 'FLOAT', 'NULL')
            add_column_if_missing(cursor, 'missions', 'end_longitude', 'FLOAT', 'NULL')
        else:
            print("  Table does not exist - creating it...")
            cursor.execute('''
                CREATE TABLE missions (
                    id INTEGER PRIMARY KEY,
                    fleet_car_id INTEGER NOT NULL,
                    driver_id INTEGER NOT NULL,
                    mission_type VARCHAR(20) DEFAULT 'admin_assigned',
                    app_name VARCHAR(50),
                    expected_cost FLOAT,
                    from_location VARCHAR(200) NOT NULL DEFAULT '',
                    to_location VARCHAR(200) NOT NULL DEFAULT '',
                    distance_km FLOAT DEFAULT 0,
                    mission_date DATE,
                    start_time TIME,
                    end_time TIME,
                    total_revenue FLOAT DEFAULT 0,
                    fuel_cost FLOAT DEFAULT 0,
                    driver_fees FLOAT DEFAULT 0,
                    company_profit FLOAT DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'pending',
                    notes TEXT,
                    is_approved BOOLEAN DEFAULT 0,
                    approved_at DATETIME,
                    can_start BOOLEAN DEFAULT 0,
                    created_at DATETIME,
                    started_at DATETIME,
                    ended_at DATETIME,
                    completed_at DATETIME,
                    start_latitude FLOAT,
                    start_longitude FLOAT,
                    end_latitude FLOAT,
                    end_longitude FLOAT,
                    FOREIGN KEY (fleet_car_id) REFERENCES fleet_cars(id),
                    FOREIGN KEY (driver_id) REFERENCES drivers(id)
                )
            ''')
            print("  [CREATED] missions table")

        # ============================================
        # FLEET_CARS TABLE
        # ============================================
        print("\n[fleet_cars table]")
        if table_exists(cursor, 'fleet_cars'):
            add_column_if_missing(cursor, 'fleet_cars', 'status', "VARCHAR(20)", "'available'")
            add_column_if_missing(cursor, 'fleet_cars', 'created_at', 'DATETIME', 'NULL')
        else:
            print("  Table does not exist - creating it...")
            cursor.execute('''
                CREATE TABLE fleet_cars (
                    id INTEGER PRIMARY KEY,
                    brand VARCHAR(100) NOT NULL,
                    model VARCHAR(100) NOT NULL,
                    plate_number VARCHAR(50) NOT NULL UNIQUE,
                    year INTEGER NOT NULL,
                    color VARCHAR(50) NOT NULL,
                    status VARCHAR(20) DEFAULT 'available',
                    created_at DATETIME
                )
            ''')
            print("  [CREATED] fleet_cars table")

        # ============================================
        # CAR_SHARES TABLE
        # ============================================
        print("\n[car_shares table]")
        if table_exists(cursor, 'car_shares'):
            add_column_if_missing(cursor, 'car_shares', 'last_auto_payout_date', 'DATETIME', 'NULL')
        else:
            print("  Table does not exist - will be created by Flask")

        # ============================================
        # WITHDRAWAL_REQUESTS TABLE
        # ============================================
        print("\n[withdrawal_requests table]")
        if not table_exists(cursor, 'withdrawal_requests'):
            print("  Table does not exist - creating it...")
            cursor.execute('''
                CREATE TABLE withdrawal_requests (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    amount FLOAT NOT NULL,
                    payment_method VARCHAR(20) NOT NULL,
                    account_details VARCHAR(200) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    admin_notes TEXT,
                    proof_image VARCHAR(300),
                    request_date DATETIME,
                    processed_date DATETIME,
                    processed_by INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (processed_by) REFERENCES users(id)
                )
            ''')
            print("  [CREATED] withdrawal_requests table")
        else:
            print("  Table exists")

        # ============================================
        # EMAIL_VERIFICATIONS TABLE
        # ============================================
        print("\n[email_verifications table]")
        if not table_exists(cursor, 'email_verifications'):
            print("  Table does not exist - creating it...")
            cursor.execute('''
                CREATE TABLE email_verifications (
                    id INTEGER PRIMARY KEY,
                    email VARCHAR(120) NOT NULL,
                    otp_code VARCHAR(10) NOT NULL,
                    created_at DATETIME,
                    expires_at DATETIME NOT NULL,
                    is_verified BOOLEAN DEFAULT 0,
                    attempts INTEGER DEFAULT 0,
                    temp_name VARCHAR(100),
                    temp_password_hash VARCHAR(200),
                    temp_phone VARCHAR(20)
                )
            ''')
            print("  [CREATED] email_verifications table")
        else:
            print("  Table exists")

        # ============================================
        # REFERRAL_USAGES TABLE
        # ============================================
        print("\n[referral_usages table]")
        if not table_exists(cursor, 'referral_usages'):
            print("  Table does not exist - creating it...")
            cursor.execute('''
                CREATE TABLE referral_usages (
                    id INTEGER PRIMARY KEY,
                    referrer_user_id INTEGER NOT NULL,
                    referee_user_id INTEGER NOT NULL,
                    asset_type VARCHAR(20) NOT NULL,
                    asset_id INTEGER NOT NULL,
                    investment_amount FLOAT NOT NULL,
                    shares_purchased INTEGER NOT NULL,
                    date_used DATETIME,
                    FOREIGN KEY (referrer_user_id) REFERENCES users(id),
                    FOREIGN KEY (referee_user_id) REFERENCES users(id)
                )
            ''')
            print("  [CREATED] referral_usages table")
        else:
            print("  Table exists")

        # ============================================
        # COMMIT CHANGES
        # ============================================
        conn.commit()
        print("\n" + "=" * 60)
        print("SUCCESS! All migrations completed.")
        print("=" * 60)
        print("\nNow reload your web app on PythonAnywhere.")
        return True

    except Exception as e:
        conn.rollback()
        print(f"\nERROR during migration: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("IPI Database Migration Script")
    print("=" * 60)
    success = migrate()
    sys.exit(0 if success else 1)
