"""
REST API Blueprint for Driver Mobile App
Provides JWT-authenticated endpoints for driver Flutter application
Version: v1
Language: Arabic
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from app.models import db, Driver, Mission, FleetCar
from datetime import datetime, timedelta
from functools import wraps

# Create Driver API blueprint
driver_api_bp = Blueprint('driver_api', __name__, url_prefix='/api/driver')


# ==================== Helper Functions ====================

def success_response(data=None, message="نجح", status=200):
    """Standard success response format"""
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status


def error_response(message="حدث خطأ", code="ERROR", details=None, status=400):
    """Standard error response format"""
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
    if details:
        response["error"]["details"] = details
    return jsonify(response), status


def serialize_driver(driver):
    """Convert Driver object to dictionary"""
    return {
        "id": driver.id,
        "name": driver.name,
        "phone": driver.phone,
        "email": driver.email,
        "driver_number": driver.driver_number,
        "national_id": driver.national_id,
        "photo_url": f"/static/uploads/drivers/{driver.photo_filename}" if driver.photo_filename else None,
        "rating": driver.rating,
        "completed_missions": driver.completed_missions,
        "total_earnings": driver.total_earnings,
        "is_approved": driver.is_approved,
        "is_verified": driver.is_verified,
        "created_at": driver.created_at.isoformat() if driver.created_at else None
    }


def serialize_mission(mission):
    """Convert Mission object to dictionary"""
    return {
        "id": mission.id,
        "mission_type": mission.mission_type,
        "mission_type_arabic": mission.mission_type_arabic,
        "app_name": mission.app_name,
        "app_name_arabic": mission.app_name_arabic,
        "from_location": mission.from_location,
        "to_location": mission.to_location,
        "route_description": mission.route_description,
        "distance_km": mission.distance_km,
        "expected_cost": mission.expected_cost,
        "total_revenue": mission.total_revenue,
        "fuel_cost": mission.fuel_cost,
        "driver_fees": mission.driver_fees,
        "company_profit": mission.company_profit,
        "mission_date": mission.mission_date.isoformat() if mission.mission_date else None,
        "start_time": mission.start_time.isoformat() if mission.start_time else None,
        "end_time": mission.end_time.isoformat() if mission.end_time else None,
        "status": mission.status,
        "status_arabic": mission.status_arabic,
        "is_approved": mission.is_approved,
        "can_start": mission.can_start,
        "notes": mission.notes,
        "created_at": mission.created_at.isoformat() if mission.created_at else None,
        "approved_at": mission.approved_at.isoformat() if mission.approved_at else None,
        "started_at": mission.started_at.isoformat() if mission.started_at else None,
        "ended_at": mission.ended_at.isoformat() if mission.ended_at else None,
        # GPS Location tracking
        "start_latitude": mission.start_latitude,
        "start_longitude": mission.start_longitude,
        "end_latitude": mission.end_latitude,
        "end_longitude": mission.end_longitude,
        "fleet_car": {
            "id": mission.fleet_car.id,
            "brand": mission.fleet_car.brand,
            "model": mission.fleet_car.model,
            "plate_number": mission.fleet_car.plate_number,
            "color": mission.fleet_car.color
        } if mission.fleet_car else None
    }


def serialize_fleet_car(car):
    """Convert FleetCar object to dictionary"""
    return {
        "id": car.id,
        "brand": car.brand,
        "model": car.model,
        "plate_number": car.plate_number,
        "year": car.year,
        "color": car.color,
        "status": car.status,
        "status_arabic": car.status_arabic
    }


def driver_required(f):
    """Decorator to ensure the JWT identity is a driver"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        identity = get_jwt_identity()

        # Check if identity is a driver (format: driver_<id>)
        if not identity or not identity.startswith('driver_'):
            return error_response(
                message="غير مصرح لك بالوصول",
                code="UNAUTHORIZED",
                status=401
            )

        try:
            driver_id = int(identity.replace('driver_', ''))
        except ValueError:
            return error_response(
                message="رمز غير صالح",
                code="INVALID_TOKEN",
                status=401
            )

        driver = Driver.query.get(driver_id)
        if not driver:
            return error_response(
                message="السائق غير موجود",
                code="DRIVER_NOT_FOUND",
                status=404
            )

        if not driver.is_verified:
            return error_response(
                message="حساب السائق غير مفعّل",
                code="DRIVER_NOT_VERIFIED",
                status=403
            )

        # Pass driver to the decorated function
        return f(driver, *args, **kwargs)

    return decorated_function


