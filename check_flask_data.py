#!/usr/bin/env python3
"""
Check which database Flask is querying for apartments
"""
import os
import sys
sys.path.insert(0, '/Users/ibrahimfakhry/Desktop/last/ipi')

from app import create_app
from app.models import db, Apartment, Car

app = create_app('development')

with app.app_context():
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print()
    
    # Count apartments and cars
    apt_count = Apartment.query.count()
    car_count = Car.query.count()
    
    print(f"Apartments in Flask database: {apt_count}")
    print(f"Cars in Flask database: {car_count}")
    
    if apt_count > 0:
        print("\nFirst 3 apartments:")
        for apt in Apartment.query.limit(3).all():
            print(f"  - {apt.title} ({apt.total_price} EGP)")
    
    if car_count > 0:
        print("\nFirst 3 cars:")
        for car in Car.query.limit(3).all():
            print(f"  - {car.title} ({car.total_price} EGP)")
