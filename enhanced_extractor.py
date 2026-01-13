"""
Enhanced Business Extractor - Crawls multiple pages for complete data
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from complete_business_extractor import CompleteBusinessExtractor
import logging

logger = logging.getLogger(__name__)


class EnhancedBusinessExtractor(CompleteBusinessExtractor):
    """
    Enhanced extractor that crawls multiple pages to find:
    - Contact page for emails
    - Team/About page for executives
    - Services page for offerings
    """
    
    def extract_complete_business_data(self, url: str, business_name=None):
        """Enhanced extraction with multi-page crawling"""
        logger.info(f"Starting enhanced extraction for: {url}")
        
        # Get base data
        result = super().extract_complete_business_data(url, business_name)
        
        # If missing critical data, crawl related pages
        if len(result.get('email', [])) == 0 or not result.get('business_owner_name'):
            logger.info("Missing critical data, crawling related pages...")
            
            # Find and crawl important pages
            important_pages = self._find_important_pages(url)
            
            for page_url in important_pages[:5]:  # Limit to 5 pages
                logger.info(f"Crawling: {page_url}")
                page_data = self._extract_from_page(page_url)
                
                # Merge emails
                if page_data.get('email'):
                    result.setdefault('email', []).extend(page_data['email'])
                    result['email'] = list(set(result['email']))[:5]
                
                # Add executives
                if page_data.get('executives'):
                    result.setdefault('key_decision_makers', []).extend(page_data['executives'])
                    if not result.get('business_owner_name') and page_data['executives']:
                        # First executive is likely the CEO/President
                        first_exec = page_data['executives'][0]
                        if 'CEO' in first_exec or 'President' in first_exec or 'Founder' in first_exec:
                            parts = first_exec.split('-')
                            if len(parts) >= 2:
                                result['business_owner_name'] = parts[0].strip()
                                result['business_owner_title'] = parts[1].strip()
                
                # Add services
                if page_data.get('services'):
                    result.setdefault('services', []).extend(page_data['services'])
                    result['services'] = list(set(result['services']))[:15]
        
        # Recalculate completeness
        result['data_completeness_score'] = self._calculate_completeness(result)
        
        return result
    
    def _find_important_pages(self, base_url: str):
        """Find contact, team, and services pages"""
        important_pages = []
        
        try:
            response = self.session.get(base_url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Keywords to look for in links
            keywords = {
                'contact': ['contact', 'get-in-touch', 'reach-us'],
                'team': ['team', 'about', 'leadership', 'staff', 'executives', 'meet-the-team'],
                'services': ['services', 'what-we-do', 'offerings', 'programs']
            }
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                # Check if link matches important keywords
                for category, terms in keywords.items():
                    if any(term in href or term in text for term in terms):
                        full_url = urljoin(base_url, link['href'])
                        if full_url not in important_pages and urlparse(full_url).netloc == urlparse(base_url).netloc:
                            important_pages.append(full_url)
                            logger.info(f"Found {category} page: {full_url}")
                            break
        
        except Exception as e:
            logger.warning(f"Error finding important pages: {e}")
        
        return important_pages
    
    def _extract_from_page(self, url: str):
        """Extract data from a specific page"""
        data = {
            'email': [],
            'executives': [],
            'services': []
        }
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # Extract emails
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            
            # Mailto links
            for link in soup.find_all('a', href=re.compile(r'mailto:', re.I)):
                match = re.search(email_pattern, link.get('href', ''))
                if match:
                    email = match.group(0)
                    if not any(x in email.lower() for x in ['example.com', 'test.com', 'domain.com']):
                        data['email'].append(email)
            
            # Text emails
            for match in re.finditer(email_pattern, page_text):
                email = match.group(0)
                if not any(x in email.lower() for x in ['example.com', 'test.com', 'domain.com', '.png', '.jpg']):
                    data['email'].append(email)
            
            # Extract executives/team members
            # Look for name + title patterns
            exec_patterns = [
                r'([A-Z][a-z]+ [A-Z][a-z]+)\s*[-–—,]\s*(CEO|President|Founder|Director|VP|Vice President|Chief|Executive|Manager|Head)',
                r'(CEO|President|Founder|Director|VP|Vice President|Chief|Executive|Manager|Head)\s*[-–—:]\s*([A-Z][a-z]+ [A-Z][a-z]+)'
            ]
            
            for pattern in exec_patterns:
                for match in re.finditer(pattern, page_text, re.I):
                    if len(match.groups()) >= 2:
                        name = match.group(1).strip()
                        title = match.group(2).strip()
                        # Swap if needed
                        if title and any(x in title for x in ['CEO', 'President', 'Director', 'Founder', 'Chief']):
                            data['executives'].append(f"{name} - {title}")
                        else:
                            data['executives'].append(f"{title} - {name}")
            
            # Look for team member cards/sections
            for elem in soup.find_all(['div', 'section'], class_=re.compile(r'team|staff|member|executive', re.I)):
                name_elem = elem.find(['h2', 'h3', 'h4', 'strong'])
                title_elem = elem.find(['p', 'span'], class_=re.compile(r'title|position|role', re.I))
                
                if name_elem and title_elem:
                    name = name_elem.get_text(strip=True)
                    title = title_elem.get_text(strip=True)
                    if len(name) < 50 and len(title) < 50:
                        data['executives'].append(f"{name} - {title}")
            
            # Extract services
            for heading in soup.find_all(['h2', 'h3'], string=re.compile(r'service|program|offering|what we (do|offer)', re.I)):
                parent = heading.find_parent(['div', 'section'])
                if parent:
                    items = parent.find_all(['li', 'p'])
                    for item in items[:15]:
                        service = item.get_text(strip=True)
                        if 10 < len(service) < 150:
                            data['services'].append(service)
            
        except Exception as e:
            logger.warning(f"Error extracting from {url}: {e}")
        
        return data


def test_enhanced():
    """Test enhanced extractor"""
    extractor = EnhancedBusinessExtractor()
    
    url = 'https://metroatlantachamber.com/'
    
    print("="*80)
    print("TESTING ENHANCED EXTRACTOR")
    print("="*80)
    
    result = extractor.extract_complete_business_data(url, business_name='Metro Atlanta Chamber')
    
    print(f"\n✓ Business: {result.get('business_name')}")
    print(f"✓ Phones: {len(result.get('phone', []))} found - {result.get('phone', [])}")
    print(f"✓ Emails: {len(result.get('email', []))} found - {result.get('email', [])}")
    print(f"✓ Owner: {result.get('business_owner_name')} ({result.get('business_owner_title')})")
    print(f"✓ Executives: {len(result.get('key_decision_makers', []))} found")
    for exec in result.get('key_decision_makers', [])[:5]:
        print(f"   - {exec}")
    print(f"✓ Services: {len(result.get('services', []))} found")
    for svc in result.get('services', [])[:5]:
        print(f"   - {svc}")
    print(f"✓ Revenue Loss: ${result.get('revenue_opportunities', {}).get('estimated_monthly_revenue_loss', 0):,}/month")
    print(f"✓ Data Completeness: {result.get('data_completeness_score')}%")
    
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    checks = {
        'Phones': len(result.get('phone', [])) > 0,
        'Emails': len(result.get('email', [])) > 0,
        'Owner': bool(result.get('business_owner_name')),
        'Executives': len(result.get('key_decision_makers', [])) > 0,
        'Services': len(result.get('services', [])) > 0,
        'Revenue Analysis': result.get('revenue_opportunities', {}).get('total_opportunities_found', 0) > 0
    }
    
    for check, passed in checks.items():
        print(f"{'✓' if passed else '✗'} {check}")
    
    passed = sum(checks.values())
    total = len(checks)
    print(f"\nResult: {passed}/{total} checks passed ({int(passed/total*100)}%)")
    
    if passed == total:
        print("\n🎉 ALL FEATURES WORKING 100%!")
    else:
        print(f"\n⚠️  {total-passed} features still need work")


if __name__ == '__main__':
    test_enhanced()
