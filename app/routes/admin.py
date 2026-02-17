"""
Admin dashboard routes
Full CRUD operations for apartments, users, and system management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, make_response, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import Optional
from werkzeug.utils import secure_filename
from app.models import db, Apartment, ApartmentImage, User, Share, Transaction, InvestmentRequest, Car, CarShare, CarInvestmentRequest, CarReferralTree, ReferralUsage, WithdrawalRequest
from app.utils.notification_service import send_push_notification, NotificationTemplates
from datetime import datetime
from sqlalchemy import func
import os
import csv
import io

bp = Blueprint('admin', __name__, url_prefix='/admin')


# Admin Forms
class UpdateStatusForm(FlaskForm):
    status = SelectField('الحالة', choices=[
        ('pending', 'قيد الانتظار'),
        ('under_review', 'قيد المراجعة'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
        ('documents_missing', 'مستندات ناقصة')
    ])
    admin_notes = TextAreaField('ملاحظات الإدارة', validators=[Optional()])
    missing_documents = TextAreaField('المستندات الناقصة', validators=[Optional()])


class UploadContractForm(FlaskForm):
    contract_file = FileField('ملف العقد', validators=[
        FileRequired(message='مطلوب'),
        FileAllowed(['pdf'], 'PDF فقط')
    ])


def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('الوصول مرفوض - صلاحيات المسؤول مطلوبة', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    # Calculate statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_apartments = Apartment.query.count()
    total_cars = Car.query.count()
    total_shares_sold = db.session.query(func.count(Share.id)).scalar() or 0
    total_revenue = db.session.query(func.sum(Share.share_price)).scalar() or 0
    
    # Investment request statistics
    pending_requests = InvestmentRequest.query.filter_by(status='pending').count()
    under_review_requests = InvestmentRequest.query.filter_by(status='under_review').count()
    
    # Referral rewards statistics
    users_with_rewards = User.query.filter(User.rewards_balance > 0).count()
    
    # Recent activity
    recent_transactions = Transaction.query.order_by(db.desc(Transaction.date)).limit(10).all()
    recent_users = User.query.filter_by(is_admin=False).order_by(db.desc(User.date_joined)).limit(5).all()
    
    # Apartment statistics
    apartments = Apartment.query.all()
    cars = Car.query.all()
    active_apartments = [apt for apt in apartments if not apt.is_closed]
    closed_apartments = [apt for apt in apartments if apt.is_closed]
    active_cars = [c for c in cars if not c.is_closed]
    closed_cars = [c for c in cars if c.is_closed]
    
    stats = {
        'total_users': total_users,
    'total_apartments': total_apartments,
    'total_cars': total_cars,
        'active_apartments': len(active_apartments),
        'closed_apartments': len(closed_apartments),
    'active_cars': len(active_cars),
    'closed_cars': len(closed_cars),
        'total_shares_sold': total_shares_sold,
        'total_revenue': total_revenue,
        'pending_requests': pending_requests,
        'under_review_requests': under_review_requests,
        'users_with_rewards': users_with_rewards
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_transactions=recent_transactions,
                         recent_users=recent_users)


# ============= CAR MANAGEMENT =============

@bp.route('/cars')
@admin_required
def cars_list():
    cars = Car.query.order_by(db.desc(Car.date_created)).all()
    return render_template('admin/cars.html', cars=cars)


@bp.route('/cars/add', methods=['GET', 'POST'])
@admin_required
def add_car():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        total_price = float(request.form.get('total_price'))
        total_shares = int(request.form.get('total_shares'))
        monthly_rent = float(request.form.get('monthly_rent'))
        location = request.form.get('location')
        brand = request.form.get('brand')
        model = request.form.get('model')
        year = request.form.get('year')

        image_filename = 'default_car.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f"{timestamp}_{filename}"
                # Save under cars images directory
                upload_dir = os.path.join(current_app.root_path, 'static', 'images', 'cars')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, image_filename))

        car = Car(
            title=title,
            description=description,
            image=image_filename,
            total_price=total_price,
            total_shares=total_shares,
            shares_available=total_shares,
            monthly_rent=monthly_rent,
            location=location,
            brand=brand,
            model=model,
            year=year
        )

        db.session.add(car)
        db.session.commit()
        
        # Broadcast new car notification to all users
        from app.utils.notification_service import send_notification_to_all_users
        notification = NotificationTemplates.new_asset(car.title, 'car')
        send_notification_to_all_users(
            title=notification["title"],
            body=notification["body"],
            data=notification.get("data")
        )

        flash('تم إضافة السيارة بنجاح', 'success')
        return redirect(url_for('admin.cars_list'))

    return render_template('admin/car_form.html', car=None)


@bp.route('/cars/edit/<int:car_id>', methods=['GET', 'POST'])
@admin_required
def edit_car(car_id):
    car = Car.query.get_or_404(car_id)
    if request.method == 'POST':
        car.title = request.form.get('title')
        car.description = request.form.get('description')
        car.total_price = float(request.form.get('total_price'))
        car.total_shares = int(request.form.get('total_shares'))
        car.monthly_rent = float(request.form.get('monthly_rent'))
        car.location = request.form.get('location')
        car.brand = request.form.get('brand')
        car.model = request.form.get('model')
        car.year = request.form.get('year')

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f"{timestamp}_{filename}"
                upload_dir = os.path.join(current_app.root_path, 'static', 'images', 'cars')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, image_filename))
                car.image = image_filename

        db.session.commit()
        flash('تم تحديث السيارة بنجاح', 'success')
        return redirect(url_for('admin.cars_list'))
    return render_template('admin/car_form.html', car=car)


@bp.route('/cars/delete/<int:car_id>', methods=['POST'])
@admin_required
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    if car.shares.count() > 0:
        flash('لا يمكن حذف سيارة تم بيع حصص فيها', 'error')
        return redirect(url_for('admin.cars_list'))
    db.session.delete(car)
    db.session.commit()
    flash('تم حذف السيارة بنجاح', 'success')
    return redirect(url_for('admin.cars_list'))


@bp.route('/cars/close/<int:car_id>', methods=['POST'])
@admin_required
def close_car(car_id):
    car = Car.query.get_or_404(car_id)
    car.is_closed = True
    db.session.commit()
    
    # Notify all car shareholders
    from app.models import CarShare
    notification = NotificationTemplates.asset_closed(car.title)
    for share in CarShare.query.filter_by(car_id=car_id).all():
        send_push_notification(
            user_id=share.user_id,
            title=notification["title"],
            body=notification["body"],
            data=notification.get("data")
        )
    
    flash(f'تم إغلاق السيارة: {car.title}', 'success')
    return redirect(url_for('admin.cars_list'))


@bp.route('/cars/reopen/<int:car_id>', methods=['POST'])
@admin_required
def reopen_car(car_id):
    car = Car.query.get_or_404(car_id)
    if car.shares_available > 0:
        car.is_closed = False
        db.session.commit()
        flash(f'تم إعادة فتح السيارة: {car.title}', 'success')
    else:
        flash('لا يمكن فتح سيارة ليس بها حصص متاحة', 'error')
    return redirect(url_for('admin.cars_list'))


# ============= APARTMENT MANAGEMENT =============

@bp.route('/apartments')
@admin_required
def apartments():
    """List all apartments"""
    apartments = Apartment.query.order_by(db.desc(Apartment.date_created)).all()
    return render_template('admin/apartments.html', apartments=apartments)


@bp.route('/apartments/add', methods=['GET', 'POST'])
@admin_required
def add_apartment():
    """Add new apartment"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        total_price = float(request.form.get('total_price'))
        total_shares = int(request.form.get('total_shares'))
        monthly_rent = float(request.form.get('monthly_rent'))
        location = request.form.get('location')
        
        # Handle main image upload (single)
        image_filename = 'default_apartment.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f"{timestamp}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))

        apartment = Apartment(
            title=title,
            description=description,
            image=image_filename,
            total_price=total_price,
            total_shares=total_shares,
            shares_available=total_shares,
            monthly_rent=monthly_rent,
            location=location
        )
        
        db.session.add(apartment)
        db.session.flush()  # get apartment.id

        # Handle additional images (multiple)
        if 'images' in request.files:
            files = request.files.getlist('images')
            order = 0
            for f in files:
                if f and f.filename:
                    filename = secure_filename(f.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    image_filename = f"{timestamp}_{filename}"
                    f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))
                    img = ApartmentImage(apartment_id=apartment.id, filename=image_filename, sort_order=order)
                    db.session.add(img)
                    order += 1

        db.session.commit()
        
        # Broadcast new asset notification to all users
        from app.utils.notification_service import send_notification_to_all_users
        notification = NotificationTemplates.new_asset(apartment.title, 'apartment')
        send_notification_to_all_users(
            title=notification["title"],
            body=notification["body"],
            data=notification.get("data")
        )
        
        flash('تم إضافة الشقة بنجاح', 'success')
        return redirect(url_for('admin.apartments'))
    
    return render_template('admin/apartment_form.html', apartment=None)


