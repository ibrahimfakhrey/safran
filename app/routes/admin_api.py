"""
Admin API Routes with JWT Authentication
RESTful API endpoints for Flutter admin app
All routes prefixed with /api/admin/
"""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
import datetime
from app.models import (
    db, User, Apartment, Car, Share, CarShare, 
    InvestmentRequest, CarInvestmentRequest, Transaction,
    WithdrawalRequest, ReferralUsage
)
from sqlalchemy import func
from werkzeug.security import check_password_hash
import os
from werkzeug.utils import secure_filename

bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')

# JWT Configuration will be accessed via current_app.config


def create_token(user_id):
    """Create JWT token for authenticated admin"""
    JWT_SECRET = current_app.config.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_EXP_DELTA_HOURS = 24
    
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXP_DELTA_HOURS),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token


def token_required(f):
    """Decorator to require valid JWT token and admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        try:
            # Decode token
            JWT_SECRET = current_app.config.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'success': False, 'message': 'User not found'}), 401
            
            if not current_user.is_admin:
                return jsonify({'success': False, 'message': 'Admin access required'}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@bp.route('/login', methods=['POST'])
def login():
    """
    Admin login - Returns JWT token
    POST /api/admin/login
    Body: {"email": "admin@example.com", "password": "password"}
    """
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    if not user.is_admin:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    token = create_token(user.id)
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'data': {
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }
    }), 200


@bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """
    Refresh JWT token
    POST /api/admin/refresh
    Headers: Authorization: Bearer <token>
    """
    new_token = create_token(current_user.id)
    
    return jsonify({
        'success': True,
        'message': 'Token refreshed',
        'data': {'token': new_token}
    }), 200


# ============================================
# DASHBOARD & ANALYTICS
# ============================================

@bp.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):
    """
    Get dashboard statistics
    GET /api/admin/dashboard
    """
    total_users = User.query.filter_by(is_admin=False).count()
    total_apartments = Apartment.query.count()
    total_cars = Car.query.count()
    
    pending_apartment_requests = InvestmentRequest.query.filter_by(status='pending').count()
    pending_car_requests = CarInvestmentRequest.query.filter_by(status='pending').count()
    pending_withdrawals = WithdrawalRequest.query.filter_by(status='pending').count()
    
    total_investments = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == 'investment'
    ).scalar() or 0
    
    recent_transactions = Transaction.query.order_by(Transaction.date.desc()).limit(10).all()
    
    return jsonify({
        'success': True,
        'data': {
            'statistics': {
                'total_users': total_users,
                'total_apartments': total_apartments,
                'total_cars': total_cars,
                'pending_apartment_requests': pending_apartment_requests,
                'pending_car_requests': pending_car_requests,
                'pending_withdrawals': pending_withdrawals,
                'total_investments': float(total_investments)
            },
            'recent_transactions': [
                {
                    'id': t.id,
                    'user_id': t.user_id,
                    'user_name': t.user.name,
                    'amount': float(t.amount),
                    'type': t.transaction_type,
                    'description': t.description,
                    'date': t.date.isoformat()
                }
                for t in recent_transactions
            ]
        }
    }), 200


@bp.route('/analytics/referrals', methods=['GET'])
@token_required
def referral_analytics(current_user):
    """
    Get referral analytics data
    GET /api/admin/analytics/referrals
    """
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
    ).group_by(User.id).order_by(func.count(ReferralUsage.id).desc()).limit(10).all()
    
    total_referrals = ReferralUsage.query.count()
    total_amount = db.session.query(func.sum(ReferralUsage.investment_amount)).scalar() or 0
    
    return jsonify({
        'success': True,
        'data': {
            'total_referrals': total_referrals,
            'total_amount': float(total_amount),
            'top_referrers': [
                {
                    'user_id': stat.id,
                    'name': stat.name,
                    'email': stat.email,
                    'referral_number': stat.referral_number,
                    'total_referrals': stat.total_referrals or 0,
                    'total_amount': float(stat.total_amount or 0),
                    'total_shares': stat.total_shares or 0
                }
                for stat in referral_stats
            ]
        }
    }), 200


# ============================================
# USER MANAGEMENT
# ============================================

@bp.route('/users', methods=['GET'])
@token_required
def list_users(current_user):
    """
    List all users with pagination
    GET /api/admin/users?page=1&per_page=20
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    users = User.query.filter_by(is_admin=False).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'users': [
                {
                    'id': u.id,
                    'name': u.name,
                    'email': u.email,
                    'phone': u.phone,
                    'wallet_balance': float(u.wallet_balance),
                    'rewards_balance': float(u.rewards_balance),
                    'referral_number': u.referral_number,
                    'date_joined': u.date_joined.isoformat() if u.date_joined else None
                }
                for u in users.items
            ],
            'pagination': {
                'page': users.page,
                'per_page': users.per_page,
                'total': users.total,
                'pages': users.pages
            }
        }
    }), 200


@bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """
    Get user details with investments
    GET /api/admin/users/{id}
    """
    user = User.query.get_or_404(user_id)
    
    # Get user's investments
    apartment_shares = Share.query.filter_by(user_id=user_id).all()
    car_shares = CarShare.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'success': True,
        'data': {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'national_id': user.national_id,
                'wallet_balance': float(user.wallet_balance),
                'rewards_balance': float(user.rewards_balance),
                'referral_number': user.referral_number,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None
            },
            'investments': {
                'apartments': [
                    {
                        'id': s.id,
                        'apartment_id': s.apartment_id,
                        'apartment_title': s.apartment.title,
                        'share_price': float(s.share_price),
                        'date_purchased': s.date_purchased.isoformat() if s.date_purchased else None
                    }
                    for s in apartment_shares
                ],
                'cars': [
                    {
                        'id': s.id,
                        'car_id': s.car_id,
                        'car_title': s.car.title,
                        'share_price': float(s.share_price),
                        'date_purchased': s.date_purchased.isoformat() if s.date_purchased else None
                    }
                    for s in car_shares
                ]
            }
        }
    }), 200


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    """
    Delete user
    DELETE /api/admin/users/{id}
    """
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        return jsonify({'success': False, 'message': 'Cannot delete admin user'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'User deleted successfully'
    }), 200


@bp.route('/users/<int:user_id>/payout-rewards', methods=['POST'])
@token_required
def payout_user_rewards(current_user, user_id):
    """
    Payout user rewards to wallet
    POST /api/admin/users/{id}/payout-rewards
    Body: {"amount": 100.0} (optional, defaults to full balance)
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    
    amount = data.get('amount')
    
    if amount is None:
        amount = user.rewards_balance
    else:
        amount = float(amount)
        if amount > user.rewards_balance:
            return jsonify({'success': False, 'message': 'Insufficient rewards balance'}), 400
    
    if amount <= 0:
        return jsonify({'success': False, 'message': 'No rewards to payout'}), 400
    
    # Transfer from rewards to wallet
    user.rewards_balance -= amount
    user.wallet_balance += amount
    
    # Create transaction
    transaction = Transaction(
        user_id=user.id,
        amount=amount,
        transaction_type='reward_payout',
        description=f'تحويل المكافآت إلى المحفظة - {amount:,.2f} جنيه'
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Rewards paid out successfully',
        'data': {
            'amount': float(amount),
            'new_rewards_balance': float(user.rewards_balance),
            'new_wallet_balance': float(user.wallet_balance)
        }
    }), 200


# Due to character limit, I'll create this in parts. Let me continue in the next file chunk...

# ============================================
# APARTMENT MANAGEMENT
# ============================================

@bp.route('/apartments', methods=['GET'])
@token_required
def list_apartments(current_user):
    """
    List all apartments with pagination
    GET /api/admin/apartments?page=1&per_page=20
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    apartments = Apartment.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'success': True,
        'data': {
            'apartments': [
                {
                    'id': a.id,
                    'title': a.title,
                    'location': a.location,
                    'total_price': float(a.total_price),
                    'total_shares': a.total_shares,
                    'shares_available': a.shares_available,
                    'monthly_rent': float(a.monthly_rent),
                    'is_closed': a.is_closed,
                    'image': a.image
                }
                for a in apartments.items
            ],
            'pagination': {
                'page': apartments.page,
                'per_page': apartments.per_page,
                'total': apartments.total,
                'pages': apartments.pages
            }
        }
    }), 200


