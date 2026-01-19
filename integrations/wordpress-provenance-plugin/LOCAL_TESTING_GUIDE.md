# WordPress C2PA Plugin - Local Testing Guide

**Date:** October 31, 2025  
**Purpose:** End-to-end local testing setup for WordPress plugin with Enterprise API

---

## Overview

This guide walks through setting up a complete local testing environment:
1. **Enterprise API** - Running locally with all microservices
2. **WordPress Site** - Local WordPress with sample publisher content
3. **Plugin Installation** - Installing and configuring the C2PA plugin
4. **End-to-End Testing** - Verifying the complete workflow

---

## Prerequisites

### Required Software

- **Python 3.11+** with UV package manager
- **Docker Desktop** (for WordPress)
- **Git**
- **Web Browser** (Chrome/Firefox recommended)

### Repository Access

Ensure you have the `encypherai-commercial` repository cloned:
```bash
cd c:\Users\eriks\encypherai-commercial
```

---

## Part 1: Start Enterprise API Locally

### Step 1: Navigate to Enterprise API Directory

```powershell
cd c:\Users\eriks\encypherai-commercial\enterprise_api
```

### Step 2: Set Up Environment Variables

Create a `.env.local` file:

```powershell
# Copy example env file
copy .env.example .env.local
```

Edit `.env.local` with local settings:

```env
# API Configuration
API_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database (if using local PostgreSQL)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/encypher_dev

# Redis (if using local Redis)
REDIS_URL=redis://localhost:6379/0

# API Keys (for testing)
DEMO_API_KEY=demo-local-key

# CORS (allow WordPress localhost)
CORS_ORIGINS=http://localhost:8085,http://localhost:3000

# Signature Settings (for testing)
USE_TEST_SIGNATURES=true
SKIP_HSM=true
```

### Step 3: Install Dependencies

```powershell
# Install all dependencies
uv sync

# Or if starting fresh
uv add fastapi uvicorn pydantic sqlalchemy redis cryptography
```

### Step 4: Start the Enterprise API

```powershell
# Run with UV (from enterprise_api directory)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or from parent directory
cd c:\Users\eriks\encypherai-commercial
uv run --directory enterprise_api uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 5: Verify API is Running

Open browser to: `http://localhost:8000/docs`

You should see the FastAPI Swagger documentation.

**Test the health endpoint:**
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-31T20:00:00Z"
}
```

### Step 6: Test Embedding Endpoint

```powershell
# Test embedding endpoint
curl -X POST http://localhost:8000/api/v1/sign/advanced `
  -H "Authorization: Bearer demo-local-key" `
  -H "Content-Type: application/json" `
  -d '{
    "text": "This is a test blog post about AI and content authentication.",
    "document_id": "test_post_1",
    "segmentation_level": "sentence",
    "action": "c2pa.created"
  }'
```

Expected: JSON response with `embedded_content`, `merkle_tree`, and `statistics`.

---

## Part 2: Set Up Local WordPress Site

### Option A: Docker Compose (Recommended)

#### Step 1: Create Docker Compose File

Navigate to the WordPress plugin directory:

```powershell
cd c:\Users\eriks\encypherai-commercial\integrations\wordpress-assurance-plugin
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  wordpress:
    image: wordpress:latest
    ports:
      - "8085:80"
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - ./plugin/encypher-provenance:/var/www/html/wp-content/plugins/encypher-provenance
      - wordpress_data:/var/www/html
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - db_data:/var/lib/mysql

  phpmyadmin:
    image: phpmyadmin:latest
    ports:
      - "8081:80"
    environment:
      PMA_HOST: db
      MYSQL_ROOT_PASSWORD: rootpassword
    depends_on:
      - db

volumes:
  wordpress_data:
  db_data:
```

#### Step 2: Start WordPress

```powershell
# Start containers
docker-compose up -d

# Check status
docker-compose ps
```

#### Step 3: Access WordPress

Open browser to: `http://localhost:8085`

**Initial Setup:**
1. Choose language: English
2. Site Title: "Test Publisher Blog"
3. Username: `admin`
4. Password: `admin123` (or generate strong password)
5. Email: `test@example.com`
6. Click "Install WordPress"

