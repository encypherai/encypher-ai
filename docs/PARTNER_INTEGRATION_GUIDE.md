# Partner Integration Guide - Encypher Embeddings

**Version:** 1.0  
**Last Updated:** October 30, 2025  
**Audience:** Web scraping partners, content monitoring services

---

## Overview

This guide explains how to integrate with Encypher's Minimal Signed Embeddings system as a **web scraping partner**. Partners help content owners monitor where their protected content appears online by scanning the web for Encypher markers and reporting findings.

### What You'll Do

1. **Scan web pages** for Encypher embeddings
2. **Extract and verify** embeddings using our public API
3. **Report findings** to Encypher (requires partner API key)
4. **Receive compensation** based on findings volume

### Benefits

- 💰 **Revenue share** on enforcement actions
- 🔧 **Free API access** for verification
- 📊 **Analytics dashboard** to track your findings
- 🤝 **Direct support** from Encypher team

---

## Quick Start

### 1. Get Partner API Key

Contact Encypher at `partners@encypher.ai` to:
- Register as a partner
- Receive your partner API key
- Set up billing/revenue share

### 2. Install Python Library

```bash
pip install requests beautifulsoup4
```

Download `encypher_extract.py` from our GitHub:
```bash
wget https://raw.githubusercontent.com/encypherai/encypher-tools/main/encypher_extract.py
```

### 3. Basic Usage

```python
from encypher_extract import EncypherExtractor
from datetime import datetime

# Initialize with your partner API key
extractor = EncypherExtractor(
    partner_api_key="your_partner_api_key_here"
)

# Scan a web page
html = fetch_webpage("https://example.com/article")
references = extractor.extract_from_html(html)

# Verify embeddings
if references:
    results = extractor.verify_batch(references)
    
    # Report findings
    findings = []
    for i, ref in enumerate(references):
        if results['results'][i]['valid']:
            findings.append({
                'ref_id': ref.ref_id,
                'found_url': 'https://example.com/article',
                'found_at': datetime.utcnow().isoformat(),
                'context': ref.context
            })
    
    if findings:
        response = extractor.report_findings(
            findings=findings,
            partner_id="your_partner_id",
            scan_date=datetime.utcnow().isoformat()
        )
        print(f"Reported {len(findings)} findings")
```

---

## Integration Patterns

### Pattern 1: Continuous Web Crawler

**Use Case:** Continuously crawl the web and report findings in real-time.

```python
import time
from encypher_extract import EncypherExtractor
from datetime import datetime

class EncypherCrawler:
    def __init__(self, partner_api_key, partner_id):
        self.extractor = EncypherExtractor(partner_api_key=partner_api_key)
        self.partner_id = partner_id
        self.findings_buffer = []
        self.buffer_size = 100  # Report every 100 findings
    
    def crawl_url(self, url):
        """Crawl a single URL and extract embeddings."""
        try:
            html = self.fetch_webpage(url)
            references = self.extractor.extract_from_html(html)
            
            if not references:
                return
            
            # Verify embeddings
            results = self.extractor.verify_batch(references)
            
            # Buffer valid findings
            for i, ref in enumerate(references):
                if results['results'][i]['valid']:
                    self.findings_buffer.append({
                        'ref_id': ref.ref_id,
                        'found_url': url,
                        'found_at': datetime.utcnow().isoformat(),
                        'context': ref.context[:200]
                    })
            
            # Report if buffer is full
            if len(self.findings_buffer) >= self.buffer_size:
                self.report_findings()
        
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    
    def report_findings(self):
        """Report buffered findings to Encypher."""
        if not self.findings_buffer:
            return
        
        try:
            response = self.extractor.report_findings(
                findings=self.findings_buffer,
                partner_id=self.partner_id,
                scan_date=datetime.utcnow().isoformat()
            )
            
            if response.get('success'):
                print(f"Reported {len(self.findings_buffer)} findings")
                self.findings_buffer = []
            else:
                print(f"Failed to report: {response.get('error')}")
        
        except Exception as e:
            print(f"Error reporting findings: {e}")
    
    def fetch_webpage(self, url):
        """Fetch webpage HTML (implement with your crawler)."""
        import requests
        response = requests.get(url, timeout=10)
        return response.text

# Usage
crawler = EncypherCrawler(
    partner_api_key="your_key",
    partner_id="your_id"
)

# Crawl URLs from your queue
urls = get_urls_from_queue()
for url in urls:
    crawler.crawl_url(url)
    time.sleep(1)  # Rate limiting

# Report remaining findings
crawler.report_findings()
```

### Pattern 2: Batch Processing

**Use Case:** Process large batches of archived web pages.

