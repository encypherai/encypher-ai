# Verification Badge Specification

**Version:** 1.0  
**Last Updated:** October 28, 2025

## Overview

The Encypher Verification Badge is an embeddable widget that allows publishers to display verification status directly on their websites. The badge verifies content on page load, displays the Encypher logo, and provides detailed metadata when clicked.

## Features

### Core Functionality
- ✅ **On-Load Verification**: Automatically verifies content when the page loads
- ✅ **Visual Indicator**: Shows Encypher logo with verification status
- ✅ **Click-to-Expand**: Displays detailed metadata in pretty-print format
- ✅ **Responsive Design**: Works on desktop and mobile
- ✅ **Lightweight**: Minimal performance impact (<50KB total)
- ✅ **No Dependencies**: Pure JavaScript, no jQuery or React required

## Implementation

### 1. Embed Code

Publishers add this snippet to their HTML:

```html
<!-- Encypher Verification Badge -->
<script src="https://encypherai.com/embed/verify.js" async></script>
<div 
  class="encypher-verify-badge" 
  data-document-id="doc_abc123"
  data-theme="light"
  data-position="bottom-right">
</div>
```

### 2. Badge States

#### 2.1 Loading State
```
┌─────────────────────────┐
│ [spinner] Verifying...  │
└─────────────────────────┘
```

#### 2.2 Verified State
```
┌─────────────────────────┐
│ ✅ [logo] Verified      │
└─────────────────────────┘
```

#### 2.3 Tampered State
```
┌─────────────────────────┐
│ ⚠️ [logo] Tampered      │
└─────────────────────────┘
```

#### 2.4 Unknown State
```
┌─────────────────────────┐
│ ❓ [logo] Unknown       │
└─────────────────────────┘
```

### 3. Expanded View (Click to Open)

```
┌───────────────────────────────────────┐
│ ✅ Verified by Encypher              │
├───────────────────────────────────────┤
│                                       │
│ Publisher: The New York Times        │
│ Published: Oct 28, 2025 3:42 PM     │
│ Document ID: doc_abc123              │
│                                       │
│ 📊 347 sentences verified            │
│ 🔐 Signed with Ed25519               │
│ 📜 C2PA 2.2 compliant                │
│                                       │
│ Certificate:                          │
│ └─ Issued by: SSL.com                │
│ └─ Valid until: Oct 28, 2026         │
│                                       │
│ [View Full Report] [Download Proof]  │
│                                       │
└───────────────────────────────────────┘
```

## API Endpoints

### 1. Badge Verification Endpoint

**Endpoint:** `GET /api/v1/badge/verify/{document_id}`

**Purpose:** Lightweight endpoint optimized for badge verification

**Response:**
```json
{
  "status": "verified",
  "document_id": "doc_abc123",
  "publisher": {
    "name": "The New York Times",
    "logo_url": "https://cdn.encypherai.com/logos/nyt.png"
  },
  "metadata": {
    "title": "Breaking News Article",
    "published_at": "2025-10-28T15:42:00Z",
    "sentence_count": 347
  },
  "signature": {
    "algorithm": "Ed25519",
    "standard": "C2PA 2.2",
    "certificate_issuer": "SSL.com",
    "certificate_expiry": "2026-10-28T00:00:00Z"
  },
  "verification_url": "https://encypherai.com/verify/doc_abc123"
}
```

**Performance Target:** <50ms p99 latency

### 2. Direct Link Verification Endpoint

**Endpoint:** `GET /verify/{document_id}`

**Purpose:** Public verification page for sharing

**Response:** HTML page with full verification details

**Features:**
- SEO-optimized meta tags
- Social media preview cards (Open Graph, Twitter Cards)
- Mobile-responsive design
- Print-friendly layout

## Technical Implementation

### 1. JavaScript Badge Library

**File:** `verify.js` (served from CDN)

