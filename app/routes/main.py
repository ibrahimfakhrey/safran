"""
Main public routes
Landing page and market listings
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from app.models import Apartment, User, ReferralTree, Car
from sqlalchemy import desc

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Landing page with hero section and featured apartments"""
    # Get statistics for counters
    total_users = User.query.count()
    total_apartments = Apartment.query.count()
    total_invested = sum([apt.total_price - (apt.shares_available * apt.share_price) 
                         for apt in Apartment.query.all()])
    
    # Get featured apartments (newest and available)
    featured_apartments = Apartment.query.filter_by(is_closed=False)\
        .order_by(desc(Apartment.date_created)).limit(6).all()
    # Get featured cars (newest and available)
    featured_cars = Car.query.filter_by(is_closed=False)\
        .order_by(desc(Car.date_created)).limit(6).all()
    
    stats = {
        'users': total_users,
        'apartments': total_apartments,
        'invested': total_invested
    }
    
    return render_template('user/landing.html', 
                         stats=stats, 
                         featured_apartments=featured_apartments,
                         featured_cars=featured_cars)


@bp.route('/market')
def market():
    """Market page showing all available apartments"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    location_filter = request.args.get('location', '')
    sort_by = request.args.get('sort', 'newest')
    
    # Base query
    query = Apartment.query
    
    # Apply filters
    if status_filter == 'available':
        query = query.filter(Apartment.is_closed == False, Apartment.shares_available > 0)
    elif status_filter == 'closed':
        query = query.filter(Apartment.is_closed == True)
    elif status_filter == 'new':
        query = query.filter(Apartment.shares_available == Apartment.total_shares)
    
    if location_filter:
        query = query.filter(Apartment.location.contains(location_filter))
    
    # Apply sorting
    if sort_by == 'newest':
        query = query.order_by(desc(Apartment.date_created))
    elif sort_by == 'price_low':
        query = query.order_by(Apartment.total_price)
    elif sort_by == 'price_high':
        query = query.order_by(desc(Apartment.total_price))
    elif sort_by == 'completion':
        query = query.order_by(Apartment.shares_available)
    
    apartments = query.all()
    
    # Get unique locations for filter dropdown
    locations = db.session.query(Apartment.location).distinct().all()
    locations = [loc[0] for loc in locations]
    
    return render_template('user/market.html', 
                         apartments=apartments,
                         locations=locations,
                         current_status=status_filter,
                         current_location=location_filter,
                         current_sort=sort_by)


@bp.route('/market/cars')
def market_cars():
    """Market page showing all available cars"""
    status_filter = request.args.get('status', 'all')
    location_filter = request.args.get('location', '')
    sort_by = request.args.get('sort', 'newest')

    query = Car.query

    if status_filter == 'available':
        query = query.filter(Car.is_closed == False, Car.shares_available > 0)
    elif status_filter == 'closed':
        query = query.filter(Car.is_closed == True)
    elif status_filter == 'new':
        query = query.filter(Car.shares_available == Car.total_shares)

    if location_filter:
        query = query.filter(Car.location.contains(location_filter))

    if sort_by == 'newest':
        query = query.order_by(desc(Car.date_created))
    elif sort_by == 'price_low':
        query = query.order_by(Car.total_price)
    elif sort_by == 'price_high':
        query = query.order_by(desc(Car.total_price))
    elif sort_by == 'completion':
        query = query.order_by(Car.shares_available)

    cars = query.all()

    locations = db.session.query(Car.location).distinct().all()
    locations = [loc[0] for loc in locations]

    return render_template('user/market_cars.html',
                         cars=cars,
                         locations=locations,
                         current_status=status_filter,
                         current_location=location_filter,
                         current_sort=sort_by)


@bp.route('/apartment/<int:apartment_id>')
def apartment_detail(apartment_id):
    """Apartment detail page"""
    apartment = Apartment.query.get_or_404(apartment_id)
    
    return render_template('user/apartment_detail.html', 
                         apartment=apartment,
                         investors_count=apartment.investors_count)


@bp.route('/car/<int:car_id>')
def car_detail(car_id):
    """Car detail page"""
    car = Car.query.get_or_404(car_id)

    return render_template('user/car_detail.html',
                         car=car,
                         investors_count=car.investors_count)


@bp.route('/invest-via-referral-car/<int:car_id>')
def referred_investment_car(car_id):
    """Handle referral links for car investment"""
    ref_code = request.args.get('ref')
    if not ref_code:
        flash('رابط الإحالة غير صحيح', 'error')
        return redirect(url_for('main.car_detail', car_id=car_id))

    referrer_tree = CarReferralTree.query.filter_by(
        car_id=car_id,
        referral_code=ref_code
    ).first()
    if not referrer_tree:
        flash('رمز الإحالة غير صحيح أو منتهي الصلاحية', 'error')
        return redirect(url_for('main.car_detail', car_id=car_id))

    session['referral_code'] = ref_code
    session['referral_car'] = car_id

    if current_user.is_authenticated:
        flash('تم تطبيق رمز الإحالة. سيحصل المُحيل على مكافأة عند قبول طلبك!', 'success')
        return redirect(url_for('user_views.car_investment_request', car_id=car_id))

    car = Car.query.get_or_404(car_id)
    referrer = User.query.get(referrer_tree.user_id)
    flash(f'تمت دعوتك للاستثمار في سيارة من قبل {referrer.name}. سجل حسابك أو سجل دخولك للمتابعة!', 'info')
    return render_template('user/referred_investment.html', car=car, referrer=referrer, ref_code=ref_code)


@bp.route('/about')
def about():
    """About page"""
    return render_template('user/about.html')


@bp.route('/faq')
def faq():
    """FAQ page in Arabic"""
    faqs = [
        {
            'question': 'ما هي المنصة؟',
            'answer': 'منصة استثمار عقاري تتيح لك شراء حصص في العقارات والحصول على دخل شهري من الإيجار'
        },
        {
            'question': 'كيف أبدأ الاستثمار؟',
            'answer': 'سجل حسابك، اختر العقار المناسب، واشترِ الحصص التي تناسب ميزانيتك'
        },
        {
            'question': 'متى أحصل على العائد؟',
            'answer': 'يتم توزيع الإيجار الشهري على المستثمرين في أول كل شهر تلقائياً'
        },
        {
            'question': 'ما هو الحد الأدنى للاستثمار؟',
            'answer': 'يمكنك شراء حصة واحدة من أي عقار، والحد الأدنى يبدأ من 5,000 جنيه'
        },
        {
            'question': 'هل يمكنني بيع حصصي؟',
            'answer': 'حالياً، الاستثمار طويل الأجل مع عوائد شهرية ثابتة'
        }
    ]
    return render_template('user/faq.html', faqs=faqs)


@bp.route('/invest-via-referral/<int:apartment_id>')
def referred_investment(apartment_id):
    """Handle referral links for investment"""
    ref_code = request.args.get('ref')
    
    if not ref_code:
        flash('رابط الإحالة غير صحيح', 'error')
        return redirect(url_for('main.apartment_detail', apartment_id=apartment_id))
    
    # Validate referral code
    referrer_tree = ReferralTree.query.filter_by(
        apartment_id=apartment_id,
        referral_code=ref_code
    ).first()
    
    if not referrer_tree:
        flash('رمز الإحالة غير صحيح أو منتهي الصلاحية', 'error')
        return redirect(url_for('main.apartment_detail', apartment_id=apartment_id))
    
    # Store referral info in session
    session['referral_code'] = ref_code
    session['referral_apartment'] = apartment_id
    
    # If user is logged in, redirect to investment request
    if current_user.is_authenticated:
        flash(f'تم تطبيق رمز الإحالة. سيحصل المُحيل على مكافأة عند قبول طلبك!', 'success')
        return redirect(url_for('user_views.investment_request', apartment_id=apartment_id))
    
    # If not logged in, show them they need to register/login
    apartment = Apartment.query.get_or_404(apartment_id)
    referrer = User.query.get(referrer_tree.user_id)
    
    flash(f'تمت دعوتك للاستثمار من قبل {referrer.name}. سجل حسابك أو سجل دخولك للمتابعة!', 'info')
    return render_template('user/referred_investment.html', 
                         apartment=apartment,
                         referrer=referrer,
                         ref_code=ref_code)


# Import db and Share for apartment_detail route
from app.models import db, Share, CarReferralTree


@bp.route('/privacy')
def privacy_policy():
    """Privacy policy page in Arabic"""
    return render_template('user/privacy.html')


@bp.route('/delete-account')
def delete_account_public():
    """Public delete account page - redirects to user route if logged in"""
    from flask_login import current_user
    if current_user.is_authenticated:
        return redirect(url_for('user_views.delete_account'))
    else:
        flash('يجب تسجيل الدخول أولاً لحذف حسابك', 'info')
        return redirect(url_for('auth.login'))