```python
from encypher_extract import EncypherExtractor
from datetime import datetime
import multiprocessing

def process_batch(urls, partner_api_key, partner_id):
    """Process a batch of URLs in parallel."""
    extractor = EncypherExtractor(partner_api_key=partner_api_key)
    all_findings = []
    
    for url in urls:
        try:
            html = fetch_from_archive(url)
            references = extractor.extract_from_html(html)
            
            if references:
                results = extractor.verify_batch(references)
                
                for i, ref in enumerate(references):
                    if results['results'][i]['valid']:
                        all_findings.append({
                            'ref_id': ref.ref_id,
                            'found_url': url,
                            'found_at': datetime.utcnow().isoformat()
                        })
        except Exception as e:
            print(f"Error processing {url}: {e}")
    
    # Report all findings
    if all_findings:
        extractor.report_findings(
            findings=all_findings,
            partner_id=partner_id,
            scan_date=datetime.utcnow().isoformat()
        )
    
    return len(all_findings)

# Parallel processing
urls = load_urls_from_file('urls.txt')
batch_size = 1000
batches = [urls[i:i+batch_size] for i in range(0, len(urls), batch_size)]

with multiprocessing.Pool(processes=4) as pool:
    results = pool.starmap(
        process_batch,
        [(batch, "your_key", "your_id") for batch in batches]
    )

print(f"Total findings: {sum(results)}")
```

### Pattern 3: Real-time Monitoring

**Use Case:** Monitor specific domains or keywords in real-time.

```python
from encypher_extract import EncypherExtractor
from datetime import datetime
import asyncio
import aiohttp

class RealtimeMonitor:
    def __init__(self, partner_api_key, partner_id, domains):
        self.extractor = EncypherExtractor(partner_api_key=partner_api_key)
        self.partner_id = partner_id
        self.domains = domains
    
    async def monitor_domain(self, domain):
        """Monitor a single domain continuously."""
        while True:
            try:
                # Get latest pages from domain
                urls = await self.get_latest_pages(domain)
                
                for url in urls:
                    await self.check_url(url)
                
                # Wait before next check
                await asyncio.sleep(300)  # 5 minutes
            
            except Exception as e:
                print(f"Error monitoring {domain}: {e}")
                await asyncio.sleep(60)
    
    async def check_url(self, url):
        """Check a URL for embeddings."""
        try:
            html = await self.fetch_async(url)
            references = self.extractor.extract_from_html(html)
            
            if references:
                results = self.extractor.verify_batch(references)
                
                findings = []
                for i, ref in enumerate(references):
                    if results['results'][i]['valid']:
                        findings.append({
                            'ref_id': ref.ref_id,
                            'found_url': url,
                            'found_at': datetime.utcnow().isoformat()
                        })
                
                if findings:
                    # Report immediately for real-time monitoring
                    self.extractor.report_findings(
                        findings=findings,
                        partner_id=self.partner_id,
                        scan_date=datetime.utcnow().isoformat()
                    )
                    print(f"Found {len(findings)} embeddings at {url}")
        
        except Exception as e:
            print(f"Error checking {url}: {e}")
    
    async def fetch_async(self, url):
        """Fetch URL asynchronously."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()
    
    async def get_latest_pages(self, domain):
        """Get latest pages from domain (implement with your crawler)."""
        # Example: query sitemap, RSS feed, or crawl homepage
        return []

# Usage
monitor = RealtimeMonitor(
    partner_api_key="your_key",
    partner_id="your_id",
    domains=["example.com", "news.example.com"]
)

# Monitor all domains concurrently
async def main():
    tasks = [monitor.monitor_domain(d) for d in monitor.domains]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

---

## API Reference

### Public Verification API

**No authentication required** - Use for verifying embeddings.

#### Verify Single Embedding

```http
GET /api/v1/public/verify/{ref_id}?signature={signature}
```

**Example:**
```python
import requests

response = requests.get(
    "https://api.encypher.ai/api/v1/public/verify/a3f9c2e1",
    params={'signature': '8k3mP9xQ'}
)

data = response.json()
if data['valid']:
    print(f"Document: {data['document']['title']}")
    print(f"Organization: {data['document']['organization']}")
```

#### Batch Verification

```http
POST /api/v1/public/verify/batch
Content-Type: application/json

{
  "references": [
    {"ref_id": "a3f9c2e1", "signature": "8k3mP9xQ"},
    {"ref_id": "b4a8d3f2", "signature": "9m4nQ0yR"}
  ]
}
```

**Example:**
```python
response = requests.post(
    "https://api.encypher.ai/api/v1/public/verify/batch",
    json={
        'references': [
            {'ref_id': 'a3f9c2e1', 'signature': '8k3mP9xQ'},
            {'ref_id': 'b4a8d3f2', 'signature': '9m4nQ0yR'}
        ]
    }
)

data = response.json()
print(f"Valid: {data['valid_count']}/{data['total']}")
```

### Partner Reporting API

**Requires partner API key** - Use for reporting findings.

#### Report Findings

```http
POST /api/v1/partner/report-findings
Authorization: Bearer {partner_api_key}
Content-Type: application/json