@bp.route('/apartments/<int:apartment_id>', methods=['GET'])
@token_required
def get_apartment(current_user, apartment_id):
    """
    Get apartment details
    GET /api/admin/apartments/{id}
    """
    apartment = Apartment.query.get_or_404(apartment_id)
    
    shares = Share.query.filter_by(apartment_id=apartment_id).all()
    
    return jsonify({
        'success': True,
        'data': {
            'apartment': {
                'id': apartment.id,
                'title': apartment.title,
                'description': apartment.description,
                'location': apartment.location,
                'total_price': float(apartment.total_price),
                'total_shares': apartment.total_shares,
                'shares_available': apartment.shares_available,
                'monthly_rent': float(apartment.monthly_rent),
                'is_closed': apartment.is_closed,
                'image': apartment.image,
                'date_created': apartment.date_created.isoformat() if apartment.date_created else None
            },
            'shares': [
                {
                    'id': s.id,
                    'user_id': s.user_id,
                    'user_name': s.investor.name,
                    'share_price': float(s.share_price),
                    'date_purchased': s.date_purchased.isoformat() if s.date_purchased else None
                }
                for s in shares
            ]
        }
    }), 200


@bp.route('/apartments/<int:apartment_id>/close', methods=['POST'])
@token_required
def close_apartment(current_user, apartment_id):
    """
    Close apartment for investments
    POST /api/admin/apartments/{id}/close
    """
    apartment = Apartment.query.get_or_404(apartment_id)
    apartment.is_closed = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Apartment closed successfully'
    }), 200


@bp.route('/apartments/<int:apartment_id>/reopen', methods=['POST'])
@token_required
def reopen_apartment(current_user, apartment_id):
    """
    Reopen apartment for investments
    POST /api/admin/apartments/{id}/reopen
    """
    apartment = Apartment.query.get_or_404(apartment_id)
    apartment.is_closed = False
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Apartment reopened successfully'
    }), 200


@bp.route('/apartments/<int:apartment_id>', methods=['DELETE'])
@token_required
def delete_apartment(current_user, apartment_id):
    """
    Delete apartment
    DELETE /api/admin/apartments/{id}
    """
    apartment = Apartment.query.get_or_404(apartment_id)
    
    # Check if there are active shares
    if apartment.shares_sold > 0:
        return jsonify({'success': False, 'message': 'Cannot delete apartment with active shares'}), 400
    
    db.session.delete(apartment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Apartment deleted successfully'
    }), 200


# ============================================
# CAR MANAGEMENT
# ============================================

