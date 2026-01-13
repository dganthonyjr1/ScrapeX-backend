"""
Directory Scraper for ScrapeX
Extracts business listings from directories like Chamber of Commerce, tourism sites, etc.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DirectoryScraper:
    """
    Scrapes business directories to extract lists of businesses
    
    Supports:
    - Chamber of Commerce member directories
    - Tourism websites (hotels, restaurants, attractions)
    - Business association directories
    - Industry-specific directories
    - Yellow Pages style listings
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.timeout = 15

    def scrape_directory(self, directory_url: str, directory_type: Optional[str] = None) -> Dict:
        """
        Scrape a business directory page
        
        Args:
            directory_url: URL of the directory page
            directory_type: Optional type hint (chamber, tourism, association, etc.)
        
        Returns:
            Dict with list of businesses found
        """
        logger.info(f"Scraping directory: {directory_url}")
        
        # Step 1: Try HTTP (fast)
        http_result = self._try_http_scrape_directory(directory_url, directory_type)
        if http_result.get('status') == 'success' and len(http_result.get('businesses', [])) > 0:
            logger.info(f"HTTP scrape successful - found {len(http_result['businesses'])} businesses")
            return http_result
        
        # Step 2: Try browser automation
        if PLAYWRIGHT_AVAILABLE:
            logger.info("Trying browser automation for directory")
            browser_result = self._try_browser_scrape_directory(directory_url, directory_type)
            if browser_result.get('status') == 'success' and len(browser_result.get('businesses', [])) > 0:
                logger.info(f"Browser scrape successful - found {len(browser_result['businesses'])} businesses")
                return browser_result
        
        # Step 3: Failed to scrape
        logger.warning(f"Failed to scrape directory: {directory_url}")
        return {
            'directory_url': directory_url,
            'status': 'failed',
            'businesses': [],
            'message': 'Unable to extract business listings from this directory',
            'scraped_at': datetime.now().isoformat()
        }

    def _try_http_scrape_directory(self, directory_url: str, directory_type: Optional[str] = None) -> Dict:
        """HTTP scraping for directory pages"""
        try:
            response = self.session.get(directory_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract businesses from the directory
            businesses = self._extract_business_listings(soup, directory_url)
            
            # Try to find pagination and additional pages
            pagination_urls = self._extract_pagination_urls(soup, directory_url)
            
            return {
                'directory_url': directory_url,
                'directory_type': directory_type or self._detect_directory_type(soup),
                'scraped_at': datetime.now().isoformat(),
                'scraping_method': 'http_request',
                'businesses': businesses,
                'total_found': len(businesses),
                'pagination_urls': pagination_urls,
                'has_more_pages': len(pagination_urls) > 0,
                'status': 'success'
            }
            
        except Exception as e:
            logger.warning(f"HTTP directory scrape failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _try_browser_scrape_directory(self, directory_url: str, directory_type: Optional[str] = None) -> Dict:
        """Browser automation scraping for directory pages"""
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
                page.goto(directory_url, wait_until='load', timeout=20000)
                page.wait_for_timeout(3000)  # Wait for dynamic content
                
                # Scroll to load lazy-loaded content
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                
                # Get content
                content = page.content()
                
                browser.close()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract businesses
                businesses = self._extract_business_listings(soup, directory_url)
                pagination_urls = self._extract_pagination_urls(soup, directory_url)
                
                return {
                    'directory_url': directory_url,
                    'directory_type': directory_type or self._detect_directory_type(soup),
                    'scraped_at': datetime.now().isoformat(),
                    'scraping_method': 'browser_automation',
                    'businesses': businesses,
                    'total_found': len(businesses),
                    'pagination_urls': pagination_urls,
                    'has_more_pages': len(pagination_urls) > 0,
                    'status': 'success'
                }
                
        except Exception as e:
            logger.error(f"Browser directory scrape failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _extract_business_listings(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        Extract business listings from directory page
        
        Looks for common patterns:
        - Links to business websites
        - Business names
        - Phone numbers
        - Addresses
        - Categories
        """
        businesses = []
        seen_urls = set()
        
        # Strategy 1: Find structured listings (most directories use these)
        listing_containers = soup.find_all(['div', 'li', 'article'], class_=re.compile(
            r'member|business|listing|company|directory-item|result', re.I
        ))
        
        for container in listing_containers:
            business = self._extract_business_from_container(container, base_url)
            if business and business.get('website'):
                url = business['website']
                if url not in seen_urls:
                    businesses.append(business)
                    seen_urls.add(url)
        
        # Strategy 2: Find all links that look like business websites
        if len(businesses) < 5:  # Fallback if structured extraction didn't work
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # Skip navigation, social media, and internal links
                if self._is_business_link(href, text):
                    full_url = urljoin(base_url, href)
                    
                    if full_url not in seen_urls and self._is_external_url(full_url, base_url):
                        businesses.append({
                            'business_name': text[:200] if text else None,
                            'website': full_url,
                            'phone': None,
                            'address': None,
                            'category': None,
                            'source': 'link_extraction'
                        })
                        seen_urls.add(full_url)
        
        logger.info(f"Extracted {len(businesses)} business listings")
        return businesses[:500]  # Limit to prevent memory issues

    def _extract_business_from_container(self, container, base_url: str) -> Optional[Dict]:
        """Extract business data from a listing container"""
        business = {
            'business_name': None,
            'website': None,
            'phone': None,
            'address': None,
            'category': None,
            'source': 'structured_extraction'
        }
        
        # Extract business name
        name_elem = container.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'name|title|business', re.I))
        if not name_elem:
            name_elem = container.find(['h2', 'h3', 'h4'])
        if name_elem:
            business['business_name'] = name_elem.get_text().strip()[:200]
        
        # Extract website URL
        website_link = container.find('a', href=True, text=re.compile(r'website|visit|view', re.I))
        if not website_link:
            website_link = container.find('a', class_=re.compile(r'website|url|link', re.I))
        if not website_link:
            # Look for any external link
            for link in container.find_all('a', href=True):
                href = link.get('href')
                if self._is_external_url(urljoin(base_url, href), base_url):
                    website_link = link
                    break
        
        if website_link:
            business['website'] = urljoin(base_url, website_link.get('href'))
        
        # Extract phone
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, container.get_text())
        if phone_match:
            business['phone'] = phone_match.group(0)
        
        # Extract address
        address_elem = container.find(class_=re.compile(r'address|location', re.I))
        if address_elem:
            business['address'] = address_elem.get_text().strip()[:300]
        
        # Extract category
        category_elem = container.find(class_=re.compile(r'category|type|industry', re.I))
        if category_elem:
            business['category'] = category_elem.get_text().strip()[:100]
        
        # Only return if we have at least a name or website
        if business['business_name'] or business['website']:
            return business
        
        return None

    def _is_business_link(self, href: str, text: str) -> bool:
        """Check if a link is likely a business website"""
        # Skip common non-business links
        skip_patterns = [
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'youtube.com', 'pinterest.com', 'tiktok.com',
            'mailto:', 'tel:', 'javascript:', '#',
            '/login', '/register', '/about', '/contact', '/privacy', '/terms',
            '.pdf', '.jpg', '.png', '.gif'
        ]
        
        href_lower = href.lower()
        for pattern in skip_patterns:
            if pattern in href_lower:
                return False
        
        # Must have a domain
        if not re.search(r'https?://', href) and not href.startswith('www.'):
            return False
        
        return True

    def _is_external_url(self, url: str, base_url: str) -> bool:
        """Check if URL is external to the directory site"""
        try:
            url_domain = urlparse(url).netloc
            base_domain = urlparse(base_url).netloc
            return url_domain != base_domain and len(url_domain) > 0
        except:
            return False

    def _extract_pagination_urls(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract pagination URLs for additional pages"""
        pagination_urls = []
        
        # Look for pagination links
        pagination = soup.find(['div', 'nav', 'ul'], class_=re.compile(r'pag', re.I))
        if pagination:
            for link in pagination.find_all('a', href=True):
                href = link.get('href')
                if href and not href.startswith('#'):
                    full_url = urljoin(base_url, href)
                    if full_url not in pagination_urls and full_url != base_url:
                        pagination_urls.append(full_url)
        
        return pagination_urls[:20]  # Limit pagination

    def _detect_directory_type(self, soup: BeautifulSoup) -> str:
        """Auto-detect directory type from content"""
        text = soup.get_text().lower()
        
        if 'chamber of commerce' in text or 'chamber' in text:
            return 'chamber_of_commerce'
        elif 'tourism' in text or 'visitor' in text or 'travel' in text:
            return 'tourism'
        elif 'association' in text or 'member' in text:
            return 'association'
        elif 'yellow pages' in text or 'business directory' in text:
            return 'yellow_pages'
        else:
            return 'general_directory'

    def scrape_multiple_pages(self, directory_url: str, max_pages: int = 10) -> Dict:
        """
        Scrape a directory with pagination
        
        Args:
            directory_url: Starting directory URL
            max_pages: Maximum number of pages to scrape
            
        Returns:
            Combined results from all pages
        """
        all_businesses = []
        seen_urls = set()
        pages_scraped = 0
        
        # Scrape first page
        result = self.scrape_directory(directory_url)
        if result.get('status') == 'success':
            for business in result.get('businesses', []):
                url = business.get('website')
                if url and url not in seen_urls:
                    all_businesses.append(business)
                    seen_urls.add(url)
            pages_scraped += 1
            
            # Scrape additional pages
            pagination_urls = result.get('pagination_urls', [])
            for page_url in pagination_urls[:max_pages-1]:
                logger.info(f"Scraping page {pages_scraped + 1}: {page_url}")
                page_result = self.scrape_directory(page_url)
                
                if page_result.get('status') == 'success':
                    for business in page_result.get('businesses', []):
                        url = business.get('website')
                        if url and url not in seen_urls:
                            all_businesses.append(business)
                            seen_urls.add(url)
                    pages_scraped += 1
        
        return {
            'directory_url': directory_url,
            'pages_scraped': pages_scraped,
            'total_businesses': len(all_businesses),
            'businesses': all_businesses,
            'scraped_at': datetime.now().isoformat(),
            'status': 'success'
        }


# Test
if __name__ == "__main__":
    scraper = DirectoryScraper()
    
    # Test on a sample directory
    test_url = "https://example-chamber.com/members"
    
    print(f"Testing directory scraper on: {test_url}")
    result = scraper.scrape_directory(test_url)
    
    print(json.dumps(result, indent=2))
    print(f"\nFound {len(result.get('businesses', []))} businesses")