# ==================== Authentication Endpoints ====================

@driver_api_bp.route('/login', methods=['POST'])
def driver_login():
    """
    Driver login with driver_number and password

    Request body:
    {
        "driver_number": "IPI-DRV-001",
        "password": "password123"
    }

    Returns JWT access and refresh tokens
    """
    data = request.get_json()

    if not data:
        return error_response(
            message="البيانات مطلوبة",
            code="MISSING_DATA",
            status=400
        )

    driver_number = data.get('driver_number', '').strip()
    password = data.get('password', '')

    if not driver_number or not password:
        return error_response(
            message="رقم السائق وكلمة المرور مطلوبان",
            code="MISSING_CREDENTIALS",
            status=400
        )

    # Find driver by driver_number
    driver = Driver.query.filter_by(driver_number=driver_number).first()

    if not driver:
        return error_response(
            message="رقم السائق غير صحيح",
            code="INVALID_DRIVER_NUMBER",
            status=401
        )

    if not driver.is_verified:
        return error_response(
            message="حساب السائق غير مفعّل. يرجى التواصل مع الإدارة",
            code="DRIVER_NOT_VERIFIED",
            status=403
        )

    if not driver.check_password(password):
        return error_response(
            message="كلمة المرور غير صحيحة",
            code="INVALID_PASSWORD",
            status=401
        )

    # Create JWT tokens with driver identity
    identity = f"driver_{driver.id}"
    access_token = create_access_token(
        identity=identity,
        expires_delta=timedelta(days=7)
    )
    refresh_token = create_refresh_token(
        identity=identity,
        expires_delta=timedelta(days=30)
    )

    return success_response(
        data={
            "driver": serialize_driver(driver),
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        message="تم تسجيل الدخول بنجاح"
    )


@driver_api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def driver_refresh_token():
    """
    Refresh access token using refresh token

    Headers:
    Authorization: Bearer <refresh_token>

    Returns new access token
    """
    identity = get_jwt_identity()

    if not identity or not identity.startswith('driver_'):
        return error_response(
            message="رمز غير صالح",
            code="INVALID_TOKEN",
            status=401
        )

    access_token = create_access_token(
        identity=identity,
        expires_delta=timedelta(days=7)
    )

    return success_response(
        data={"access_token": access_token},
        message="تم تجديد الرمز بنجاح"
    )


@driver_api_bp.route('/me', methods=['GET'])
@driver_required
def get_current_driver(driver):
    """
    Get current authenticated driver profile

    Headers:
    Authorization: Bearer <access_token>
    """
    return success_response(
        data={"driver": serialize_driver(driver)},
        message="تم جلب البيانات بنجاح"
    )


@driver_api_bp.route('/update-fcm-token', methods=['POST'])
@driver_required
def update_driver_fcm_token(driver):
    """
    Update driver's FCM token for push notifications

    Request body:
    {
        "fcm_token": "firebase_cloud_messaging_token"
    }
    """
    # Debug logging
    print(f"[FCM UPDATE] Driver {driver.id} ({driver.name}) requesting FCM token update")
    print(f"[FCM UPDATE] Request headers: {dict(request.headers)}")

    data = request.get_json()
    print(f"[FCM UPDATE] Request data: {data}")

    if not data or 'fcm_token' not in data:
        print(f"[FCM UPDATE] ERROR: Missing FCM token in request")
        return error_response(
            message="رمز FCM مطلوب",
            code="MISSING_FCM_TOKEN",
            status=400
        )

    old_token = driver.fcm_token
    new_token = data['fcm_token']

    print(f"[FCM UPDATE] Old token: {old_token[:50] if old_token else 'None'}...")
    print(f"[FCM UPDATE] New token: {new_token[:50] if new_token else 'None'}...")

    driver.fcm_token = new_token
    driver.fcm_token_updated_at = datetime.utcnow()
    db.session.commit()

    print(f"[FCM UPDATE] SUCCESS: Token saved for driver {driver.id}")
    print(f"[FCM UPDATE] Updated at: {driver.fcm_token_updated_at}")

    return success_response(
        message="تم تحديث رمز الإشعارات بنجاح"
    )


@driver_api_bp.route('/debug/fcm-status', methods=['GET'])
def debug_fcm_status():
    """
    Debug endpoint to check FCM token status for all drivers
    Access: /api/driver/debug/fcm-status
    """
    drivers = Driver.query.all()

    result = []
    for d in drivers:
        result.append({
            "id": d.id,
            "name": d.name,
            "driver_number": d.driver_number,
            "has_password": bool(d.password_hash),
            "phone": d.phone,
            "email": d.email,
            "national_id": d.national_id,
            "is_verified": d.is_verified,
            "is_approved": d.is_approved,
            "has_fcm_token": bool(d.fcm_token),
            "fcm_token_preview": d.fcm_token[:50] + "..." if d.fcm_token else None,
            "fcm_token_length": len(d.fcm_token) if d.fcm_token else 0,
            "fcm_token_updated_at": d.fcm_token_updated_at.isoformat() if d.fcm_token_updated_at else None,
            "created_at": d.created_at.isoformat() if d.created_at else None
        })

    return jsonify({
        "success": True,
        "total_drivers": len(drivers),
        "drivers_with_token": sum(1 for d in drivers if d.fcm_token),
        "drivers_without_token": sum(1 for d in drivers if not d.fcm_token),
        "drivers": result,
        "note": "Passwords are hashed and cannot be displayed. Use /admin/fleet/drivers/<id>/reset-password to generate a new password."
    })


@driver_api_bp.route('/debug/test-notification/<int:driver_id>', methods=['POST'])
def debug_test_notification(driver_id):
    """
    Debug endpoint to test sending notification to a specific driver
    Access: POST /api/driver/debug/test-notification/1
    """
    driver = Driver.query.get(driver_id)

    if not driver:
        return jsonify({"success": False, "error": "Driver not found"}), 404

    if not driver.fcm_token:
        return jsonify({
            "success": False,
            "error": "Driver has no FCM token",
            "driver_name": driver.name
        }), 400

    try:
        from app.utils.notification_service import send_driver_notification
        result = send_driver_notification(
            driver_id,
            "اختبار الإشعارات",
            "هذه رسالة اختبار - Test notification",
            {"type": "test", "timestamp": datetime.utcnow().isoformat()}
        )

        return jsonify({
            "success": result,
            "driver_id": driver_id,
            "driver_name": driver.name,
            "fcm_token_preview": driver.fcm_token[:50] + "...",
            "message": "Notification sent successfully" if result else "Failed to send notification"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "driver_name": driver.name
        }), 500


# ==================== Mission Endpoints ====================

@driver_api_bp.route('/missions', methods=['GET'])
@driver_required
def get_driver_missions(driver):
    """
    Get driver's missions with optional status filter

    Query params:
    - status: filter by mission status (pending, approved, in_progress, completed, rejected)
    - page: page number (default: 1)
    - per_page: items per page (default: 20)
    """
    status_filter = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Mission.query.filter_by(driver_id=driver.id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    # Order by most recent first
    query = query.order_by(Mission.created_at.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    missions = pagination.items

    return success_response(
        data={
            "missions": [serialize_mission(m) for m in missions],
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "total_pages": pagination.pages
        },
        message="تم جلب المهام بنجاح"
    )


@driver_api_bp.route('/missions/<int:mission_id>', methods=['GET'])
@driver_required
def get_mission_details(driver, mission_id):
    """
    Get details of a specific mission
    """
    mission = Mission.query.get(mission_id)

    if not mission:
        return error_response(
            message="المهمة غير موجودة",
            code="MISSION_NOT_FOUND",
            status=404
        )

    if mission.driver_id != driver.id:
        return error_response(
            message="لا يمكنك الوصول لهذه المهمة",
            code="ACCESS_DENIED",
            status=403
        )

    return success_response(
        data={"mission": serialize_mission(mission)},
        message="تم جلب تفاصيل المهمة بنجاح"
    )


@driver_api_bp.route('/missions/report', methods=['POST'])
@driver_required
def report_mission(driver):
    """
    Driver reports a new mission found on ride-sharing app

    Request body:
    {
        "from_location": "المعادي",
        "to_location": "مدينة نصر",
        "app_name": "uber",  // uber, indriver, didi, other
        "expected_cost": 150.0,
        "fleet_car_id": 1
    }
    """
    if not driver.is_approved:
        return error_response(
            message="يجب أن تكون معتمداً لإنشاء مهام",
            code="DRIVER_NOT_APPROVED",
            status=403
        )

    data = request.get_json()

    if not data:
        return error_response(
            message="البيانات مطلوبة",
            code="MISSING_DATA",
            status=400
        )

    # Validate required fields
    required_fields = ['from_location', 'to_location', 'app_name', 'expected_cost', 'fleet_car_id']
    missing_fields = [f for f in required_fields if not data.get(f)]

    if missing_fields:
        return error_response(
            message=f"الحقول التالية مطلوبة: {', '.join(missing_fields)}",
            code="MISSING_FIELDS",
            status=400
        )

    # Validate app_name
    valid_apps = ['uber', 'indriver', 'didi', 'other']
    app_name = data['app_name'].lower()
    if app_name not in valid_apps:
        return error_response(
            message="اسم التطبيق غير صالح",
            code="INVALID_APP_NAME",
            status=400
        )

    # Validate fleet car
    fleet_car = FleetCar.query.get(data['fleet_car_id'])
    if not fleet_car:
        return error_response(
            message="السيارة غير موجودة",
            code="CAR_NOT_FOUND",
            status=404
        )

    if fleet_car.status != 'available':
        return error_response(
            message="السيارة غير متاحة حالياً",
            code="CAR_NOT_AVAILABLE",
            status=400
        )

    try:
        # Create new mission
        mission = Mission(
            driver_id=driver.id,
            fleet_car_id=fleet_car.id,
            mission_type='driver_reported',
            app_name=app_name,
            from_location=data['from_location'],
            to_location=data['to_location'],
            expected_cost=float(data['expected_cost']),
            mission_date=datetime.utcnow().date(),
            status='pending',
            is_approved=False,
            can_start=False
        )

        db.session.add(mission)
        db.session.commit()

        # Send notification to admin (will be implemented in notification_service)
        try:
            from app.utils.notification_service import notify_admin_new_mission_request
            notify_admin_new_mission_request(driver, mission)
        except Exception as e:
            print(f"Failed to send admin notification: {e}")

        return success_response(
            data={"mission": serialize_mission(mission)},
            message="تم إرسال طلب المهمة بنجاح. في انتظار موافقة الإدارة",
            status=201
        )

    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء إنشاء المهمة",
            code="CREATE_ERROR",
            details=str(e),
            status=500
        )


@driver_api_bp.route('/missions/<int:mission_id>/start', methods=['POST'])
@driver_required
def start_mission(driver, mission_id):
    """
    Driver starts a mission (requires admin permission via can_start=True)

    Request body (optional):
    {
        "latitude": 30.0444,
        "longitude": 31.2357
    }
    """
    mission = Mission.query.get(mission_id)

    if not mission:
        return error_response(
            message="المهمة غير موجودة",
            code="MISSION_NOT_FOUND",
            status=404
        )

    if mission.driver_id != driver.id:
        return error_response(
            message="لا يمكنك الوصول لهذه المهمة",
            code="ACCESS_DENIED",
            status=403
        )

    # Check if mission can be started
    if mission.status == 'in_progress':
        return error_response(
            message="المهمة بدأت بالفعل",
            code="ALREADY_STARTED",
            status=400
        )

    if mission.status == 'completed':
        return error_response(
            message="المهمة مكتملة بالفعل",
            code="ALREADY_COMPLETED",
            status=400
        )

    if mission.status == 'rejected':
        return error_response(
            message="المهمة مرفوضة",
            code="MISSION_REJECTED",
            status=400
        )

    if not mission.can_start:
        return error_response(
            message="في انتظار إذن الإدارة للبدء",
            code="START_NOT_ALLOWED",
            status=403
        )

    try:
        # Get location from request body (optional)
        data = request.get_json() or {}
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not mission.start_mission(latitude=latitude, longitude=longitude):
            return error_response(
                message="لا يمكن بدء المهمة",
                code="START_FAILED",
                status=400
            )

        db.session.commit()

        # Send notification to admin
        try:
            from app.utils.notification_service import notify_admin_mission_started
            notify_admin_mission_started(driver, mission)
        except Exception as e:
            print(f"Failed to send admin notification: {e}")

        return success_response(
            data={"mission": serialize_mission(mission)},
            message="تم بدء المهمة بنجاح"
        )

    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء بدء المهمة",
            code="START_ERROR",
            details=str(e),
            status=500
        )


@driver_api_bp.route('/missions/<int:mission_id>/end', methods=['POST'])
@driver_required
def end_mission(driver, mission_id):
    """
    Driver ends a mission with actual costs

    Request body:
    {
        "total_revenue": 150.0,
        "fuel_cost": 30.0,
        "driver_fees": 50.0,  // Optional, can be set by admin later
        "distance_km": 15.5,
        "latitude": 30.0444,  // Optional, end location
        "longitude": 31.2357, // Optional, end location
        "notes": "تم بنجاح"
    }
    """
    mission = Mission.query.get(mission_id)

    if not mission:
        return error_response(
            message="المهمة غير موجودة",
            code="MISSION_NOT_FOUND",
            status=404
        )

    if mission.driver_id != driver.id:
        return error_response(
            message="لا يمكنك الوصول لهذه المهمة",
            code="ACCESS_DENIED",
            status=403
        )

    if mission.status != 'in_progress':
        return error_response(
            message="المهمة يجب أن تكون جارية لإنهائها",
            code="INVALID_STATUS",
            status=400
        )

    data = request.get_json()

    if not data:
        return error_response(
            message="البيانات مطلوبة",
            code="MISSING_DATA",
            status=400
        )

    # Validate required fields
    if 'total_revenue' not in data:
        return error_response(
            message="الإيراد الكلي مطلوب",
            code="MISSING_REVENUE",
            status=400
        )

    try:
        # Update mission with actual costs and location
        mission.end_mission(
            total_revenue=float(data.get('total_revenue', 0)),
            fuel_cost=float(data.get('fuel_cost', 0)),
            driver_fees=float(data.get('driver_fees', 0)),
            distance_km=float(data.get('distance_km', 0)),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )

        if data.get('notes'):
            mission.notes = data['notes']

        # Mark as completed
        mission.complete_mission()

        db.session.commit()

        # Send notification to admin
        try:
            from app.utils.notification_service import notify_admin_mission_completed
            notify_admin_mission_completed(driver, mission)
        except Exception as e:
            print(f"Failed to send admin notification: {e}")

        return success_response(
            data={"mission": serialize_mission(mission)},
            message="تم إنهاء المهمة بنجاح"
        )

    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء إنهاء المهمة",
            code="END_ERROR",
            details=str(e),
            status=500
        )