@bp.route('/cars', methods=['GET'])
@token_required
def list_cars(current_user):
    """
    List all cars with pagination
    GET /api/admin/cars?page=1&per_page=20
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    cars = Car.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'success': True,
        'data': {
            'cars': [
                {
                    'id': c.id,
                    'title': c.title,
                    'brand': c.brand,
                    'model': c.model,
                    'year': c.year,
                    'total_price': float(c.total_price),
                    'total_shares': c.total_shares,
                    'shares_available': c.shares_available,
                    'monthly_rent': float(c.monthly_rent),
                    'is_closed': c.is_closed,
                    'image': c.image
                }
                for c in cars.items
            ],
            'pagination': {
                'page': cars.page,
                'per_page': cars.per_page,
                'total': cars.total,
                'pages': cars.pages
            }
        }
    }), 200


@bp.route('/cars/<int:car_id>', methods=['GET'])
@token_required
def get_car(current_user, car_id):
    """
    Get car details
    GET /api/admin/cars/{id}
    """
    car = Car.query.get_or_404(car_id)
    
    shares = CarShare.query.filter_by(car_id=car_id).all()
    
    return jsonify({
        'success': True,
        'data': {
            'car': {
                'id': car.id,
                'title': car.title,
                'description': car.description,
                'brand': car.brand,
                'model': car.model,
                'year': car.year,
                'total_price': float(car.total_price),
                'total_shares': car.total_shares,
                'shares_available': car.shares_available,
                'monthly_rent': float(car.monthly_rent),
                'is_closed': car.is_closed,
                'image': car.image
            },
            'shares': [
                {
                    'id': s.id,
                    'user_id': s.user_id,
                    'user_name': s.investor.name,
                    'share_price': float(s.share_price),
                    'date_purchased': s.date_purchased.isoformat() if s.date_purchased else None
                }
                for s in shares
            ]
        }
    }), 200


@bp.route('/cars/<int:car_id>/close', methods=['POST'])
@token_required
def close_car(current_user, car_id):
    """
    Close car for investments
    POST /api/admin/cars/{id}/close
    """
    car = Car.query.get_or_404(car_id)
    car.is_closed = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Car closed successfully'
    }), 200


@bp.route('/cars/<int:car_id>/reopen', methods=['POST'])
@token_required
def reopen_car(current_user, car_id):
    """
    Reopen car for investments
    POST /api/admin/cars/{id}/reopen
    """
    car = Car.query.get_or_404(car_id)
    car.is_closed = False
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Car reopened successfully'
    }), 200


@bp.route('/cars/<int:car_id>', methods=['DELETE'])
@token_required
def delete_car(current_user, car_id):
    """
    Delete car
    DELETE /api/admin/cars/{id}
    """
    car = Car.query.get_or_404(car_id)
    
    # Check if there are active shares
    if car.shares_sold > 0:
        return jsonify({'success': False, 'message': 'Cannot delete car with active shares'}), 400
    
    db.session.delete(car)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Car deleted successfully'
    }), 200


# ============================================
# INVESTMENT REQUEST MANAGEMENT (APARTMENTS)
# ============================================

@bp.route('/investment-requests', methods=['GET'])
@token_required
def list_investment_requests(current_user):
    """
    List apartment investment requests
    GET /api/admin/investment-requests?status=pending&page=1&per_page=20
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')  # pending, approved, rejected
    
    query = InvestmentRequest.query
    
    if status:
        query = query.filter_by(status=status)
    
    requests = query.order_by(InvestmentRequest.date_submitted.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'requests': [
                {
                    'id': r.id,
                    'user_id': r.user_id,
                    'user_name': r.full_name,
                    'apartment_id': r.apartment_id,
                    'apartment_title': r.apartment.title if r.apartment else None,
                    'shares_requested': r.shares_requested,
                    'total_amount': float(r.shares_requested * (r.apartment.total_price / r.apartment.total_shares)) if r.apartment else 0,
                    'status': r.status,
                    'date_submitted': r.date_submitted.isoformat() if r.date_submitted else None,
                    'date_reviewed': r.date_reviewed.isoformat() if r.date_reviewed else None
                }
                for r in requests.items
            ],
            'pagination': {
                'page': requests.page,
                'per_page': requests.per_page,
                'total': requests.total,
                'pages': requests.pages
            }
        }
    }), 200


@bp.route('/investment-requests/<int:request_id>', methods=['GET'])
@token_required
def get_investment_request(current_user, request_id):
    """
    Get investment request details
    GET /api/admin/investment-requests/{id}
    """
    req = InvestmentRequest.query.get_or_404(request_id)
    
    return jsonify({
        'success': True,
        'data': {
            'request': {
                'id': req.id,
                'user_id': req.user_id,
                'apartment_id': req.apartment_id,
                'shares_requested': req.shares_requested,
                'full_name': req.full_name,
                'phone': req.phone,
                'national_id': req.national_id,
                'status': req.status,
                'admin_notes': req.admin_notes,
                'date_submitted': req.date_submitted.isoformat() if req.date_submitted else None,
                'date_reviewed': req.date_reviewed.isoformat() if req.date_reviewed else None,
                'apartment': {
                    'title': req.apartment.title,
                    'total_price': float(req.apartment.total_price),
                    'total_shares': req.apartment.total_shares
                } if req.apartment else None
            }
        }
    }), 200


