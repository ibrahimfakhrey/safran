"""
Firebase Cloud Messaging (FCM) Push Notification Service
Uses Firebase Admin SDK (NEW METHOD - Legacy Server Key is deprecated)
"""
import os
import json
from flask import current_app

# Initialize Firebase Admin SDK
firebase_app = None

def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials"""
    global firebase_app
    
    if firebase_app is not None:
        return True
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        # Get service account path from config or environment
        service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT') or \
                              current_app.config.get('FIREBASE_SERVICE_ACCOUNT')
        
        if not service_account_path:
            current_app.logger.error("FIREBASE_SERVICE_ACCOUNT path not configured")
            return False
        
        # Check if it's a path to JSON file or the JSON content itself
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
        else:
            # Try parsing as JSON string
            try:
                service_account_info = json.loads(service_account_path)
                cred = credentials.Certificate(service_account_info)
            except json.JSONDecodeError:
                current_app.logger.error("Invalid FIREBASE_SERVICE_ACCOUNT - not a valid path or JSON")
                return False
        
        firebase_app = firebase_admin.initialize_app(cred)
        current_app.logger.info("Firebase Admin SDK initialized successfully")
        return True
        
    except ImportError:
        current_app.logger.error("firebase-admin package not installed. Run: pip install firebase-admin")
        return False
    except Exception as e:
        current_app.logger.error(f"Failed to initialize Firebase: {str(e)}")
        return False


def send_push_notification(user_id, title, body, data=None, badge=None):
    """
    Send FCM push notification to a specific user using Firebase Admin SDK
    
    Args:
        user_id (int): User ID to send notification to
        title (str): Notification title (max 65 chars)
        body (str): Notification body (max 240 chars)
        data (dict): Additional data payload for deep linking
        badge (int): Badge count for iOS (optional)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        from app.models import User
        from firebase_admin import messaging
        
        # Initialize Firebase if not already done
        if not initialize_firebase():
            return False
        
        # Get user's FCM token
        user = User.query.get(user_id)
        if not user or not hasattr(user, 'fcm_token') or not user.fcm_token:
            current_app.logger.warning(f"No FCM token for user {user_id}")
            return False
        
        # Convert data values to strings (FCM requirement)
        string_data = None
        if data:
            string_data = {k: str(v) for k, v in data.items()}
        
        # Create message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=string_data,
            token=user.fcm_token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default',
                    click_action='FLUTTER_NOTIFICATION_CLICK',
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=badge or 1,
                    ),
                ),
            ),
        )
        
        # Send message
        response = messaging.send(message)
        current_app.logger.info(f"Notification sent to user {user_id}: {response}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send notification to user {user_id}: {str(e)}")
        return False


def send_bulk_notification(user_ids, title, body, data=None):
    """
    Send notification to multiple users
    
    Args:
        user_ids (list): List of user IDs
        title (str): Notification title
        body (str): Notification body
        data (dict): Additional data payload
    
    Returns:
        dict: {"success": int, "failed": int}
    """
    success_count = 0
    failed_count = 0
    
    for user_id in user_ids:
        if send_push_notification(user_id, title, body, data):
            success_count += 1
        else:
            failed_count += 1
    
    return {"success": success_count, "failed": failed_count}


def send_notification_to_all_users(title, body, data=None):
    """
    Send notification to all users with FCM tokens
    
    Args:
        title (str): Notification title
        body (str): Notification body
        data (dict): Additional data payload
    
    Returns:
        dict: {"success": int, "failed": int}
    """
    from app.models import User
    
    # Get all users with FCM tokens
    users = User.query.filter(User.fcm_token.isnot(None)).all()
    user_ids = [user.id for user in users]
    
    return send_bulk_notification(user_ids, title, body, data)


