"""
Seed data script to populate the database with sample data
Run this file to add test apartments and users
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, User, Apartment, Car, ApartmentImage
from datetime import datetime

def seed_database():
    """Populate database with sample data"""
    app = create_app('development')
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Check if data already exists
        if Apartment.query.count() > 0:
            print("Database already contains data. Skipping seed.")
            return
        
        # Create sample users
        print("Creating sample users...")
        users = []
        
        user1 = User(
            name="أحمد محمد",
            email="ahmed@example.com",
            wallet_balance=500000.0
        )
        user1.set_password("password123")
        users.append(user1)
        
        user2 = User(
            name="فاطمة علي",
            email="fatima@example.com",
            wallet_balance=750000.0
        )
        user2.set_password("password123")
        users.append(user2)
        
        user3 = User(
            name="محمود حسن",
            email="mahmoud@example.com",
            wallet_balance=300000.0
        )
        user3.set_password("password123")
        users.append(user3)
        
        for user in users:
            db.session.add(user)
        
    # Create sample apartments
        print("Creating sample apartments...")
        apartments = [
            {
                'title': 'شقة فاخرة في الزمالك',
                'description': 'شقة 200 متر مربع، 3 غرف نوم، 2 حمام، مطبخ حديث، إطلالة على النيل. موقع متميز في قلب الزمالك.',
                'total_price': 5000000.0,
                'total_shares': 50,
                'monthly_rent': 30000.0,
                'location': 'الزمالك، القاهرة',
                'images': ['unit1_1.jpg', 'unit1_2.jpg', 'unit1_3.jpg']
            },
            {
                'title': 'استوديو في المعادي',
                'description': 'استوديو 80 متر مربع، مفروش بالكامل، قريب من المترو والخدمات. مثالي للإيجار السريع.',
                'total_price': 2000000.0,
                'total_shares': 40,
                'monthly_rent': 12000.0,
                'location': 'المعادي، القاهرة',
                'images': ['unit2_1.jpg', 'unit2_2.jpg']
            },
            {
                'title': 'فيلا في التجمع الخامس',
                'description': 'فيلا 400 متر، 5 غرف نوم، حديقة خاصة، موقف سيارات. منطقة راقية وآمنة.',
                'total_price': 8000000.0,
                'total_shares': 80,
                'monthly_rent': 50000.0,
                'location': 'التجمع الخامس، القاهرة الجديدة',
                'images': ['unit3_1.jpg', 'unit3_2.jpg', 'unit3_3.jpg', 'unit3_4.jpg']
            },
            {
                'title': 'شقة عائلية في مدينة نصر',
                'description': 'شقة 150 متر، 3 غرف نوم، تشطيب سوبر لوكس، قريبة من المدارس والمستشفيات.',
                'total_price': 3500000.0,
                'total_shares': 35,
                'monthly_rent': 20000.0,
                'location': 'مدينة نصر، القاهرة',
                'images': ['unit4_1.jpg']
            },
            {
                'title': 'محل تجاري في وسط البلد',
                'description': 'محل 50 متر، موقع حيوي، حركة عالية، مناسب لجميع الأنشطة التجارية.',
                'total_price': 4000000.0,
                'total_shares': 40,
                'monthly_rent': 25000.0,
                'location': 'وسط البلد، القاهرة',
                'images': ['unit5_1.jpg', 'unit5_2.jpg']
            },
            {
                'title': 'شقة بنتهاوس في الشيخ زايد',
                'description': 'بنتهاوس 300 متر مع روف، 4 غرف نوم، إطلالة بانورامية، تشطيب فاخر جداً.',
                'total_price': 10000000.0,
                'total_shares': 100,
                'monthly_rent': 60000.0,
                'location': 'الشيخ زايد، الجيزة',
                'images': ['unit6_1.jpg', 'unit6_2.jpg', 'unit6_3.jpg']
            },
            # More units for gallery testing
            {
                'title': 'شقة جديدة في أكتوبر',
                'description': 'شقة 120 متر، 2 غرف نوم، قريبة من مول العرب، تشطيب حديث.',
                'total_price': 2500000.0,
                'total_shares': 25,
                'monthly_rent': 15000.0,
                'location': '6 أكتوبر، الجيزة',
                'images': ['unit7_1.jpg', 'unit7_2.jpg']
            },
            {
                'title': 'شاليه في الساحل الشمالي',
                'description': 'شاليه 90 متر، إطلالة بحرية، مفروش بالكامل، مناسب للعطلات.',
                'total_price': 3500000.0,
                'total_shares': 30,
                'monthly_rent': 18000.0,
                'location': 'الساحل الشمالي، مطروح',
                'images': ['unit8_1.jpg', 'unit8_2.jpg', 'unit8_3.jpg']
            }
        ]
        
        for apt_data in apartments:
            apartment = Apartment(
                title=apt_data['title'],
                description=apt_data['description'],
                total_price=apt_data['total_price'],
                total_shares=apt_data['total_shares'],
                shares_available=apt_data['total_shares'],
                monthly_rent=apt_data['monthly_rent'],
                location=apt_data['location'],
                image=apt_data['images'][0] if 'images' in apt_data and len(apt_data['images']) > 0 else 'default_apartment.jpg'
            )
            db.session.add(apartment)
            db.session.flush() # Generate ID
            
            # Create ApartmentImage objects
            for i, img_name in enumerate(apt_data.get('images', [])):
                img = ApartmentImage(
                    apartment_id=apartment.id,
                    filename=img_name,
                    sort_order=i
                )
                db.session.add(img)
        
        # Seed sample cars if none exist
        if Car.query.count() == 0:
            print("Creating sample cars...")
            cars = [
                {
                    'title': 'تويوتا كورولا 2022',
                    'description': 'سيارة اقتصادية مثالية للتأجير الشهري، صيانة منخفضة واستهلاك وقود ممتاز.',
                    'total_price': 800000.0,
                    'total_shares': 40,
                    'monthly_rent': 12000.0,
                    'location': 'القاهرة',
                    'brand': 'Toyota', 'model': 'Corolla', 'year': '2022'
                },
                {
                    'title': 'هيونداي إلنترا 2021',
                    'description': 'سيارة مريحة وموثوقة لعقود الإيجار، مناسبة للعائلات والشركات.',
                    'total_price': 700000.0,
                    'total_shares': 35,
                    'monthly_rent': 11000.0,
                    'location': 'الجيزة',
                    'brand': 'Hyundai', 'model': 'Elantra', 'year': '2021'
                },
                {
                    'title': 'كيا سبورتاج 2020',
                    'description': 'SUV مدمجة مطلوبة للغاية لمرونة الاستخدام وتأجير طويل الأجل.',
                    'total_price': 950000.0,
                    'total_shares': 50,
                    'monthly_rent': 15000.0,
                    'location': 'القاهرة الجديدة',
                    'brand': 'Kia', 'model': 'Sportage', 'year': '2020'
                }
            ]
            for car_data in cars:
                car = Car(
                    title=car_data['title'],
                    description=car_data['description'],
                    total_price=car_data['total_price'],
                    total_shares=car_data['total_shares'],
                    shares_available=car_data['total_shares'],
                    monthly_rent=car_data['monthly_rent'],
                    location=car_data['location'],
                    brand=car_data.get('brand'),
                    model=car_data.get('model'),
                    year=car_data.get('year'),
                    image='default_car.jpg'
                )
                db.session.add(car)

        # Commit all data
        db.session.commit()
        print("Database seeded successfully!")
        print(f"   - Created {len(users)} users")
        print(f"   - Created {len(apartments)} apartments")
        print("\nSample user credentials:")
        print("   Email: ahmed@example.com")
        print("   Password: password123")
        print("\nAdmin credentials:")
        print("   Email: admin@apartmentshare.com")
        print("   Password: admin123")
        

if __name__ == '__main__':
    seed_database()
