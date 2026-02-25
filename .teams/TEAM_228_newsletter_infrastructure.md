# TEAM_228 - Newsletter Infrastructure

## Session Start: 2026-02-23

## Objective
Implement full newsletter pipeline: subscribe capture, broadcast on publish, unsubscribe flow.

## Tasks
- [x] TEAM ID claimed (TEAM_228)
- [ ] A. DB migration: newsletter_subscribers table
- [ ] B. SQLAlchemy model
- [ ] C. Pydantic schemas
- [ ] D. Web-service endpoints (subscribe, unsubscribe, broadcast)
- [ ] E. Email service functions (welcome, newsletter post)
- [ ] F. Config updates
- [ ] G. Unsubscribe page (Next.js)
- [ ] H. GitHub Actions workflow: newsletter-send.yml
- [ ] Fix Next.js API route URL (currently missing /api/v1 prefix)

## Status: COMPLETE

## Files Created
- services/web-service/alembic/versions/a1b2c3d4e5f6_newsletter_subscribers.py
- services/web-service/app/models/newsletter_subscriber.py
- services/web-service/app/schemas/newsletter.py
- services/web-service/app/api/v1/endpoints/newsletter.py
- apps/marketing-site/src/app/(marketing)/newsletter/unsubscribe/page.tsx
- .github/workflows/newsletter-send.yml
- scripts/newsletter/broadcast.js

## Files Modified
- services/web-service/app/api/api_v1/__init__.py (added newsletter router)
- services/web-service/app/core/config.py (added NEWSLETTER_BROADCAST_SECRET, SITE_URL)
- services/web-service/.env.example (added newsletter vars)
- services/web-service/app/services/email.py (added send_newsletter_welcome, send_newsletter_broadcast)
- apps/marketing-site/src/app/api/newsletter/subscribe/route.ts (fixed /api/v1/ prefix)

## Verification
- All Python imports pass
- Newsletter routes registered: /newsletter/subscribe, /newsletter/unsubscribe, /newsletter/broadcast
- ruff check: all passed
- next lint (new files only): no warnings or errors

## GH Secrets - SET 2026-02-24
- WEB_SERVICE_URL = https://web-service-staging-4e0d.up.railway.app (set via GH API)
- NEWSLETTER_BROADCAST_SECRET = (set via GH API + Railway variableUpsert on 2026-02-24)

## Additional Fixes (session 2026-02-24)
- fix(enterprise-api): run Alembic migrations against content DB on startup (5abcca88)
- fix(enterprise-api): fix request_id logging flood and content DB schema patch (11345989)
- fix(email): use PNG logo in emails - SVG is blocked by Gmail and Outlook (612f13bb)
- Railway web-service auto-redeploy triggered after NEWSLETTER_BROADCAST_SECRET was set

## Dashboard Enhancement (session 2026-02-24 continued)
- feat(dashboard): enhanced AI Crawler Analytics page for Valnet-style publisher review
  - AI Company Breakdown section: per-company cards (OpenAI, Anthropic, Google, Meta, etc.) with brand accent colors, crawl event counts, crawler counts, bypass alerts, and Enterprise-gated compliance labels
  - "Encypher goes where TollBit can't" callout: positions Encypher's content spread tracking as the differentiator (who scraped vs. where content appeared)
  - Scrape-to-Referral Ratio callout: explains TollBit's headline metric and teases it as an upcoming Encypher feature via analytics integration
  - Bot Purpose Breakdown: upgraded Bot Categories to show purpose labels (Training Data / RAG-Inference / Search Indexing) with color-coded badges and descriptions
  - Updated page header: "AI Crawler Analytics" with publisher-focused description
  - Capability callout rewritten: "Two layers of crawler intelligence -- Layer 1 crawl detection, Layer 2 content spread"
  - No API changes needed: derives company groupings client-side from existing CrawlerSummaryEntry.company field

## Suggested Commit Message
feat(newsletter): full subscriber pipeline - capture, broadcast, unsubscribe

- Add newsletter_subscribers table (Alembic migration a1b2c3d4e5f6)
- SQLAlchemy model with unsubscribe_token, active flag, ip/ua tracking
- Pydantic schemas for subscribe, unsubscribe, broadcast requests
- Three endpoints at /api/v1/newsletter/{subscribe,unsubscribe,broadcast}
  - subscribe: idempotent (silent 200 on duplicate), generates unsubscribe token
  - unsubscribe: token-based, always returns 200 (no enumeration)
  - broadcast: secret-protected, fans out to all active subscribers
- Email functions: send_newsletter_welcome, send_newsletter_broadcast (HTML + plain)
- Next.js unsubscribe page at /newsletter/unsubscribe?token=XXX (server component)
- GitHub Actions newsletter-send.yml triggers on new .md in blog/
  - Parses frontmatter (gray-matter), derives slug, builds URLs
  - POSTs to /api/v1/newsletter/broadcast with secret
- Fix Next.js subscribe route to use /api/v1/ prefix
- Add NEWSLETTER_BROADCAST_SECRET + SITE_URL to config and .env.example
