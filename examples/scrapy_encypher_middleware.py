"""
Scrapy Middleware for Encypher Embedding Detection

This middleware automatically detects Encypher embeddings in scraped pages
and reports findings to the Encypher API.

Installation:
    1. Copy this file to your Scrapy project
    2. Add to settings.py:
        DOWNLOADER_MIDDLEWARES = {
            'your_project.middlewares.EncypherMiddleware': 543,
        }
        
        ENCYPHER_PARTNER_API_KEY = 'your_partner_api_key'
        ENCYPHER_PARTNER_ID = 'your_partner_id'
        ENCYPHER_BATCH_SIZE = 100

Usage:
    The middleware will automatically detect embeddings in all scraped pages.
    Access findings via spider.encypher_findings
"""
import sys
import os
import logging
from datetime import datetime
from typing import List, Dict

from scrapy import signals
from scrapy.http import Response
from scrapy.exceptions import NotConfigured

# Add path for encypher_extract
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'enterprise_api', 'app', 'utils', 'embeddings'))
from encypher_extract import EncypherExtractor

logger = logging.getLogger(__name__)


class EncypherMiddleware:
    """
    Scrapy middleware for detecting Encypher embeddings.
    """
    
    def __init__(self, partner_api_key, partner_id, batch_size):
        """
        Initialize middleware.
        
        Args:
            partner_api_key: Partner API key
            partner_id: Partner identifier
            batch_size: Number of findings to buffer before reporting
        """
        self.extractor = EncypherExtractor(partner_api_key=partner_api_key)
        self.partner_id = partner_id
        self.batch_size = batch_size
        self.findings_buffer = []
        
        self.stats = {
            'pages_processed': 0,
            'embeddings_found': 0,
            'valid_embeddings': 0,
            'findings_reported': 0
        }
    
    @classmethod
    def from_crawler(cls, crawler):
        """
        Create middleware from crawler.
        
        Args:
            crawler: Scrapy crawler
        
        Returns:
            EncypherMiddleware instance
        
        Raises:
            NotConfigured: If required settings are missing
        """
        # Get settings
        partner_api_key = crawler.settings.get('ENCYPHER_PARTNER_API_KEY')
        partner_id = crawler.settings.get('ENCYPHER_PARTNER_ID')
        batch_size = crawler.settings.getint('ENCYPHER_BATCH_SIZE', 100)
        
        if not partner_api_key or not partner_id:
            raise NotConfigured('ENCYPHER_PARTNER_API_KEY and ENCYPHER_PARTNER_ID required')
        
        # Create middleware
        middleware = cls(
            partner_api_key=partner_api_key,
            partner_id=partner_id,
            batch_size=batch_size
        )
        
        # Connect signals
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        
        return middleware
    
    def spider_opened(self, spider):
        """Called when spider is opened."""
        logger.info(f'Encypher middleware enabled for spider: {spider.name}')
        spider.encypher_findings = []
        spider.encypher_stats = self.stats
    
    def spider_closed(self, spider):
        """Called when spider is closed."""
        # Report remaining findings
        self.flush_findings(spider)
        
        # Log stats
        logger.info('=' * 60)
        logger.info('ENCYPHER DETECTION STATISTICS')
        logger.info('=' * 60)
        logger.info(f"Pages processed: {self.stats['pages_processed']}")
        logger.info(f"Embeddings found: {self.stats['embeddings_found']}")
        logger.info(f"Valid embeddings: {self.stats['valid_embeddings']}")
        logger.info(f"Findings reported: {self.stats['findings_reported']}")
        logger.info('=' * 60)
    
    def process_response(self, request, response, spider):
        """
        Process response and detect embeddings.
        
        Args:
            request: Scrapy request
            response: Scrapy response
            spider: Scrapy spider
        
        Returns:
            Response (unchanged)
        """
        # Only process HTML responses
        if not isinstance(response, Response):
            return response
        
        if 'text/html' not in response.headers.get('Content-Type', b'').decode('utf-8'):
            return response
        
        try:
            self.detect_embeddings(response, spider)
        except Exception as e:
            logger.error(f"Error detecting embeddings in {response.url}: {e}")
        
        return response
    
    def detect_embeddings(self, response, spider):
        """
        Detect embeddings in response.
        
        Args:
            response: Scrapy response
            spider: Scrapy spider
        """
        self.stats['pages_processed'] += 1
        
        # Extract embeddings
        html = response.text
        references = self.extractor.extract_from_html(html)
        
        if not references:
            return
        
        logger.info(f"Found {len(references)} embeddings on {response.url}")
        self.stats['embeddings_found'] += len(references)
        
        # Verify embeddings
        results = self.extractor.verify_batch(references)
        
        # Process valid embeddings
        for i, ref in enumerate(references):
            result = results['results'][i]
            
            if result['valid']:
                self.stats['valid_embeddings'] += 1
                
                # Create finding
                finding = {
                    'ref_id': ref.ref_id,
                    'found_url': response.url,
                    'found_at': datetime.utcnow().isoformat(),
                    'context': ref.context[:200] if ref.context else None,
                    'method': ref.method,
                    'document_id': result.get('document_id')
                }
                
                # Add to buffer and spider findings
                self.findings_buffer.append(finding)
                spider.encypher_findings.append(finding)
                
                logger.info(f"Valid embedding: {ref.embedding} (doc: {result.get('document_id')})")
        
        # Report if buffer is full
        if len(self.findings_buffer) >= self.batch_size:
            self.flush_findings(spider)
    
    def flush_findings(self, spider):
        """
        Report buffered findings to Encypher.
        
        Args:
            spider: Scrapy spider
        """
        if not self.findings_buffer:
            return
        
        try:
            logger.info(f"Reporting {len(self.findings_buffer)} findings...")
            
            response = self.extractor.report_findings(
                findings=self.findings_buffer,
                partner_id=self.partner_id,
                scan_date=datetime.utcnow().isoformat()
            )
            
            if response.get('success'):
                self.stats['findings_reported'] += len(self.findings_buffer)
                logger.info(f"Successfully reported {len(self.findings_buffer)} findings")
                logger.info(f"Summary: {response.get('summary')}")
            else:
                logger.error(f"Failed to report findings: {response.get('error')}")
            
            self.findings_buffer = []
        
        except Exception as e:
            logger.error(f"Error reporting findings: {e}")


