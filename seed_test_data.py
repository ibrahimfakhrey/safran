"""
Seed database with test data for referral system testing
"""
from app import create_app, db
from app.models import User, Apartment
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

with app.app_context():
    print("🌱 Seeding database with test data...\n")
    
    # Create test users
    users_data = [
        {
            'name': 'Ibrahim Mohamed',
            'email': 'ibrahim@test.com',
            'password': 'password123',
            'wallet_balance': 500000.0
        },
        {
            'name': 'Mohamed Ahmed',
            'email': 'mohamed@test.com',
            'password': 'password123',
            'wallet_balance': 300000.0
        },
        {
            'name': 'Ahmed Ali',
            'email': 'ahmed@test.com',
            'password': 'password123',
            'wallet_balance': 200000.0
        },
        {
            'name': 'Ali Hassan',
            'email': 'ali@test.com',
            'password': 'password123',
            'wallet_balance': 150000.0
        },
        {
            'name': 'Hassan Mahmoud',
            'email': 'hassan@test.com',
            'password': 'password123',
            'wallet_balance': 100000.0
        }
    ]
    
    created_users = []
    for user_data in users_data:
        existing = User.query.filter_by(email=user_data['email']).first()
        if not existing:
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                wallet_balance=user_data['wallet_balance'],
                rewards_balance=0.0,
                is_admin=False,
                date_joined=datetime.utcnow()
            )
            db.session.add(user)
            created_users.append(user)
            print(f"✓ Created user: {user_data['name']} ({user_data['email']})")
        else:
            created_users.append(existing)
            print(f"  User already exists: {user_data['email']}")
    
    # Create test apartments
    apartments_data = [
        {
            'title': 'فيلا فاخرة في القاهرة الجديدة',
            'description': 'فيلا عصرية بتصميم فاخر في قلب القاهرة الجديدة، مكونة من 4 غرف نوم، 3 حمامات، حديقة خاصة وموقف سيارات. موقع استراتيجي قريب من المدارس والمراكز التجارية.',
            'image': 'villa1.jpg',
            'total_price': 5000000.0,
            'total_shares': 100,
            'shares_available': 100,
            'monthly_rent': 25000.0,
            'location': 'القاهرة الجديدة'
        },
        {
            'title': 'شقة تمليك في المعادي',
            'description': 'شقة مميزة في أرقى أحياء المعادي، 200 متر، 3 غرف نوم، 2 حمام، صالة واسعة، بلكونة كبيرة مطلة على حديقة. قريبة من المترو والخدمات.',
            'image': 'apartment1.jpg',
            'total_price': 3500000.0,
            'total_shares': 70,
            'shares_available': 70,
            'monthly_rent': 18000.0,
            'location': 'المعادي'
        },
        {
            'title': 'استوديو في الشيخ زايد',
            'description': 'استوديو عصري في مدينة الشيخ زايد، مفروش بالكامل، مساحة 60 متر، مناسب للاستثمار أو السكن. قريب من الخدمات والمواصلات.',
            'image': 'studio1.jpg',
            'total_price': 1200000.0,
            'total_shares': 40,
            'shares_available': 40,
            'monthly_rent': 7000.0,
            'location': 'الشيخ زايد'
        },
        {
            'title': 'دوبلكس في مدينة نصر',
            'description': 'دوبلكس فاخر في قلب مدينة نصر، 250 متر، 4 غرف نوم، 3 حمامات، تراس كبير، تشطيب سوبر لوكس. إطلالة رائعة ومنطقة حيوية.',
            'image': 'duplex1.jpg',
            'total_price': 4200000.0,
            'total_shares': 84,
            'shares_available': 84,
            'monthly_rent': 22000.0,
            'location': 'مدينة نصر'
        },
        {
            'title': 'شقة استثمارية في التجمع الخامس',
            'description': 'شقة حديثة في التجمع الخامس، 180 متر، 3 غرف، 2 حمام، مطبخ أمريكي، في كمبوند مغلق بحراسة وخدمات متكاملة.',
            'image': 'apartment2.jpg',
            'total_price': 2800000.0,
            'total_shares': 56,
            'shares_available': 56,
            'monthly_rent': 15000.0,
            'location': 'التجمع الخامس'
        }
    ]
    
    print()
    created_apartments = []
    for apt_data in apartments_data:
        existing = Apartment.query.filter_by(title=apt_data['title']).first()
        if not existing:
            apartment = Apartment(**apt_data, date_created=datetime.utcnow())
            db.session.add(apartment)
            created_apartments.append(apartment)
            print(f"✓ Created apartment: {apt_data['title']}")
        else:
            created_apartments.append(existing)
            print(f"  Apartment already exists: {apt_data['title']}")
    
    db.session.commit()
    
    print("\n✅ Database seeded successfully!\n")
    print("=" * 60)
    print("TEST ACCOUNTS:")
    print("=" * 60)
    print("\nADMIN:")
    print("  Email: admin@apartmentshare.com")
    print("  Password: admin123")
    print("\nTEST USERS (all with password: password123):")
    for user_data in users_data:
        print(f"  • {user_data['name']} - {user_data['email']}")
    print("\n" + "=" * 60)
    print(f"Created {len(created_apartments)} apartments")
    print(f"Created {len(created_users)} users")
    print("=" * 60)
    print("\n🎯 TO TEST REFERRAL SYSTEM:")
    print("1. Login as Ibrahim (ibrahim@test.com)")
    print("2. Submit investment request for any apartment")
    print("3. Login as Admin and approve the request")
    print("4. Ibrahim will get a referral link from 'My Investments'")
    print("5. Login as Mohamed and use Ibrahim's referral link")
    print("6. Admin approves Mohamed's investment")
    print("7. Ibrahim gets 0.05% reward automatically!")
    print("8. Check 'My Referrals' to see the tree")
    print("9. Admin can payout rewards from dashboard")
    print("=" * 60)
