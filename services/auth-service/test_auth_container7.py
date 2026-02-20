import urllib.request
import json
import psycopg2
import os
import pyotp

# 1. Login to get MFA token
req = urllib.request.Request(
    "http://localhost:8001/api/v1/auth/login",
    data=json.dumps({
        "email": "test_5fc8a3@encypherai.com",
        "password": "Password123!"
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    with urllib.request.urlopen(req) as res:
        login_data = json.loads(res.read().decode('utf-8'))
        print("Login 1:", res.status)
except urllib.error.HTTPError as e:
    login_data = json.loads(e.read().decode('utf-8'))
    print("Login 1 Error:", e.code, login_data)

mfa_token = login_data.get('data', {}).get('mfa_token')
if not mfa_token:
    print("No MFA token found")
    exit(1)

# Wait, the user `test_5fc8a3@encypherai.com` has `totp_enabled` but hasn't actually configured a secret!
# A user who has `totp_enabled` but no secret will fail verification because there's no secret to verify against.
# Let's check if the secret is in the database.
db_url = os.environ.get('DATABASE_URL', 'postgresql://encypher:encypher@127.0.0.1:15432/encypher_auth')
conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("SELECT totp_secret FROM users WHERE email='test_5fc8a3@encypherai.com'")
row = cur.fetchone()
print("Secret in DB:", row[0] if row else "None")
cur.close()
conn.close()
