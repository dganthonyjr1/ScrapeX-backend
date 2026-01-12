"""
Hybrid Healthcare Facility Scraper
Tries HTTP first (fast), falls back to browser automation if needed
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Import browser scraper for fallback
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available, browser automation disabled")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridScraper:
    """
    Intelligent scraper that:
    1. Tries fast HTTP request first
    2. Falls back to browser automation if blocked (403) or no data found
    3. Returns comprehensive facility data
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.timeout = 15

    def scrape_facility_website(self, url: str) -> Dict:
        """
        Scrape facility website using hybrid approach
        """
        logger.info(f"Starting hybrid scrape of {url}")
        
        # Step 1: Try HTTP request first (fast)
        http_result = self._try_http_scrape(url)
        
        # Check if HTTP scrape was successful and found data
        if http_result.get('status') == 'success' and len(http_result.get('phone', [])) > 0:
            logger.info(f"HTTP scrape successful for {url}")
            return http_result
        
        # Step 2: If HTTP failed or no phone found, try browser automation
        if PLAYWRIGHT_AVAILABLE:
            logger.info(f"HTTP scrape failed or incomplete, trying browser automation for {url}")
            browser_result = self._try_browser_scrape(url)
            return browser_result
        else:
            logger.warning("Browser automation not available, returning HTTP result")
            return http_result

    def _try_http_scrape(self, url: str) -> Dict:
        """Try to scrape using HTTP request"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            facility_data = {
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'scraping_method': 'http_request',
                'facility_name': self._extract_facility_name(soup),
                'phone': self._extract_phone(soup, response.text),
                'email': self._extract_email(soup),
                'address': self._extract_address(soup),
                'hours': self._extract_hours(soup),
                'services': self._extract_services(soup),
                'website_quality': self._assess_website_quality(soup),
                'status': 'success'
            }
            
            return facility_data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.warning(f"HTTP 403 Forbidden for {url}")
                return {'status': 'blocked', 'error': '403 Forbidden', 'url': url}
            else:
                logger.error(f"HTTP error for {url}: {e}")
                return {'status': 'error', 'error': str(e), 'url': url}
                
        except Exception as e:
            logger.error(f"HTTP scrape failed for {url}: {e}")
            return {'status': 'error', 'error': str(e), 'url': url}

    def _try_browser_scrape(self, url: str) -> Dict:
        """Scrape using Playwright browser automation"""
        try:
            with sync_playwright() as p:
                # Launch browser with args to bypass detection
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                
                # Create context
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                )
                
                page = context.new_page()
                
                # Add script to remove webdriver property
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                # Navigate with shorter timeout
                logger.info(f"Browser navigating to {url}")
                try:
                    page.goto(url, wait_until='domcontentloaded', timeout=20000)
                    page.wait_for_timeout(2000)
                except:
                    # If networkidle fails, try with just load
                    logger.warning("Network idle timeout, continuing anyway")
                
                # Get content
                content = page.content()
                page_text = page.inner_text('body') if page else ""
                
                browser.close()
                
                # Parse content
                soup = BeautifulSoup(content, 'html.parser')
                
                facility_data = {
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'scraping_method': 'browser_automation',
                    'facility_name': self._extract_facility_name(soup),
                    'phone': self._extract_phone_from_text(page_text),
                    'email': self._extract_email(soup),
                    'address': self._extract_address(soup),
                    'hours': self._extract_hours(soup),
                    'services': self._extract_services(soup),
                    'website_quality': self._assess_website_quality(soup),
                    'status': 'success'
                }
                
                logger.info(f"Browser scrape complete for {url}, found {len(facility_data['phone'])} phones")
                return facility_data
                
        except Exception as e:
            logger.error(f"Browser scrape failed for {url}: {e}")
            return {
                'status': 'error',
                'error': f"Browser automation failed: {str(e)}",
                'url': url,
                'scraping_method': 'browser_automation',
                'phone': [],
                'scraped_at': datetime.now().isoformat()
            }

    def _extract_facility_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract facility name"""
        patterns = [
            soup.find('h1'),
            soup.find('title'),
            soup.find('meta', {'property': 'og:title'}),
        ]
        
        for element in patterns:
            if element:
                text = element.get('content') if element.name == 'meta' else element.get_text()
                if text:
                    text = text.strip()
                    text = re.sub(r'\s*[\|\-]\s*.*$', '', text)
                    return text[:200]
        return None

    def _extract_phone(self, soup: BeautifulSoup, raw_html: str = None) -> List[str]:
        """Extract phone numbers from HTML"""
        phones = set()
        
        patterns = [
            r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',
            r'\((\d{3})\)\s*(\d{3})-(\d{4})',
        ]
        
        text_sources = [soup.get_text()]
        if raw_html:
            text_sources.append(raw_html)
        
        for text in text_sources:
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    phone = f"({match[0]}) {match[1]}-{match[2]}"
                    phones.add(phone)
        
        # Check tel: links
        tel_links = soup.find_all('a', href=re.compile(r'tel:', re.I))
        for link in tel_links:
            href = link.get('href', '')
            digits = re.findall(r'\d+', href)
            if digits:
                digits_str = ''.join(digits)
                if len(digits_str) >= 10:
                    phone_digits = digits_str[-10:]
                    phone = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
                    phones.add(phone)
        
        return sorted(list(phones))[:5]

    def _extract_phone_from_text(self, text: str) -> List[str]:
        """Extract phone numbers from plain text"""
        phones = set()
        
        patterns = [
            r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',
            r'\((\d{3})\)\s*(\d{3})-(\d{4})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                phone = f"({match[0]}) {match[1]}-{match[2]}"
                phones.add(phone)
        
        result = sorted(list(phones))[:5]
        logger.info(f"Extracted {len(result)} phone numbers from text: {result}")
        return result

    def _extract_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract email address"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        mailto_links = soup.find_all('a', href=re.compile(r'mailto:', re.I))
        for link in mailto_links:
            href = link.get('href', '')
            email_match = re.search(email_pattern, href)
            if email_match:
                return email_match.group(0)
        
        text = soup.get_text()
        email_match = re.search(email_pattern, text)
        if email_match:
            return email_match.group(0)
        
        return None

    def _extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract physical address"""
        address_patterns = [
            soup.find('address'),
            soup.find(class_=re.compile('address', re.I)),
            soup.find(class_=re.compile('location', re.I)),
        ]
        
        for element in address_patterns:
            if element:
                addr = element.get_text().strip()
                if len(addr) > 10:
                    return addr[:300]
        return None

    def _extract_hours(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract business hours"""
        hours_elements = soup.find_all(class_=re.compile('hours|schedule', re.I))
        
        if hours_elements:
            for element in hours_elements:
                text = element.get_text()
                if text and len(text) > 10:
                    return {'raw': text.strip()[:500]}
        return None

    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract services"""
        service_keywords = [
            'emergency', 'consultation', 'installation', 'repair', 
            'maintenance', 'inspection', 'irrigation', 'lighting'
        ]
        
        page_text = soup.get_text().lower()
        services = [kw.title() for kw in service_keywords if kw in page_text]
        return list(set(services))[:10]

    def _assess_website_quality(self, soup: BeautifulSoup) -> Dict:
        """Assess website quality"""
        checks = {
            'has_title': bool(soup.find('title')),
            'has_contact_info': bool(re.search(r'\d{3}[-.]?\d{3}[-.]?\d{4}', soup.get_text())),
            'has_images': len(soup.find_all('img')) > 3,
            'has_navigation': bool(soup.find('nav')),
        }
        
        score = sum(checks.values())
        max_score = len(checks)
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': round((score / max_score) * 100, 1),
        }


# Test the hybrid scraper
if __name__ == "__main__":
    scraper = HybridScraper()
    
    test_url = "https://www.ocnjirrigation.com/"
    print(f"Testing hybrid scraper on: {test_url}")
    print("=" * 60)
    
    result = scraper.scrape_facility_website(test_url)
    
    print("\n=== SCRAPING RESULT ===")
    print(json.dumps(result, indent=2))
    
    print("\n=== SUMMARY ===")
    print(f"Status: {result.get('status')}")
    print(f"Method: {result.get('scraping_method')}")
    print(f"Phone numbers found: {len(result.get('phone', []))}")
    print(f"Phones: {result.get('phone', [])}")
    print(f"Facility: {result.get('facility_name')}")
