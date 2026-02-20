import bcrypt
import base64
import hashlib

hash_in_db = b"$2b$12$eFAeMW68xuMJ8JTANok7deUOhNGXB9c28FnO8oT9xd9nz74tarnyW"
password = "Password123!"
prehashed = base64.b64encode(hashlib.sha256(password.encode("utf-8")).digest())
print("Is Password123!?", bcrypt.checkpw(prehashed, hash_in_db))
