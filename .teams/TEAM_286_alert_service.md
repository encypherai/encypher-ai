# TEAM_286 - Alert Service

## Status: In Progress

## Goal
Build a Railway-hosted alert-service that monitors all Encypher microservices for errors, aggregates incidents, sends Discord notifications, and exposes a structured API for AI-assisted investigation.

## Scope
1. New `alert-service` FastAPI microservice on Railway
2. Redis Stream consumer (reads existing `encypher:metrics:events`)
3. Incident fingerprinting, deduplication, spike detection
4. Discord webhook notifications with rich embeds
5. Alertmanager webhook receiver for Prometheus alerts
6. API for querying incidents/patterns (AI-optimized /summary endpoint)
7. Traefik routing + Prometheus scrape config