@bp.route('/apartments/edit/<int:apartment_id>', methods=['GET', 'POST'])
@admin_required
def edit_apartment(apartment_id):
    """Edit existing apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)
    
    if request.method == 'POST':
        apartment.title = request.form.get('title')
        apartment.description = request.form.get('description')
        apartment.total_price = float(request.form.get('total_price'))
        apartment.total_shares = int(request.form.get('total_shares'))
        apartment.monthly_rent = float(request.form.get('monthly_rent'))
        apartment.location = request.form.get('location')
        
        # Handle main image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f"{timestamp}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))
                apartment.image = image_filename

        # Handle deletion of selected additional images
        delete_ids = request.form.getlist('delete_images')
        if delete_ids:
            for img_id in delete_ids:
                try:
                    img = ApartmentImage.query.get(int(img_id))
                    if img and img.apartment_id == apartment.id:
                        # remove file from disk if exists
                        try:
                            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], img.filename))
                        except Exception:
                            pass
                        db.session.delete(img)
                except Exception:
                    # Ignore invalid ids or database issues for individual deletions
                    pass

        # Handle additional images upload
        if 'images' in request.files:
            files = request.files.getlist('images')
            # determine current max order
            max_order = db.session.query(db.func.coalesce(db.func.max(ApartmentImage.sort_order), 0)).filter(ApartmentImage.apartment_id == apartment.id).scalar() or 0
            order = max_order + 1
            for f in files:
                if f and f.filename:
                    filename = secure_filename(f.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    image_filename = f"{timestamp}_{filename}"
                    f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))
                    img = ApartmentImage(apartment_id=apartment.id, filename=image_filename, sort_order=order)
                    db.session.add(img)
                    order += 1
        
        db.session.commit()
        flash('تم تحديث الشقة بنجاح', 'success')
        return redirect(url_for('admin.apartments'))
    
    return render_template('admin/apartment_form.html', apartment=apartment)


@bp.route('/apartments/delete/<int:apartment_id>', methods=['POST'])
@admin_required
def delete_apartment(apartment_id):
    """Delete apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)
    
    # Check if apartment has shares sold
    if apartment.shares.count() > 0:
        flash('لا يمكن حذف شقة تم بيع حصص فيها', 'error')
        return redirect(url_for('admin.apartments'))
    
    db.session.delete(apartment)
    db.session.commit()
    
    flash('تم حذف الشقة بنجاح', 'success')
    return redirect(url_for('admin.apartments'))


@bp.route('/apartments/close/<int:apartment_id>', methods=['POST'])
@admin_required
def close_apartment(apartment_id):
    """Manually close an apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)
    apartment.is_closed = True
    db.session.commit()
    
    # Notify all shareholders that asset is closed
    from app.models import Share
    from app.utils.notification_service import send_push_notification
    shares = Share.query.filter_by(apartment_id=apartment_id).all()
    notification = NotificationTemplates.asset_closed(apartment.title)
    
    for share in shares:
        send_push_notification(
            user_id=share.user_id,
            title=notification["title"],
            body=notification["body"],
            data=notification.get("data")
        )
    
    flash(f'تم إغلاق الشقة: {apartment.title}', 'success')
    return redirect(url_for('admin.apartments'))


@bp.route('/apartments/reopen/<int:apartment_id>', methods=['POST'])
@admin_required
def reopen_apartment(apartment_id):
    """Reopen a closed apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)
    if apartment.shares_available > 0:
        apartment.is_closed = False
        db.session.commit()
        flash(f'تم إعادة فتح الشقة: {apartment.title}', 'success')
    else:
        flash('لا يمكن فتح شقة ليس بها حصص متاحة', 'error')
    
    return redirect(url_for('admin.apartments'))


# ============= USER MANAGEMENT =============

@bp.route('/users')
@admin_required
def users():
    """List all users"""
    users = User.query.filter_by(is_admin=False).order_by(db.desc(User.date_joined)).all()
    return render_template('admin/users.html', users=users)


@bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """View user details and investments"""
    user = User.query.get_or_404(user_id)
    
    # Get user's investments
    shares = Share.query.filter_by(user_id=user_id).all()
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(db.desc(Transaction.date)).all()
    
    # Group shares by apartment
    investments = {}
    for share in shares:
        apt_id = share.apartment_id
        if apt_id not in investments:
            investments[apt_id] = {
                'apartment': share.apartment,
                'shares_count': 0,
                'total_invested': 0
            }
        investments[apt_id]['shares_count'] += 1
        investments[apt_id]['total_invested'] += share.share_price
    
    return render_template('admin/user_detail.html',
                         user=user,
                         investments=investments.values(),
                         transactions=transactions)


@bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user (only if no investments)"""
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        flash('لا يمكن حذف حساب المسؤول', 'error')
        return redirect(url_for('admin.users'))
    
    if user.shares.count() > 0:
        flash('لا يمكن حذف مستخدم لديه استثمارات', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('تم حذف المستخدم بنجاح', 'success')
    return redirect(url_for('admin.users'))


# ============= TRANSACTION MANAGEMENT =============

@bp.route('/transactions')
@admin_required
def transactions():
    """View all transactions"""
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.order_by(db.desc(Transaction.date)).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('admin/transactions.html', transactions=transactions)


# ============= PAYOUT MANAGEMENT =============

@bp.route('/payouts')
@admin_required
def payouts():
    """Payout management page"""
    # Closed & eligible units
    closed_apartments = Apartment.query.filter_by(is_closed=True).all()
    eligible_apartments = Apartment.query.filter(
        Apartment.is_closed == False,
        Apartment.shares_available < Apartment.total_shares
    ).all()
    # Closed & eligible cars
    closed_cars = Car.query.filter_by(is_closed=True).all()
    eligible_cars = Car.query.filter(
        Car.is_closed == False,
        Car.shares_available < Car.total_shares
    ).all()

    return render_template('admin/payouts.html', 
                         closed_apartments=closed_apartments,
                         eligible_apartments=eligible_apartments,
                         closed_cars=closed_cars,
                         eligible_cars=eligible_cars)


@bp.route('/payouts/apartment/<int:apartment_id>')
@admin_required
def payout_apartment_detail(apartment_id):
    """Detail page showing all investors and payout history for an apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)

    # Get all unique investors with their share counts
    investor_data = db.session.query(
        User,
        func.count(Share.id).label('share_count')
    ).join(Share, Share.user_id == User.id)\
     .filter(Share.apartment_id == apartment_id)\
     .group_by(User.id)\
     .all()

    rent_per_share = apartment.monthly_rent / apartment.total_shares if apartment.total_shares > 0 else 0

    investors = []
    for user, share_count in investor_data:
        # Get total rental_income transactions for this user
        total_received = db.session.query(func.sum(Transaction.amount))\
            .filter(
                Transaction.user_id == user.id,
                Transaction.transaction_type == 'rental_income'
            ).scalar() or 0

        # Get last payout transaction
        last_payout = Transaction.query.filter(
            Transaction.user_id == user.id,
            Transaction.transaction_type == 'rental_income'
        ).order_by(Transaction.date.desc()).first()

        investors.append({
            'user': user,
            'share_count': share_count,
            'amount_per_payout': rent_per_share * share_count,
            'total_received': total_received,
            'last_payout_date': last_payout.date if last_payout else None
        })

    # Get payout history (all rental_income transactions for investors in this apartment)
    investor_ids = [inv['user'].id for inv in investors]
    payout_history = Transaction.query.filter(
        Transaction.user_id.in_(investor_ids),
        Transaction.transaction_type == 'rental_income'
    ).order_by(Transaction.date.desc()).limit(50).all()

    return render_template('admin/payout_detail.html',
                         asset=apartment,
                         asset_type='apartment',
                         investors=investors,
                         rent_per_share=rent_per_share,
                         payout_history=payout_history)


@bp.route('/payouts/car/<int:car_id>')
@admin_required
def payout_car_detail(car_id):
    """Detail page showing all investors and payout history for a car"""
    car = Car.query.get_or_404(car_id)

    investor_data = db.session.query(
        User,
        func.count(CarShare.id).label('share_count')
    ).join(CarShare, CarShare.user_id == User.id)\
     .filter(CarShare.car_id == car_id)\
     .group_by(User.id)\
     .all()

    rent_per_share = car.monthly_rent / car.total_shares if car.total_shares > 0 else 0

    investors = []
    for user, share_count in investor_data:
        total_received = db.session.query(func.sum(Transaction.amount))\
            .filter(
                Transaction.user_id == user.id,
                Transaction.transaction_type == 'rental_income'
            ).scalar() or 0

        last_payout = Transaction.query.filter(
            Transaction.user_id == user.id,
            Transaction.transaction_type == 'rental_income'
        ).order_by(Transaction.date.desc()).first()

        investors.append({
            'user': user,
            'share_count': share_count,
            'amount_per_payout': rent_per_share * share_count,
            'total_received': total_received,
            'last_payout_date': last_payout.date if last_payout else None
        })

    investor_ids = [inv['user'].id for inv in investors]
    payout_history = Transaction.query.filter(
        Transaction.user_id.in_(investor_ids),
        Transaction.transaction_type == 'rental_income'
    ).order_by(Transaction.date.desc()).limit(50).all()

    return render_template('admin/payout_detail.html',
                         asset=car,
                         asset_type='car',
                         investors=investors,
                         rent_per_share=rent_per_share,
                         payout_history=payout_history)


@bp.route('/debug/fix-approved-requests')
@admin_required
def fix_approved_requests():
    """Debug: Create missing shares for all approved requests that don't have shares yet"""
    fixed = []
    skipped = []

    for inv_request in InvestmentRequest.query.filter_by(status='approved').all():
        # Check if shares already exist for this user+apartment combo
        existing = Share.query.filter_by(
            user_id=inv_request.user_id,
            apartment_id=inv_request.apartment_id
        ).count()

        if existing >= inv_request.shares_requested:
            skipped.append(f"Request #{inv_request.id}: {inv_request.user.name} already has {existing} shares in {inv_request.apartment.title}")
            continue

        apartment = inv_request.apartment
        shares_to_create = inv_request.shares_requested - existing

        for _ in range(shares_to_create):
            share = Share(
                user_id=inv_request.user_id,
                apartment_id=inv_request.apartment_id,
                share_price=apartment.share_price
            )
            db.session.add(share)

        apartment.shares_available -= shares_to_create
        if apartment.shares_available <= 0:
            apartment.is_closed = True

        fixed.append(f"Request #{inv_request.id}: Created {shares_to_create} shares for {inv_request.user.name} in {apartment.title}")

    # Same for car investment requests
    for inv_request in CarInvestmentRequest.query.filter_by(status='approved').all():
        existing = CarShare.query.filter_by(
            user_id=inv_request.user_id,
            car_id=inv_request.car_id
        ).count()

        if existing >= inv_request.shares_requested:
            skipped.append(f"Car Request #{inv_request.id}: {inv_request.user.name} already has {existing} shares in {inv_request.car.title}")
            continue

        car = inv_request.car
        shares_to_create = inv_request.shares_requested - existing

        for _ in range(shares_to_create):
            share = CarShare(
                user_id=inv_request.user_id,
                car_id=inv_request.car_id,
                share_price=car.share_price
            )
            db.session.add(share)

        car.shares_available -= shares_to_create
        if car.shares_available <= 0:
            car.is_closed = True

        fixed.append(f"Car Request #{inv_request.id}: Created {shares_to_create} shares for {inv_request.user.name} in {car.title}")

    db.session.commit()

    return jsonify({
        "success": True,
        "fixed": fixed,
        "skipped": skipped,
        "total_fixed": len(fixed),
        "total_skipped": len(skipped)
    })


@bp.route('/debug/user-info/<email>')
@admin_required
def debug_user_info(email):
    """Debug: Show full user info including FCM token status and test notification"""
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": f"User with email {email} not found"}), 404

    # Get user shares
    apartment_shares = Share.query.filter_by(user_id=user.id).all()
    car_shares = CarShare.query.filter_by(user_id=user.id).all()

    # Get transactions
    recent_transactions = Transaction.query.filter_by(user_id=user.id)\
        .order_by(Transaction.date.desc()).limit(10).all()

    # Get investment requests
    inv_requests = InvestmentRequest.query.filter_by(user_id=user.id).all()

    # Try sending a test notification with detailed error reporting
    test_result = {"sent": None, "error": None, "firebase_init": None, "response": None}
    if user.fcm_token:
        try:
            import os
            from app.utils.notification_service import initialize_firebase

            # Step 1: Check Firebase config
            service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT') or \
                                   current_app.config.get('FIREBASE_SERVICE_ACCOUNT')
            test_result["firebase_config_exists"] = bool(service_account_path)
            if service_account_path:
                test_result["firebase_config_is_file"] = os.path.exists(service_account_path)
                test_result["firebase_config_path"] = service_account_path[:60] + "..." if len(service_account_path) > 60 else service_account_path

            # Step 2: Try init
            init_ok = initialize_firebase()
            test_result["firebase_init"] = init_ok

            if init_ok:
                # Step 3: Try sending directly
                from firebase_admin import messaging

                message = messaging.Message(
                    notification=messaging.Notification(
                        title="اختبار الإشعارات",
                        body="هذا إشعار تجريبي من لوحة التحكم",
                    ),
                    data={"type": "test", "screen": "wallet"},
                    token=user.fcm_token,
                )
                response = messaging.send(message)
                test_result["sent"] = True
                test_result["response"] = str(response)
        except Exception as e:
            test_result["sent"] = False
            test_result["error"] = f"{type(e).__name__}: {str(e)}"

    return jsonify({
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "wallet_balance": user.wallet_balance,
            "rewards_balance": user.rewards_balance,
            "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        },
        "fcm": {
            "has_token": bool(user.fcm_token),
            "token_preview": user.fcm_token[:80] + "..." if user.fcm_token else None,
            "token_length": len(user.fcm_token) if user.fcm_token else 0,
            "test_notification": test_result,
        },
        "apartment_shares": [
            {
                "share_id": s.id,
                "apartment_id": s.apartment_id,
                "apartment_title": s.apartment.title,
                "share_price": s.share_price,
                "date_purchased": s.date_purchased.isoformat() if s.date_purchased else None,
            } for s in apartment_shares
        ],
        "car_shares": [
            {
                "share_id": s.id,
                "car_id": s.car_id,
                "car_title": s.car.title,
                "share_price": s.share_price,
                "date_purchased": s.date_purchased.isoformat() if s.date_purchased else None,
            } for s in car_shares
        ],
        "investment_requests": [
            {
                "id": r.id,
                "apartment": r.apartment.title,
                "shares_requested": r.shares_requested,
                "status": r.status,
                "date_submitted": r.date_submitted.isoformat() if r.date_submitted else None,
            } for r in inv_requests
        ],
        "recent_transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "type": t.transaction_type,
                "date": t.date.isoformat() if t.date else None,
                "description": t.description,
            } for t in recent_transactions
        ],
    })


