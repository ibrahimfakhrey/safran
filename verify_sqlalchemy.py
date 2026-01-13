from app import create_app, db
from sqlalchemy import text
import os

app = create_app('development')
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    try:
        print("Connecting to database...")
        with db.engine.connect() as conn:
            print("Connected.")
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            print(f"Columns in users table: {columns}")
            
            if 'auth_provider' in columns:
                print("✅ SUCCESS: auth_provider column found.")
            else:
                print("❌ FAILURE: auth_provider column NOT found.")
                
            # Also check the actual file path being used
            db_file = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            print(f"Expected DB file: {db_file}")
            if os.path.exists(db_file):
                print(f"File exists. Size: {os.path.getsize(db_file)} bytes")
            else:
                print("❌ File does NOT exist at expected path!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
