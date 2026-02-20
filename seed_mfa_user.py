import urllib.request
import json
import uuid

# 1. Create a user
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
        user_data = json.loads(res.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Signup Error:", e.code, e.read().decode('utf-8'))
    exit(1)

# 2. Login to get token
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

# 3. Setup MFA
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
        print("MFA Setup:", res.status)
        
        # Manually verify it with pyotp - wait, we just need to confirm it.
        # We can write a quick pyotp script or skip confirming if possible?
        # Actually, confirming requires the code. Let's install pyotp temporarily or use a python library.
        secret = setup_data['data']['secret']
except urllib.error.HTTPError as e:
    print("MFA Setup Error:", e.code, e.read().decode('utf-8'))
    exit(1)

print("Email:", email)
print("Password:", password)
print("Secret:", secret)

