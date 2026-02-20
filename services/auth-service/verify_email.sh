docker exec -i encypher-postgres psql -U encypher -d encypher_auth -c "UPDATE users SET email_verified = true WHERE email = 'test_5fc8a3@encypherai.com';"