@bp.route('/payouts/distribute/<int:apartment_id>', methods=['POST'])
@admin_required
def distribute_payout(apartment_id):
    """Manually trigger payout for specific apartment"""
    apartment = Apartment.query.get_or_404(apartment_id)
    # Allow payouts for any apartment with investors (shares sold)
    if apartment.shares.count() == 0:
        flash('لا يمكن توزيع الإيجار على شقة بدون مستثمرين', 'error')
        return redirect(url_for('admin.payouts'))

    payouts = apartment.distribute_monthly_rent()
    db.session.commit()
    
    # Send notifications to all shareholders
    from app.models import Share
    shares = Share.query.filter_by(apartment_id=apartment_id).all()
    rent_per_share = apartment.monthly_rent / apartment.total_shares
    
    for share in shares:
        notification = NotificationTemplates.rental_income(rent_per_share, apartment.title)
        send_push_notification(
            user_id=share.user_id,
            title=notification["title"],
            body=notification["body"],
            data=notification.get("data")
        )
    
    flash(f'تم توزيع {payouts} دفعة بنجاح للشقة: {apartment.title}', 'success')
    return redirect(url_for('admin.payouts'))


@bp.route('/payouts/distribute-car/<int:car_id>', methods=['POST'])
@admin_required
def distribute_car_payout(car_id):
    """Manually trigger payout for specific car"""
    car = Car.query.get_or_404(car_id)
    if car.shares.count() == 0:
        flash('لا يمكن توزيع العائد على سيارة بدون مستثمرين', 'error')
        return redirect(url_for('admin.payouts'))
    payouts = car.distribute_monthly_rent()
    db.session.commit()
    
    # Send notifications to all shareholders
    rent_per_share = car.monthly_rent / car.total_shares
    for share in car.shares:
        notification = NotificationTemplates.car_income(rent_per_share, car.title)
        send_push_notification(
            user_id=share.user_id,
            title=notification["title"],
            body=notification["body"],
            data=notification.get("data")
        )
    
    flash(f'تم  توزيع {payouts} دفعة بنجاح للسيارة: {car.title}', 'success')
    return redirect(url_for('admin.payouts'))


@bp.route('/payouts/distribute-all', methods=['POST'])
@admin_required
def distribute_all_payouts():
    """Distribute payouts to all eligible units and cars"""
    apartments = Apartment.query.filter(
        Apartment.shares_available < Apartment.total_shares
    ).all()
    cars = Car.query.filter(
        Car.shares_available < Car.total_shares
    ).all()
    total_payouts = 0

    for apartment in apartments:
        if apartment.shares.count() > 0:
            total_payouts += apartment.distribute_monthly_rent()

    for car in cars:
        if car.shares.count() > 0:
            total_payouts += car.distribute_monthly_rent()

    db.session.commit()
    flash(f'تم توزيع {total_payouts} دفعة بنجاح على جميع الأصول', 'success')
    return redirect(url_for('admin.payouts'))


# Car Investment Requests

@bp.route('/car-investment-requests')
@admin_required
def car_investment_requests():
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    query = CarInvestmentRequest.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    pagination = query.order_by(db.desc(CarInvestmentRequest.date_submitted))\
        .paginate(page=page, per_page=20, error_out=False)

    all_count = CarInvestmentRequest.query.count()
    pending_count = CarInvestmentRequest.query.filter_by(status='pending').count()
    under_review_count = CarInvestmentRequest.query.filter_by(status='under_review').count()
    approved_count = CarInvestmentRequest.query.filter_by(status='approved').count()
    rejected_count = CarInvestmentRequest.query.filter_by(status='rejected').count()

    return render_template('admin/car_investment_requests.html',
                         requests=pagination.items,
                         pagination=pagination,
                         status_filter=status_filter,
                         all_count=all_count,
                         pending_count=pending_count,
                         under_review_count=under_review_count,
                         approved_count=approved_count,
                         rejected_count=rejected_count)


@bp.route('/car-investment-request/<int:request_id>')
@admin_required
def review_car_investment_request(request_id):
    inv_request = CarInvestmentRequest.query.get_or_404(request_id)
    status_form = UpdateStatusForm(obj=inv_request)
    contract_form = UploadContractForm()
    return render_template('admin/review_car_investment_request.html',
                         request=inv_request,
                         status_form=status_form,
                         contract_form=contract_form)


@bp.route('/car-investment-request/<int:request_id>/update-status', methods=['POST'])
@admin_required
def update_car_investment_request_status(request_id):
    inv_request = CarInvestmentRequest.query.get_or_404(request_id)
    form = UpdateStatusForm()
    if form.validate_on_submit():
        inv_request.status = form.status.data
        inv_request.admin_notes = form.admin_notes.data
        inv_request.missing_documents = form.missing_documents.data
        inv_request.date_reviewed = datetime.utcnow()
        inv_request.reviewed_by = current_user.id
        db.session.commit()
        flash('تم تحديث حالة الطلب بنجاح', 'success')
    else:
        flash('حدث خطأ في تحديث الحالة', 'error')
    return redirect(url_for('admin.review_car_investment_request', request_id=request_id))


@bp.route('/car-investment-request/<int:request_id>/upload-contract', methods=['POST'])
@admin_required
def upload_car_contract(request_id):
    inv_request = CarInvestmentRequest.query.get_or_404(request_id)
    form = UploadContractForm()
    if form.validate_on_submit():
        contracts_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'contracts')
        os.makedirs(contracts_dir, exist_ok=True)
        contract_file = form.contract_file.data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"car_contract_{request_id}_{timestamp}_{contract_file.filename}")
        filepath = os.path.join(contracts_dir, filename)
        contract_file.save(filepath)
        inv_request.contract_pdf = filename
        db.session.commit()
        flash('تم رفع العقد بنجاح', 'success')
    else:
        flash('حدث خطأ في رفع العقد', 'error')
    return redirect(url_for('admin.review_car_investment_request', request_id=request_id))


