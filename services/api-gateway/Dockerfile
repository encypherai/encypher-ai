# Traefik API Gateway for Railway
FROM traefik:v3.0

# Copy static configuration
COPY traefik.yml /etc/traefik/traefik.yml

# Copy dynamic configuration
COPY dynamic.yml /etc/traefik/dynamic.yml

# Expose port (Railway uses 8080 by default)
EXPOSE 8080

# Traefik will read config from /etc/traefik/