# Notification templates for common events
class NotificationTemplates:
    """Pre-defined notification templates in Arabic"""
    
    @staticmethod
    def investment_approved(asset_name, shares_count):
        return {
            "title": "✅ تمت الموافقة على طلب استثمارك",
            "body": f"تم اعتماد استثمارك في {asset_name}. تم شراء {shares_count} حصة بنجاح!",
            "data": {"type": "investment_approved", "screen": "investments"}
        }
    
    @staticmethod
    def investment_rejected():
        return {
            "title": "❌ تم رفض طلب الاستثمار",
            "body": "عذراً، لم تتم الموافقة على طلبك. يرجى التواصل معنا للمزيد من المعلومات.",
            "data": {"type": "investment_rejected", "screen": "requests"}
        }
    
    @staticmethod
    def investment_under_review():
        return {
            "title": "🔍 طلبك قيد المراجعة",
            "body": "جاري مراجعة طلب الاستثمار الخاص بك. سنبلغك قريباً!",
            "data": {"type": "investment_under_review", "screen": "requests"}
        }
    
    @staticmethod
    def documents_missing():
        return {
            "title": "⚠️ مستندات ناقصة",
            "body": "يرجى تحميل المستندات المطلوبة لإكمال طلب الاستثمار.",
            "data": {"type": "documents_missing", "screen": "requests"}
        }
    
    @staticmethod
    def withdrawal_approved(amount):
        return {
            "title": "✅ تمت الموافقة على طلب السحب",
            "body": f"تم تحويل {amount:,.0f} جنيه إلى حسابك. شكراً لثقتك!",
            "data": {"type": "withdrawal_approved", "screen": "wallet"}
        }
    
    @staticmethod
    def withdrawal_rejected():
        return {
            "title": "❌ تم رفض طلب السحب",
            "body": "لم تتم الموافقة على طلب السحب. يرجى مراجعة التفاصيل.",
            "data": {"type": "withdrawal_rejected", "screen": "wallet"}
        }
    
    @staticmethod
    def rental_income(amount, asset_name):
        return {
            "title": "💰 تم إضافة الإيجار الشهري",
            "body": f"تم إضافة {amount:,.0f} جنيه من إيجار {asset_name} إلى محفظتك!",
            "data": {"type": "rental_income", "screen": "wallet"}
        }
    
    @staticmethod
    def car_income(amount, car_name):
        return {
            "title": "💰 تم إضافة دخل السيارة",
            "body": f"تم إضافة {amount:,.0f} جنيه من دخل {car_name} إلى محفظتك!",
            "data": {"type": "car_income", "screen": "wallet"}
        }
    
    @staticmethod
    def rewards_payout(amount):
        return {
            "title": "🎁 تم تحويل مكافآتك",
            "body": f"تم تحويل {amount:,.0f} جنيه من رصيد المكافآت إلى محفظتك!",
            "data": {"type": "rewards_payout", "screen": "wallet"}
        }
    
    @staticmethod
    def referral_used(referee_name, asset_name):
        return {
            "title": "🎉 شخص استخدم رمز الإحالة الخاص بك!",
            "body": f"{referee_name} استخدم رمزك للاستثمار في {asset_name}!",
            "data": {"type": "referral_used", "screen": "referrals"}
        }
    
    @staticmethod
    def referral_reward(amount):
        return {
            "title": "💎 ربحت مكافأة إحالة!",
            "body": f"تم إضافة {amount:,.0f} جنيه إلى رصيد مكافآتك!",
            "data": {"type": "referral_reward", "screen": "wallet"}
        }
    
    @staticmethod
    def welcome(user_name):
        return {
            "title": "🎊 مرحباً بك في i pillars i!",
            "body": f"مرحباً {user_name}، تم تفعيل حسابك بنجاح. ابدأ الاستثمار الآن!",
            "data": {"type": "welcome", "screen": "dashboard"}
        }
    
    @staticmethod
    def password_changed():
        return {
            "title": "🔐 تم تغيير كلمة المرور",
            "body": "تم تغيير كلمة المرور الخاصة بك بنجاح.",
            "data": {"type": "password_changed", "screen": "profile"}
        }
    
    @staticmethod
    def asset_closed(asset_name):
        return {
            "title": f"ℹ️ تم إغلاق {asset_name}",
            "body": f"تم إغلاق {asset_name} الذي استثمرت فيه. سيتم توزيع الأرباح كالمعتاد.",
            "data": {"type": "asset_closed", "screen": "investments"}
        }
    
    @staticmethod
    def new_asset(asset_name, asset_type):
        return {
            "title": "🆕 فرصة استثمار جديدة!",
            "body": f"تم إضافة {asset_name} - ابدأ الاستثمار الآن!",
            "data": {"type": "new_asset", "asset_type": asset_type, "screen": "market"}
        }


# ==================== DRIVER NOTIFICATIONS ====================

