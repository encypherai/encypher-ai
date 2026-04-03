import urllib.request
import json
import uuid

# Let's just create a completely fresh user to be absolutely sure the hash matches the exact passlib version running in the backend
email = f"test_{uuid.uuid4().hex[:6]}@encypher.com"
password = "Password123!"

req = urllib.request.Request(
    "http://localhost:8001/api/v1/auth/signup",
    data=json.dumps({"email": email, "password": password, "name": "Fresh Test User"}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

try:
    with urllib.request.urlopen(req) as res:
        print("Signup:", res.status)
except urllib.error.HTTPError as e:
    print("Signup Error:", e.code, e.read().decode("utf-8"))
    exit(1)

# Verify email directly in DB
with open("verify_email.sh", "w") as f:
    f.write(
        f"docker exec -i encypher-postgres psql -U encypher -d encypher_auth -c \"UPDATE users SET email_verified = true WHERE email = '{email}';\"\n"
    )

# Enable TOTP directly in DB
with open("enable_totp.sh", "w") as f:
    f.write(
        f"docker exec -i encypher-postgres psql -U encypher -d encypher_auth -c \"UPDATE users SET totp_enabled = true WHERE email = '{email}';\"\n"
    )

print(f"Created {email}")
