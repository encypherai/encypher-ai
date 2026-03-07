import os
import psycopg2
import bcrypt
import hashlib
import base64

db_url = os.environ.get('DATABASE_URL', 'postgresql://encypher:encypher@127.0.0.1:5432/encypher_auth')

password = "Password123!"
sha256_hash = hashlib.sha256(password.encode("utf-8")).digest()
prehashed = base64.b64encode(sha256_hash)
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(prehashed, salt).decode("utf-8")

conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("UPDATE users SET password_hash = %s WHERE email='test@encypherai.com'", (hashed,))
conn.commit()
cur.close()
conn.close()

print("Password reset to 'Password123!' with pre-hashing")
