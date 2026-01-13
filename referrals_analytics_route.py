"""
Admin referral analytics route
Shows all referral usage statistics
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, make_response
from app.models import db, ReferralUsage, User
from datetime import datetime
from sqlalchemy import func
import csv
import io

# Add this to existing admin.py after the last route

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
    
    return render_template('admin/referrals_analytics.html',
                         referrals=referrals_with_details,
                         referral_stats=referral_stats,
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
