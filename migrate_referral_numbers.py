"""
Migration script to add referral numbers to existing users
and create the referral_usages table
"""
from app import create_app
from app.models import db, User, ReferralUsage

def migrate_referral_system():
    app = create_app('production')
    
    with app.app_context():
        print("=== Referral System Migration ===\n")
        
        # Step 1: Create the referral_usages table
        print("Step 1: Creating referral_usages table...")
        try:
            db.create_all()
            print("✓ Table created successfully\n")
        except Exception as e:
            print(f"Note: {e}\n")
        
        # Step 2: Generate referral numbers for existing users
        print("Step 2: Generating referral numbers for existing users...")
        users_without_referral = User.query.filter(
            (User.referral_number == None) | (User.referral_number == '')
        ).all()
        
        count = 0
        for user in users_without_referral:
            user.generate_referral_number()
            count += 1
            print(f"   User #{user.id} ({user.name}): {user.referral_number}")
        
        if count > 0:
            db.session.commit()
            print(f"\n✓ Generated referral numbers for {count} users\n")
        else:
            print("✓ All users already have referral numbers\n")
        
        # Step 3: Show summary
        print("=== Migration Complete ===")
        total_users = User.query.count()
        total_with_numbers = User.query.filter(User.referral_number != None).count()
        print(f"Total users: {total_users}")
        print(f"Users with referral numbers: {total_with_numbers}")
        
        if total_users == total_with_numbers:
            print("\n✅ All users now have referral numbers!")
        else:
            print(f"\n⚠️  {total_users - total_with_numbers} users still need referral numbers")

if __name__ == '__main__':
    migrate_referral_system()
