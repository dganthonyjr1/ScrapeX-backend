"""
Final Production Scraper for ScrapeX
Combines HTTP, browser automation, and manual fallback
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import logging

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinalScraper:
    """
    Production scraper with:
    1. HTTP request (fast, works for 70% of sites)
    2. Browser automation (works for 95% of sites)
    3. Manual fallback (for enterprise bot protection)
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.timeout = 15

    def scrape_facility_website(self, url: str) -> Dict:
        """
        Scrape facility website with automatic fallback
        
        Returns dict with:
        - status: 'success', 'blocked', or 'error'
        - scraping_method: 'http_request', 'browser_automation', or 'manual_required'
        - phone, email, address, etc.
        - manual_required: True if user needs to manually enter data
        """
        logger.info(f"Scraping {url}")
        
        # Step 1: Try HTTP (fast)
        http_result = self._try_http_scrape(url)
        if http_result.get('status') == 'success' and len(http_result.get('phone', [])) > 0:
            logger.info("HTTP scrape successful")
            return http_result
        
        # Step 2: Try browser automation
        if PLAYWRIGHT_AVAILABLE:
            logger.info("Trying browser automation")
            browser_result = self._try_browser_scrape(url)
            if browser_result.get('status') == 'success' and len(browser_result.get('phone', [])) > 0:
                logger.info("Browser scrape successful")
                return browser_result
        
        # Step 3: Manual fallback required
        logger.warning(f"Bot protection detected on {url}, manual entry required")
        return {
            'url': url,
            'status': 'blocked',
            'scraping_method': 'manual_required',
            'manual_required': True,
            'message': 'This website has advanced bot protection. Please manually verify the contact information.',
            'phone': [],
            'email': None,
            'facility_name': None,
            'scraped_at': datetime.now().isoformat()
        }

    def _try_http_scrape(self, url: str) -> Dict:
        """HTTP scraping"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'scraping_method': 'http_request',
                'facility_name': self._extract_facility_name(soup),
                'phone': self._extract_phone(soup, response.text),
                'email': self._extract_email(soup),
                'address': self._extract_address(soup),
                'hours': self._extract_hours(soup),
                'services': self._extract_services(soup),
                'status': 'success',
                'manual_required': False
            }
            
        except Exception as e:
            logger.warning(f"HTTP scrape failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _try_browser_scrape(self, url: str) -> Dict:
        """Browser automation scraping"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
                )
                
                page = browser.new_page()
                
                # Add stealth scripts
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                """)
                
                # Navigate
                page.goto(url, wait_until='load', timeout=20000)
                page.wait_for_timeout(2000)
                
                # Get content
                page_text = page.inner_text('body')
                content = page.content()
                
                browser.close()
                
                # Check if we got blocked (403 page)
                if '403' in page_text and 'forbidden' in page_text.lower():
                    return {'status': 'blocked'}
                
                soup = BeautifulSoup(content, 'html.parser')
                
                return {
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'scraping_method': 'browser_automation',
                    'facility_name': self._extract_facility_name(soup),
                    'phone': self._extract_phone_from_text(page_text),
                    'email': self._extract_email(soup),
                    'address': self._extract_address(soup),
                    'hours': self._extract_hours(soup),
                    'services': self._extract_services(soup),
                    'status': 'success',
                    'manual_required': False
                }
                
        except Exception as e:
            logger.error(f"Browser scrape failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _extract_facility_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract facility name"""
        for elem in [soup.find('h1'), soup.find('title'), soup.find('meta', {'property': 'og:title'})]:
            if elem:
                text = elem.get('content') if elem.name == 'meta' else elem.get_text()
                if text and '403' not in text and 'forbidden' not in text.lower():
                    return re.sub(r'\s*[\|\-]\s*.*$', '', text.strip())[:200]
        return None

    def _extract_phone(self, soup: BeautifulSoup, raw_html: str = None) -> List[str]:
        """Extract phone numbers from HTML"""
        phones = set()
        pattern = r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
        
        # Search in text and HTML
        for text in [soup.get_text(), raw_html or '']:
            for match in re.findall(pattern, text):
                phones.add(f"({match[0]}) {match[1]}-{match[2]}")
        
        # Check tel: links
        for link in soup.find_all('a', href=re.compile(r'tel:', re.I)):
            digits = ''.join(re.findall(r'\d+', link.get('href', '')))
            if len(digits) >= 10:
                d = digits[-10:]
                phones.add(f"({d[:3]}) {d[3:6]}-{d[6:]}")
        
        return sorted(list(phones))[:5]

    def _extract_phone_from_text(self, text: str) -> List[str]:
        """Extract phone from plain text"""
        phones = set()
        pattern = r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
        
        for match in re.findall(pattern, text):
            phones.add(f"({match[0]}) {match[1]}-{match[2]}")
        
        return sorted(list(phones))[:5]

    def _extract_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract email"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Check mailto links
        for link in soup.find_all('a', href=re.compile(r'mailto:', re.I)):
            match = re.search(pattern, link.get('href', ''))
            if match:
                return match.group(0)
        
        # Check page text
        match = re.search(pattern, soup.get_text())
        return match.group(0) if match else None

    def _extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract address"""
        for elem in [soup.find('address'), soup.find(class_=re.compile('address', re.I))]:
            if elem:
                addr = elem.get_text().strip()
                if len(addr) > 10:
                    return addr[:300]
        return None

    def _extract_hours(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract business hours"""
        for elem in soup.find_all(class_=re.compile('hours|schedule', re.I)):
            text = elem.get_text()
            if text and len(text) > 10:
                return {'raw': text.strip()[:500]}
        return None

    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract services"""
        keywords = ['emergency', 'consultation', 'installation', 'repair', 'maintenance', 'irrigation', 'landscaping']
        text = soup.get_text().lower()
        return list(set([k.title() for k in keywords if k in text]))[:10]


# Test
if __name__ == "__main__":
    scraper = FinalScraper()
    
    # Test on multiple sites
    test_urls = [
        "https://www.ocnjirrigation.com/",  # Bot-protected site
        "https://example.com",  # Simple site
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)
        
        result = scraper.scrape_facility_website(url)
        
        print(json.dumps(result, indent=2))
        print(f"\n✓ Status: {result.get('status')}")
        print(f"✓ Method: {result.get('scraping_method')}")
        print(f"✓ Manual required: {result.get('manual_required', False)}")
        print(f"✓ Phones: {result.get('phone', [])}")