@bp.route('/investment-requests/<int:request_id>/approve', methods=['POST'])
@token_required
def approve_investment_request(current_user, request_id):
    """
    Approve investment request
    POST /api/admin/investment-requests/{id}/approve
    """
    req = InvestmentRequest.query.get_or_404(request_id)
    
    if req.status != 'pending':
        return jsonify({'success': False, 'message': 'Request already processed'}), 400
    
    apartment = req.apartment
    share_price = apartment.total_price / apartment.total_shares
    total_investment = share_price * req.shares_requested
    
    # Create shares
    for _ in range(req.shares_requested):
        share = Share(
            user_id=req.user_id,
            apartment_id=apartment.id,
            share_price=share_price
        )
        db.session.add(share)
    
    # Update request
    req.status = 'approved'
    req.date_reviewed = datetime.datetime.utcnow()
    req.reviewed_by = current_user.id
    
    # Update apartment shares
    apartment.shares_available -= req.shares_requested
    
    # Create transaction
    transaction = Transaction(
        user_id=req.user_id,
        amount=total_investment,
        transaction_type='investment',
        description=f'استثمار في {apartment.title} - {req.shares_requested} سهم'
    )
    db.session.add(transaction)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Investment request approved successfully'
    }), 200


@bp.route('/investment-requests/<int:request_id>/reject', methods=['POST'])
@token_required
def reject_investment_request(current_user, request_id):
    """
    Reject investment request
    POST /api/admin/investment-requests/{id}/reject
    Body: {"reason": "Rejection reason"}
    """
    req = InvestmentRequest.query.get_or_404(request_id)
    data = request.get_json() or {}
    
    if req.status != 'pending':
        return jsonify({'success': False, 'message': 'Request already processed'}), 400
    
    req.status = 'rejected'
    req.admin_notes = data.get('reason', 'تم الرفض')
    req.date_reviewed = datetime.datetime.utcnow()
    req.reviewed_by = current_user.id
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Investment request rejected'
    }), 200


# ============================================
# CAR INVESTMENT REQUEST MANAGEMENT
# ============================================

