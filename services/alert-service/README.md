# Encypher Alert Service

Monitors all Encypher microservices for errors, aggregates incidents with fingerprinting and deduplication, detects spikes, and sends Discord notifications.

## Data Sources

- **Redis Stream** (`encypher:metrics:events`): Real-time error events from MetricsMiddleware across all services
- **Alertmanager webhook**: Prometheus infrastructure alerts (ServiceDown, HighErrorRate, etc.)
- **Direct push API**: Business-logic alerts from services (billing failures, key expiry, etc.)

## Key Endpoints

- `GET /api/v1/alerts/summary` - Current system health (AI-optimized)
- `GET /api/v1/alerts/incidents` - List incidents with filters
- `GET /api/v1/alerts/incidents/{id}` - Incident detail with events
- `GET /api/v1/alerts/patterns` - Error pattern analysis
- `POST /api/v1/alerts/alertmanager` - Alertmanager webhook receiver
- `POST /api/v1/alerts/events` - Direct event push

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string (for stream consumption)
- `DISCORD_WEBHOOK_URL` - Discord webhook for notifications
- `ALERT_EMAIL_RECIPIENT` - Email for critical escalations (optional)
- `NOTIFICATION_SERVICE_URL` - Internal URL for email delivery (optional)
