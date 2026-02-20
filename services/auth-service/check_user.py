import os
import psycopg2

db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/encypher_auth')

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT id, email, is_active, email_verified, totp_enabled FROM users WHERE email = 'test@encypherai.com'")
    user = cur.fetchone()
    if user:
        print(f"User found: id={user[0]}, email={user[1]}, is_active={user[2]}, email_verified={user[3]}, totp_enabled={user[4]}")
    else:
        print("User not found.")
    
    cur.execute("SELECT id, email, is_active, email_verified, totp_enabled FROM users ORDER BY created_at DESC LIMIT 5")
    print("\nRecent users:")
    for row in cur.fetchall():
        print(row)
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