@bp.route('/car-investment-request/<int:request_id>/approve', methods=['POST'])
@admin_required
def approve_car_investment_request(request_id):
    inv_request = CarInvestmentRequest.query.get_or_404(request_id)
    inv_request.status = 'approved'
    inv_request.date_reviewed = datetime.utcnow()
    inv_request.reviewed_by = current_user.id

    car = inv_request.car
    investment_amount = car.share_price * inv_request.shares_requested

    for _ in range(inv_request.shares_requested):
        share = CarShare(
            user_id=inv_request.user_id,
            car_id=inv_request.car_id,
            share_price=car.share_price
        )
        db.session.add(share)

    car.shares_available -= inv_request.shares_requested
    if car.shares_available <= 0:
        car.is_closed = True

    if inv_request.referred_by_user_id:
        referrer_tree = CarReferralTree.query.filter_by(
            user_id=inv_request.referred_by_user_id,
            car_id=inv_request.car_id
        ).first()
        if referrer_tree:
            with db.session.no_autoflush:
                investor_tree = CarReferralTree.query.filter_by(
                    user_id=inv_request.user_id,
                    car_id=inv_request.car_id
                ).first()
                if investor_tree:
                    investor_tree.referred_by_user_id = inv_request.referred_by_user_id
                    investor_tree.level = referrer_tree.level + 1
                else:
                    investor_tree = CarReferralTree(
                        user_id=inv_request.user_id,
                        car_id=inv_request.car_id,
                        referred_by_user_id=inv_request.referred_by_user_id,
                        level=referrer_tree.level + 1
                    )
                    # Create a referral code for car context
                    investor_tree.referral_code = f"REF{inv_request.user_id}CAR{inv_request.car_id}{os.urandom(4).hex().upper()}"
                    db.session.add(investor_tree)

            upline = referrer_tree.get_upline(max_levels=10)
            upline.insert(0, referrer_tree)
            for level, node in enumerate(upline):
                reward_percentage = 0.05 * (0.1 ** level)
                reward_amount = investment_amount * (reward_percentage / 100)
                if reward_amount > 0:
                    upline_user = User.query.get(node.user_id)
                    upline_user.add_rewards(
                        reward_amount,
                        f'إحالة سيارة من {inv_request.user.name} - {car.title}'
                    )
                    node.total_rewards_earned += reward_amount
                    
                    # Send referral reward notification
                    ref_notification = NotificationTemplates.referral_reward(reward_amount)
                    send_push_notification(
                        user_id=node.user_id,
                        title=ref_notification["title"],
                        body=ref_notification["body"],
                        data=ref_notification.get("data")
                    )

    # NEW SIMPLE REFERRAL SYSTEM: Create ReferralUsage record
    if inv_request.referred_by_user_id:
        from app.models import ReferralUsage
        
        # Create usage record
        referral_usage = ReferralUsage(
            referrer_user_id=inv_request.referred_by_user_id,
            referee_user_id=inv_request.user_id,
            asset_type='car',
            asset_id=inv_request.car_id,
            investment_amount=investment_amount,
            shares_purchased=inv_request.shares_requested,
            date_used=datetime.utcnow()
        )
        db.session.add(referral_usage)
        print(f"✅ Created ReferralUsage record for car referrer user #{inv_request.referred_by_user_id}")

    db.session.commit()
    
    # Send push notification to user
    notification = NotificationTemplates.investment_approved(car.title, inv_request.shares_requested)
    send_push_notification(
        user_id=inv_request.user_id,
        title=notification["title"],
        body=notification["body"],
        data=notification.get("data")
    )
    
    flash(f'تمت الموافقة على الطلب #{request_id}', 'success')
    if inv_request.referred_by_user_id:
        flash('تم توزيع مكافآت الإحالة على السلسلة', 'info')
    return redirect(url_for('admin.review_car_investment_request', request_id=request_id))


@bp.route('/car-investment-request/<int:request_id>/reject', methods=['POST'])
@admin_required
def reject_car_investment_request(request_id):
    inv_request = CarInvestmentRequest.query.get_or_404(request_id)
    inv_request.status = 'rejected'
    inv_request.date_reviewed = datetime.utcnow()
    inv_request.reviewed_by = current_user.id
    db.session.commit()
    
    # Send push notification to user
    notification = NotificationTemplates.investment_rejected()
    send_push_notification(
        user_id=inv_request.user_id,
        title=notification["title"],
        body=notification["body"],
        data=notification.get("data")
    )
    
    flash(f'تم رفض الطلب #{request_id}', 'success')
    return redirect(url_for('admin.review_car_investment_request', request_id=request_id))


# Investment Requests Management

@bp.route('/investment-requests')
@admin_required
def investment_requests():
    """List all investment requests with filters"""
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = InvestmentRequest.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    pagination = query.order_by(db.desc(InvestmentRequest.date_submitted))\
        .paginate(page=page, per_page=20, error_out=False)
    
    # Get counts for each status
    all_count = InvestmentRequest.query.count()
    pending_count = InvestmentRequest.query.filter_by(status='pending').count()
    under_review_count = InvestmentRequest.query.filter_by(status='under_review').count()
    approved_count = InvestmentRequest.query.filter_by(status='approved').count()
    rejected_count = InvestmentRequest.query.filter_by(status='rejected').count()
    
    return render_template('admin/investment_requests.html',
                         requests=pagination.items,
                         pagination=pagination,
                         status_filter=status_filter,
                         all_count=all_count,
                         pending_count=pending_count,
                         under_review_count=under_review_count,
                         approved_count=approved_count,
                         rejected_count=rejected_count)


@bp.route('/investment-request/<int:request_id>')
@admin_required
def review_investment_request(request_id):
    """Review specific investment request"""
    inv_request = InvestmentRequest.query.get_or_404(request_id)
    status_form = UpdateStatusForm(obj=inv_request)
    contract_form = UploadContractForm()
    
    return render_template('admin/review_investment_request.html',
                         request=inv_request,
                         status_form=status_form,
                         contract_form=contract_form)


@bp.route('/investment-request/<int:request_id>/update-status', methods=['POST'])
@admin_required
def update_investment_request_status(request_id):
    """Update investment request status"""
    inv_request = InvestmentRequest.query.get_or_404(request_id)
    form = UpdateStatusForm()
    
    if form.validate_on_submit():
        old_status = inv_request.status
        inv_request.status = form.status.data
        inv_request.admin_notes = form.admin_notes.data
        inv_request.missing_documents = form.missing_documents.data
        inv_request.date_reviewed = datetime.utcnow()
        inv_request.reviewed_by = current_user.id

        # If status changed to approved, create shares (same as quick approve)
        if form.status.data == 'approved' and old_status != 'approved':
            apartment = inv_request.apartment

            # Create Share records
            for _ in range(inv_request.shares_requested):
                share = Share(
                    user_id=inv_request.user_id,
                    apartment_id=inv_request.apartment_id,
                    share_price=apartment.share_price
                )
                db.session.add(share)

            # Update available shares
            apartment.shares_available -= inv_request.shares_requested
            if apartment.shares_available <= 0:
                apartment.is_closed = True

            print(f"✅ Status update: Created {inv_request.shares_requested} shares for user {inv_request.user.email} in {apartment.title}")

        db.session.commit()

        # Send appropriate notification based on status
        if form.status.data == 'under_review':
            notification = NotificationTemplates.investment_under_review()
            send_push_notification(
                user_id=inv_request.user_id,
                title=notification["title"],
                body=notification["body"],
                data=notification.get("data")
            )
        elif form.status.data == 'documents_missing':
            notification = NotificationTemplates.documents_missing()
            send_push_notification(
                user_id=inv_request.user_id,
                title=notification["title"],
                body=notification["body"],
                data=notification.get("data")
            )
        elif form.status.data == 'approved' and old_status != 'approved':
            notification = NotificationTemplates.investment_approved(inv_request.apartment.title, inv_request.shares_requested)
            send_push_notification(
                user_id=inv_request.user_id,
                title=notification["title"],
                body=notification["body"],
                data=notification.get("data")
            )

        flash('تم تحديث حالة الطلب بنجاح', 'success')
    else:
        flash('حدث خطأ في تحديث الحالة', 'error')

    return redirect(url_for('admin.review_investment_request', request_id=request_id))


