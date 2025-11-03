docker-compose exec -T enterprise-db psql -U encypher -d encypher_enterprise -c 'ALTER TABLE content_references ALTER COLUMN merkle_root_id DROP NOT NULL;'
