"""
Browser-Based Healthcare Facility Scraper using Playwright
Bypasses bot detection by using a real browser engine
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserScraper:
    """Scraper using Playwright for browser automation"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.timeout = 30000  # 30 seconds in milliseconds

    def scrape_facility_website(self, url: str) -> Dict:
        """
        Scrape a healthcare facility website using browser automation
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dictionary with extracted facility data
        """
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=self.headless)
                
                # Create context with realistic settings and stealth mode
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York',
                    permissions=['geolocation'],
                    extra_http_headers={
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1'
                    }
                )
                
                # Create page
                page = context.new_page()
                
                # Navigate to URL
                logger.info(f"Navigating to {url}")
                page.goto(url, wait_until='networkidle', timeout=self.timeout)
                
                # Wait for page to fully load and render
                page.wait_for_timeout(3000)
                
                # Scroll to trigger lazy loading
                page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')
                page.wait_for_timeout(1000)
                
                # Get page content
                content = page.content()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract data
                facility_data = {
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'scraping_method': 'browser_automation',
                    'facility_name': self._extract_facility_name(soup, page),
                    'phone': self._extract_phone(soup, page),
                    'email': self._extract_email(soup, page),
                    'address': self._extract_address(soup, page),
                    'hours': self._extract_hours(soup),
                    'services': self._extract_services(soup),
                    'website_quality': self._assess_website_quality(soup),
                    'contact_methods': self._extract_contact_methods(soup),
                    'status': 'success'
                }
                
                # Close browser
                browser.close()
                
                logger.info(f"Successfully scraped {url} using browser automation")
                logger.info(f"Found {len(facility_data['phone'])} phone numbers")
                
                return facility_data
                
        except PlaywrightTimeout as e:
            logger.error(f"Timeout while scraping {url}: {str(e)}")
            return self._create_error_response(url, f"Page load timeout: {str(e)}")
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            return self._create_error_response(url, str(e))

    def _create_error_response(self, url: str, error: str) -> Dict:
        """Create a standardized error response"""
        return {
            'url': url,
            'error': error,
            'status': 'error',
            'scraping_method': 'browser_automation',
            'scraped_at': datetime.now().isoformat(),
            'phone': [],
            'facility_name': None,
        }

    def _extract_facility_name(self, soup: BeautifulSoup, page) -> Optional[str]:
        """Extract facility name from various sources"""
        # Try page title first
        try:
            title = page.title()
            if title:
                # Clean up title
                title = title.strip()
                # Remove common suffixes
                title = re.sub(r'\s*[\|\-]\s*.*$', '', title)
                return title[:200]
        except:
            pass
        
        # Fallback to soup parsing
        patterns = [
            soup.find('h1'),
            soup.find('title'),
            soup.find('meta', {'property': 'og:title'}),
            soup.find('meta', {'name': 'title'}),
        ]
        
        for element in patterns:
            if element:
                text = element.get('content') if element.name == 'meta' else element.get_text()
                if text:
                    text = text.strip()
                    text = re.sub(r'\s*[\|\-]\s*.*$', '', text)
                    return text[:200]
        
        return None

    def _extract_phone(self, soup: BeautifulSoup, page) -> List[str]:
        """
        Extract phone numbers with comprehensive pattern matching
        """
        phones = set()
        
        # Get page text
        try:
            page_text = page.inner_text('body')
        except:
            page_text = soup.get_text()
        
        # Multiple regex patterns to catch different formats
        patterns = [
            r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',  # Most common
            r'\((\d{3})\)\s*(\d{3})-(\d{4})',  # (609) 628-3103
            r'(\d{3})[-.](\d{3})[-.](\d{4})',  # 609-628-3103
            r'(\d{3})\s+(\d{3})\s+(\d{4})',    # 609 628 3103
        ]
        
        # Search in page text
        for pattern in patterns:
            matches = re.findall(pattern, page_text)
            for match in matches:
                # Format consistently
                phone = f"({match[0]}) {match[1]}-{match[2]}"
                phones.add(phone)
        
        # Also check HTML for tel: links
        tel_links = soup.find_all('a', href=re.compile(r'tel:', re.I))
        for link in tel_links:
            href = link.get('href', '')
            # Extract digits only
            digits = re.findall(r'\d+', href)
            if digits:
                digits_str = ''.join(digits)
                # Take last 10 digits (phone number)
                if len(digits_str) >= 10:
                    phone_digits = digits_str[-10:]
                    phone = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
                    phones.add(phone)
        
        # Also check visible text in links
        phone_links = soup.find_all('a', string=re.compile(r'\d{3}[-.\s)]\d{3}[-.\s]\d{4}'))
        for link in phone_links:
            text = link.get_text()
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    phone = f"({match[0]}) {match[1]}-{match[2]}"
                    phones.add(phone)
        
        result = sorted(list(phones))[:10]  # Return top 10 unique numbers
        logger.info(f"Extracted phone numbers: {result}")
        return result

    def _extract_email(self, soup: BeautifulSoup, page) -> Optional[str]:
        """Extract email address"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Check mailto links first
        mailto_links = soup.find_all('a', href=re.compile(r'mailto:', re.I))
        for link in mailto_links:
            href = link.get('href', '')
            email_match = re.search(email_pattern, href)
            if email_match:
                return email_match.group(0)
        
        # Check page text
        try:
            page_text = page.inner_text('body')
            email_match = re.search(email_pattern, page_text)
            if email_match:
                # Validate it's not an image or common fake email
                email = email_match.group(0)
                if not any(x in email.lower() for x in ['example.com', 'test.com', 'image', '.png', '.jpg']):
                    return email
        except:
            pass
        
        return None

    def _extract_address(self, soup: BeautifulSoup, page) -> Optional[str]:
        """Extract physical address"""
        address_patterns = [
            soup.find('address'),
            soup.find(class_=re.compile('address', re.I)),
            soup.find(class_=re.compile('location', re.I)),
            soup.find(itemprop='address'),
        ]
        
        for element in address_patterns:
            if element:
                addr = element.get_text().strip()
                if len(addr) > 10:  # Ensure it's substantial
                    return addr[:300]
        
        return None

    def _extract_hours(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract business hours"""
        hours_data = {}
        
        hours_elements = soup.find_all(class_=re.compile('hours|schedule|operating', re.I))
        
        if hours_elements:
            for element in hours_elements:
                text = element.get_text()
                if text and len(text) > 10:
                    hours_data['raw'] = text.strip()[:500]
                    break
        
        return hours_data if hours_data else None

    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract services offered"""
        services = []
        
        service_keywords = [
            'emergency', 'urgent care', 'surgery', 'consultation',
            'installation', 'repair', 'maintenance', 'inspection',
            'landscaping', 'irrigation', 'lighting', 'design',
            'sprinkler', 'lawn care', 'winterization', 'blowout'
        ]
        
        page_text = soup.get_text().lower()
        
        for keyword in service_keywords:
            if keyword in page_text:
                services.append(keyword.title())
        
        return list(set(services))[:15]

    def _extract_contact_methods(self, soup: BeautifulSoup) -> Dict:
        """Extract available contact methods"""
        contact_methods = {
            'phone': len(self._extract_phone(soup, None)) > 0 if soup else False,
            'email': bool(self._extract_email(soup, None)) if soup else False,
            'contact_form': bool(soup.find('form')) if soup else False,
            'online_booking': bool(re.search(r'book|appointment|schedule|request', soup.get_text(), re.I)) if soup else False,
        }
        return contact_methods

    def _assess_website_quality(self, soup: BeautifulSoup) -> Dict:
        """Assess the quality and completeness of the website"""
        checks = {
            'has_title': bool(soup.find('title')),
            'has_meta_description': bool(soup.find('meta', {'name': 'description'})),
            'has_contact_info': bool(re.search(r'\d{3}[-.]?\d{3}[-.]?\d{4}', soup.get_text())),
            'has_address': bool(soup.find('address') or soup.find(class_=re.compile('address', re.I))),
            'has_images': len(soup.find_all('img')) > 3,
            'is_mobile_responsive': bool(soup.find('meta', {'name': 'viewport'})),
            'has_ssl': True,
            'has_social_links': len(soup.find_all('a', href=re.compile(r'facebook|twitter|linkedin|instagram', re.I))) > 0,
            'has_navigation': bool(soup.find('nav') or soup.find(role='navigation')),
        }
        
        quality_score = sum(checks.values())
        max_score = len(checks)
        
        return {
            'score': quality_score,
            'max_score': max_score,
            'percentage': round((quality_score / max_score) * 100, 1),
            'checks': checks
        }

    def scrape_multiple_facilities(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple facility websites"""
        results = []
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            result = self.scrape_facility_website(url)
            results.append(result)
        return results


# Test the browser scraper
if __name__ == "__main__":
    scraper = BrowserScraper(headless=True)
    
    test_url = "https://www.ocnjirrigation.com/"
    print(f"Testing browser scraper on: {test_url}")
    print("=" * 60)
    
    result = scraper.scrape_facility_website(test_url)
    
    print("\n=== SCRAPING RESULT ===")
    print(json.dumps(result, indent=2))
    
    print("\n=== SUMMARY ===")
    print(f"Status: {result.get('status')}")
    print(f"Phone numbers found: {len(result.get('phone', []))}")
    print(f"Phone numbers: {result.get('phone', [])}")
    print(f"Facility name: {result.get('facility_name')}")
    print(f"Email: {result.get('email')}")