@bp.route('/investment-request/<int:request_id>/upload-contract', methods=['POST'])
@admin_required
def upload_contract(request_id):
    """Upload contract PDF for investment request"""
    inv_request = InvestmentRequest.query.get_or_404(request_id)
    form = UploadContractForm()
    
    if form.validate_on_submit():
        # Create contracts directory if it doesn't exist - use absolute path
        contracts_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'contracts')
        os.makedirs(contracts_dir, exist_ok=True)
        
        # Save contract file
        contract_file = form.contract_file.data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"contract_{request_id}_{timestamp}_{contract_file.filename}")
        filepath = os.path.join(contracts_dir, filename)
        contract_file.save(filepath)
        
        # Update request
        inv_request.contract_pdf = filename
        db.session.commit()
        
        flash('تم رفع العقد بنجاح', 'success')
    else:
        flash('حدث خطأ في رفع العقد', 'error')
    
    return redirect(url_for('admin.review_investment_request', request_id=request_id))


@bp.route('/investment-request/<int:request_id>/approve', methods=['POST'])
@admin_required
def approve_investment_request(request_id):
    """Quick approve investment request"""
    from app.models import ReferralTree, Share
    
    inv_request = InvestmentRequest.query.get_or_404(request_id)
    
    inv_request.status = 'approved'
    inv_request.date_reviewed = datetime.utcnow()
    inv_request.reviewed_by = current_user.id
    
    # Calculate investment amount
    apartment = inv_request.apartment
    investment_amount = apartment.share_price * inv_request.shares_requested
    
    # Create Share records for the approved investment
    created_shares = 0
    for _ in range(inv_request.shares_requested):
        share = Share(
            user_id=inv_request.user_id,
            apartment_id=inv_request.apartment_id,
            share_price=apartment.share_price
        )
        db.session.add(share)
        created_shares += 1
    
    print(f"✅ Created {created_shares} shares for user {inv_request.user.email}")
    
    # Update available shares
    apartment.shares_available -= inv_request.shares_requested
    
    # Close apartment if all shares sold
    if apartment.shares_available <= 0:
        apartment.is_closed = True
    
    # Add investor to referral tree if referred
    if inv_request.referred_by_user_id:
        # Get referrer's tree node
        referrer_tree = ReferralTree.query.filter_by(
            user_id=inv_request.referred_by_user_id,
            apartment_id=inv_request.apartment_id
        ).first()
        
        if referrer_tree:
            # Use session.no_autoflush to avoid premature flush and UNIQUE constraint error
            with db.session.no_autoflush:
                # Check if investor already has a tree node for this apartment
                investor_tree = ReferralTree.query.filter_by(
                    user_id=inv_request.user_id,
                    apartment_id=inv_request.apartment_id
                ).first()
                
                if investor_tree:
                    # User already has a tree node - update it with referral info
                    investor_tree.referred_by_user_id = inv_request.referred_by_user_id
                    investor_tree.level = referrer_tree.level + 1
                else:
                    # Create new tree node for investor
                    investor_tree = ReferralTree(
                        user_id=inv_request.user_id,
                        apartment_id=inv_request.apartment_id,
                        referred_by_user_id=inv_request.referred_by_user_id,
                        level=referrer_tree.level + 1
                    )
                    investor_tree.referral_code = inv_request.user.get_or_create_referral_code(investor_tree.apartment_id)
                    db.session.add(investor_tree)

            # Distribute rewards up the referral tree
            upline = referrer_tree.get_upline(max_levels=10)
            upline.insert(0, referrer_tree)  # Include direct referrer

            for level, node in enumerate(upline):
                # Calculate reward: 0.05% for level 0, 0.005% for level 1, etc.
                reward_percentage = 0.05 * (0.1 ** level)  # 0.05%, 0.005%, 0.0005%, etc.
                reward_amount = investment_amount * (reward_percentage / 100)

                if reward_amount > 0:
                    # Add reward to user's rewards balance
                    upline_user = User.query.get(node.user_id)
                    upline_user.add_rewards(
                        reward_amount, 
                        f'إحالة من {inv_request.user.name} - {apartment.title}'
                    )

                    # Update tree node's total rewards
                    node.total_rewards_earned += reward_amount
                    
                    # Send referral reward notification
                    ref_notification = NotificationTemplates.referral_reward(reward_amount)
                    send_push_notification(
                        user_id=node.user_id,
                        title=ref_notification["title"],
                        body=ref_notification["body"],
                        data=ref_notification.get("data")
                    )
    
    # NEW SIMPLE REFERRAL SYSTEM: Create ReferralUsage record
    if inv_request.referred_by_user_id:
        from app.models import ReferralUsage
        
        # Create usage record for the new simple system
        referral_usage = ReferralUsage(
            referrer_user_id=inv_request.referred_by_user_id,
            referee_user_id=inv_request.user_id,
            asset_type='apartment',
            asset_id=inv_request.apartment_id,
            investment_amount=investment_amount,
            shares_purchased=inv_request.shares_requested,
            date_used=datetime.utcnow()
        )
        db.session.add(referral_usage)
        print(f"✅ Created ReferralUsage record for referrer user #{inv_request.referred_by_user_id}")
    
    db.session.commit()
    
    # Send push notification to user
    notification = NotificationTemplates.investment_approved(apartment.title, inv_request.shares_requested)
    send_push_notification(
        user_id=inv_request.user_id,
        title=notification["title"],
        body=notification["body"],
        data=notification.get("data")
    )
    
    flash(f'تمت الموافقة على الطلب #{request_id}', 'success')
    if inv_request.referred_by_user_id:
        flash(f'تم توزيع مكافآت الإحالة على السلسلة', 'info')
    
    return redirect(url_for('admin.review_investment_request', request_id=request_id))


@bp.route('/investment-request/<int:request_id>/reject', methods=['POST'])
@admin_required
def reject_investment_request(request_id):
    """Quick reject investment request"""
    inv_request = InvestmentRequest.query.get_or_404(request_id)
    
    inv_request.status = 'rejected'
    inv_request.date_reviewed = datetime.utcnow()
    inv_request.reviewed_by = current_user.id
    
    db.session.commit()
    
    # Send push notification to user
    notification = NotificationTemplates.investment_rejected()
    send_push_notification(
        user_id=inv_request.user_id,
        title=notification["title"],
        body=notification["body"],
        data=notification.get("data")
    )
    
    flash(f'تم رفض الطلب #{request_id}', 'success')
    return redirect(url_for('admin.review_investment_request', request_id=request_id))


# ============= REFERRAL REWARDS MANAGEMENT =============

@bp.route('/users-with-rewards')
@admin_required
def users_with_rewards():
    """List all users with pending referral rewards"""
    users = User.query.filter(User.rewards_balance > 0).order_by(User.rewards_balance.desc()).all()
    
    return render_template('admin/users_rewards.html', users=users)


