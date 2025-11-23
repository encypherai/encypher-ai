"""
Complete Web Scraper Example for Encypher Partner Integration

This example demonstrates a production-ready web scraper that:
1. Crawls websites for content
2. Extracts Encypher embeddings
3. Verifies embeddings with the public API
4. Reports findings to Encypher (requires partner API key)

Requirements:
    pip install requests beautifulsoup4 lxml
"""
import sys
import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'enterprise_api', 'app', 'utils', 'embeddings'))
from encypher_extract import EncypherExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EncypherWebScraper:
    """
    Web scraper that detects and reports Encypher embeddings.
    """
    
    def __init__(
        self,
        partner_api_key: str = None,
        partner_id: str = None,
        max_depth: int = 3,
        max_pages: int = 1000,
        delay: float = 1.0,
        batch_size: int = 100
    ):
        """
        Initialize the scraper.
        
        Args:
            partner_api_key: Partner API key for reporting findings
            partner_id: Partner identifier
            max_depth: Maximum crawl depth
            max_pages: Maximum pages to crawl
            delay: Delay between requests (seconds)
            batch_size: Number of findings to buffer before reporting
        """
        self.extractor = EncypherExtractor(partner_api_key=partner_api_key)
        self.partner_id = partner_id
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay
        self.batch_size = batch_size
        
        self.visited_urls: Set[str] = set()
        self.findings_buffer: List[Dict] = []
        self.stats = {
            'pages_crawled': 0,
            'embeddings_found': 0,
            'valid_embeddings': 0,
            'findings_reported': 0
        }
    
    def crawl_website(self, start_url: str, allowed_domains: List[str] = None):
        """
        Crawl a website starting from start_url.
        
        Args:
            start_url: URL to start crawling from
            allowed_domains: List of allowed domains (default: same domain as start_url)
        """
        if allowed_domains is None:
            parsed = urlparse(start_url)
            allowed_domains = [parsed.netloc]
        
        logger.info(f"Starting crawl from {start_url}")
        logger.info(f"Allowed domains: {allowed_domains}")
        
        # BFS crawl
        queue = [(start_url, 0)]  # (url, depth)
        
        while queue and len(self.visited_urls) < self.max_pages:
            url, depth = queue.pop(0)
            
            if url in self.visited_urls:
                continue
            
            if depth > self.max_depth:
                continue
            
            # Check if URL is in allowed domains
            parsed = urlparse(url)
            if parsed.netloc not in allowed_domains:
                continue
            
            # Crawl page
            try:
                self.crawl_page(url)
                self.visited_urls.add(url)
                
                # Get links for next level
                if depth < self.max_depth:
                    links = self.extract_links(url)
                    for link in links:
                        if link not in self.visited_urls:
                            queue.append((link, depth + 1))
                
                # Rate limiting
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
        
        # Report remaining findings
        self.flush_findings()
        
        # Print stats
        self.print_stats()
    
    def crawl_page(self, url: str):
        """
        Crawl a single page and extract embeddings.
        
        Args:
            url: URL to crawl
        """
        logger.info(f"Crawling: {url}")
        
        try:
            # Fetch page
            response = requests.get(
                url,
                timeout=10,
                headers={'User-Agent': 'EncypherBot/1.0 (+https://encypher.ai/bot)'}
            )
            response.raise_for_status()
            
            html = response.text
            self.stats['pages_crawled'] += 1
            
            # Extract embeddings
            references = self.extractor.extract_from_html(html)
            
            if not references:
                logger.debug(f"No embeddings found on {url}")
                return
            
            logger.info(f"Found {len(references)} embeddings on {url}")
            self.stats['embeddings_found'] += len(references)
            
            # Verify embeddings
            results = self.extractor.verify_batch(references)
            
            # Process valid embeddings
            for i, ref in enumerate(references):
                result = results['results'][i]
                
                if result['valid']:
                    self.stats['valid_embeddings'] += 1
                    
                    # Add to findings buffer
                    finding = {
                        'ref_id': ref.ref_id,
                        'found_url': url,
                        'found_at': datetime.utcnow().isoformat(),
                        'context': ref.context[:200] if ref.context else None,
                        'method': ref.method,
                        'document_id': result.get('document_id')
                    }
                    
                    self.findings_buffer.append(finding)
                    logger.info(f"Valid embedding: {ref.embedding} (doc: {result.get('document_id')})")
            
            # Report if buffer is full
            if len(self.findings_buffer) >= self.batch_size:
                self.flush_findings()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
    
    def extract_links(self, url: str) -> List[str]:
        """
        Extract all links from a page.
        
        Args:
            url: URL of the page
        
        Returns:
            List of absolute URLs
        """
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                absolute_url = urljoin(url, href)
                
                # Filter out non-http links
                if absolute_url.startswith(('http://', 'https://')):
                    links.append(absolute_url)
            
            return links
        
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {e}")
            return []
    
    def flush_findings(self):
        """Report all buffered findings to Encypher."""
        if not self.findings_buffer:
            return
        
        if not self.partner_id:
            logger.warning("No partner_id set - skipping reporting")
            logger.info(f"Would have reported {len(self.findings_buffer)} findings")
            self.findings_buffer = []
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
    
    def print_stats(self):
        """Print crawl statistics."""
        logger.info("=" * 60)
        logger.info("CRAWL STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Pages crawled: {self.stats['pages_crawled']}")
        logger.info(f"Embeddings found: {self.stats['embeddings_found']}")
        logger.info(f"Valid embeddings: {self.stats['valid_embeddings']}")
        logger.info(f"Findings reported: {self.stats['findings_reported']}")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Encypher Web Scraper - Detect and report Encypher embeddings'
    )
    parser.add_argument(
        'url',
        help='Starting URL to crawl'
    )
    parser.add_argument(
        '--partner-key',
        help='Partner API key (for reporting findings)',
        default=None
    )
    parser.add_argument(
        '--partner-id',
        help='Partner ID',
        default=None
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=3,
        help='Maximum crawl depth (default: 3)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=1000,
        help='Maximum pages to crawl (default: 1000)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Findings batch size (default: 100)'
    )
    parser.add_argument(
        '--allowed-domains',
        nargs='+',
        help='Allowed domains to crawl (default: same as start URL)'
    )
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = EncypherWebScraper(
        partner_api_key=args.partner_key,
        partner_id=args.partner_id,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
        delay=args.delay,
        batch_size=args.batch_size
    )
    
    # Start crawl
    scraper.crawl_website(
        start_url=args.url,
        allowed_domains=args.allowed_domains
    )


if __name__ == '__main__':
    main()
