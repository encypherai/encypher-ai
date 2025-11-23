# Web Service Agents Guide

## Context
This service handles the backend functionality for the public marketing website (encypherai.com).
It is designed to be a lightweight service separate from the core `enterprise_api`.

## Responsibilities
- **Sales/Contact Forms**: Handling submissions from "Contact Us" and "Request Demo" forms.
- **Web Analytics**: Tracking page views and user events.
- **Lead Notification**: Sending email notifications to sales/admin.

## Dependencies
- **Database**: PostgreSQL (separate schema `web_service` or shared instance with separate DB).
- **Auth**: Currently public endpoints for submission. Admin endpoints require internal auth (TODO: Integrate with `auth-service`).
- **Email**: SMTP server configuration.

## Development
- **Port**: Defaults to 8000 (configurable).
- **Framework**: FastAPI.
- **ORM**: SQLAlchemy + Alembic.

## Known Issues / Todo
- [ ] **Authentication**: Admin endpoints are currently stripped of auth dependencies. Need to integrate with `auth-service` or implement API key auth.
- [ ] **Email Templates**: HTML templates are currently hardcoded in `app/services/email.py`. Should be moved to external template files.
- [ ] **Analytics**: Basic implementation. Consider migrating to a dedicated analytics tool (PostHog/Plausible) if scale increases.
