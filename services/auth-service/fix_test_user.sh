HASH='$2b$12$eFAeMW68xuMJ8JTANok7deUOhNGXB9c28FnO8oT9xd9nz74tarnyW'
docker exec -i encypher-postgres psql -U encypher -d encypher_auth -c "UPDATE users SET password_hash='$HASH' WHERE email='test@encypherai.com';"
