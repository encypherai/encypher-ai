import urllib.request
import json

req = urllib.request.Request(
    "http://localhost:8001/api/v1/auth/login",
    data=json.dumps({"email": "test_5fc8a3@encypher.com", "password": "Password123!"}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req) as res:
        print("Status:", res.status)
        print("Body:", res.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("Error Status:", e.code)
    print("Error Body:", e.read().decode("utf-8"))
