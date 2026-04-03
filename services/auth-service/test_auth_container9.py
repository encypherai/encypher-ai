import urllib.request
import json
import psycopg2
import os

req = urllib.request.Request(
    "http://localhost:8001/api/v1/auth/login",
    data=json.dumps({"email": "test@encypher.com", "password": "Password123!"}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req) as res:
        login_data = json.loads(res.read().decode("utf-8"))
        print("Login 1:", res.status)
except urllib.error.HTTPError as e:
    login_data = json.loads(e.read().decode("utf-8"))
    print("Login 1 Error:", e.code, login_data)
