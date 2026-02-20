import urllib.request
import json
import psycopg2
import os

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
        login_data = json.loads(res.read().decode('utf-8'))
        print("Login 1:", res.status)
except urllib.error.HTTPError as e:
    login_data = json.loads(e.read().decode('utf-8'))
    print("Login 1 Error:", e.code, login_data)

mfa_token = login_data.get('data', {}).get('mfa_token')
if not mfa_token:
    print("No MFA token found for test@encypherai.com")
    exit(1)

print("MFA Token:", mfa_token[:20] + "...")

# Now try complete
req = urllib.request.Request(
    "http://localhost:8001/api/v1/auth/login/mfa/complete",
    data=json.dumps({
        "mfa_token": mfa_token,
        "mfa_code": "000000" # Intentionally wrong to see error
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    with urllib.request.urlopen(req) as res:
        complete_data = json.loads(res.read().decode('utf-8'))
        print("Complete:", res.status)
except urllib.error.HTTPError as e:
    complete_data = json.loads(e.read().decode('utf-8'))
    print("Complete Error:", e.code, complete_data)