### Option B: Local by Flywheel (Alternative)

1. Download Local by Flywheel: https://localwp.com/
2. Create new site:
   - Site name: "test-publisher"
   - Environment: Preferred (PHP 8.1+)
   - WordPress username: `admin`
   - WordPress password: `admin123`
3. Start site
4. Access via: `http://test-publisher.local`

---

## Part 3: Install and Configure Plugin

### Step 1: Activate Plugin

**Via Docker:**
The plugin is already mounted in the container. Just activate it.

1. Go to: `http://localhost:8085/wp-admin`
2. Login with admin credentials
3. Navigate to: **Plugins → Installed Plugins**
4. Find "Encypher C2PA Content Authentication"
5. Click **Activate**

**Via Local by Flywheel:**
1. Copy plugin folder:
   ```powershell
   copy -Recurse plugin\encypher-provenance "C:\Users\eriks\Local Sites\test-publisher\app\public\wp-content\plugins\"
   ```
2. Activate in WordPress admin

### Step 2: Configure Plugin Settings

1. Go to: **Settings → Encypher C2PA**
2. Configure:
   - **API Base URL:** `http://host.docker.internal:8000/api/v1` or `http://enterprise-api:8000/api/v1`
     - (Use `http://localhost:8000/api/v1` if not using Docker)
   - **API Key:** `demo-local-key`
   - **Auto-mark on publish:** ✓ Enabled
   - **Auto-mark on update:** ✓ Enabled
   - **Metadata format:** C2PA
   - **Hard binding:** ✓ Enabled
   - **Show C2PA badge:** ✓ Enabled
   - **Badge position:** Bottom-right corner
3. Click **Save Changes**

### Step 3: Verify API Connection

The settings page should show a success message if the API is reachable.

If you see an error:
- Check that Enterprise API is running (`http://localhost:8000/health`)
- Verify API key matches
- Check CORS settings in Enterprise API `.env.local`

---

## Part 4: Create Sample Publisher Content

### Step 1: Install Sample Content Plugin (Optional)

For quick testing, install WordPress Importer:

1. Go to: **Plugins → Add New**
2. Search: "WordPress Importer"
3. Install and activate

### Step 2: Create Sample Posts Manually

Create realistic publisher content:

#### Post 1: News Article

**Title:** "Breaking: New AI Regulations Announced"

**Content:**
```
The government announced sweeping new regulations for artificial intelligence today. 
The new framework aims to balance innovation with safety and ethical considerations.

Key points of the regulation include:
- Mandatory transparency requirements for AI systems
- Strict data privacy protections
- Regular audits for high-risk AI applications
- Consumer rights to understand AI decisions

Industry experts have mixed reactions. Tech companies warn of potential innovation slowdown, 
while consumer advocates praise the protective measures.

The regulations will take effect in six months, giving companies time to comply.
```

**Categories:** News, Technology  
**Tags:** AI, Regulation, Policy

#### Post 2: Opinion Piece

**Title:** "Why Content Authentication Matters in 2025"

**Content:**
```
In an era of deepfakes and misinformation, content authentication has never been more critical.

The rise of generative AI has made it trivially easy to create convincing fake content. 
From fabricated news articles to synthetic images, the line between real and fake is blurring.

This is where technologies like C2PA come in. By embedding cryptographic proofs directly 
into content, publishers can provide verifiable proof of origin and authenticity.

For readers, this means:
- Confidence in content sources
- Ability to verify claims
- Protection against manipulation

For publishers, it means:
- Protecting brand reputation
- Building reader trust
- Combating misinformation

The future of journalism depends on our ability to prove authenticity. 
Content authentication isn't just a nice-to-have—it's essential.
```

**Categories:** Opinion, Technology  
**Tags:** C2PA, Authentication, Trust

#### Post 3: How-To Guide

**Title:** "How to Verify Content Authenticity Online"