@driver_api_bp.route('/fleet-cars', methods=['GET'])
@driver_required
def get_available_fleet_cars(driver):
    """
    Get list of available fleet cars for mission reporting
    """
    cars = FleetCar.query.filter_by(status='available').all()

    return success_response(
        data={
            "cars": [serialize_fleet_car(car) for car in cars]
        },
        message="تم جلب السيارات المتاحة بنجاح"
    )


@driver_api_bp.route('/stats', methods=['GET'])
@driver_required
def get_driver_stats(driver):
    """
    Get driver's statistics and performance metrics
    """
    # Count missions by status
    total_missions = Mission.query.filter_by(driver_id=driver.id).count()
    completed_missions = Mission.query.filter_by(driver_id=driver.id, status='completed').count()
    pending_missions = Mission.query.filter_by(driver_id=driver.id, status='pending').count()
    in_progress_missions = Mission.query.filter_by(driver_id=driver.id, status='in_progress').count()

    # Calculate totals from completed missions
    completed = Mission.query.filter_by(driver_id=driver.id, status='completed').all()
    total_revenue = sum(m.total_revenue for m in completed)
    total_distance = sum(m.distance_km for m in completed)

    return success_response(
        data={
            "total_missions": total_missions,
            "completed_missions": completed_missions,
            "pending_missions": pending_missions,
            "in_progress_missions": in_progress_missions,
            "total_earnings": driver.total_earnings,
            "total_revenue_generated": total_revenue,
            "total_distance_km": total_distance,
            "rating": driver.rating
        },
        message="تم جلب الإحصائيات بنجاح"
    )