@bp.route('/payout-rewards/<int:user_id>', methods=['POST'])
@admin_required
def payout_rewards(user_id):
    """Transfer rewards from rewards_balance to wallet_balance"""
    user = User.query.get_or_404(user_id)
    
    if user.rewards_balance <= 0:
        flash('لا توجد مكافآت متاحة للدفع', 'error')
        return redirect(url_for('admin.users_with_rewards'))
    
    amount = user.rewards_balance
    
    # Transfer from rewards to wallet
    user.wallet_balance += amount
    user.rewards_balance = 0
    
    # Create transaction record
    transaction = Transaction(
        user_id=user.id,
        transaction_type='reward_payout',
        amount=amount,
        description=f'صرف مكافآت الإحالة - {amount:.2f} جنيه'
    )
    db.session.add(transaction)
    db.session.commit()
    
    # Send push notification to user
    notification = NotificationTemplates.rewards_payout(amount)
    send_push_notification(
        user_id=user.id,
        title=notification["title"],
        body=notification["body"],
        data=notification.get("data")
    )
    
    flash(f'تم صرف {amount:.2f} جنيه من مكافآت الإحالة إلى محفظة {user.name}', 'success')
    return redirect(url_for('admin.users_with_rewards'))


@bp.route('/payout-partial-rewards/<int:user_id>', methods=['POST'])
@admin_required
def payout_partial_rewards(user_id):
    """Transfer partial amount from rewards_balance to wallet_balance"""
    user = User.query.get_or_404(user_id)
    
    amount = float(request.form.get('amount', 0))
    
    if amount <= 0:
        flash('المبلغ يجب أن يكون أكبر من صفر', 'error')
        return redirect(url_for('admin.users_with_rewards'))
    
    if amount > user.rewards_balance:
        flash('المبلغ أكبر من رصيد المكافآت المتاح', 'error')
        return redirect(url_for('admin.users_with_rewards'))
    
    # Transfer from rewards to wallet
    user.wallet_balance += amount
    user.rewards_balance -= amount
    
    # Create transaction record
    transaction = Transaction(
        user_id=user.id,
        transaction_type='reward_payout',
        amount=amount,
        description=f'صرف جزئي لمكافآت الإحالة - {amount:.2f} جنيه'
    )
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'تم صرف {amount:.2f} جنيه من مكافآت الإحالة إلى محفظة {user.name}', 'success')
    return redirect(url_for('admin.users_with_rewards'))


@bp.route('/referrals-analytics')
@admin_required
def referrals_analytics():
    """Admin referral analytics dashboard"""
    
    # Get all referral usages with user details
    referral_usages = db.session.query(
        ReferralUsage,
        User.name.label('referrer_name'),
        User.email.label('referrer_email'),
        User.referral_number.label('referrer_ref_number')
    ).join(
        User, ReferralUsage.referrer_user_id == User.id
    ).order_by(ReferralUsage.date_used.desc()).all()
    
    # Get referee details for each usage
    referrals_with_details = []
    for usage, ref_name, ref_email, ref_number in referral_usages:
        referee = User.query.get(usage.referee_user_id)
        referrals_with_details.append({
            'usage': usage,
            'referrer_name': ref_name,
            'referrer_email': ref_email,
            'referrer_ref_number': ref_number,
            'referee_name': referee.name if referee else 'غير معروف',
            'referee_email': referee.email if referee else 'غير معروف'
        })
    
    # Get referral statistics per user
    referral_stats = db.session.query(
        User.id,
        User.name,
        User.email,
        User.referral_number,
        func.count(ReferralUsage.id).label('total_referrals'),
        func.sum(ReferralUsage.investment_amount).label('total_amount'),
        func.sum(ReferralUsage.shares_purchased).label('total_shares')
    ).outerjoin(
        ReferralUsage, User.id == ReferralUsage.referrer_user_id
    ).group_by(User.id).order_by(func.count(ReferralUsage.id).desc()).all()
    
    # Calculate totals
    total_referrals = len(referral_usages)
    total_amount = sum([usage[0].investment_amount for usage in referral_usages]) if referral_usages else 0
    total_shares = sum([usage[0].shares_purchased for usage in referral_usages]) if referral_usages else 0
    active_referrers = sum([1 for stat in referral_stats if stat.total_referrals > 0])
    
    # Convert Row objects to dictionaries for JSON serialization
    referral_stats_dict = [
        {
            'id': stat.id,
            'name': stat.name,
            'email': stat.email,
            'referral_number': stat.referral_number,
            'total_referrals': stat.total_referrals or 0,
            'total_amount': float(stat.total_amount or 0),
            'total_shares': stat.total_shares or 0
        }
        for stat in referral_stats
    ]
    
    return render_template('admin/referrals_analytics.html',
                         referrals=referrals_with_details,
                         referral_stats=referral_stats_dict,
                         total_referrals=total_referrals,
                         total_amount=total_amount,
                         total_shares=total_shares,
                         active_referrers=active_referrers)


@bp.route('/referrals-analytics/export')
@admin_required
def export_referrals():
    """Export referral data to CSV"""
    
    # Get all referral usages
    referral_usages = db.session.query(
        ReferralUsage,
        User.name.label('referrer_name'),
        User.email.label('referrer_email'),
        User.referral_number.label('referrer_ref_number')
    ).join(
        User, ReferralUsage.referrer_user_id == User.id
    ).order_by(ReferralUsage.date_used.desc()).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        'رقم الإحالة',
        'اسم المُحيل',
        'بريد المُحيل',
        'اسم المُستثمر',
        'نوع الأصل',
        'مبلغ الاستثمار',
        'عدد الأسهم',
        'التاريخ'
    ])
    
    # Write data
    for usage, ref_name, ref_email, ref_number in referral_usages:
        referee = User.query.get(usage.referee_user_id)
        writer.writerow([
            ref_number,
            ref_name,
            ref_email,
            referee.name if referee else 'غير معروف',
            'شقة' if usage.asset_type == 'apartment' else 'سيارة',
            f"{usage.investment_amount:,.0f} EGP",
            usage.shares_purchased,
            usage.date_used.strftime('%Y-%m-%d %H:%M')
        ])
    
    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=referrals_export.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    
    return response


# ==================== Withdrawal Requests (Admin) ====================

@bp.route('/withdrawal-requests')
@admin_required
def withdrawal_requests():
    """List all withdrawal requests"""
    status_filter = request.args.get('status', 'all')
    
    query = WithdrawalRequest.query
    
    if status_filter == 'pending':
        query = query.filter_by(status='pending')
    elif status_filter == 'approved':
        query = query.filter_by(status='approved')
    elif status_filter == 'rejected':
        query = query.filter_by(status='rejected')
    
    requests = query.order_by(WithdrawalRequest.request_date.desc()).all()
    
    # Count by status
    pending_count = WithdrawalRequest.query.filter_by(status='pending').count()
    
    return render_template('admin/withdrawal_requests.html',
                         requests=requests,
                         current_filter=status_filter,
                         pending_count=pending_count)


@bp.route('/withdrawal-request/<int:request_id>')
@admin_required
def withdrawal_request_detail(request_id):
    """View withdrawal request details"""
    withdrawal = WithdrawalRequest.query.get_or_404(request_id)
    form = WithdrawalProofForm()
    return render_template('admin/withdrawal_request_detail.html',
                         withdrawal=withdrawal, form=form)


class WithdrawalProofForm(FlaskForm):
    """Form for uploading withdrawal proof"""
    proof_image = FileField('صورة إثبات التحويل', validators=[
        FileRequired(message='مطلوب'),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images/PDF only')
    ])