```javascript
(function() {
  'use strict';
  
  const ENCYPHER_API = 'https://encypherai.com/api/v1';
  const CACHE_TTL = 300000; // 5 minutes
  
  class EncypherBadge {
    constructor(element) {
      this.element = element;
      this.documentId = element.dataset.documentId;
      this.theme = element.dataset.theme || 'light';
      this.position = element.dataset.position || 'bottom-right';
      this.expanded = false;
      
      this.init();
    }
    
    async init() {
      this.render('loading');
      
      try {
        const data = await this.verify();
        this.data = data;
        this.render(data.status);
      } catch (error) {
        console.error('Encypher verification failed:', error);
        this.render('error');
      }
    }
    
    async verify() {
      // Check cache first
      const cached = this.getCache();
      if (cached) return cached;
      
      // Fetch from API
      const response = await fetch(
        `${ENCYPHER_API}/badge/verify/${this.documentId}`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json'
          }
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      this.setCache(data);
      
      return data;
    }
    
    render(status) {
      const badge = this.createBadge(status);
      this.element.innerHTML = '';
      this.element.appendChild(badge);
      
      // Add click handler
      badge.addEventListener('click', () => this.toggle());
    }
    
    createBadge(status) {
      const badge = document.createElement('div');
      badge.className = `encypher-badge encypher-badge--${status} encypher-badge--${this.theme}`;
      
      const icon = this.getIcon(status);
      const text = this.getText(status);
      
      badge.innerHTML = `
        <div class="encypher-badge__compact">
          <span class="encypher-badge__icon">${icon}</span>
          <img src="https://encypherai.com/assets/logo-icon.svg" 
               alt="Encypher" 
               class="encypher-badge__logo">
          <span class="encypher-badge__text">${text}</span>
        </div>
      `;
      
      return badge;
    }
    
    toggle() {
      if (!this.data) return;
      
      this.expanded = !this.expanded;
      
      if (this.expanded) {
        this.showDetails();
      } else {
        this.render(this.data.status);
      }
    }
    
    showDetails() {
      const details = this.createDetails();
      this.element.innerHTML = '';
      this.element.appendChild(details);
    }
    
    createDetails() {
      const details = document.createElement('div');
      details.className = `encypher-details encypher-details--${this.theme}`;
      
      details.innerHTML = `
        <div class="encypher-details__header">
          <span class="encypher-details__status">
            ${this.getIcon(this.data.status)} Verified by Encypher
          </span>
          <button class="encypher-details__close" aria-label="Close">×</button>
        </div>
        
        <div class="encypher-details__body">
          <div class="encypher-details__field">
            <strong>Publisher:</strong> ${this.data.publisher.name}
          </div>
          <div class="encypher-details__field">
            <strong>Published:</strong> ${this.formatDate(this.data.metadata.published_at)}
          </div>
          <div class="encypher-details__field">
            <strong>Document ID:</strong> <code>${this.data.document_id}</code>
          </div>
          
          <div class="encypher-details__stats">
            <div>📊 ${this.data.metadata.sentence_count} sentences verified</div>
            <div>🔐 Signed with ${this.data.signature.algorithm}</div>
            <div>📜 ${this.data.signature.standard} compliant</div>
          </div>
          
          <div class="encypher-details__certificate">
            <strong>Certificate:</strong>
            <div>└─ Issued by: ${this.data.signature.certificate_issuer}</div>
            <div>└─ Valid until: ${this.formatDate(this.data.signature.certificate_expiry)}</div>
          </div>
        </div>
        
        <div class="encypher-details__footer">
          <a href="${this.data.verification_url}" 
             target="_blank" 
             class="encypher-details__button">
            View Full Report
          </a>
          <a href="${this.data.verification_url}/proof" 
             target="_blank" 
             class="encypher-details__button encypher-details__button--secondary">
            Download Proof
          </a>
        </div>
      `;
      
      // Add close handler
      const closeBtn = details.querySelector('.encypher-details__close');
      closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggle();
      });
      
      return details;
    }
    
    getIcon(status) {
      const icons = {
        'verified': '✅',
        'tampered': '⚠️',
        'unknown': '❓',
        'loading': '⏳',
        'error': '❌'
      };
      return icons[status] || '❓';
    }
    
    getText(status) {
      const texts = {
        'verified': 'Verified',
        'tampered': 'Tampered',
        'unknown': 'Unknown',
        'loading': 'Verifying...',
        'error': 'Error'
      };
      return texts[status] || 'Unknown';
    }
    
    formatDate(isoString) {
      const date = new Date(isoString);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
    
    getCache() {
      const key = `encypher_verify_${this.documentId}`;
      const cached = localStorage.getItem(key);
      
      if (!cached) return null;
      
      const { data, timestamp } = JSON.parse(cached);
      
      if (Date.now() - timestamp > CACHE_TTL) {
        localStorage.removeItem(key);
        return null;
      }
      
      return data;
    }
    
    setCache(data) {
      const key = `encypher_verify_${this.documentId}`;
      localStorage.setItem(key, JSON.stringify({
        data,
        timestamp: Date.now()
      }));
    }
  }
  
  // Auto-initialize badges on page load
  function initBadges() {
    const badges = document.querySelectorAll('.encypher-verify-badge');
    badges.forEach(badge => new EncypherBadge(badge));
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBadges);
  } else {
    initBadges();
  }
})();
```

### 2. CSS Styles

**File:** `verify.css` (embedded in verify.js)