def send_driver_notification(driver_id, title, body, data=None, badge=None):
    """
    Send FCM push notification to a specific driver using Firebase Admin SDK

    Args:
        driver_id (int): Driver ID to send notification to
        title (str): Notification title (max 65 chars)
        body (str): Notification body (max 240 chars)
        data (dict): Additional data payload for deep linking
        badge (int): Badge count for iOS (optional)

    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        from app.models import Driver
        from firebase_admin import messaging

        # Initialize Firebase if not already done
        if not initialize_firebase():
            return False

        # Get driver's FCM token
        driver = Driver.query.get(driver_id)
        if not driver or not hasattr(driver, 'fcm_token') or not driver.fcm_token:
            current_app.logger.warning(f"No FCM token for driver {driver_id}")
            return False

        # Convert data values to strings (FCM requirement)
        string_data = None
        if data:
            string_data = {k: str(v) for k, v in data.items()}

        # Create message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=string_data,
            token=driver.fcm_token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default',
                    click_action='FLUTTER_NOTIFICATION_CLICK',
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=badge or 1,
                    ),
                ),
            ),
        )

        # Send message
        response = messaging.send(message)
        current_app.logger.info(f"Notification sent to driver {driver_id}: {response}")
        return True

    except Exception as e:
        current_app.logger.error(f"Failed to send notification to driver {driver_id}: {str(e)}")
        return False


def notify_admin_new_mission_request(driver, mission):
    """
    Notify admin(s) when a driver reports a new mission

    Args:
        driver: Driver object
        mission: Mission object
    """
    from app.models import User

    # Get all admin users
    admins = User.query.filter_by(is_admin=True).all()

    title = "🚗 طلب مهمة جديد"
    body = f"السائق {driver.name} أبلغ عن مهمة من {mission.from_location} إلى {mission.to_location}"
    data = {
        "type": "mission_request",
        "screen": "fleet_mission_requests",
        "mission_id": mission.id,
        "driver_id": driver.id
    }

    for admin in admins:
        if admin.fcm_token:
            send_push_notification(admin.id, title, body, data)


def notify_admin_mission_started(driver, mission):
    """
    Notify admin(s) when a driver starts a mission

    Args:
        driver: Driver object
        mission: Mission object
    """
    from app.models import User

    # Get all admin users
    admins = User.query.filter_by(is_admin=True).all()

    title = "▶️ بدأ السائق المهمة"
    body = f"السائق {driver.name} بدأ المهمة من {mission.from_location} إلى {mission.to_location}"
    data = {
        "type": "mission_started",
        "screen": "fleet_missions",
        "mission_id": mission.id,
        "driver_id": driver.id
    }

    for admin in admins:
        if admin.fcm_token:
            send_push_notification(admin.id, title, body, data)


def notify_admin_mission_completed(driver, mission):
    """
    Notify admin(s) when a driver completes a mission

    Args:
        driver: Driver object
        mission: Mission object
    """
    from app.models import User

    # Get all admin users
    admins = User.query.filter_by(is_admin=True).all()

    title = "✅ أنهى السائق المهمة"
    body = f"السائق {driver.name} أنهى المهمة. الإيراد: {mission.total_revenue:,.0f} جنيه"
    data = {
        "type": "mission_completed",
        "screen": "fleet_missions",
        "mission_id": mission.id,
        "driver_id": driver.id
    }

    for admin in admins:
        if admin.fcm_token:
            send_push_notification(admin.id, title, body, data)


# Driver notification templates
class DriverNotificationTemplates:
    """Pre-defined notification templates for drivers in Arabic"""

    @staticmethod
    def mission_assigned(from_location, to_location):
        return {
            "title": "🚗 لديك مهمة جديدة",
            "body": f"تم تعيين مهمة لك من {from_location} إلى {to_location}",
            "data": {"type": "mission_assigned", "screen": "missions"}
        }

    @staticmethod
    def mission_approved(from_location, to_location):
        return {
            "title": "✅ تمت الموافقة على المهمة",
            "body": f"تمت الموافقة على مهمتك من {from_location} إلى {to_location}. في انتظار إذن البدء.",
            "data": {"type": "mission_approved", "screen": "missions"}
        }

    @staticmethod
    def mission_rejected(reason=None):
        body = "تم رفض طلب المهمة."
        if reason:
            body += f" السبب: {reason}"
        return {
            "title": "❌ تم رفض المهمة",
            "body": body,
            "data": {"type": "mission_rejected", "screen": "missions"}
        }

    @staticmethod
    def start_permission_granted(from_location, to_location):
        return {
            "title": "▶️ يمكنك بدء المهمة الآن",
            "body": f"تم إعطاؤك إذن بدء المهمة من {from_location} إلى {to_location}. ابدأ الآن!",
            "data": {"type": "start_permission", "screen": "missions"}
        }

    @staticmethod
    def mission_cancelled(from_location=None, to_location=None):
        if from_location and to_location:
            body = f"تم إلغاء المهمة من {from_location} إلى {to_location}"
        else:
            body = "تم إلغاء المهمة"
        return {
            "title": "🚫 تم إلغاء المهمة",
            "body": body,
            "data": {"type": "mission_cancelled", "screen": "missions"}
        }
