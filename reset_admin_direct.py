"""
Direct SQL script to reset admin password
"""
import sqlite3
from werkzeug.security import generate_password_hash

databases = [
    '/Users/ibrahimfakhry/Desktop/last/ipi/instance/app.db',
    '/Users/ibrahimfakhry/Desktop/last/ipi/apartment_platform.db'
]

admin_email = 'admin@apartmentshare.com'
new_password = 'admin123'
password_hash = generate_password_hash(new_password)

print(f"=== Resetting Admin Password ===\n")
print(f"Email: {admin_email}")
print(f"New Password: {new_password}\n")

for db_path in databases:
    print(f"Processing: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if admin exists
    cursor.execute("SELECT id, name, email, is_admin FROM users WHERE email = ?", (admin_email,))
    admin = cursor.fetchone()
    
    if admin:
        admin_id, name, email, is_admin = admin
        print(f"  ✓ Found: {name} (ID: {admin_id}, Admin: {bool(is_admin)})")
        
        # Update password
        cursor.execute("UPDATE users SET password_hash = ?, is_admin = 1 WHERE id = ?", 
                      (password_hash, admin_id))
        
        # Ensure referral number exists
        cursor.execute("SELECT referral_number FROM users WHERE id = ?", (admin_id,))
        ref_num = cursor.fetchone()[0]
        
        if not ref_num:
            cursor.execute("UPDATE users SET referral_number = ? WHERE id = ?", 
                          (f"IPI{str(admin_id).zfill(6)}", admin_id))
            print(f"  ✓ Added referral number: IPI{str(admin_id).zfill(6)}")
        
        conn.commit()
        print(f"  ✅ Password reset successfully!\n")
    else:
        print(f"  ⚠️ Admin not found in this database\n")
    
    conn.close()

print("✅ Done! You can now login with:")
print(f"   Email: {admin_email}")
print(f"   Password: {new_password}")
