"""
Direct test of User.check_password method
"""
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, '/Users/ibrahimfakhry/Desktop/last/ipi')

# Import without initializing the full Flask app
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'
test_email = 'admin@apartmentshare.com'
test_password = 'admin123'

print("=== Testing Password Hash Directly ===\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT password_hash FROM users WHERE email = ?", (test_email,))
result = cursor.fetchone()

if result:
    stored_hash = result[0]
    print(f"Stored hash: {stored_hash[:80]}...")
    print(f"Testing password: '{test_password}'")
    print(f"Result: {check_password_hash(stored_hash, test_password)}")
    
    # Also test what a fresh hash would look like
    fresh_hash = generate_password_hash(test_password)
    print(f"\nFresh hash: {fresh_hash[:80]}...")
    print(f"Fresh hash works: {check_password_hash(fresh_hash, test_password)}")
else:
    print("User not found")

conn.close()