**Content:**
```
With misinformation rampant online, knowing how to verify content is crucial. 
Here's your step-by-step guide.

Step 1: Look for Authentication Badges
Many reputable publishers now use C2PA badges. Look for the Encypher icon or similar 
authentication markers on articles.

Step 2: Click to Verify
Click the authentication badge to view the content's digital signature and metadata. 
This shows who created it and when.

Step 3: Check the Source
Verify the publisher's identity in the authentication details. Look for:
- Organization name
- Signing authority
- Timestamp

Step 4: Cross-Reference
Compare information across multiple trusted sources. Authenticated content from 
multiple publishers strengthens credibility.

Step 5: Report Suspicious Content
If something seems off, report it. Most platforms have mechanisms for flagging 
potentially false information.

Remember: Authentication is your first line of defense against misinformation.
```

**Categories:** How-To, Education  
**Tags:** Verification, Tutorial, Guide

#### Post 4: Interview

**Title:** "Interview: The Future of Digital Trust"

**Content:**
```
We sat down with Dr. Sarah Chen, a leading expert in digital authentication, 
to discuss the future of online trust.

Q: Why is content authentication becoming so important?

A: We're at an inflection point. The same AI technologies that enable creativity 
also enable deception. Without authentication, we risk losing the ability to 
distinguish truth from fiction online.

Q: How does C2PA technology work?

A: C2PA embeds cryptographic signatures directly into content. Think of it as 
a digital seal that proves who created something and whether it's been altered. 
It's tamper-evident and verifiable by anyone.

Q: What challenges remain?

A: Adoption is the biggest challenge. We need publishers, platforms, and consumers 
all on board. The technology exists—now we need the ecosystem.

Q: What's your prediction for 2026?

A: I believe authenticated content will become the norm for professional publishers. 
Readers will expect it, and platforms will prioritize it. It's not a question of if, 
but when.
```

**Categories:** Interview, Technology  
**Tags:** Expert, Future, Trust

### Step 3: Publish Posts

1. Create each post in WordPress
2. Click **Publish**
3. Watch the plugin automatically mark content with C2PA
4. Check post meta to verify marking

---

## Part 5: End-to-End Testing

### Test 1: Auto-Mark on Publish

**Objective:** Verify automatic C2PA marking when publishing new posts.

**Steps:**
1. Create a new post
2. Add title and content
3. Click **Publish**
4. Wait for success message

**Verify:**
- Post content should have invisible C2PA embeddings
- Post meta `_encypher_marked` should be `true`
- Post meta `_encypher_action_type` should be `c2pa.created`

**Check in Database:**
```sql
SELECT post_id, meta_key, meta_value 
FROM wp_postmeta 
WHERE post_id = [POST_ID] 
AND meta_key LIKE '_encypher%';
```

### Test 2: Auto-Mark on Update

**Objective:** Verify re-marking when updating existing posts.

**Steps:**
1. Edit a published post
2. Change some content
3. Click **Update**
4. Wait for success message

**Verify:**
- Content should be re-marked
- Post meta `_encypher_action_type` should be `c2pa.edited`
- Post meta `_encypher_marked_date` should be updated

### Test 3: Manual Marking

**Objective:** Test manual marking via editor panel.

**Steps:**
1. Create a post but DON'T publish yet
2. In the Gutenberg sidebar, find "Encypher C2PA" panel
3. Click **Mark with C2PA**
4. Wait for confirmation
5. Then publish the post

**Verify:**
- Post should be marked before publishing
- Status indicator should show "C2PA Protected"

### Test 4: Bulk Marking

**Objective:** Test bulk archive marking tool.

**Steps:**
1. Create 5-10 posts without marking (disable auto-mark temporarily)
2. Go to: **Tools → Encypher C2PA**
3. Select post types: Posts
4. Status filter: Unmarked only
5. Batch size: 5
6. Click **Start Bulk Marking**

**Verify:**
- Progress bar updates in real-time
- All posts get marked successfully
- Success count matches total posts
- No errors in error log

### Test 5: Frontend Badge Display

**Objective:** Verify badge appears on published posts.

**Steps:**
1. Open a marked post on the frontend: `http://localhost:8085/[post-slug]`
2. Look for Encypher icon in bottom-right corner
3. Hover over icon (should scale up)
4. Click icon

**Verify:**
- Badge appears in bottom-right corner
- Badge is clickable
- Modal opens on click
- Modal shows verification details

