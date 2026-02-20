import urllib.request
import json
import psycopg2
import os

db_url = os.environ.get('DATABASE_URL', 'postgresql://encypher:encypher@localhost:5432/encypher_auth')

conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("SELECT password_hash FROM users WHERE email='test@encypherai.com'")
row = cur.fetchone()
print("Hash in DB:", row[0] if row else "None")
cur.close()
conn.close()

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print("Does 'Password123!' match?", pwd_context.verify("Password123!", row[0]) if row else "N/A")
print("Does 'password' match?", pwd_context.verify("password", row[0]) if row else "N/A")
print("Does 'test' match?", pwd_context.verify("test", row[0]) if row else "N/A")

