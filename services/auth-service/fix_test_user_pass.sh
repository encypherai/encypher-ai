HASH='$2b$12$OrxH0TsUKSSl3fGz7d0cse45n2J.XYzo8OWJl4w7t1c.YCL2yptZC'
docker exec -i encypher-postgres psql -U encypher -d encypher_auth -c "UPDATE users SET password_hash='$HASH' WHERE email='test@encypherai.com';"
