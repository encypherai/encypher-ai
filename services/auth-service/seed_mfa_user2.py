import urllib.request
import json
import sqlite3
import os

db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/encypher_auth')

# Connect to postgres and set email_verified=true
import psycopg2
import uuid
import pyotp

email = f"test_mfa_{uuid.uuid4().hex[:6]}@encypherai.com"
password = "Password123!"

# 1. Create a user
req = urllib.request.Request(
    "http://localhost:8001/api/v1/auth/signup",
    data=json.dumps({
        "email": email,
        "password": password,
        "name": "MFA Test User"
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as res:
        print("Signup:", res.status)
except urllib.error.HTTPError as e:
    print("Signup Error:", e.code, e.read().decode('utf-8'))
    exit(1)

# 2. Verify email directly in DB
conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("UPDATE users SET email_verified = true WHERE email = %s", (email,))
conn.commit()
cur.close()
conn.close()

# 3. Login to get token
req = urllib.request.Request(
    "http://localhost:8001/api/v1/auth/login",
    data=json.dumps({
        "email": email,
        "password": password
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as res:
        login_data = json.loads(res.read().decode('utf-8'))
        token = login_data['data']['access_token']
        print("Login:", res.status)
except urllib.error.HTTPError as e:
    print("Login Error:", e.code, e.read().decode('utf-8'))
    exit(1)

# 4. Setup MFA
req = urllib.request.Request(
    "http://localhost:8001/api/v1/auth/mfa/totp/setup",
    data=b'',
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Length': '0'
    }
)

try:
    with urllib.request.urlopen(req) as res:
        setup_data = json.loads(res.read().decode('utf-8'))
        secret = setup_data['data']['secret']
        print("MFA Setup:", res.status)
except urllib.error.HTTPError as e:
    print("MFA Setup Error:", e.code, e.read().decode('utf-8'))
    exit(1)

# 5. Confirm MFA
code = pyotp.TOTP(secret).now()
req = urllib.request.Request(
    "http://localhost:8001/api/v1/auth/mfa/totp/confirm",
    data=json.dumps({"code": code}).encode('utf-8'),
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
)

try:
    with urllib.request.urlopen(req) as res:
        print("MFA Confirm:", res.status)
except urllib.error.HTTPError as e:
    print("MFA Confirm Error:", e.code, e.read().decode('utf-8'))
    exit(1)

print("Email:", email)
print("Password:", password)

