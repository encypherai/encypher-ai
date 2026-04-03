HASH='$2b$12$lRDebAgGLOWRKM9oIqPtyOe4J5FukF.8SsxbeDuVUGAD3a95kUieG'
docker exec -i encypher-postgres psql -U encypher -d encypher_auth -c "UPDATE users SET password_hash='$HASH' WHERE email='test@encypher.com';"
