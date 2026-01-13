from werkzeug.security import generate_password_hash
import sqlite3

conn = sqlite3.connect('instance/app.db')
c = conn.cursor()
h = generate_password_hash('admin123')
c.execute("UPDATE users SET password_hash = ? WHERE email = 'amsprog2022@gmail.com'", (h,))
conn.commit()
conn.close()
print('Password reset successfully!')
