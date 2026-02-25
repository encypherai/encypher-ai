# TEAM_236 - Auth Service Circuit Breaker Fix

## Status: COMPLETE

## Problem
500 error on `GET /api/v1/auth/admin/newsletter-subscribers` (and potentially other endpoints using `call_service_with_breaker`).

Traefik routing was correct - requests were reaching auth-service at `auth-service.railway.internal:8080`.

Root cause: `pybreaker` library API mismatch.
- Code used: `CircuitBreaker(timeout_duration=...)`
- pybreaker 1.4.1 (installed version) uses: `CircuitBreaker(reset_timeout=...)`

Also removed invalid `listeners` argument (raw lambdas incompatible with pybreaker's `CircuitBreakerListener` interface).

## Fix
File: `services/auth-service/app/utils/resilience.py`

Changed `timeout_duration=timeout_duration` -> `reset_timeout=timeout_duration` in `get_circuit_breaker()`.
Removed lambda listeners (wrong interface for pybreaker).

## Commit Message Suggestion
```
fix(auth-service): fix CircuitBreaker constructor - rename timeout_duration to reset_timeout for pybreaker 1.4.1 compat

pybreaker>=1.4.1 uses reset_timeout instead of timeout_duration.
Also removed invalid lambda listeners (pybreaker requires CircuitBreakerListener subclass instances).
Fixes 500 on /api/v1/auth/admin/newsletter-subscribers and all other admin routes using call_service_with_breaker.
```