{
  "partner_id": "partner_001",
  "scan_date": "2025-10-30T19:00:00Z",
  "findings": [
    {
      "ref_id": "a3f9c2e1",
      "found_url": "https://example.com/article",
      "found_at": "2025-10-30T19:15:00Z",
      "context": "Article text preview...",
      "screenshot_url": "https://partner.com/screenshots/abc123.png"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "findings_processed": 1,
  "notifications_sent": 1,
  "summary": {
    "new_findings": 1,
    "duplicate_findings": 0,
    "invalid_findings": 0
  }
}
```

---

## Best Practices

### 1. Rate Limiting

Respect API rate limits:
- **Public API:** 1000 requests/hour per IP
- **Partner API:** 10,000 requests/hour

```python
import time
from functools import wraps

def rate_limit(calls_per_second=10):
    """Rate limiting decorator."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=10)
def verify_embedding(ref_id, signature):
    # Your verification code
    pass
```

### 2. Error Handling

Handle errors gracefully:

```python
import requests
from requests.exceptions import RequestException

def safe_verify(extractor, ref_id, signature, max_retries=3):
    """Verify with retry logic."""
    for attempt in range(max_retries):
        try:
            result = extractor.verify(ref_id, signature)
            return result
        except RequestException as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts: {e}")
                return {'valid': False, 'error': str(e)}
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 3. Deduplication

Avoid reporting duplicate findings:

```python
class FindingsTracker:
    def __init__(self):
        self.seen = set()  # (ref_id, url) tuples
    
    def is_duplicate(self, ref_id, url):
        """Check if finding was already reported."""
        key = (ref_id, url)
        if key in self.seen:
            return True
        self.seen.add(key)
        return False
    
    def should_report(self, ref_id, url):
        """Check if finding should be reported."""
        return not self.is_duplicate(ref_id, url)

tracker = FindingsTracker()

for finding in findings:
    if tracker.should_report(finding['ref_id'], finding['found_url']):
        # Report finding
        pass
```

### 4. Batch Reporting

Report findings in batches for efficiency:

```python
class BatchReporter:
    def __init__(self, extractor, partner_id, batch_size=100):
        self.extractor = extractor
        self.partner_id = partner_id
        self.batch_size = batch_size
        self.buffer = []
    
    def add_finding(self, finding):
        """Add finding to buffer."""
        self.buffer.append(finding)
        
        if len(self.buffer) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """Report all buffered findings."""
        if not self.buffer:
            return
        
        try:
            self.extractor.report_findings(
                findings=self.buffer,
                partner_id=self.partner_id,
                scan_date=datetime.utcnow().isoformat()
            )
            print(f"Reported {len(self.buffer)} findings")
            self.buffer = []
        except Exception as e:
            print(f"Error reporting: {e}")
```

---

## Testing

### Test with Sample Data

```python
from encypher_extract import EncypherExtractor

# Initialize without API key for testing
extractor = EncypherExtractor()

# Test HTML with embeddings
test_html = '''
<html>
<body>
    <p data-encypher="ency:v1/a3f9c2e1/8k3mP9xQ">
        This is a test paragraph with an embedding.
    </p>
</body>
</html>
'''

# Extract
references = extractor.extract_from_html(test_html)
print(f"Found {len(references)} embeddings")

# Verify (uses public API - no key needed)
if references:
    results = extractor.verify_batch(references)
    print(f"Verified {results['valid_count']}/{results['total']}")
```

### Test Reporting (Sandbox)

Contact Encypher for sandbox API credentials to test reporting without affecting production data.

---

## Revenue Model

### How You Get Paid

1. **Per Finding:** $0.10 per unique, valid finding
2. **Enforcement Bonus:** 10% of settlement/licensing fees
3. **Volume Tiers:**
   - 0-10,000 findings/month: $0.10 per finding
   - 10,001-100,000: $0.08 per finding
   - 100,001+: $0.05 per finding

### Payment Schedule

- Monthly invoicing
- Net-30 payment terms
- Direct deposit or wire transfer

### Reporting Dashboard

Access your partner dashboard at `https://partners.encypher.ai` to view:
- Total findings this month
- Revenue earned
- Top domains scanned
- Finding success rate

---

## Support

### Documentation
- **API Docs:** https://docs.encypher.ai/api
- **GitHub:** https://github.com/encypherai/encypher-tools
- **Examples:** https://github.com/encypherai/partner-examples

### Contact
- **Email:** partners@encypher.ai
- **Slack:** Join our partner Slack channel
- **Support Hours:** 9am-5pm PST, Monday-Friday

### SLA
- **API Uptime:** 99.9%
- **Support Response:** <24 hours
- **Bug Fixes:** <72 hours

---

## Appendix

### Example: Complete Web Scraper

See `examples/web_scraper.py` in our GitHub repository for a complete, production-ready web scraper implementation.

### Example: Scrapy Integration

See `examples/scrapy_middleware.py` for integrating Encypher detection into Scrapy spiders.

### Example: Selenium Integration

See `examples/selenium_detector.py` for detecting embeddings in JavaScript-rendered pages.

---

**Questions?** Contact partners@encypher.ai
