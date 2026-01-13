"""
Migration script to create Share records for existing approved investments
and update apartments shares_available counts
"""
from app import create_app, db
from app.models import InvestmentRequest, Share, Apartment

app = create_app()

with app.app_context():
    # Get all approved investment requests
    approved_requests = InvestmentRequest.query.filter_by(status='approved').all()
    
    print(f"Found {len(approved_requests)} approved investment requests")
    
    for req in approved_requests:
        # Check if shares already exist for this request
        existing_shares = Share.query.filter_by(
            user_id=req.user_id,
            apartment_id=req.apartment_id
        ).count()
        
        if existing_shares >= req.shares_requested:
            print(f"Request #{req.id}: Shares already exist (user {req.user_id}, apartment {req.apartment_id})")
            continue
        
        # Calculate how many shares to create
        shares_to_create = req.shares_requested - existing_shares
        
        print(f"Request #{req.id}: Creating {shares_to_create} shares for user {req.user_id}, apartment {req.apartment_id}")
        
        # Create missing Share records
        apartment = req.apartment
        for _ in range(shares_to_create):
            share = Share(
                user_id=req.user_id,
                apartment_id=req.apartment_id,
                share_price=apartment.share_price
            )
            db.session.add(share)
        
        # Update shares_available
        apartment.shares_available -= shares_to_create
        
        # Close apartment if all shares sold
        if apartment.shares_available <= 0:
            apartment.is_closed = True
            print(f"  -> Apartment {apartment.id} is now closed (all shares sold)")
    
    # Commit all changes
    db.session.commit()
    print("\nMigration completed successfully!")
    
    # Show summary
    print("\n=== Summary ===")
    for apt in Apartment.query.all():
        shares_count = Share.query.filter_by(apartment_id=apt.id).count()
        investors_count = apt.investors_count
        print(f"Apartment #{apt.id} ({apt.title}):")
        print(f"  - Total shares: {apt.total_shares}")
        print(f"  - Available: {apt.shares_available}")
        print(f"  - Sold: {shares_count}")
        print(f"  - Investors: {investors_count}")
        print()
