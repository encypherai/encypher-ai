import psycopg2

db_url = 'postgresql://encypher:encypher@127.0.0.1:5432/encypher_auth'

conn = psycopg2.connect(db_url)
cur = conn.cursor()
# Hardcode known working passlib hash for "Password123!"
# Let's generate it directly using passlib in python 3.10 inside the container if needed,
# or we can just use a hash generated elsewhere that passlib accepts.
# Wait, we can just use passlib inside a python container without the bcrypt 4.1 bug.
