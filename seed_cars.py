#!/usr/bin/env python3
"""
Seed script to add real cars to the database
Note: This script uses the application's database configuration
"""
from app import create_app
from app.models import db, Car
from datetime import datetime

def seed_cars():
    app = create_app('development')
    
    with app.app_context():
        print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Clear existing cars
        print("Clearing existing cars...")
        Car.query.delete()
        db.session.commit()
        
        # Real cars data
        cars_data = [
            {
                'title': 'تويوتا كامري 2024',
                'description': 'سيارة كامري موديل 2024 للإيجار اليومي والشهري. حالة ممتازة مع صيانة دورية كاملة.',
                'location': 'القاهرة',
                'total_price': 450000,
                'total_shares': 100,
                'monthly_rent': 12000,
                'image': '20251104_111246_Screenshot_2025-10-23_at_12.22.33_PM.png',
                'brand': 'تويوتا',
                'model': 'كامري',
                'year': '2024'
            },
            {
                'title': 'هيونداي إلنترا 2023',
                'description': 'سيارة إلنترا حديثة ومجهزة للإيجار اليومي. مثالية للعمل في شركات النقل التشاركي.',
                'location': 'الإسكندرية',
                'total_price': 320000,
                'total_shares': 100,
                'monthly_rent': 9500,
                'image': 'default_car.jpg',
                'brand': 'هيونداي',
                'model': 'إلنترا',
                'year': '2023'
            },
            {
                'title': 'كيا سيراتو 2024',
                'description': 'سيارة سيراتو جديدة بالكامل للإيجار. توفر عائد شهري مضمون من الإيجار اليومي.',
                'location': 'الجيزة',
                'total_price': 380000,
                'total_shares': 100,
                'monthly_rent': 11000,
                'image': 'default_car.jpg',
                'brand': 'كيا',
                'model': 'سيراتو',
                'year': '2024'
            },
            {
                'title': 'تويوتا كورولا 2023',
                'description': 'كورولا موديل 2023 في حالة ممتازة. مستأجرة حالياً لشركة نقل موثوقة.',
                'location': 'القاهرة',
                'total_price': 360000,
                'total_shares': 100,
                'monthly_rent': 10500,
                'image': 'default_car.jpg',
                'brand': 'تويوتا',
                'model': 'كورولا',
                'year': '2023'
            },
            {
                'title': 'شيفروليه أوبترا 2022',
                'description': 'سيارة أوبترا اقتصادية ومربحة للإيجار اليومي والشهري.',
                'location': 'المنصورة',
                'total_price': 280000,
                'total_shares': 100,
                'monthly_rent': 8500,
                'image': 'default_car.jpg',
                'brand': 'شيفروليه',
                'model': 'أوبترا',
                'year': '2022'
            },
            {
                'title': 'هيونداي أكسنت 2024',
                'description': 'أكسنت موديل 2024 جديدة بالكامل. فرصة استثمارية ممتازة مع عائد شهري مرتفع.',
                'location': 'طنطا',
                'total_price': 310000,
                'total_shares': 100,
                'monthly_rent': 9200,
                'image': 'default_car.jpg',
                'brand': 'هيونداي',
                'model': 'أكسنت',
                'year': '2024'
            },
            {
                'title': 'رينو لوجان 2023',
                'description': 'سيارة لوجان عملية واقتصادية للإيجار. تعمل مع شركات التوصيل.',
                'location': 'القاهرة',
                'total_price': 240000,
                'total_shares': 100,
                'monthly_rent': 7500,
                'image': 'default_car.jpg',
                'brand': 'رينو',
                'model': 'لوجان',
                'year': '2023'
            },
            {
                'title': 'تويوتا يارس 2024',
                'description': 'يارس حديثة واقتصادية في استهلاك الوقود. مثالية للإيجار اليومي.',
                'location': 'الإسكندرية',
                'total_price': 330000,
                'total_shares': 100,
                'monthly_rent': 9800,
                'image': 'default_car.jpg',
                'brand': 'تويوتا',
                'model': 'يارس',
                'year': '2024'
            },
        ]
        
        print(f"Adding {len(cars_data)} cars...")
        for car_info in cars_data:
            car = Car(
                title=car_info['title'],
                description=car_info['description'],
                location=car_info['location'],
                total_price=car_info['total_price'],
                total_shares=car_info['total_shares'],
                shares_available=car_info['total_shares'],
                monthly_rent=car_info['monthly_rent'],
                image=car_info['image'],
                brand=car_info.get('brand'),
                model=car_info.get('model'),
                year=car_info.get('year'),
                is_closed=False
            )
            db.session.add(car)
            print(f"  Added car index: {cars_data.index(car_info)}")
        
        db.session.commit()
        print(f"\nSuccessfully seeded {len(cars_data)} cars!")
        
        # Verify
        total_cars = Car.query.count()
        print(f"Total cars in database: {total_cars}")

if __name__ == '__main__':
    seed_cars()
