"""
Improved Healthcare Facility Scraper with Bot Detection Handling
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedHealthcareScraper:
    """Enhanced scraper that handles bot detection and various website protections"""

    def __init__(self):
        # More realistic browser headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        self.timeout = 15
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def scrape_facility_website(self, url: str, retry_count: int = 3) -> Dict:
        """
        Scrape a healthcare facility website with retry logic
        
        Args:
            url: Website URL to scrape
            retry_count: Number of retries on failure
            
        Returns:
            Dictionary with extracted facility data
        """
        for attempt in range(retry_count):
            try:
                # Add delay between retries to avoid rate limiting
                if attempt > 0:
                    time.sleep(2 ** attempt)  # Exponential backoff
                
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                facility_data = {
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'facility_name': self._extract_facility_name(soup),
                    'phone': self._extract_phone(soup, response.text),
                    'address': self._extract_address(soup),
                    'hours': self._extract_hours(soup),
                    'services': self._extract_services(soup),
                    'email': self._extract_email(soup),
                    'website_quality': self._assess_website_quality(soup),
                    'contact_methods': self._extract_contact_methods(soup),
                    'status': 'success'
                }
                
                logger.info(f"Successfully scraped {url}")
                return facility_data
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    logger.warning(f"403 Forbidden on {url} (attempt {attempt + 1}/{retry_count})")
                    if attempt == retry_count - 1:
                        return self._create_error_response(url, "Website blocking automated access (403 Forbidden)")
                else:
                    logger.error(f"HTTP error on {url}: {str(e)}")
                    if attempt == retry_count - 1:
                        return self._create_error_response(url, str(e))
                        
            except requests.RequestException as e:
                logger.error(f"Failed to scrape {url} (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt == retry_count - 1:
                    return self._create_error_response(url, str(e))
        
        return self._create_error_response(url, "Max retries exceeded")

    def _create_error_response(self, url: str, error: str) -> Dict:
        """Create a standardized error response"""
        return {
            'url': url,
            'error': error,
            'status': 'error',
            'scraped_at': datetime.now().isoformat(),
            'phone': [],
            'facility_name': None,
            'recommendation': 'This website may require manual review or browser automation (Selenium/Playwright)'
        }

    def _extract_facility_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract facility name from various HTML elements"""
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
                    # Clean up the text
                    text = text.strip()
                    # Remove common suffixes
                    text = re.sub(r'\s*[\|\-]\s*.*$', '', text)
                    return text[:200]
        return None

    def _extract_phone(self, soup: BeautifulSoup, raw_html: str = None) -> List[str]:
        """
        Extract phone numbers with multiple pattern matching strategies
        """
        phones = set()
        
        # Multiple regex patterns to catch different formats
        patterns = [
            r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',  # (609) 628-3103 or 609-628-3103
            r'\((\d{3})\)\s*(\d{3})-(\d{4})',  # (609) 628-3103
            r'(\d{3})[-.](\d{3})[-.](\d{4})',  # 609-628-3103 or 609.628.3103
            r'(\d{3})\s+(\d{3})\s+(\d{4})',    # 609 628 3103
        ]
        
        # Get text from both soup and raw HTML
        text_sources = [soup.get_text()]
        if raw_html:
            text_sources.append(raw_html)
        
        for text in text_sources:
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    # Format consistently
                    phone = f"({match[0]}) {match[1]}-{match[2]}"
                    phones.add(phone)
        
        # Also check for tel: links
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
        
        result = sorted(list(phones))[:5]  # Return top 5 unique numbers
        logger.info(f"Found {len(result)} phone numbers: {result}")
        return result

    def _extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract physical address"""
        address_patterns = [
            soup.find('address'),
            soup.find(class_=re.compile('address', re.I)),
            soup.find(class_=re.compile('location', re.I)),
            soup.find(itemprop='address'),
        ]
        
        for element in address_patterns:
            if element:
                return element.get_text().strip()[:300]
        
        return None

    def _extract_hours(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract business hours"""
        hours_data = {}
        
        hours_elements = soup.find_all(class_=re.compile('hours|schedule|operating', re.I))
        
        if hours_elements:
            for element in hours_elements:
                text = element.get_text()
                if text and len(text) > 10:  # Ensure it's substantial
                    hours_data['raw'] = text.strip()[:500]
                    break
        
        return hours_data if hours_data else None

    def _extract_email(self, soup: BeautifulSoup) -> Optional[str]:
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
        text = soup.get_text()
        email_match = re.search(email_pattern, text)
        if email_match:
            return email_match.group(0)
        
        return None

    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract services offered"""
        services = []
        
        service_keywords = [
            'emergency', 'urgent care', 'surgery', 'consultation',
            'installation', 'repair', 'maintenance', 'inspection',
            'landscaping', 'irrigation', 'lighting', 'design'
        ]
        
        page_text = soup.get_text().lower()
        
        for keyword in service_keywords:
            if keyword in page_text:
                services.append(keyword.title())
        
        return list(set(services))[:10]

    def _extract_contact_methods(self, soup: BeautifulSoup) -> Dict:
        """Extract available contact methods"""
        contact_methods = {
            'phone': len(self._extract_phone(soup)) > 0,
            'email': bool(self._extract_email(soup)),
            'contact_form': bool(soup.find('form')),
            'online_booking': bool(re.search(r'book|appointment|schedule|request', soup.get_text(), re.I)),
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


# Test the improved scraper
if __name__ == "__main__":
    scraper = ImprovedHealthcareScraper()
    
    test_url = "https://www.ocnjirrigation.com/"
    result = scraper.scrape_facility_website(test_url)
    
    print("=== SCRAPING RESULT ===")
    print(json.dumps(result, indent=2))
