"""
Working Business Scraper - Actually Extracts Data
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import Dict, List
import logging
from dns_fix import configure_dns_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkingBusinessScraper:
    """
    Scraper that actually extracts data from websites
    """
    
    def __init__(self):
        self.session = configure_dns_session()
        self.timeout = 30
        
    def scrape_business(self, url: str, business_type: str = None) -> Dict:
        """
        Scrape business data from website
        """
        logger.info(f"Scraping: {url}")
        
        result = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'business_name': None,
            'phone': [],
            'email': [],
            'social_media': {},
            'address': [],
            'description': None,
            'business_owner_name': None,
            'key_decision_makers': [],
            'services': [],
            'data_completeness_score': 0
        }
        
        try:
            # Get page content
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract business name
            result['business_name'] = self._extract_business_name(soup, url)
            
            # Extract phone numbers
            result['phone'] = self._extract_phones(soup, response.text)
            
            # Extract emails
            result['email'] = self._extract_emails(soup, response.text)
            
            # Extract social media
            result['social_media'] = self._extract_social_media(soup)
            
            # Extract address
            result['address'] = self._extract_addresses(soup, response.text)
            
            # Extract description
            result['description'] = self._extract_description(soup)
            
            # Calculate completeness
            result['data_completeness_score'] = self._calculate_completeness(result)
            
            logger.info(f"Extraction complete: {result['data_completeness_score']}% complete")
            logger.info(f"Found: {len(result['phone'])} phones, {len(result['email'])} emails")
            
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            result['error'] = str(e)
            
        return result
    
    def _extract_business_name(self, soup: BeautifulSoup, url: str) -> str:
        """Extract business name"""
        # Try title tag
        if soup.title:
            return soup.title.string.strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        # Use domain name
        domain = urlparse(url).netloc
        return domain.replace('www.', '').replace('.com', '').title()
    
    def _extract_phones(self, soup: BeautifulSoup, text: str) -> List[str]:
        """Extract ALL phone numbers - CRITICAL for voice dialer"""
        phones = set()
        
        # Invalid phone patterns to exclude
        invalid_patterns = [
            r'^(000|111|222|333|444|555|666|777|888|999)',  # Repeated digits
            r'^(123|234|345|456|567|678|789)',  # Sequential
            r'(\d)\1{6,}',  # Same digit repeated 7+ times
        ]
        
        def is_valid_phone(area, prefix, line):
            """Validate phone number components"""
            # Area code must be 2-9 for first digit
            if area[0] in ['0', '1']:
                return False
            
            # Prefix must be 2-9 for first digit  
            if prefix[0] in ['0', '1']:
                return False
            
            # Check for invalid patterns
            full_number = area + prefix + line
            for pattern in invalid_patterns:
                if re.match(pattern, full_number):
                    return False
            
            # Check if all same digit
            if len(set(full_number)) == 1:
                return False
            
            return True
        
        # Priority 1: tel: links (most reliable)
        for link in soup.find_all('a', href=re.compile(r'^tel:')):
            phone = link['href'].replace('tel:', '').replace('+1', '').strip()
            clean = re.sub(r'[^\d]', '', phone)
            if len(clean) == 10:
                area, prefix, line = clean[:3], clean[3:6], clean[6:]
                if is_valid_phone(area, prefix, line):
                    formatted = f"({area}) {prefix}-{line}"  
                    phones.add(formatted)
        
        # Priority 2: Search entire page HTML for phone patterns
        patterns = [
            r'\(?([2-9]\d{2})\)?[\s.-]?([2-9]\d{2})[\s.-]?(\d{4})',
            r'([2-9]\d{2})\.([2-9]\d{2})\.(\d{4})',
            r'\+?1?[\s.-]?\(?([2-9]\d{2})\)?[\s.-]?([2-9]\d{2})[\s.-]?(\d{4})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 3:
                    area, prefix, line = match[0], match[1], match[2]
                    if is_valid_phone(area, prefix, line):
                        formatted = f"({area}) {prefix}-{line}"
                        phones.add(formatted)
        
        # Priority 3: Look in common contact areas
        contact_selectors = [
            'footer', 'header', '.contact', '#contact', '.phone', '#phone',
            '[class*="contact"]', '[id*="contact"]', '[class*="phone"]',
            '[href^="tel:"]', '.footer', '#footer'
        ]
        
        for selector in contact_selectors:
            try:
                elements = soup.select(selector)
                for elem in elements:
                    elem_text = elem.get_text()
                    for pattern in patterns:
                        matches = re.findall(pattern, elem_text)
                        for match in matches:
                            if len(match) == 3:
                                area, prefix, line = match[0], match[1], match[2]
                                if is_valid_phone(area, prefix, line):
                                    formatted = f"({area}) {prefix}-{line}"
                                    phones.add(formatted)
            except:
                continue
        
        # Return ALL unique valid phone numbers found
        return list(phones)
    
    def _extract_emails(self, soup: BeautifulSoup, text: str) -> List[str]:
        """Extract email addresses"""
        emails = set()
        
        # Priority 1: mailto: links (most reliable)
        for link in soup.find_all('a', href=re.compile(r'^mailto:')):
            email = link['href'].replace('mailto:', '').strip().split('?')[0]
            if '@' in email and '.' in email.split('@')[1]:
                emails.add(email.lower())
        
        # Priority 2: Email pattern in visible text
        # Remove script/style tags first
        for script in soup(['script', 'style', 'noscript']):
            script.decompose()
        
        visible_text = soup.get_text()
        
        # Email regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, visible_text)
        
        # Filter out false positives
        invalid_patterns = [
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp',  # Image files
            'example.com', 'domain.com', 'email.com', 'test.com',  # Test domains
            'wixpress.com', 'sentry.io', 'cloudflare.com',  # Service domains
            '@2x', '@3x',  # Retina image naming
        ]
        
        for match in matches:
            # Skip if contains invalid patterns
            if any(pattern in match.lower() for pattern in invalid_patterns):
                continue
            
            # Must have valid TLD
            if '.' in match.split('@')[1]:
                emails.add(match.lower())
        
        return list(emails)
    
    def _extract_social_media(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links"""
        social = {}
        
        social_patterns = {
            'facebook': r'facebook\.com/[^/\s"\']+',
            'linkedin': r'linkedin\.com/(company|in)/[^/\s"\']+',
            'twitter': r'(twitter\.com|x\.com)/[^/\s"\']+',
            'instagram': r'instagram\.com/[^/\s"\']+',
            'youtube': r'youtube\.com/(channel|c|user)/[^/\s"\']+',
            'tiktok': r'tiktok\.com/@[^/\s"\']+',
        }
        
        # Check all links
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            
            for platform, pattern in social_patterns.items():
                if platform in href or pattern.split('\\.')[0] in href:
                    match = re.search(pattern, href)
                    if match:
                        full_url = match.group(0)
                        if not full_url.startswith('http'):
                            full_url = 'https://' + full_url
                        social[platform] = full_url
        
        return social
    
    def _extract_addresses(self, soup: BeautifulSoup, text: str) -> List[str]:
        """Extract physical addresses"""
        addresses = []
        
        # Look for address schema markup
        for elem in soup.find_all(attrs={"itemprop": "address"}):
            addr = elem.get_text().strip()
            if addr:
                addresses.append(addr)
        
        # Look for common address patterns
        address_pattern = r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way)[,\s]+[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}'
        matches = re.findall(address_pattern, text)
        addresses.extend(matches)
        
        return list(set(addresses))
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract business description"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try og:description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # Try first paragraph
        p = soup.find('p')
        if p:
            text = p.get_text().strip()
            if len(text) > 50:
                return text[:300]
        
        return None
    
    def _calculate_completeness(self, result: Dict) -> int:
        """Calculate data completeness percentage"""
        score = 0
        total = 7
        
        if result.get('business_name'):
            score += 1
        if result.get('phone'):
            score += 1
        if result.get('email'):
            score += 1
        if result.get('social_media'):
            score += 1
        if result.get('address'):
            score += 1
        if result.get('description'):
            score += 1
        if result.get('business_owner_name'):
            score += 1
        
        return int((score / total) * 100)
