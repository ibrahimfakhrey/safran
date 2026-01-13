"""
Automatic Monthly Payout System
Distributes rental income to investors based on their investment approval dates
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.models import db, Share, CarShare, Transaction, InvestmentRequest, CarInvestmentRequest, Apartment, Car
import logging

logger = logging.getLogger(__name__)


def calculate_months_elapsed(start_date, end_date=None):
    """Calculate complete months elapsed between two dates"""
    if end_date is None:
        end_date = datetime.utcnow()
    
    # Calculate month difference
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    
    # If we haven't reached the same day yet in the current month, don't count it
    if end_date.day < start_date.day:
        months -= 1
    
    return max(0, months)


def get_approval_date_for_share(share, is_car=False):
    """Get the investment approval date for a share"""
    if is_car:
        # Find the car investment request for this user and car
        request = CarInvestmentRequest.query.filter_by(
            user_id=share.user_id,
            car_id=share.car_id,
            status='approved'
        ).first()
    else:
        # Find the apartment investment request for this user and apartment
        request = InvestmentRequest.query.filter_by(
            user_id=share.user_id,
            apartment_id=share.apartment_id,
            status='approved'
        ).first()
    
    return request.date_reviewed if request and request.date_reviewed else share.date_purchased


def distribute_share_income(share, apartment, months_to_pay):
    """
    Distribute rental income for a share
    Returns: (success, amount_distributed, error_message)
    """
    try:
        # Calculate monthly income per share
        total_shares = apartment.total_shares
        monthly_rent = apartment.monthly_rent
        income_per_share = monthly_rent / total_shares if total_shares > 0 else 0
        
        # Calculate total amount for all months
        total_amount = income_per_share * months_to_pay
        
        if total_amount <= 0:
            return False, 0, "No income to distribute"
        
        # Add to user wallet
        user = share.investor
        user.wallet_balance += total_amount
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            amount=total_amount,
            transaction_type='rental_income',
            description=f'دخل إيجار {months_to_pay} شهر - {apartment.title}'
        )
        db.session.add(transaction)
        
        # Update last payout date
        share.last_auto_payout_date = datetime.utcnow()
        
        logger.info(f"Auto-payout: Distributed {total_amount:.2f} EGP ({months_to_pay} months) to {user.name} for {apartment.title}")
        
        return True, total_amount, None
        
    except Exception as e:
        logger.error(f"Auto-payout: Failed for share {share.id}: {str(e)}")
        return False, 0, str(e)


def distribute_car_share_income(car_share, car, months_to_pay):
    """
    Distribute car rental income for a share
    Returns: (success, amount_distributed, error_message)
    """
    try:
        # Calculate monthly income per share
        total_shares = car.total_shares
        monthly_rent = car.monthly_rent
        income_per_share = monthly_rent / total_shares if total_shares > 0 else 0
        
        # Calculate total amount for all months
        total_amount = income_per_share * months_to_pay
        
        if total_amount <= 0:
            return False, 0, "No income to distribute"
        
        # Add to user wallet
        user = car_share.investor
        user.wallet_balance += total_amount
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            amount=total_amount,
            transaction_type='rental_income',
            description=f'دخل إيجار {months_to_pay} شهر - {car.title}'
        )
        db.session.add(transaction)
        
        # Update last payout date
        car_share.last_auto_payout_date = datetime.utcnow()
        
        logger.info(f"Auto-payout: Distributed {total_amount:.2f} EGP ({months_to_pay} months) to {user.name} for {car.title}")
        
        return True, total_amount, None
        
    except Exception as e:
        logger.error(f"Auto-payout: Failed for car share {car_share.id}: {str(e)}")
        return False, 0, str(e)


def process_automatic_payouts():
    """
    Main function to process all automatic monthly payouts
    Called by the scheduler daily
    """
    logger.info("=== Starting automatic monthly payout process ===")
    
    total_distributed = 0
    shares_processed = 0
    errors = []
    
    try:
        # Process apartment shares
        apartment_shares = Share.query.all()
        
        for share in apartment_shares:
            try:
                apartment = share.apartment
                
                # Get approval date
                approval_date = get_approval_date_for_share(share)
                
                # Calculate months since approval
                months_since_approval = calculate_months_elapsed(approval_date)
                
                if months_since_approval < 1:
                    continue  # No payout yet, less than 1 month
                
                # Calculate months already paid
                if share.last_auto_payout_date:
                    months_already_paid = calculate_months_elapsed(approval_date, share.last_auto_payout_date)
                else:
                    months_already_paid = 0
                
                # Calculate months to pay now
                months_to_pay = months_since_approval - months_already_paid
                
                if months_to_pay > 0:
                    success, amount, error = distribute_share_income(share, apartment, months_to_pay)
                    if success:
                        total_distributed += amount
                        shares_processed += 1
                    else:
                        errors.append(f"Share {share.id}: {error}")
                
            except Exception as e:
                errors.append(f"Share {share.id}: {str(e)}")
                logger.error(f"Error processing share {share.id}: {str(e)}")
        
        # Process car shares
        car_shares = CarShare.query.all()
        
        for car_share in car_shares:
            try:
                car = car_share.car
                
                # Get approval date
                approval_date = get_approval_date_for_share(car_share, is_car=True)
                
                # Calculate months since approval
                months_since_approval = calculate_months_elapsed(approval_date)
                
                if months_since_approval < 1:
                    continue
                
                # Calculate months already paid
                if car_share.last_auto_payout_date:
                    months_already_paid = calculate_months_elapsed(approval_date, car_share.last_auto_payout_date)
                else:
                    months_already_paid = 0
                
                # Calculate months to pay now
                months_to_pay = months_since_approval - months_already_paid
                
                if months_to_pay > 0:
                    success, amount, error = distribute_car_share_income(car_share, car, months_to_pay)
                    if success:
                        total_distributed += amount
                        shares_processed += 1
                    else:
                        errors.append(f"CarShare {car_share.id}: {error}")
                
            except Exception as e:
                errors.append(f"CarShare {car_share.id}: {str(e)}")
                logger.error(f"Error processing car share {car_share.id}: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"=== Automatic payout complete: {shares_processed} shares processed, {total_distributed:.2f} EGP distributed ===")
        
        if errors:
            logger.warning(f"Errors encountered: {len(errors)}")
            for error in errors[:5]:  # Log first 5 errors
                logger.warning(f"  - {error}")
        
        return {
            'success': True,
            'shares_processed': shares_processed,
            'total_distributed': total_distributed,
            'errors': errors
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Fatal error in automatic payout process: {str(e)}")
        return {
            'success': False,
            'shares_processed': 0,
            'total_distributed': 0,
            'errors': [str(e)]
        }