# Example Scrapy spider using the middleware
class ExampleSpider:
    """
    Example spider that uses Encypher middleware.
    
    Usage:
        scrapy crawl example -a start_url=https://example.com
    """
    name = 'example'
    
    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []
    
    def parse(self, response):
        """
        Parse response.
        
        The middleware will automatically detect embeddings.
        """
        # Your normal parsing logic here
        yield {
            'url': response.url,
            'title': response.css('title::text').get()
        }
        
        # Follow links
        for link in response.css('a::attr(href)').getall():
            yield response.follow(link, self.parse)


# Example settings.py configuration
EXAMPLE_SETTINGS = """
# settings.py

# Enable Encypher middleware
DOWNLOADER_MIDDLEWARES = {
    'your_project.middlewares.EncypherMiddleware': 543,
}

# Encypher configuration
ENCYPHER_PARTNER_API_KEY = 'your_partner_api_key_here'
ENCYPHER_PARTNER_ID = 'your_partner_id_here'
ENCYPHER_BATCH_SIZE = 100

# Optional: Rate limiting
DOWNLOAD_DELAY = 1.0
CONCURRENT_REQUESTS = 16
"""

if __name__ == '__main__':
    print("Scrapy Encypher Middleware")
    print("=" * 60)
    print("\nAdd this to your settings.py:")
    print(EXAMPLE_SETTINGS)