### Test 6: Verification Modal

**Objective:** Test verification modal functionality.

**Steps:**
1. Click badge icon on a marked post
2. Wait for modal to load
3. Review displayed information
4. Click close button or press Escape

**Verify:**
- Modal opens smoothly
- Loading spinner appears
- Verification data displays in table format
- Shows document info, C2PA metadata, Merkle proof
- Modal closes properly

### Test 7: API Error Handling

**Objective:** Test plugin behavior when API is unavailable.

**Steps:**
1. Stop the Enterprise API: `Ctrl+C` in API terminal
2. Try to publish a new post in WordPress
3. Observe error handling

**Verify:**
- Plugin shows error message
- Post still publishes (doesn't block)
- Error is logged
- User is notified

**Restart API:**
```powershell
cd c:\Users\eriks\encypherai-commercial\enterprise_api
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Test 8: Settings Changes

**Objective:** Test settings persistence and application.

**Steps:**
1. Go to: **Settings → Encypher C2PA**
2. Disable "Auto-mark on publish"
3. Save changes
4. Create and publish a new post
5. Verify post is NOT marked
6. Re-enable auto-mark
7. Update the post
8. Verify post IS now marked

### Test 9: Per-Post Override

**Objective:** Test per-post marking override.

**Steps:**
1. Create a new post
2. Add custom field: `_encypher_skip_marking` = `1`
3. Publish post

**Verify:**
- Post should NOT be marked
- Even with auto-mark enabled
- No C2PA badge appears on frontend

### Test 10: Tier Restrictions

**Objective:** Test free tier limitations.

**Steps:**
1. Go to: **Settings → Encypher C2PA**
2. Verify tier is "Free"
3. Check badge position setting
4. Verify it's locked to "Bottom-right corner"
5. Try bulk marking more than 100 posts

**Verify:**
- Badge position cannot be changed
- Upgrade prompt is shown
- Bulk marking stops at 100 posts
- Warning message appears

---

## Part 6: Debugging and Logs

### WordPress Debug Mode

Enable WordPress debugging in `wp-config.php`:

```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
```

**View logs:**
```powershell
# Docker
docker-compose exec wordpress tail -f /var/www/html/wp-content/debug.log

# Local
tail -f "C:\Users\eriks\Local Sites\test-publisher\app\public\wp-content\debug.log"
```

### Enterprise API Logs

API logs appear in the terminal where you started the API.

**Increase verbosity:**
```env
LOG_LEVEL=DEBUG
```

### Browser Console

Open browser DevTools (F12) and check:
- **Console tab:** JavaScript errors
- **Network tab:** API requests/responses
- **Application tab:** Local storage, cookies

### Common Issues

**Issue: API connection failed**
- Check API is running: `http://localhost:8000/health`
- Verify API key matches
- Check CORS settings
- Use `host.docker.internal` instead of `localhost` in Docker

**Issue: Badge not appearing**
- Check "Show C2PA badge" is enabled
- Verify post is marked (check post meta)
- Clear browser cache
- Check browser console for JavaScript errors

**Issue: Modal not opening**
- Check browser console for errors
- Verify REST API is accessible
- Check WordPress nonce is valid
- Test REST endpoint directly

**Issue: Verification fails**
- Check post content has embeddings
- Verify Enterprise API `/public/extract-and-verify` endpoint
- Check post meta for `_encypher_manifest_id`
- Review API logs for errors

---

## Part 7: Sample Test Data

### SQL Queries for Testing

**Check marked posts:**
```sql
SELECT p.ID, p.post_title, pm.meta_value as marked
FROM wp_posts p
LEFT JOIN wp_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_encypher_marked'
WHERE p.post_type = 'post' AND p.post_status = 'publish';
```

**View all Encypher metadata:**
```sql
SELECT post_id, meta_key, meta_value
FROM wp_postmeta
WHERE meta_key LIKE '_encypher%'
ORDER BY post_id, meta_key;
```

**Count marked vs unmarked:**
```sql
SELECT 
  COUNT(*) as total_posts,
  SUM(CASE WHEN pm.meta_value = '1' THEN 1 ELSE 0 END) as marked_posts,
  SUM(CASE WHEN pm.meta_value IS NULL OR pm.meta_value != '1' THEN 1 ELSE 0 END) as unmarked_posts
FROM wp_posts p
LEFT JOIN wp_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_encypher_marked'
WHERE p.post_type = 'post' AND p.post_status = 'publish';
```

### REST API Testing

**Test sign endpoint:**
```powershell
curl -X POST http://localhost:8085/wp-json/encypher-provenance/v1/sign `
  -H "X-WP-Nonce: [GET_FROM_BROWSER]" `
  -H "Content-Type: application/json" `
  -d '{"post_id": 1}'
```

**Test verify endpoint:**
```powershell
curl -X POST http://localhost:8085/wp-json/encypher-provenance/v1/verify `
  -H "X-WP-Nonce: [GET_FROM_BROWSER]" `
  -H "Content-Type: application/json" `
  -d '{"post_id": 1}'
```

**Test status endpoint:**
```powershell
curl http://localhost:8085/wp-json/encypher-provenance/v1/status?post_id=1 `
  -H "X-WP-Nonce: [GET_FROM_BROWSER]"
```

---

## Part 8: Clean Up

### Stop Services

**WordPress (Docker):**
```powershell
cd c:\Users\eriks\encypherai-commercial\integrations\wordpress-assurance-plugin
docker-compose down
```

**Enterprise API:**
```powershell
# Press Ctrl+C in the API terminal
```

### Remove Test Data

**Remove Docker volumes:**
```powershell
docker-compose down -v
```

**Reset WordPress:**
```powershell
# Remove all data and start fresh
docker-compose down -v
docker-compose up -d
```

---

## Part 9: Automated Testing Script

Create a PowerShell script for quick setup:

**File:** `test-setup.ps1`

```powershell
# WordPress C2PA Plugin - Local Test Setup
Write-Host "Starting local test environment..." -ForegroundColor Green

# Start Enterprise API
Write-Host "`n1. Starting Enterprise API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\eriks\encypherai-commercial\enterprise_api; uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# Wait for API to start
Write-Host "Waiting for API to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test API health
$apiHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
if ($apiHealth.status -eq "healthy") {
    Write-Host "✓ Enterprise API is running" -ForegroundColor Green
} else {
    Write-Host "✗ Enterprise API failed to start" -ForegroundColor Red
    exit 1
}

# Start WordPress
Write-Host "`n2. Starting WordPress..." -ForegroundColor Yellow
cd c:\Users\eriks\encypherai-commercial\integrations\wordpress-assurance-plugin
docker-compose up -d

# Wait for WordPress to start
Write-Host "Waiting for WordPress to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check WordPress
$wpHealth = Invoke-WebRequest -Uri "http://localhost:8085" -UseBasicParsing
if ($wpHealth.StatusCode -eq 200) {
    Write-Host "✓ WordPress is running" -ForegroundColor Green
} else {
    Write-Host "✗ WordPress failed to start" -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ Test environment ready!" -ForegroundColor Green
Write-Host "`nAccess points:" -ForegroundColor Cyan
Write-Host "  - WordPress: http://localhost:8085" -ForegroundColor White
Write-Host "  - WordPress Admin: http://localhost:8085/wp-admin" -ForegroundColor White
Write-Host "  - Enterprise API: http://localhost:8000" -ForegroundColor White
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - phpMyAdmin: http://localhost:8081" -ForegroundColor White
Write-Host "`nPress Ctrl+C to stop services" -ForegroundColor Yellow
```

**Run:**
```powershell
.\test-setup.ps1
```

---

## Summary

You now have a complete local testing environment:

✅ **Enterprise API** running on `http://localhost:8000`  
✅ **WordPress Site** running on `http://localhost:8085`  
✅ **Plugin Installed** and configured  
✅ **Sample Content** ready for testing  
✅ **End-to-End Tests** documented  

**Next Steps:**
1. Run through all 10 test scenarios
2. Document any issues found
3. Test edge cases
4. Verify performance with large posts
5. Test with different WordPress themes

**Happy Testing!** 🚀