# ==================== Location Tracking Endpoints ====================

@driver_api_bp.route('/update-location', methods=['POST'])
@driver_required
def update_driver_location(driver):
    """
    Update driver's current GPS location

    Request body:
    {
        "latitude": 30.0444,
        "longitude": 31.2357
    }

    This should be called periodically by the driver app (every 10-30 seconds)
    to keep the location updated for fleet managers to track.
    """
    data = request.get_json()

    if not data:
        return error_response(
            message="البيانات مطلوبة",
            code="MISSING_DATA",
            status=400
        )

    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        return error_response(
            message="إحداثيات الموقع مطلوبة",
            code="MISSING_COORDINATES",
            status=400
        )

    try:
        # Validate coordinates are within reasonable range
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return error_response(
                message="إحداثيات غير صالحة",
                code="INVALID_COORDINATES",
                status=400
            )

        # Update driver location
        driver.update_location(latitude, longitude)
        db.session.commit()

        return success_response(
            data={
                "latitude": driver.current_latitude,
                "longitude": driver.current_longitude,
                "updated_at": driver.current_location_updated_at.isoformat()
            },
            message="تم تحديث الموقع بنجاح"
        )

    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ أثناء تحديث الموقع",
            code="UPDATE_ERROR",
            details=str(e),
            status=500
        )