@bp.route('/car-investment-requests', methods=['GET'])
@token_required
def list_car_investment_requests(current_user):
    """
    List car investment requests
    GET /api/admin/car-investment-requests?status=pending&page=1&per_page=20
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = CarInvestmentRequest.query
    
    if status:
        query = query.filter_by(status=status)
    
    requests = query.order_by(CarInvestmentRequest.date_submitted.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'requests': [
                {
                    'id': r.id,
                    'user_id': r.user_id,
                    'user_name': r.full_name,
                    'car_id': r.car_id,
                    'car_title': r.car.title if r.car else None,
                    'shares_requested': r.shares_requested,
                    'total_amount': float(r.shares_requested * (r.car.total_price / r.car.total_shares)) if r.car else 0,
                    'status': r.status,
                    'date_submitted': r.date_submitted.isoformat() if r.date_submitted else None
                }
                for r in requests.items
            ],
            'pagination': {
                'page': requests.page,
                'per_page': requests.per_page,
                'total': requests.total,
                'pages': requests.pages
            }
        }
    }), 200


@bp.route('/car-investment-requests/<int:request_id>/approve', methods=['POST'])
@token_required
def approve_car_investment_request(current_user, request_id):
    """
    Approve car investment request
    POST /api/admin/car-investment-requests/{id}/approve
    """
    req = CarInvestmentRequest.query.get_or_404(request_id)
    
    if req.status != 'pending':
        return jsonify({'success': False, 'message': 'Request already processed'}), 400
    
    car = req.car
    share_price = car.total_price / car.total_shares
    total_investment = share_price * req.shares_requested
    
    # Create car shares
    for _ in range(req.shares_requested):
        share = CarShare(
            user_id=req.user_id,
            car_id=car.id,
            share_price=share_price
        )
        db.session.add(share)
    
    # Update request
    req.status = 'approved'
    req.date_reviewed = datetime.datetime.utcnow()
    req.reviewed_by = current_user.id
    
    # Update car shares
    car.shares_available -= req.shares_requested
    
    # Create transaction
    transaction = Transaction(
        user_id=req.user_id,
        amount=total_investment,
        transaction_type='investment',
        description=f'استثمار في {car.title} - {req.shares_requested} سهم'
    )
    db.session.add(transaction)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Car investment request approved successfully'
    }), 200


@bp.route('/car-investment-requests/<int:request_id>/reject', methods=['POST'])
@token_required
def reject_car_investment_request(current_user, request_id):
    """
    Reject car investment request
    POST /api/admin/car-investment-requests/{id}/reject
    Body: {"reason": "Rejection reason"}
    """
    req = CarInvestmentRequest.query.get_or_404(request_id)
    data = request.get_json() or {}
    
    if req.status != 'pending':
        return jsonify({'success': False, 'message': 'Request already processed'}), 400
    
    req.status = 'rejected'
    req.admin_notes = data.get('reason', 'تم الرفض')
    req.date_reviewed = datetime.datetime.utcnow()
    req.reviewed_by = current_user.id
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Car investment request rejected'
    }), 200


# ============================================
# PAYOUT MANAGEMENT
# ============================================

@bp.route('/payouts', methods=['GET'])
@token_required
def get_payouts(current_user):
    """
    Get payout summary for all assets
    GET /api/admin/payouts
    """
    apartments = Apartment.query.filter_by(is_closed=False).all()
    cars = Car.query.filter_by(is_closed=False).all()
    
    apartment_data = []
    for apt in apartments:
        shares_sold = Share.query.filter_by(apartment_id=apt.id).count()
        if shares_sold > 0:
            monthly_per_share = apt.monthly_rent / apt.total_shares
            apartment_data.append({
                'id': apt.id,
                'title': apt.title,
                'shares_sold': shares_sold,
                'monthly_per_share': float(monthly_per_share),
                'total_monthly_payout': float(monthly_per_share * shares_sold)
            })
    
    car_data = []
    for car in cars:
        shares_sold = CarShare.query.filter_by(car_id=car.id).count()
        if shares_sold > 0:
            monthly_per_share = car.monthly_rent / car.total_shares
            car_data.append({
                'id': car.id,
                'title': car.title,
                'shares_sold': shares_sold,
                'monthly_per_share': float(monthly_per_share),
                'total_monthly_payout': float(monthly_per_share * shares_sold)
            })
    
    return jsonify({
        'success': True,
        'data': {
            'apartments': apartment_data,
            'cars': car_data
        }
    }), 200


@bp.route('/payouts/distribute-all', methods=['POST'])
@token_required
def distribute_all_payouts(current_user):
    """
    Distribute payouts for all assets (manual override)
    POST /api/admin/payouts/distribute-all
    """
    total_distributed = 0
    distributions = []
    
    # Distribute for all apartments
    apartments = Apartment.query.filter_by(is_closed=False).all()
    for apartment in apartments:
        shares = Share.query.filter_by(apartment_id=apartment.id).all()
        if shares:
            monthly_per_share = apartment.monthly_rent / apartment.total_shares
            for share in shares:
                share.investor.wallet_balance += monthly_per_share
                transaction = Transaction(
                    user_id=share.user_id,
                    amount=monthly_per_share,
                    transaction_type='rental_income',
                    description=f'دخل إيجار - {apartment.title}'
                )
                db.session.add(transaction)
                total_distributed += monthly_per_share
                distributions.append({
                    'user_id': share.user_id,
                    'amount': float(monthly_per_share),
                    'asset': apartment.title
                })
    
    # Distribute for all cars
    cars = Car.query.filter_by(is_closed=False).all()
    for car in cars:
        shares = CarShare.query.filter_by(car_id=car.id).all()
        if shares:
            monthly_per_share = car.monthly_rent / car.total_shares
            for share in shares:
                share.investor.wallet_balance += monthly_per_share
                transaction = Transaction(
                    user_id=share.user_id,
                    amount=monthly_per_share,
                    transaction_type='rental_income',
                    description=f'دخل إيجار - {car.title}'
                )
                db.session.add(transaction)
                total_distributed += monthly_per_share
                distributions.append({
                    'user_id': share.user_id,
                    'amount': float(monthly_per_share),
                    'asset': car.title
                })
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Distributed {total_distributed:,.2f} EGP to {len(distributions)} investors',
        'data': {
            'total_distributed': float(total_distributed),
            'total_distributions': len(distributions)
        }
    }), 200


# ============================================
# WITHDRAWAL REQUEST MANAGEMENT
# ============================================

@bp.route('/withdrawal-requests', methods=['GET'])
@token_required
def list_withdrawal_requests(current_user):
    """
    List withdrawal requests
    GET /api/admin/withdrawal-requests?status=pending&page=1&per_page=20
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = WithdrawalRequest.query
    
    if status:
        query = query.filter_by(status=status)
    
    requests = query.order_by(WithdrawalRequest.request_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'requests': [
                {
                    'id': r.id,
                    'user_id': r.user_id,
                    'user_name': r.user.name if r.user else None,
                    'amount': float(r.amount),
                    'payment_method': r.payment_method,
                    'status': r.status,
                    'request_date': r.request_date.isoformat() if r.request_date else None,
                    'processed_date': r.processed_date.isoformat() if r.processed_date else None
                }
                for r in requests.items
            ],
            'pagination': {
                'page': requests.page,
                'per_page': requests.per_page,
                'total': requests.total,
                'pages': requests.pages
            }
        }
    }), 200


