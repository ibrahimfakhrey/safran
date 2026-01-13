"""
Migration script: Migrate data from instance/app.db to apartment_platform.db
Then delete instance/app.db
"""
import sqlite3
import os
import shutil
from datetime import datetime

old_db = '/Users/ibrahimfakhry/Desktop/last/ipi/instance/app.db'
new_db = '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'
backup_db = '/Users/ibrahimfakhry/Desktop/last/ipi/instance/app.db.backup'

print("=" * 60)
print("DATABASE MIGRATION SCRIPT")
print("=" * 60)
print(f"\nSource: {old_db}")
print(f"Target: {new_db}")
print(f"Backup: {backup_db}")

# Step 1: Backup the old database
print("\n[1/5] Creating backup of old database...")
if os.path.exists(old_db):
    shutil.copy2(old_db, backup_db)
    print(f"✓ Backup created: {backup_db}")
else:
    print(f"⚠️  Old database not found at {old_db}")
    exit(1)

# Step 2: Read all data from old database
print("\n[2/5] Reading data from old database...")
old_conn = sqlite3.connect(old_db)
old_cursor = old_conn.cursor()

# Get all table names
old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [row[0] for row in old_cursor.fetchall()]
print(f"Found {len(tables)} tables: {', '.join(tables)}")

# Read data from each table
table_data = {}
for table in tables:
    old_cursor.execute(f"SELECT * FROM {table}")
    rows = old_cursor.fetchall()
    
    # Get column names
    old_cursor.execute(f"PRAGMA table_info({table})")
    columns = [col[1] for col in old_cursor.fetchall()]
    
    table_data[table] = {
        'columns': columns,
        'rows': rows
    }
    print(f"  - {table}: {len(rows)} rows, {len(columns)} columns")

old_conn.close()

# Step 3: Connect to new database and ensure schema exists
print("\n[3/5] Preparing new database schema...")
new_conn = sqlite3.connect(new_db)
new_cursor = new_conn.cursor()

# Check if referral_number column exists in users table
new_cursor.execute("PRAGMA table_info(users)")
user_columns = [col[1] for col in new_cursor.fetchall()]

if 'referral_number' not in user_columns:
    print("  Adding referral_number column to users table...")
    new_cursor.execute("ALTER TABLE users ADD COLUMN referral_number VARCHAR(20)")
    new_cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_referral_number ON users(referral_number)")
    print("  ✓ Column added")
else:
    print("  ✓ referral_number column already exists")

# Create referral_usages table if it doesn't exist
new_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='referral_usages'")
if not new_cursor.fetchone():
    print("  Creating referral_usages table...")
    new_cursor.execute("""
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
    new_cursor.execute("CREATE INDEX IF NOT EXISTS idx_referral_usages_referrer ON referral_usages(referrer_user_id)")
    new_cursor.execute("CREATE INDEX IF NOT EXISTS idx_referral_usages_referee ON referral_usages(referee_user_id)")
    new_cursor.execute("CREATE INDEX IF NOT EXISTS idx_referral_usages_date ON referral_usages(date_used)")
    print("  ✓ Table created")
else:
    print("  ✓ referral_usages table already exists")

new_conn.commit()

# Step 4: Migrate data
print("\n[4/5] Migrating data...")

# Get existing IDs to avoid duplicates
for table in table_data.keys():
    if table not in ['sqlite_sequence']:  # Skip SQLite internal tables
        print(f"\n  Migrating table: {table}")
        
        # Check what columns exist in the new database
        new_cursor.execute(f"PRAGMA table_info({table})")
        new_columns = [col[1] for col in new_cursor.fetchall()]
        
        old_columns = table_data[table]['columns']
        rows = table_data[table]['rows']
        
        # Find common columns
        common_columns = [col for col in old_columns if col in new_columns]
        
        if not rows:
            print(f"    No data to migrate")
            continue
            
        print(f"    Columns to migrate: {', '.join(common_columns)}")
        
        # Check for existing data to avoid duplicates
        new_cursor.execute(f"SELECT id FROM {table} LIMIT 1")
        has_data = new_cursor.fetchone() is not None
        
        migrated_count = 0
        skipped_count = 0
        
        for row in rows:
            # Map old row to new row based on common columns
            row_dict = dict(zip(old_columns, row))
            values = [row_dict.get(col) for col in common_columns]
            
            # Check if record already exists (by id if available)
            if 'id' in common_columns and row_dict.get('id'):
                new_cursor.execute(f"SELECT id FROM {table} WHERE id = ?", (row_dict['id'],))
                if new_cursor.fetchone():
                    skipped_count += 1
                    continue
            
            # Insert the record
            placeholders = ','.join(['?' for _ in common_columns])
            columns_str = ','.join(common_columns)
            
            try:
                new_cursor.execute(
                    f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})",
                    values
                )
                migrated_count += 1
            except sqlite3.IntegrityError as e:
                print(f"    ⚠️  Skipped duplicate record: {e}")
                skipped_count += 1
        
        print(f"    ✓ Migrated: {migrated_count} rows")
        if skipped_count > 0:
            print(f"    ⚠️  Skipped: {skipped_count} rows (already exist)")

# Generate referral numbers for users without them
print("\n  Generating referral numbers for users...")
new_cursor.execute("SELECT id FROM users WHERE referral_number IS NULL OR referral_number = ''")
users_without_ref = new_cursor.fetchall()

for (user_id,) in users_without_ref:
    ref_num = f"IPI{str(user_id).zfill(6)}"
    new_cursor.execute("UPDATE users SET referral_number = ? WHERE id = ?", (ref_num, user_id))

if users_without_ref:
    print(f"    ✓ Generated {len(users_without_ref)} referral numbers")
else:
    print(f"    ✓ All users already have referral numbers")

new_conn.commit()
new_conn.close()

# Step 5: Delete old database
print("\n[5/5] Cleaning up...")
if os.path.exists(old_db):
    os.remove(old_db)
    print(f"✓ Deleted {old_db}")
    print(f"✓ Backup preserved at {backup_db}")
else:
    print(f"⚠️  Old database already removed")

print("\n" + "=" * 60)
print("MIGRATION COMPLETE!")
print("=" * 60)
print(f"\n✅ All data has been migrated to: {new_db}")
print(f"✅ Old database backed up to: {backup_db}")
print(f"✅ Old database removed from: {old_db}")
print("\nYou can now use apartment_platform.db as your primary database.")
