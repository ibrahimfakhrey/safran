from werkzeug.security import generate_password_hash
import sqlite3

conn = sqlite3.connect('instance/app.db')
c = conn.cursor()
h = generate_password_hash('admin123')
c.execute("INSERT INTO users (name, email, password_hash, is_admin, wallet_balance, rewards_balance, is_fleet_manager, email_verified, auth_provider) VALUES ('Admin', 'admin@ipi.com', ?, 1, 0.0, 0.0, 0, 0, 'email')", (h,))
conn.commit()
conn.close()
print('Admin created!')
