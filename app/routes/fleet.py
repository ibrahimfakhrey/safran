"""
Fleet Management Routes
Admin-only routes for managing company cars, drivers, and missions
Includes driver verification and mission approval workflows
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date, time
import os
import secrets
import string

from app import db
from app.models import FleetCar, Driver, Mission
from config import Config


def generate_random_password(length=8):
    """Generate a random password for driver accounts"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Create blueprint
fleet = Blueprint('fleet', __name__, url_prefix='/admin/fleet')


def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('يجب أن تكون مسؤولاً للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def fleet_access_required(f):
    """Decorator to require fleet access (admin OR fleet_manager)"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('يجب تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('fleet.fleet_login'))
        if not (current_user.is_admin or current_user.is_fleet_manager):
            flash('ليس لديك صلاحية الوصول إلى إدارة الأسطول', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_driver_file(file, driver_id, file_type='photo'):
    """Save uploaded driver file and return filename"""
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"driver_{driver_id}_{file_type}.{ext}"
        filepath = os.path.join(Config.UPLOAD_FOLDER.replace('apartments', 'drivers'), filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        file.save(filepath)
        return filename
    return None


# ==================== FLEET DASHBOARD ====================

@fleet.route('/')
@login_required
@fleet_access_required
def dashboard():
    """Fleet management dashboard with statistics"""
    # Get statistics
    total_cars = FleetCar.query.count()
    available_cars = FleetCar.query.filter_by(status='available').count()
    total_drivers = Driver.query.count()
    approved_drivers = Driver.query.filter_by(is_approved=True).count()
    
    total_missions = Mission.query.count()
    completed_missions = Mission.query.filter_by(status='completed').count()
    active_missions = Mission.query.filter(Mission.status.in_(['pending', 'in_progress'])).count()
    
    # Calculate total revenue and profit
    completed = Mission.query.filter_by(status='completed').all()
    total_revenue = sum(m.total_revenue for m in completed)
    total_fuel_cost = sum(m.fuel_cost for m in completed)
    total_driver_fees = sum(m.driver_fees for m in completed)
    total_profit = sum(m.company_profit for m in completed)
    
    # Recent missions
    recent_missions = Mission.query.order_by(Mission.created_at.desc()).limit(10).all()
    
    return render_template('admin/fleet/dashboard.html',
                         total_cars=total_cars,
                         available_cars=available_cars,
                         total_drivers=total_drivers,
                         approved_drivers=approved_drivers,
                         total_missions=total_missions,
                         completed_missions=completed_missions,
                        active_missions=active_missions,
                         total_revenue=total_revenue,
                         total_fuel_cost=total_fuel_cost,
                         total_driver_fees=total_driver_fees,
                         total_profit=total_profit,
                         recent_missions=recent_missions)


# ==================== FLEET CARS ====================

@fleet.route('/cars')
@login_required
@fleet_access_required
def cars_list():
    """List all fleet cars"""
    status_filter = request.args.get('status', '')
    
    query = FleetCar.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    cars = query.order_by(FleetCar.created_at.desc()).all()
    
    return render_template('admin/fleet/cars.html', cars=cars, status_filter=status_filter)


@fleet.route('/cars/add', methods=['GET', 'POST'])
@login_required
@fleet_access_required
def add_car():
    """Add new fleet car"""
    if request.method == 'POST':
        try:
            car = FleetCar(
                brand=request.form.get('brand'),
                model=request.form.get('model'),
                plate_number=request.form.get('plate_number'),
                year=int(request.form.get('year')),
                color=request.form.get('color'),
                status=request.form.get('status', 'available')
            )
            
            db.session.add(car)
            db.session.commit()
            
            flash('تم إضافة السيارة بنجاح', 'success')
            return redirect(url_for('fleet.cars_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'error')
    
    return render_template('admin/fleet/car_form.html', car=None)


@fleet.route('/cars/<int:id>')
@login_required
@fleet_access_required
def car_details(id):
    """View fleet car details and mission history"""
    car = FleetCar.query.get_or_404(id)
    missions = car.missions.order_by(Mission.mission_date.desc()).all()
    
    return render_template('admin/fleet/car_details.html', car=car, missions=missions)


@fleet.route('/cars/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@fleet_access_required
def edit_car(id):
    """Edit fleet car"""
    car = FleetCar.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            car.brand = request.form.get('brand')
            car.model = request.form.get('model')
            car.plate_number = request.form.get('plate_number')
            car.year = int(request.form.get('year'))
            car.color = request.form.get('color')
            car.status = request.form.get('status')
            
            db.session.commit()
            
            flash('تم تحديث السيارة بنجاح', 'success')
            return redirect(url_for('fleet.car_details', id=car.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'error')
    
    return render_template('admin/fleet/car_form.html', car=car)


@fleet.route('/cars/<int:id>/delete', methods=['POST'])
@login_required
@fleet_access_required
def delete_car(id):
    """Delete fleet car"""
    car = FleetCar.query.get_or_404(id)
    
    # Check if car has missions
    if car.missions.count() > 0:
        flash('لا يمكن حذف السيارة لأنها مرتبطة بمهام', 'error')
        return redirect(url_for('fleet.car_details', id=id))
    
    try:
        db.session.delete(car)
        db.session.commit()
        flash('تم حذف السيارة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')
    
    return redirect(url_for('fleet.cars_list'))


# ==================== DRIVERS ====================

@fleet.route('/drivers')
@login_required
@fleet_access_required
def drivers_list():
    """List all drivers"""
    approval_filter = request.args.get('approved', '')
    
    query = Driver.query
    if approval_filter == 'yes':
        query = query.filter_by(is_approved=True)
    elif approval_filter == 'no':
        query = query.filter_by(is_approved=False)
    
    drivers = query.order_by(Driver.created_at.desc()).all()
    
    return render_template('admin/fleet/drivers.html', drivers=drivers, approval_filter=approval_filter)


@fleet.route('/drivers/add', methods=['GET', 'POST'])
@login_required
@fleet_access_required
def add_driver():
    """Add new driver"""
    if request.method == 'POST':
        try:
            driver = Driver(
                name=request.form.get('name'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                national_id=request.form.get('national_id'),
                rating=float(request.form.get('rating', 0)),
                is_approved=request.form.get('is_approved') == 'on'
            )
            
            db.session.add(driver)
            db.session.flush()  # Get driver ID
            
            # Handle file uploads
            if 'photo' in request.files:
                photo_file = request.files['photo']
                if photo_file.filename:
                    driver.photo_filename = save_driver_file(photo_file, driver.id, 'photo')
            
            if 'license' in request.files:
                license_file = request.files['license']
                if license_file.filename:
                    driver.license_filename = save_driver_file(license_file, driver.id, 'license')
            
            db.session.commit()
            
            flash('تم إضافة السائق بنجاح', 'success')
            return redirect(url_for('fleet.drivers_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'error')
    
    return render_template('admin/fleet/driver_form.html', driver=None)


@fleet.route('/drivers/<int:id>')
@login_required
@fleet_access_required
def driver_details(id):
    """View driver details and mission history"""
    driver = Driver.query.get_or_404(id)
    missions = driver.missions.order_by(Mission.mission_date.desc()).all()
    
    return render_template('admin/fleet/driver_details.html', driver=driver, missions=missions)


@fleet.route('/drivers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@fleet_access_required
def edit_driver(id):
    """Edit driver"""
    driver = Driver.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            driver.name = request.form.get('name')
            driver.phone = request.form.get('phone')
            driver.email = request.form.get('email')
            driver.national_id = request.form.get('national_id')
            driver.rating = float(request.form.get('rating', driver.rating))
            driver.is_approved = request.form.get('is_approved') == 'on'
            
            # Handle file uploads
            if 'photo' in request.files:
                photo_file = request.files['photo']
                if photo_file.filename:
                    driver.photo_filename = save_driver_file(photo_file, driver.id, 'photo')
            
            if 'license' in request.files:
                license_file = request.files['license']
                if license_file.filename:
                    driver.license_filename = save_driver_file(license_file, driver.id, 'license')
            
            db.session.commit()
            
            flash('تم تحديث السائق بنجاح', 'success')
            return redirect(url_for('fleet.driver_details', id=driver.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'error')
    
    return render_template('admin/fleet/driver_form.html', driver=driver)


@fleet.route('/drivers/<int:id>/approve', methods=['POST'])
@login_required
@fleet_access_required
def toggle_driver_approval(id):
    """Toggle driver approval status"""
    driver = Driver.query.get_or_404(id)

    try:
        driver.is_approved = not driver.is_approved
        db.session.commit()

        status = 'تم اعتماد' if driver.is_approved else 'تم إلغاء اعتماد'
        flash(f'{status} السائق بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')

    return redirect(url_for('fleet.driver_details', id=id))


@fleet.route('/drivers/<int:id>/verify', methods=['POST'])
@login_required
@fleet_access_required
def verify_driver(id):
    """
    Verify driver and generate login credentials for mobile app
    Creates driver_number and password
    """
    try:
        driver = Driver.query.get(id)
        if not driver:
            return jsonify({'success': False, 'error': 'السائق غير موجود'}), 404

        if driver.is_verified:
            return jsonify({
                'success': False,
                'error': 'السائق مفعّل بالفعل',
                'driver_number': driver.driver_number
            })

        # Generate unique driver number
        driver_number = Driver.generate_driver_number()

        # Generate random password
        password = generate_random_password(8)

        # Update driver
        driver.driver_number = driver_number
        driver.set_password(password)
        driver.is_verified = True

        # Also approve the driver if not already approved
        if not driver.is_approved:
            driver.is_approved = True

        db.session.commit()

        return jsonify({
            'success': True,
            'driver_number': driver_number,
            'password': password,
            'message': 'تم تفعيل السائق بنجاح'
        })

    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in verify_driver: {error_details}")
        return jsonify({'success': False, 'error': str(e)}), 500


@fleet.route('/drivers/<int:id>/reset-password', methods=['POST'])
@login_required
@fleet_access_required
def reset_driver_password(id):
    """Reset driver password and generate a new one"""
    try:
        driver = Driver.query.get(id)
        if not driver:
            return jsonify({'success': False, 'error': 'السائق غير موجود'}), 404

        if not driver.is_verified:
            return jsonify({'success': False, 'error': 'السائق غير مفعّل. قم بتفعيله أولاً'})

        # Generate new password
        new_password = generate_random_password(8)
        driver.set_password(new_password)
        db.session.commit()

        return jsonify({
            'success': True,
            'password': new_password,
            'driver_number': driver.driver_number,
            'message': 'تم إعادة تعيين كلمة المرور بنجاح'
        })

    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error in reset_driver_password: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500


@fleet.route('/drivers/<int:id>/delete', methods=['POST'])
@login_required
@fleet_access_required
def delete_driver(id):
    """Delete driver"""
    driver = Driver.query.get_or_404(id)
    
    # Check if driver has missions
    if driver.missions.count() > 0:
        flash('لا يمكن حذف السائق لأنه مرتبط بمهام', 'error')
        return redirect(url_for('fleet.driver_details', id=id))
    
    try:
        # Delete uploaded files
        if driver.photo_filename:
            photo_path = os.path.join(Config.UPLOAD_FOLDER.replace('apartments', 'drivers'), driver.photo_filename)
            if os.path.exists(photo_path):
                os.remove(photo_path)
        
        if driver.license_filename:
            license_path = os.path.join(Config.UPLOAD_FOLDER.replace('apartments', 'drivers'), driver.license_filename)
            if os.path.exists(license_path):
                os.remove(license_path)
        
        db.session.delete(driver)
        db.session.commit()
        flash('تم حذف السائق بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')
    
    return redirect(url_for('fleet.drivers_list'))


# ==================== MISSIONS ====================

@fleet.route('/missions')
@login_required
@fleet_access_required
def missions_list():
    """List all missions"""
    status_filter = request.args.get('status', '')
    car_filter = request.args.get('car_id', '')
    driver_filter = request.args.get('driver_id', '')
    
    query = Mission.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    if car_filter:
        query = query.filter_by(fleet_car_id=int(car_filter))
    if driver_filter:
        query = query.filter_by(driver_id=int(driver_filter))
    
    missions = query.order_by(Mission.mission_date.desc(), Mission.created_at.desc()).all()
    
    # Get all cars and drivers for filter dropdowns
    all_cars = FleetCar.query.order_by(FleetCar.brand, FleetCar.model).all()
    all_drivers = Driver.query.order_by(Driver.name).all()
    
    return render_template('admin/fleet/missions.html',
                         missions=missions,
                         all_cars=all_cars,
                         all_drivers=all_drivers,
                         status_filter=status_filter,
                         car_filter=car_filter,
                         driver_filter=driver_filter)


@fleet.route('/missions/add', methods=['GET', 'POST'])
@login_required
@fleet_access_required
def add_mission():
    """Create new mission"""
    if request.method == 'POST':
        try:
            # Parse date and time
            mission_date_str = request.form.get('mission_date')
            start_time_str = request.form.get('start_time')
            end_time_str = request.form.get('end_time')
            
            mission_date = datetime.strptime(mission_date_str, '%Y-%m-%d').date() if mission_date_str else date.today()
            start_time = datetime.strptime(start_time_str, '%H:%M').time() if start_time_str else None
            end_time = datetime.strptime(end_time_str, '%H:%M').time() if end_time_str else None
            
            # Calculate profit
            total_revenue = float(request.form.get('total_revenue', 0))
            fuel_cost = float(request.form.get('fuel_cost', 0))
            driver_fees = float(request.form.get('driver_fees', 0))
            company_profit = total_revenue - fuel_cost - driver_fees
            
            mission = Mission(
                fleet_car_id=int(request.form.get('fleet_car_id')),
                driver_id=int(request.form.get('driver_id')),
                from_location=request.form.get('from_location'),
                to_location=request.form.get('to_location'),
                distance_km=float(request.form.get('distance_km')),
                mission_date=mission_date,
                start_time=start_time,
                end_time=end_time,
                total_revenue=total_revenue,
                fuel_cost=fuel_cost,
                driver_fees=driver_fees,
                company_profit=company_profit,
                status=request.form.get('status', 'pending'),
                notes=request.form.get('notes')
            )
            
            # Update car status to in_mission if status is in_progress
            if mission.status == 'in_progress':
                car = FleetCar.query.get(mission.fleet_car_id)
                if car:
                    car.status = 'in_mission'
            
            db.session.add(mission)
            db.session.commit()

            # Send notification to driver about new mission assignment
            try:
                from app.utils.notification_service import send_driver_notification, DriverNotificationTemplates
                template = DriverNotificationTemplates.mission_assigned(
                    mission.from_location,
                    mission.to_location
                )
                send_driver_notification(
                    mission.driver_id,
                    template['title'],
                    template['body'],
                    {**template['data'], 'mission_id': str(mission.id)}
                )
            except Exception as e:
                print(f"Failed to send driver notification: {e}")

            flash('تم إنشاء المهمة بنجاح', 'success')
            return redirect(url_for('fleet.missions_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'error')
    
    # Get available cars and approved drivers
    cars = FleetCar.query.order_by(FleetCar.brand, FleetCar.model).all()
    drivers = Driver.query.filter_by(is_approved=True).order_by(Driver.name).all()
    
    return render_template('admin/fleet/mission_form.html',
                         mission=None,
                         cars=cars,
                         drivers=drivers)


@fleet.route('/missions/<int:id>')
@login_required
@fleet_access_required
def mission_details(id):
    """View mission details"""
    mission = Mission.query.get_or_404(id)
    
    return render_template('admin/fleet/mission_details.html', mission=mission)


@fleet.route('/missions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@fleet_access_required
def edit_mission(id):
    """Edit mission"""
    mission = Mission.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Parse date and time
            mission_date_str = request.form.get('mission_date')
            start_time_str = request.form.get('start_time')
            end_time_str = request.form.get('end_time')
            
            mission.mission_date = datetime.strptime(mission_date_str, '%Y-%m-%d').date() if mission_date_str else mission.mission_date
            mission.start_time = datetime.strptime(start_time_str, '%H:%M').time() if start_time_str else None
            mission.end_time = datetime.strptime(end_time_str, '%H:%M').time() if end_time_str else None
            
            mission.fleet_car_id = int(request.form.get('fleet_car_id'))
            mission.driver_id = int(request.form.get('driver_id'))
            mission.from_location = request.form.get('from_location')
            mission.to_location = request.form.get('to_location')
            mission.distance_km = float(request.form.get('distance_km'))
            mission.total_revenue = float(request.form.get('total_revenue'))
            mission.fuel_cost = float(request.form.get('fuel_cost'))
            mission.driver_fees = float(request.form.get('driver_fees'))
            mission.company_profit = mission.total_revenue - mission.fuel_cost - mission.driver_fees
            mission.status = request.form.get('status')
            mission.notes = request.form.get('notes')
            
            db.session.commit()
            
            flash('تم تحديث المهمة بنجاح', 'success')
            return redirect(url_for('fleet.mission_details', id=mission.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'error')
    
    # Get all cars and approved drivers
    cars = FleetCar.query.order_by(FleetCar.brand, FleetCar.model).all()
    drivers = Driver.query.filter_by(is_approved=True).order_by(Driver.name).all()
    
    return render_template('admin/fleet/mission_form.html',
                         mission=mission,
                         cars=cars,
                         drivers=drivers)


@fleet.route('/missions/<int:id>/complete', methods=['POST'])
@login_required
@fleet_access_required
def complete_mission(id):
    """Mark mission as completed"""
    mission = Mission.query.get_or_404(id)
    
    try:
        mission.complete_mission()  # Uses the model method
        db.session.commit()
        
        flash('تم إكمال المهمة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')
    
    return redirect(url_for('fleet.mission_details', id=id))


@fleet.route('/missions/<int:id>/cancel', methods=['POST'])
@login_required
@fleet_access_required
def cancel_mission(id):
    """Cancel a mission and notify driver"""
    mission = Mission.query.get_or_404(id)

    if mission.status in ['completed', 'cancelled']:
        flash('لا يمكن إلغاء هذه المهمة', 'warning')
        return redirect(url_for('fleet.mission_details', id=id))

    try:
        old_status = mission.status
        mission.status = 'cancelled'
        db.session.commit()

        # Send notification to driver
        try:
            from app.utils.notification_service import send_driver_notification, DriverNotificationTemplates
            template = DriverNotificationTemplates.mission_cancelled(
                mission.from_location,
                mission.to_location
            )
            send_driver_notification(
                mission.driver_id,
                template['title'],
                template['body'],
                {**template['data'], 'mission_id': str(mission.id)}
            )
        except Exception as e:
            print(f"Failed to send driver notification: {e}")

        flash('تم إلغاء المهمة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')

    return redirect(url_for('fleet.mission_details', id=id))


@fleet.route('/missions/<int:id>/delete', methods=['POST'])
@login_required
@fleet_access_required
def delete_mission(id):
    """Delete mission"""
    mission = Mission.query.get_or_404(id)

    try:
        db.session.delete(mission)
        db.session.commit()
        flash('تم حذف المهمة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')

    return redirect(url_for('fleet.missions_list'))


# ==================== MISSION REQUESTS (Driver-Reported) ====================

@fleet.route('/mission-requests')
@login_required
@fleet_access_required
def mission_requests():
    """List pending driver-reported mission requests"""
    status_filter = request.args.get('status', 'pending')

    query = Mission.query.filter_by(mission_type='driver_reported')

    if status_filter:
        query = query.filter_by(status=status_filter)

    missions = query.order_by(Mission.created_at.desc()).all()

    # Count by status for badges
    pending_count = Mission.query.filter_by(mission_type='driver_reported', status='pending').count()
    approved_count = Mission.query.filter_by(mission_type='driver_reported', status='approved').count()

    return render_template('admin/fleet/mission_requests.html',
                         missions=missions,
                         status_filter=status_filter,
                         pending_count=pending_count,
                         approved_count=approved_count)


@fleet.route('/missions/<int:id>/approve', methods=['POST'])
@login_required
@fleet_access_required
def approve_mission(id):
    """Approve a driver-reported mission request"""
    mission = Mission.query.get_or_404(id)

    if mission.mission_type != 'driver_reported':
        flash('هذه المهمة ليست من السائق', 'error')
        return redirect(url_for('fleet.mission_details', id=id))

    if mission.status != 'pending':
        flash('المهمة ليست في حالة انتظار', 'warning')
        return redirect(url_for('fleet.mission_details', id=id))

    try:
        mission.approve_mission()
        db.session.commit()

        # Send notification to driver
        try:
            from app.utils.notification_service import send_driver_notification, DriverNotificationTemplates
            template = DriverNotificationTemplates.mission_approved(
                mission.from_location,
                mission.to_location
            )
            send_driver_notification(
                mission.driver_id,
                template['title'],
                template['body'],
                template['data']
            )
        except Exception as e:
            print(f"Failed to send driver notification: {e}")

        flash('تم الموافقة على المهمة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')

    return redirect(url_for('fleet.mission_requests'))


@fleet.route('/missions/<int:id>/reject', methods=['POST'])
@login_required
@fleet_access_required
def reject_mission(id):
    """Reject a driver-reported mission request"""
    mission = Mission.query.get_or_404(id)

    if mission.mission_type != 'driver_reported':
        flash('هذه المهمة ليست من السائق', 'error')
        return redirect(url_for('fleet.mission_details', id=id))

    if mission.status not in ['pending', 'approved']:
        flash('لا يمكن رفض هذه المهمة', 'warning')
        return redirect(url_for('fleet.mission_details', id=id))

    reason = request.form.get('reason', '')

    try:
        mission.reject_mission(reason)
        db.session.commit()

        # Send notification to driver
        try:
            from app.utils.notification_service import send_driver_notification, DriverNotificationTemplates
            template = DriverNotificationTemplates.mission_rejected(reason)
            send_driver_notification(
                mission.driver_id,
                template['title'],
                template['body'],
                template['data']
            )
        except Exception as e:
            print(f"Failed to send driver notification: {e}")

        flash('تم رفض المهمة', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')

    return redirect(url_for('fleet.mission_requests'))


@fleet.route('/missions/<int:id>/allow-start', methods=['POST'])
@login_required
@fleet_access_required
def allow_mission_start(id):
    """Give driver permission to start the mission"""
    mission = Mission.query.get_or_404(id)

    # For admin-assigned missions, they should be approved first
    if mission.mission_type == 'driver_reported' and not mission.is_approved:
        flash('يجب الموافقة على المهمة أولاً', 'warning')
        return redirect(url_for('fleet.mission_details', id=id))

    if mission.can_start:
        flash('السائق لديه إذن البدء بالفعل', 'warning')
        return redirect(url_for('fleet.mission_details', id=id))

    if mission.status in ['completed', 'cancelled', 'rejected']:
        flash('لا يمكن السماح ببدء هذه المهمة', 'error')
        return redirect(url_for('fleet.mission_details', id=id))

    try:
        mission.allow_start()

        # For admin-assigned missions, also mark as approved if not already
        if mission.mission_type == 'admin_assigned' and not mission.is_approved:
            mission.is_approved = True
            mission.approved_at = datetime.utcnow()

        db.session.commit()

        # Send notification to driver
        try:
            from app.utils.notification_service import send_driver_notification, DriverNotificationTemplates
            template = DriverNotificationTemplates.start_permission_granted(
                mission.from_location,
                mission.to_location
            )
            send_driver_notification(
                mission.driver_id,
                template['title'],
                template['body'],
                template['data']
            )
        except Exception as e:
            print(f"Failed to send driver notification: {e}")

        flash('تم إعطاء إذن البدء للسائق', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')

    # Redirect based on where the request came from
    if request.form.get('from_requests'):
        return redirect(url_for('fleet.mission_requests'))
    return redirect(url_for('fleet.mission_details', id=id))


# ==================== FLEET MANAGER AUTHENTICATION ====================

@fleet.route('/login', methods=['GET', 'POST'])
def fleet_login():
    """Fleet manager login page"""
    from flask_login import login_user
    from app.models import User

    if current_user.is_authenticated:
        if current_user.is_admin or current_user.is_fleet_manager:
            return redirect(url_for('fleet.dashboard'))
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('البريد الإلكتروني غير مسجل', 'error')
            return render_template('fleet/login.html')

        if not user.check_password(password):
            flash('كلمة المرور غير صحيحة', 'error')
            return render_template('fleet/login.html')

        if not user.is_fleet_manager and not user.is_admin:
            flash('هذا الحساب ليس لديه صلاحية إدارة الأسطول', 'error')
            return render_template('fleet/login.html')

        login_user(user, remember=True)
        flash(f'مرحباً {user.name}!', 'success')
        return redirect(url_for('fleet.dashboard'))

    return render_template('fleet/login.html')


@fleet.route('/logout')
@login_required
def fleet_logout():
    """Fleet manager logout"""
    from flask_login import logout_user
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('fleet.fleet_login'))


# ==================== DRIVER LOCATION TRACKING ====================

@fleet.route('/drivers/locations')
@login_required
@fleet_access_required
def driver_locations():
    """Page showing all drivers on a map with real-time locations"""
    drivers = Driver.query.filter_by(is_approved=True).all()

    # Count online drivers (using is_truly_online which checks heartbeat timeout)
    online_count = sum(1 for d in drivers if d.is_truly_online)
    total_count = len(drivers)

    return render_template('fleet/driver_locations.html',
                         drivers=drivers,
                         online_count=online_count,
                         total_count=total_count)


@fleet.route('/api/drivers/locations')
@login_required
@fleet_access_required
def api_driver_locations():
    """API endpoint to get all driver locations for real-time updates"""
    drivers = Driver.query.filter_by(is_approved=True).all()

    drivers_data = []
    for driver in drivers:
        # Convert UTC to Egypt time (UTC+2) for display
        location_updated_egypt = None
        if driver.current_location_updated_at:
            from datetime import timedelta
            egypt_time = driver.current_location_updated_at + timedelta(hours=2)
            location_updated_egypt = egypt_time.strftime('%H:%M:%S')

        driver_info = {
            'id': driver.id,
            'name': driver.name,
            'phone': driver.phone,
            'driver_number': driver.driver_number,
            'is_online': driver.is_truly_online,  # Use timeout-based check
            'has_location': driver.current_latitude is not None,
            'latitude': driver.current_latitude,
            'longitude': driver.current_longitude,
            'location_updated_at': driver.current_location_updated_at.isoformat() if driver.current_location_updated_at else None,
            'location_updated_at_egypt': location_updated_egypt,  # Egyptian time
            'has_recent_location': driver.has_recent_location,
            'photo_url': f"/static/uploads/drivers/{driver.photo_filename}" if driver.photo_filename else None,
            'current_mission': None
        }

        # Get current active mission if any
        active_mission = Mission.query.filter_by(
            driver_id=driver.id,
            status='in_progress'
        ).first()

        if active_mission:
            driver_info['current_mission'] = {
                'id': active_mission.id,
                'from': active_mission.from_location,
                'to': active_mission.to_location,
                'car': f"{active_mission.fleet_car.brand} {active_mission.fleet_car.model}" if active_mission.fleet_car else None
            }

        drivers_data.append(driver_info)

    return jsonify({
        'success': True,
        'drivers': drivers_data,
        'online_count': sum(1 for d in drivers if d.is_truly_online),
        'total_count': len(drivers_data)
    })


@fleet.route('/api/driver/<int:id>/location')
@login_required
@fleet_access_required
def api_single_driver_location(id):
    """API endpoint to get single driver location"""
    driver = Driver.query.get_or_404(id)

    return jsonify({
        'success': True,
        'driver': {
            'id': driver.id,
            'name': driver.name,
            'is_online': driver.is_online,
            'latitude': driver.current_latitude,
            'longitude': driver.current_longitude,
            'location_updated_at': driver.current_location_updated_at.isoformat() if driver.current_location_updated_at else None,
            'has_recent_location': driver.has_recent_location
        }
    })
