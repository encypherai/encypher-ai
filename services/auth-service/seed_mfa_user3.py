import urllib.request
import json
import psycopg2
import uuid
import pyotp
import os

db_url = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/encypher_auth')

email = f"test_mfa_{uuid.uuid4().hex[:6]}@encypherai.com"
password = "Password123!"

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

# Connect to database directly
# Use the correct internal container url from compose if running inside it, 
# but we are running on host. Let's find the correct port.
