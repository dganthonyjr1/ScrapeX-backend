"""
Production Healthcare Facility Scraper
Uses advanced techniques to bypass bot detection
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
    from playwright_stealth import stealth
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionScraper:
    """
    Production-ready scraper with:
    - HTTP request (fast)
    - Browser automation with stealth (bypass detection)
    - Comprehensive data extraction
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.timeout = 15

    def scrape_facility_website(self, url: str, force_browser: bool = False) -> Dict:
        """
        Scrape facility website
        
        Args:
            url: Website URL
            force_browser: Skip HTTP and go straight to browser
        """
        logger.info(f"Scraping {url}")
        
        if not force_browser:
            # Try HTTP first
            http_result = self._try_http_scrape(url)
            if http_result.get('status') == 'success' and len(http_result.get('phone', [])) > 0:
                logger.info(f"HTTP scrape successful")
                return http_result
        
        # Use browser automation
        if PLAYWRIGHT_AVAILABLE:
            logger.info(f"Using browser automation")
            return self._browser_scrape_with_stealth(url)
        else:
            return http_result if not force_browser else {
                'status': 'error',
                'error': 'Browser automation not available',
                'url': url
            }

    def _try_http_scrape(self, url: str) -> Dict:
        """HTTP scraping attempt"""
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
                'status': 'success'
            }
            
        except Exception as e:
            logger.warning(f"HTTP scrape failed: {e}")
            return {'status': 'failed', 'error': str(e), 'url': url}

    def _browser_scrape_with_stealth(self, url: str) -> Dict:
        """Browser scraping with stealth mode"""
        try:
            with sync_playwright() as p:
                # Launch with stealth args
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu'
                    ]
                )
                
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                )
                
                page = context.new_page()
                
                # Apply stealth
                stealth(page)
                
                # Navigate
                logger.info(f"Navigating to {url}")
                page.goto(url, wait_until='load', timeout=20000)
                page.wait_for_timeout(3000)
                
                # Get text content
                try:
                    page_text = page.inner_text('body')
                except:
                    page_text = page.content()
                
                # Get HTML
                content = page.content()
                
                browser.close()
                
                # Parse
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract data
                result = {
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'scraping_method': 'browser_stealth',
                    'facility_name': self._extract_facility_name(soup),
                    'phone': self._extract_phone_from_text(page_text),
                    'email': self._extract_email(soup),
                    'address': self._extract_address(soup),
                    'hours': self._extract_hours(soup),
                    'services': self._extract_services(soup),
                    'status': 'success'
                }
                
                logger.info(f"Browser scrape complete: {len(result['phone'])} phones found")
                return result
                
        except Exception as e:
            logger.error(f"Browser scrape failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'url': url,
                'scraping_method': 'browser_stealth',
                'phone': [],
                'scraped_at': datetime.now().isoformat()
            }

    def _extract_facility_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract facility name"""
        for elem in [soup.find('h1'), soup.find('title'), soup.find('meta', {'property': 'og:title'})]:
            if elem:
                text = elem.get('content') if elem.name == 'meta' else elem.get_text()
                if text and '403' not in text and 'forbidden' not in text.lower():
                    return re.sub(r'\s*[\|\-]\s*.*$', '', text.strip())[:200]
        return None

    def _extract_phone(self, soup: BeautifulSoup, raw_html: str = None) -> List[str]:
        """Extract phone numbers"""
        phones = set()
        pattern = r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
        
        for text in [soup.get_text(), raw_html or '']:
            for match in re.findall(pattern, text):
                phones.add(f"({match[0]}) {match[1]}-{match[2]}")
        
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
        
        result = sorted(list(phones))[:5]
        logger.info(f"Found {len(result)} phones in text")
        return result

    def _extract_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract email"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        for link in soup.find_all('a', href=re.compile(r'mailto:', re.I)):
            match = re.search(pattern, link.get('href', ''))
            if match:
                return match.group(0)
        
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
        """Extract hours"""
        for elem in soup.find_all(class_=re.compile('hours|schedule', re.I)):
            text = elem.get_text()
            if text and len(text) > 10:
                return {'raw': text.strip()[:500]}
        return None

    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract services"""
        keywords = ['emergency', 'consultation', 'installation', 'repair', 'maintenance', 'irrigation']
        text = soup.get_text().lower()
        return list(set([k.title() for k in keywords if k in text]))[:10]


# Test
if __name__ == "__main__":
    scraper = ProductionScraper()
    
    test_url = "https://www.ocnjirrigation.com/"
    print(f"Testing production scraper: {test_url}\n")
    
    result = scraper.scrape_facility_website(test_url)
    
    print("=== RESULT ===")
    print(json.dumps(result, indent=2))
    print(f"\n✓ Status: {result.get('status')}")
    print(f"✓ Method: {result.get('scraping_method')}")
    print(f"✓ Phones: {result.get('phone', [])}")
    print(f"✓ Name: {result.get('facility_name')}")
