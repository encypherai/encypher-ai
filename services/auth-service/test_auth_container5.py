import urllib.request
import json
import psycopg2
import os

db_url = os.environ.get('DATABASE_URL', 'postgresql://encypher:encypher_dev_password@127.0.0.1:15432/encypher_auth')

conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("SELECT email, password_hash, is_active, email_verified FROM users WHERE email='test@encypherai.com'")
row = cur.fetchone()
print("DB User:", row)
cur.close()
conn.close()

req = urllib.request.Request(
    "http://localhost:8001/api/v1/auth/login",
    data=json.dumps({
        "email": "test@encypherai.com",
        "password": "Password123!"
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    with urllib.request.urlopen(req) as res:
        print("Status:", res.status)
        print("Body:", res.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Error Status:", e.code)
    print("Error Body:", e.read().decode('utf-8'))
