"""
Simple test to see which database Flask actually connects to
"""
import os
import sys

# Set environment
os.environ['FLASK_ENV'] = 'production'

# Add to path
sys.path.insert(0, '/Users/ibrahimfakhry/Desktop/last/ipi')

from app import create_app
from app.models import db, User

# Create app
app = create_app('production')

with app.app_context():
    # Print database URI
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Try to query users
    users = User.query.all()
    print(f"\nTotal users in database: {len(users)}")
    
    # Show first 5 users
    for user in users[:5]:
        print(f"  - ID:{user.id}, Name:{user.name}, Email:{user.email}, IsAdmin:{user.is_admin}")
    
    # Look for admin
    admin = User.query.filter_by(email='admin@apartmentshare.com').first()
    if admin:
        print(f"\n✓ Found admin@apartmentshare.com: ID={admin.id}")
    else:
        print(f"\n❌ admin@apartmentshare.com NOT FOUND")
    
    # Check for admin@example.com
    admin2 = User.query.filter_by(email='admin@example.com').first()
    if admin2:
        print(f"✓ Found admin@example.com: ID={admin2.id}")
    else:
        print(f"❌ admin@example.com NOT FOUND")