```css
.encypher-badge {
  display: inline-block;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.encypher-badge__compact {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 6px;
  background: #fff;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.encypher-badge:hover .encypher-badge__compact {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  transform: translateY(-1px);
}

.encypher-badge__logo {
  width: 16px;
  height: 16px;
}

.encypher-badge--verified .encypher-badge__compact {
  border-color: #10b981;
  background: #f0fdf4;
}

.encypher-badge--tampered .encypher-badge__compact {
  border-color: #ef4444;
  background: #fef2f2;
}

.encypher-details {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 400px;
  max-width: calc(100vw - 40px);
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  z-index: 10000;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.encypher-details__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  background: #f9fafb;
  border-radius: 12px 12px 0 0;
}

.encypher-details__close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.encypher-details__close:hover {
  background: #e5e7eb;
}

.encypher-details__body {
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.encypher-details__field {
  margin-bottom: 12px;
  line-height: 1.5;
}

.encypher-details__stats {
  margin: 16px 0;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.encypher-details__stats > div {
  margin: 4px 0;
}

.encypher-details__certificate {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.encypher-details__footer {
  display: flex;
  gap: 8px;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
}

.encypher-details__button {
  flex: 1;
  padding: 10px 16px;
  border-radius: 6px;
  text-align: center;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  background: #3b82f6;
  color: #fff;
  border: none;
}

.encypher-details__button:hover {
  background: #2563eb;
}

.encypher-details__button--secondary {
  background: #fff;
  color: #3b82f6;
  border: 1px solid #3b82f6;
}

.encypher-details__button--secondary:hover {
  background: #eff6ff;
}

/* Dark theme */
.encypher-badge--dark .encypher-badge__compact {
  background: #1f2937;
  border-color: #374151;
  color: #f9fafb;
}

.encypher-details--dark {
  background: #1f2937;
  color: #f9fafb;
}

.encypher-details--dark .encypher-details__header {
  background: #111827;
  border-color: #374151;
}

.encypher-details--dark .encypher-details__stats {
  background: #111827;
}
```

## Deployment

### 1. CDN Hosting

Host `verify.js` on a CDN for global distribution:

```
https://encypherai.com/embed/verify.js
https://cdn.encypherai.com/embed/verify.js (CDN)
```

**CDN Requirements:**
- Global edge distribution
- Gzip/Brotli compression
- Cache-Control: max-age=3600 (1 hour)
- CORS headers enabled
- HTTPS only

### 2. Versioning

Support versioned URLs for stability:

```
https://encypherai.com/embed/verify.js (latest)
https://encypherai.com/embed/v1/verify.js (v1)
https://encypherai.com/embed/v1.0.0/verify.js (specific version)
```

### 3. Fallback

Include fallback for API failures:

```javascript
// If API fails, show "Unable to verify" state
// with link to manual verification page
```

## Performance Optimization

### 1. Caching Strategy

- **Client-side**: localStorage cache (5 min TTL)
- **CDN**: Edge caching (1 hour)
- **API**: Redis cache (5 min TTL)

### 2. Lazy Loading

Badge script loads asynchronously:
```html
<script src="..." async></script>
```

### 3. Size Optimization

- Minified JS: ~15KB
- Gzipped: ~5KB
- No external dependencies

## Security

### 1. Content Security Policy (CSP)

Publishers need to allow:
```
script-src https://encypherai.com;
connect-src https://encypherai.com;
img-src https://encypherai.com https://cdn.encypherai.com;
```

### 2. Subresource Integrity (SRI)

Provide SRI hashes for integrity verification:
```html
<script 
  src="https://encypherai.com/embed/verify.js" 
  integrity="sha384-..." 
  crossorigin="anonymous">
</script>
```

### 3. Rate Limiting

Badge endpoint has higher rate limits:
- Free tier: 1000 requests/hour
- Business tier: 10000 requests/hour
- Enterprise tier: Unlimited

## Analytics

Track badge usage (privacy-respecting):
- Badge impressions (page loads)
- Badge clicks (expansions)
- Verification failures
- Average load time

No PII collected.

## Browser Support

- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions
- Safari: Last 2 versions
- Mobile browsers: iOS Safari 12+, Chrome Android 90+

## Testing

### 1. Unit Tests

Test badge functionality:
- Verification API calls
- Cache behavior
- UI rendering
- Error handling

### 2. Integration Tests

Test with real API:
- Verified documents
- Tampered documents
- Unknown documents
- API failures

### 3. Visual Regression Tests

Test UI across:
- Different themes
- Different screen sizes
- Different browsers

## Documentation for Publishers

### Quick Start Guide

```markdown
# Add Encypher Verification Badge

1. Sign your content using the Encypher API
2. Get your document ID from the API response
3. Add this code to your HTML:

<script src="https://encypherai.com/embed/verify.js" async></script>
<div class="encypher-verify-badge" data-document-id="YOUR_DOCUMENT_ID"></div>

4. Customize (optional):
   - data-theme="light" or "dark"
   - data-position="bottom-right", "bottom-left", "top-right", "top-left"
```

## Future Enhancements

- [ ] Multiple badge styles (compact, full, minimal)
- [ ] Custom branding (Enterprise tier)
- [ ] Sentence-level highlighting
- [ ] Real-time verification updates
- [ ] Accessibility improvements (ARIA labels)
- [ ] Internationalization (i18n)