@bp.route('/withdrawal-request/<int:request_id>/approve', methods=['POST'])
@admin_required
def approve_withdrawal(request_id):
    """Approve withdrawal request with proof upload"""
    withdrawal = WithdrawalRequest.query.get_or_404(request_id)
    
    if withdrawal.status != 'pending':
        flash('لا يمكن الموافقة على هذا الطلب', 'error')
        return redirect(url_for('admin.withdrawal_request_detail', request_id=request_id))
    
    form = WithdrawalProofForm()
    
    if form.validate_on_submit():
        # Upload proof image
        proof_file = form.proof_image.data
        if proof_file:
            filename = secure_filename(proof_file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"withdrawal_proof_{withdrawal.id}_{timestamp}_{filename}"
            
            # Save to uploads/withdrawal_proofs
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'withdrawal_proofs')
            os.makedirs(upload_folder, exist_ok=True)
            proof_path = os.path.join(upload_folder, filename)
            proof_file.save(proof_path)
            
            withdrawal.proof_image = filename
        
        # Check if user has sufficient balance
        user = withdrawal.user
        if user.wallet_balance < withdrawal.amount:
            flash('رصيد المستخدم غير كافي', 'error')
            return redirect(url_for('admin.withdrawal_request_detail', request_id=request_id))
        
        # Deduct from wallet
        user.wallet_balance -= withdrawal.amount
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            amount=-withdrawal.amount,  # Negative for withdrawal
            transaction_type='withdrawal',
            description=f'سحب عبر {withdrawal.payment_method_arabic} - {withdrawal.account_details}'
        )
        db.session.add(transaction)
        
        # Update withdrawal request
        withdrawal.status = 'approved'
        withdrawal.processed_date = datetime.utcnow()
        withdrawal.processed_by = current_user.id
        withdrawal.admin_notes = request.form.get('admin_notes', '')
        
        db.session.commit()
        
        # Send push notification to user
        notification = NotificationTemplates.withdrawal_approved(withdrawal.amount)
        send_push_notification(
            user_id=withdrawal.user_id,
            title=notification["title"],
            body=notification["body"],
            data=notification.get("data")
        )
        
        flash(f'تم الموافقة على طلب السحب وخصم {withdrawal.amount:,.0f} جنيه من محفظة {user.name}', 'success')
        return redirect(url_for('admin.withdrawal_requests'))
    
    # Form validation failed
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{error}', 'error')
    
    return redirect(url_for('admin.withdrawal_request_detail', request_id=request_id))


@bp.route('/withdrawal-request/<int:request_id>/reject', methods=['POST'])
@admin_required
def reject_withdrawal(request_id):
    """Reject withdrawal request"""
    withdrawal = WithdrawalRequest.query.get_or_404(request_id)
    
    if withdrawal.status != 'pending':
        flash('لا يمكن رفض هذا الطلب', 'error')
        return redirect(url_for('admin.withdrawal_request_detail', request_id=request_id))
    
    admin_notes = request.form.get('admin_notes', '').strip()
    
    if not admin_notes:
        flash('يرجى إضافة سبب الرفض', 'error')
        return redirect(url_for('admin.withdrawal_request_detail', request_id=request_id))
    
    withdrawal.status = 'rejected'
    withdrawal.processed_date = datetime.utcnow()
    withdrawal.processed_by = current_user.id
    withdrawal.admin_notes = admin_notes
    db.session.commit()
    
    # Send push notification to user
    notification = NotificationTemplates.withdrawal_rejected()
    send_push_notification(
        user_id=withdrawal.user_id,
        title=notification["title"],
        body=notification["body"],
        data=notification.get("data")
    )
    
    flash(f'تم رفض طلب السحب', 'success')
    return redirect(url_for('admin.withdrawal_requests'))


# ============= FLEET MANAGER MANAGEMENT =============

@bp.route('/fleet-managers')
@admin_required
def fleet_managers():
    """List all fleet managers"""
    managers = User.query.filter_by(is_fleet_manager=True).order_by(db.desc(User.date_joined)).all()
    return render_template('admin/fleet_managers.html', managers=managers)


@bp.route('/fleet-managers/add', methods=['GET', 'POST'])
@admin_required
def add_fleet_manager():
    """Add new fleet manager account"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()

        # Validation
        if not name or not email or not password:
            flash('جميع الحقول مطلوبة', 'error')
            return render_template('admin/fleet_manager_form.html', manager=None)

        # Check if email exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return render_template('admin/fleet_manager_form.html', manager=None)

        try:
            # Create new fleet manager user
            manager = User(
                name=name,
                email=email,
                phone=phone,
                is_fleet_manager=True,
                email_verified=True  # Auto verify admin-created accounts
            )
            manager.set_password(password)

            db.session.add(manager)
            db.session.commit()

            flash(f'تم إنشاء حساب مدير الأسطول: {name}', 'success')
            return redirect(url_for('admin.fleet_managers'))

        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'error')

    return render_template('admin/fleet_manager_form.html', manager=None)


@bp.route('/fleet-managers/<int:manager_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_fleet_manager(manager_id):
    """Edit fleet manager account"""
    manager = User.query.get_or_404(manager_id)

    if not manager.is_fleet_manager:
        flash('هذا المستخدم ليس مدير أسطول', 'error')
        return redirect(url_for('admin.fleet_managers'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        new_password = request.form.get('password', '')

        # Validation
        if not name or not email:
            flash('الاسم والبريد الإلكتروني مطلوبان', 'error')
            return render_template('admin/fleet_manager_form.html', manager=manager)

        # Check if email exists for another user
        existing_user = User.query.filter(User.email == email, User.id != manager_id).first()
        if existing_user:
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return render_template('admin/fleet_manager_form.html', manager=manager)

        try:
            manager.name = name
            manager.email = email
            manager.phone = phone

            # Update password if provided
            if new_password:
                manager.set_password(new_password)

            db.session.commit()

            flash('تم تحديث بيانات مدير الأسطول', 'success')
            return redirect(url_for('admin.fleet_managers'))

        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'error')

    return render_template('admin/fleet_manager_form.html', manager=manager)


@bp.route('/fleet-managers/<int:manager_id>/toggle', methods=['POST'])
@admin_required
def toggle_fleet_manager(manager_id):
    """Toggle fleet manager status"""
    manager = User.query.get_or_404(manager_id)

    try:
        manager.is_fleet_manager = not manager.is_fleet_manager
        db.session.commit()

        status = 'تم تفعيل' if manager.is_fleet_manager else 'تم إلغاء تفعيل'
        flash(f'{status} صلاحية مدير الأسطول لـ {manager.name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')

    return redirect(url_for('admin.fleet_managers'))


@bp.route('/fleet-managers/<int:manager_id>/delete', methods=['POST'])
@admin_required
def delete_fleet_manager(manager_id):
    """Delete fleet manager account"""
    manager = User.query.get_or_404(manager_id)

    if manager.is_admin:
        flash('لا يمكن حذف حساب المسؤول', 'error')
        return redirect(url_for('admin.fleet_managers'))

    try:
        # Just remove fleet manager role, don't delete if they have other data
        if manager.shares.count() > 0 or manager.transactions.count() > 0:
            manager.is_fleet_manager = False
            db.session.commit()
            flash('تم إلغاء صلاحية مدير الأسطول (المستخدم لديه بيانات أخرى)', 'success')
        else:
            db.session.delete(manager)
            db.session.commit()
            flash('تم حذف حساب مدير الأسطول', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')

    return redirect(url_for('admin.fleet_managers'))
