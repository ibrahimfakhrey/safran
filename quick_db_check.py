#!/usr/bin/env python3
"""
Direct database check - count what's really in apartment_platform.db
"""
import sqlite3

db_path = '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'

print("Checking apartment_platform.db directly...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM apartments")
apt_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM cars")
car_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]

print(f"\n✓ Apartments: {apt_count}")
print(f"✓ Cars: {car_count}")
print(f"✓ Users: {user_count}")

if apt_count > 0:
    cursor.execute("SELECT title FROM apartments LIMIT 3")
    apartments = cursor.fetchall()
    print(f"\nSample apartments:")
    for apt in apartments:
        print(f"  - {apt[0]}")

conn.close()
