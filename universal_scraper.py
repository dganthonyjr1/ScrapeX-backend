"""
Universal Business Scraper for ScrapeX
Scrapes ANY business type with owner/decision-maker contact extraction
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


class UniversalBusinessScraper:
    """
    Universal scraper that works for ANY business type:
    - Restaurants, retail stores, professional services
    - Healthcare, legal, financial services
    - Contractors, landscaping, home services
    - B2B services, SaaS companies, agencies
    
    Extracts:
    - Business name, phone, email, address
    - Owner/decision-maker names and contact info
    - LinkedIn profiles, social media
    - Services, industry type, business description
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.timeout = 15

    def scrape_business(self, url: str, business_type: Optional[str] = None) -> Dict:
        """
        Scrape any business website
        
        Args:
            url: Business website URL
            business_type: Optional business type hint (e.g., 'restaurant', 'law_firm', 'contractor')
        
        Returns:
            Dict with comprehensive business data including owner contact info
        """
        logger.info(f"Scraping business: {url}")
        
        # Step 1: Try HTTP (fast)
        http_result = self._try_http_scrape(url, business_type)
        if http_result.get('status') == 'success' and len(http_result.get('phone', [])) > 0:
            logger.info("HTTP scrape successful")
            return http_result
        
        # Step 2: Try browser automation
        if PLAYWRIGHT_AVAILABLE:
            logger.info("Trying browser automation")
            browser_result = self._try_browser_scrape(url, business_type)
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
            'business_name': None,
            'phone': [],
            'email': None,
            'owner_info': {},
            'scraped_at': datetime.now().isoformat()
        }

    def _try_http_scrape(self, url: str, business_type: Optional[str] = None) -> Dict:
        """HTTP scraping with owner contact extraction"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # Extract all business data
            result = {
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'scraping_method': 'http_request',
                'business_name': self._extract_business_name(soup),
                'business_type': business_type or self._detect_business_type(soup, page_text),
                'phone': self._extract_phone(soup, response.text),
                'email': self._extract_emails(soup),
                'address': self._extract_address(soup),
                'hours': self._extract_hours(soup),
                'services': self._extract_services(soup, page_text),
                'description': self._extract_description(soup),
                'social_media': self._extract_social_media(soup),
                'owner_info': self._extract_owner_info(soup, page_text),
                'status': 'success',
                'manual_required': False
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"HTTP scrape failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _try_browser_scrape(self, url: str, business_type: Optional[str] = None) -> Dict:
        """Browser automation scraping with owner contact extraction"""
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
                
                # Check if we got blocked
                if '403' in page_text and 'forbidden' in page_text.lower():
                    return {'status': 'blocked'}
                
                soup = BeautifulSoup(content, 'html.parser')
                
                result = {
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'scraping_method': 'browser_automation',
                    'business_name': self._extract_business_name(soup),
                    'business_type': business_type or self._detect_business_type(soup, page_text),
                    'phone': self._extract_phone_from_text(page_text),
                    'email': self._extract_emails(soup),
                    'address': self._extract_address(soup),
                    'hours': self._extract_hours(soup),
                    'services': self._extract_services(soup, page_text),
                    'description': self._extract_description(soup),
                    'social_media': self._extract_social_media(soup),
                    'owner_info': self._extract_owner_info(soup, page_text),
                    'status': 'success',
                    'manual_required': False
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Browser scrape failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _extract_business_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract business name from multiple sources"""
        # Try multiple sources in order of reliability
        for elem in [
            soup.find('h1'),
            soup.find('meta', {'property': 'og:site_name'}),
            soup.find('meta', {'property': 'og:title'}),
            soup.find('title'),
            soup.find(class_=re.compile('business-name|company-name|brand', re.I))
        ]:
            if elem:
                text = elem.get('content') if elem.name == 'meta' else elem.get_text()
                if text and '403' not in text and 'forbidden' not in text.lower():
                    # Clean up common suffixes
                    text = re.sub(r'\s*[\|\-]\s*(Home|About|Contact|Welcome).*$', '', text.strip(), flags=re.I)
                    return text[:200]
        return None

    def _detect_business_type(self, soup: BeautifulSoup, page_text: str) -> Optional[str]:
        """Auto-detect business type from content"""
        text_lower = page_text.lower()
        
        # Business type keywords
        types = {
            'restaurant': ['menu', 'reservation', 'dining', 'cuisine', 'chef', 'food'],
            'law_firm': ['attorney', 'lawyer', 'legal', 'law firm', 'litigation', 'counsel'],
            'medical': ['doctor', 'physician', 'medical', 'healthcare', 'clinic', 'hospital'],
            'dental': ['dentist', 'dental', 'orthodontic', 'teeth', 'oral health'],
            'contractor': ['contractor', 'construction', 'remodeling', 'renovation', 'building'],
            'landscaping': ['landscaping', 'lawn care', 'irrigation', 'landscape design'],
            'plumbing': ['plumber', 'plumbing', 'pipe', 'drain', 'water heater'],
            'hvac': ['hvac', 'heating', 'cooling', 'air conditioning', 'furnace'],
            'electrical': ['electrician', 'electrical', 'wiring', 'circuit'],
            'real_estate': ['real estate', 'realtor', 'property', 'homes for sale'],
            'accounting': ['accountant', 'accounting', 'cpa', 'tax', 'bookkeeping'],
            'insurance': ['insurance', 'coverage', 'policy', 'claims'],
            'auto_repair': ['auto repair', 'mechanic', 'car service', 'vehicle'],
            'salon': ['salon', 'hair', 'beauty', 'spa', 'barber'],
            'fitness': ['gym', 'fitness', 'personal training', 'workout'],
            'retail': ['shop', 'store', 'retail', 'buy online', 'products'],
            'agency': ['agency', 'marketing', 'advertising', 'creative', 'digital'],
            'saas': ['software', 'platform', 'saas', 'cloud', 'api', 'subscription']
        }
        
        # Count keyword matches
        matches = {}
        for biz_type, keywords in types.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                matches[biz_type] = count
        
        # Return type with most matches
        if matches:
            return max(matches, key=matches.get)
        
        return 'general_business'

    def _extract_phone(self, soup: BeautifulSoup, raw_html: str = None) -> List[str]:
        """Extract phone numbers"""
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

    def _extract_emails(self, soup: BeautifulSoup) -> List[str]:
        """Extract all email addresses (including owner emails)"""
        emails = set()
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Check mailto links
        for link in soup.find_all('a', href=re.compile(r'mailto:', re.I)):
            match = re.search(pattern, link.get('href', ''))
            if match:
                emails.add(match.group(0))
        
        # Check page text
        for match in re.finditer(pattern, soup.get_text()):
            email = match.group(0)
            # Filter out common non-contact emails
            if not any(x in email.lower() for x in ['example.com', 'domain.com', 'email.com']):
                emails.add(email)
        
        return sorted(list(emails))[:10]

    def _extract_owner_info(self, soup: BeautifulSoup, page_text: str) -> Dict:
        """
        Extract owner/decision-maker contact information
        
        Looks for:
        - Owner names (CEO, Founder, Owner, President)
        - Direct contact info
        - LinkedIn profiles
        """
        owner_info = {
            'names': [],
            'titles': [],
            'emails': [],
            'linkedin': [],
            'phones': []
        }
        
        # Common owner/decision-maker titles
        title_patterns = [
            r'(?:CEO|Chief Executive Officer)[\s:]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(?:Founder|Co-Founder)[\s:]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(?:Owner|Business Owner)[\s:]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(?:President)[\s:]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(?:Managing Director)[\s:]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)[\s,]+(?:CEO|Founder|Owner|President)'
        ]
        
        # Search for owner names and titles
        for pattern in title_patterns:
            matches = re.findall(pattern, page_text)
            for match in matches:
                if match and len(match) > 3:
                    owner_info['names'].append(match.strip())
        
        # Look for "About" or "Team" pages
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            if any(x in href or x in text for x in ['about', 'team', 'leadership', 'founder']):
                owner_info['about_page'] = link.get('href')
                break
        
        # Extract LinkedIn profiles
        for link in soup.find_all('a', href=re.compile(r'linkedin\.com', re.I)):
            linkedin_url = link.get('href')
            if '/in/' in linkedin_url:  # Personal profile
                owner_info['linkedin'].append(linkedin_url)
        
        # Look for owner-specific emails (common patterns)
        all_emails = self._extract_emails(soup)
        owner_email_patterns = ['owner@', 'ceo@', 'founder@', 'president@', 'contact@']
        for email in all_emails:
            if any(pattern in email.lower() for pattern in owner_email_patterns):
                owner_info['emails'].append(email)
        
        # Remove duplicates
        owner_info['names'] = list(set(owner_info['names']))[:5]
        owner_info['linkedin'] = list(set(owner_info['linkedin']))[:5]
        owner_info['emails'] = list(set(owner_info['emails']))[:5]
        
        return owner_info

    def _extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract business address"""
        # Try multiple methods
        for elem in [
            soup.find('address'),
            soup.find(class_=re.compile('address|location', re.I)),
            soup.find(itemprop='address')
        ]:
            if elem:
                addr = elem.get_text().strip()
                if len(addr) > 10:
                    return addr[:300]
        
        # Look for structured data
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'address' in data:
                    addr = data['address']
                    if isinstance(addr, dict):
                        return f"{addr.get('streetAddress', '')}, {addr.get('addressLocality', '')}, {addr.get('addressRegion', '')} {addr.get('postalCode', '')}"
            except:
                pass
        
        return None

    def _extract_hours(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract business hours"""
        for elem in soup.find_all(class_=re.compile('hours|schedule|open', re.I)):
            text = elem.get_text()
            if text and len(text) > 10:
                return {'raw': text.strip()[:500]}
        return None

    def _extract_services(self, soup: BeautifulSoup, page_text: str) -> List[str]:
        """Extract services offered"""
        services = []
        
        # Look for services section
        for elem in soup.find_all(['div', 'section'], class_=re.compile('service|offering|what-we-do', re.I)):
            # Extract list items or headings
            for item in elem.find_all(['li', 'h3', 'h4']):
                service = item.get_text().strip()
                if 5 < len(service) < 100:
                    services.append(service)
        
        return services[:15]

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract business description"""
        # Try meta description first
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content')[:500]
        
        # Try og:description
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc.get('content')[:500]
        
        # Try first paragraph
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 50:
                return text[:500]
        
        return None

    def _extract_social_media(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media profiles"""
        social = {}
        
        platforms = {
            'facebook': r'facebook\.com',
            'twitter': r'twitter\.com|x\.com',
            'instagram': r'instagram\.com',
            'linkedin': r'linkedin\.com/company',
            'youtube': r'youtube\.com',
            'tiktok': r'tiktok\.com'
        }
        
        for platform, pattern in platforms.items():
            for link in soup.find_all('a', href=re.compile(pattern, re.I)):
                social[platform] = link.get('href')
                break
        
        return social

    def scrape_multiple_businesses(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple businesses"""
        results = []
        for url in urls:
            try:
                result = self.scrape_business(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                results.append({
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
        return results


# Test
if __name__ == "__main__":
    scraper = UniversalBusinessScraper()
    
    # Test on different business types
    test_urls = [
        "https://www.example-restaurant.com",
        "https://www.example-law-firm.com",
        "https://www.example-contractor.com",
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)
        
        result = scraper.scrape_business(url)
        
        print(json.dumps(result, indent=2))
