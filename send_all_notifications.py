"""
Test script to send all notification types to a test user
Run on PythonAnywhere: python3 send_all_notifications.py
"""
from app import create_app, db
from app.models import User
from app.utils.notification_service import send_push_notification, NotificationTemplates, initialize_firebase
import time

app = create_app('production')

with app.app_context():
    # Find test user
    user = User.query.filter_by(email='a@aa.com').first()
    
    if not user:
        print('❌ User not found: a@aa.com')
        exit()
    
    print(f'✅ User: {user.name} ({user.email})')
    print(f'📱 FCM Token: {user.fcm_token[:50]}...' if user.fcm_token else '❌ No FCM token')
    
    if not user.fcm_token:
        print('\n⚠️  User has no FCM token. Flutter app needs to send it after login.')
        exit()
    
    # Initialize Firebase
    if not initialize_firebase():
        print('❌ Failed to initialize Firebase')
        exit()
    
    print('\n🔔 Sending all 14 notification types...\n')
    print('=' * 60)
    
    notifications = [
        ('1. Welcome', NotificationTemplates.welcome(user.name)),
        ('2. Investment Approved', NotificationTemplates.investment_approved('شقة النيل', 5)),
        ('3. Investment Rejected', NotificationTemplates.investment_rejected()),
        ('4. Under Review', NotificationTemplates.investment_under_review()),
        ('5. Documents Missing', NotificationTemplates.documents_missing()),
        ('6. Withdrawal Approved', NotificationTemplates.withdrawal_approved(5000)),
        ('7. Withdrawal Rejected', NotificationTemplates.withdrawal_rejected()),
        ('8. Rental Income', NotificationTemplates.rental_income(1500, 'شقة المعادي')),
        ('9. Car Income', NotificationTemplates.car_income(800, 'تويوتا كامري')),
        ('10. Rewards Payout', NotificationTemplates.rewards_payout(250)),
        ('11. Referral Reward', NotificationTemplates.referral_reward(100)),
        ('12. Password Changed', NotificationTemplates.password_changed()),
        ('13. Asset Closed', NotificationTemplates.asset_closed('شقة الزمالك')),
        ('14. New Asset', NotificationTemplates.new_asset('فيلا 6 أكتوبر', 'apartment')),
    ]
    
    success = 0
    failed = 0
    
    for name, notif in notifications:
        print(f'\n{name}')
        print(f'  Title: {notif["title"]}')
        print(f'  Body:  {notif["body"]}')
        
        result = send_push_notification(
            user_id=user.id,
            title=notif['title'],
            body=notif['body'],
            data=notif.get('data')
        )
        
        if result:
            print('  ✅ Sent!')
            success += 1
        else:
            print('  ❌ Failed')
            failed += 1
        
        print('-' * 60)
        time.sleep(3)  # Wait 3 seconds between notifications
    
    print(f'\n🎉 Done! Sent: {success}, Failed: {failed}')
    print('Check the phone for notifications! 📱')
