#!/usr/bin/env python3
"""
Test script to verify landing page data
"""
from app import create_app
from app.models import Car, Apartment
from sqlalchemy import desc

app = create_app('development')

with app.app_context():
    print("=" * 60)
    print("LANDING PAGE DATA TEST")
    print("=" * 60)
    
    # Test featured apartments
    featured_apartments = Apartment.query.filter_by(is_closed=False)\
        .order_by(desc(Apartment.date_created)).limit(6).all()
    print(f"\n✓ Featured Apartments: {len(featured_apartments)}")
    for apt in featured_apartments[:3]:
        print(f"  - {apt.title}")
    
    # Test featured cars
    featured_cars = Car.query.filter_by(is_closed=False)\
        .order_by(desc(Car.date_created)).limit(6).all()
    print(f"\n✓ Featured Cars: {len(featured_cars)}")
    for car in featured_cars[:3]:
        print(f"  - {car.title}")
    
    # Test if section will render
    print(f"\n✓ Section will render: {bool(featured_apartments or featured_cars)}")
    
    # Test car properties
    if featured_cars:
        test_car = featured_cars[0]
        print(f"\n✓ Testing first car: {test_car.title}")
        print(f"  - Share Price: {test_car.share_price:,.0f}")
        print(f"  - Investors Count: {test_car.investors_count}")
        print(f"  - Completion %: {test_car.completion_percentage:.1f}")
        print(f"  - Status: {test_car.status}")
        print(f"  - Image: {test_car.image}")
        print(f"  - Is Closed: {test_car.is_closed}")
        print(f"  - Shares Available: {test_car.shares_available}/{test_car.total_shares}")
    
    print("\n" + "=" * 60)