@driver_api_bp.route('/go-online', methods=['POST'])
@driver_required
def driver_go_online(driver):
    """
    Mark driver as online (active in the app)

    Call this when driver opens the app or goes on duty
    """
    try:
        driver.is_online = True
        driver.last_seen_at = datetime.utcnow()
        db.session.commit()

        return success_response(
            message="أنت الآن متصل"
        )

    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ",
            code="ERROR",
            details=str(e),
            status=500
        )


@driver_api_bp.route('/go-offline', methods=['POST'])
@driver_required
def driver_go_offline(driver):
    """
    Mark driver as offline

    Call this when driver closes the app or goes off duty
    """
    try:
        driver.set_offline()
        db.session.commit()

        return success_response(
            message="أنت الآن غير متصل"
        )

    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ",
            code="ERROR",
            details=str(e),
            status=500
        )


@driver_api_bp.route('/heartbeat', methods=['POST'])
@driver_required
def driver_heartbeat(driver):
    """
    Heartbeat endpoint to keep driver marked as online
    and optionally update location

    Request body (optional):
    {
        "latitude": 30.0444,
        "longitude": 31.2357
    }

    Call this every 30 seconds to maintain online status
    """
    try:
        data = request.get_json() or {}

        # Update last seen
        driver.is_online = True
        driver.last_seen_at = datetime.utcnow()

        # Update location if provided
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude is not None and longitude is not None:
            if -90 <= latitude <= 90 and -180 <= longitude <= 180:
                driver.update_location(latitude, longitude)

        db.session.commit()

        return success_response(
            data={
                "is_online": driver.is_online,
                "last_seen_at": driver.last_seen_at.isoformat()
            },
            message="تم التحديث"
        )

    except Exception as e:
        db.session.rollback()
        return error_response(
            message="حدث خطأ",
            code="ERROR",
            details=str(e),
            status=500
        )