@bp.route('/withdrawal-requests/<int:request_id>', methods=['GET'])
@token_required
def get_withdrawal_request(current_user, request_id):
    """
    Get withdrawal request details
    GET /api/admin/withdrawal-requests/{id}
    """
    req = WithdrawalRequest.query.get_or_404(request_id)
    
    return jsonify({
        'success': True,
        'data': {
            'request': {
                'id': req.id,
                'user_id': req.user_id,
                'user_name': req.user.name,
                'user_email': req.user.email,
                'user_wallet_balance': float(req.user.wallet_balance),
                'amount': float(req.amount),
                'payment_method': req.payment_method,
                'account_details': req.account_details,
                'status': req.status,
                'admin_notes': req.admin_notes,
                'request_date': req.request_date.isoformat() if req.request_date else None,
                'processed_date': req.processed_date.isoformat() if req.processed_date else None
            }
        }
    }), 200


@bp.route('/withdrawal-requests/<int:request_id>/approve', methods=['POST'])
@token_required
def approve_withdrawal_request(current_user, request_id):
    """
    Approve withdrawal request
    POST /api/admin/withdrawal-requests/{id}/approve
    Body: {"notes": "Optional notes"}
    """
    req = WithdrawalRequest.query.get_or_404(request_id)
    data = request.get_json() or {}
    
    if req.status != 'pending':
        return jsonify({'success': False, 'message': 'Request already processed'}), 400
    
    user = req.user
    
    if user.wallet_balance < req.amount:
        return jsonify({'success': False, 'message': 'Insufficient wallet balance'}), 400
    
    # Deduct from wallet
    user.wallet_balance -= req.amount
    
    # Create transaction
    transaction = Transaction(
        user_id=user.id,
        amount=-req.amount,
        transaction_type='withdrawal',
        description=f'سحب من المحفظة - {req.payment_method}'
    )
    db.session.add(transaction)
    
    # Update request
    req.status = 'approved'
    req.processed_date = datetime.datetime.utcnow()
    req.processed_by = current_user.id
    req.admin_notes = data.get('notes', '')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Withdrawal request approved successfully'
    }), 200


@bp.route('/withdrawal-requests/<int:request_id>/reject', methods=['POST'])
@token_required
def reject_withdrawal_request(current_user, request_id):
    """
    Reject withdrawal request
    POST /api/admin/withdrawal-requests/{id}/reject
    Body: {"reason": "Rejection reason"}
    """
    req = WithdrawalRequest.query.get_or_404(request_id)
    data = request.get_json() or {}
    
    if req.status != 'pending':
        return jsonify({'success': False, 'message': 'Request already processed'}), 400
    
    req.status = 'rejected'
    req.processed_date = datetime.datetime.utcnow()
    req.processed_by = current_user.id
    req.admin_notes = data.get('reason', 'تم الرفض')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Withdrawal request rejected'
    }), 200


# ============================================
# TRANSACTIONS
# ============================================

@bp.route('/transactions', methods=['GET'])
@token_required
def list_transactions(current_user):
    """
    List all transactions
    GET /api/admin/transactions?page=1&per_page=50
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    transactions = Transaction.query.order_by(Transaction.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'transactions': [
                {
                    'id': t.id,
                    'user_id': t.user_id,
                    'user_name': t.user.name if t.user else None,
                    'amount': float(t.amount),
                    'type': t.transaction_type,
                    'description': t.description,
                    'date': t.date.isoformat() if t.date else None
                }
                for t in transactions.items
            ],
            'pagination': {
                'page': transactions.page,
                'per_page': transactions.per_page,
                'total': transactions.total,
                'pages': transactions.pages
            }
        }
    }), 200
