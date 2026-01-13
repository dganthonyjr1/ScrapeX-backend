"""
Universal Business Scraper - Production Version
Extracts publicly available business information from any website
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import Dict, List, Optional
import logging
from openai import OpenAI
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniversalBusinessScraper:
    """
    Universal scraper that extracts publicly available business information
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = 15
        
    def scrape_business(self, url: str, business_type: Optional[str] = None) -> Dict:
        """
        Scrape publicly available business information from a website
        
        DISCLAIMER: Extracts only publicly available data. Results depend on what
        businesses publicly display. No guarantee of completeness.
        
        Args:
            url: Business website URL
            business_type: Optional business type hint
            
        Returns:
            Dict with publicly available business data
        """
        logger.info(f"Starting extraction for: {url}")
        
        # Initialize result
        result = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'scraping_method': 'enhanced_multi_page',
            'status': 'success',
            'disclaimer': 'Contains only publicly available information. Completeness depends on website content.',
            'business_name': None,
            'business_type': business_type,
            'phone': [],
            'email': [],
            'address': [],
            'website': url,
            'description': None,
            'services': [],
            'social_media': {},
            'business_owner_name': None,
            'business_owner_title': None,
            'key_decision_makers': [],
            'employee_count': None,
            'employee_range': None,
            'industries': [],
            'revenue_opportunities': {},
            'missing_services': [],
            'technology_gaps': [],
            'competitive_weaknesses': [],
            'ideal_solution': None,
            'urgency_score': None,
            'extraction_methods_used': [],
            'data_completeness_score': 0
        }
        
        try:
            # Step 1: Extract from main page
            main_data = self._extract_from_page(url)
            self._merge_data(result, main_data)
            result['extraction_methods_used'].append('main_page_scraping')
            
            # Step 2: If missing critical data, crawl related pages
            if len(result['email']) == 0 or not result['business_owner_name']:
                logger.info("Missing critical data, crawling related pages...")
                important_pages = self._find_important_pages(url)
                
                for page_url in important_pages[:5]:  # Limit to 5 pages
                    logger.info(f"Crawling: {page_url}")
                    page_data = self._extract_from_page(page_url)
                    self._merge_data(result, page_data)
                
                result['extraction_methods_used'].append('multi_page_crawling')
            
            # Step 3: LinkedIn enrichment (if available)
            linkedin_data = self._get_linkedin_data(url, result.get('business_name'))
            if linkedin_data:
                self._merge_data(result, linkedin_data)
                result['extraction_methods_used'].append('linkedin_api')
            
            # Step 4: AI analysis
            ai_analysis = self._ai_analyze(result)
            if ai_analysis:
                result.update(ai_analysis)
                result['extraction_methods_used'].append('ai_analysis')
            
            # Step 5: Revenue opportunity analysis
            revenue_ops = self._analyze_revenue_opportunities(result)
            result['revenue_opportunities'] = revenue_ops
            result['extraction_methods_used'].append('revenue_analysis')
            
            # Calculate completeness
            result['data_completeness_score'] = self._calculate_completeness(result)
            
            logger.info(f"Extraction complete. Data completeness: {result['data_completeness_score']}%")
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
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
                    'status': 'failed',
                    'error': str(e)
                })
        return results
    
    def _extract_from_page(self, url: str) -> Dict:
        """Extract data from a specific page"""
        data = {
            'business_name': None,
            'phone': [],
            'email': [],
            'address': [],
            'description': None,
            'services': [],
            'social_media': {},
            'executives': []
        }
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # Business name
            if not data['business_name']:
                title = soup.find('title')
                if title:
                    data['business_name'] = title.get_text().split('|')[0].split('-')[0].strip()
            
            # Phone numbers
            phone_pattern = r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            for match in re.finditer(phone_pattern, page_text):
                phone = match.group(0)
                if len(phone) >= 10:
                    data['phone'].append(phone)
            
            # Remove duplicates
            data['phone'] = list(set(data['phone']))[:5]
            
            # Email addresses
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
            
            # Remove duplicates
            data['email'] = list(set(data['email']))[:5]
            
            # Social media
            social_patterns = {
                'facebook': r'facebook\.com/[\w.-]+',
                'twitter': r'twitter\.com/[\w.-]+',
                'linkedin': r'linkedin\.com/(company|in)/[\w.-]+',
                'instagram': r'instagram\.com/[\w.-]+'
            }
            
            for platform, pattern in social_patterns.items():
                match = re.search(pattern, page_text, re.I)
                if match:
                    data['social_media'][platform] = 'https://' + match.group(0)
            
            # Description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                data['description'] = meta_desc.get('content', '')[:500]
            
            # Executives
            exec_patterns = [
                r'([A-Z][a-z]+ [A-Z][a-z]+)\s*[-–—,]\s*(CEO|President|Founder|Director|VP|Vice President|Chief|Executive)',
            ]
            
            for pattern in exec_patterns:
                for match in re.finditer(pattern, page_text, re.I):
                    if len(match.groups()) >= 2:
                        name = match.group(1).strip()
                        title = match.group(2).strip()
                        data['executives'].append(f"{name} - {title}")
            
        except Exception as e:
            logger.warning(f"Error extracting from {url}: {e}")
        
        return data
    
    def _find_important_pages(self, base_url: str) -> List[str]:
        """Find contact, team, and services pages"""
        important_pages = []
        
        try:
            response = self.session.get(base_url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            keywords = {
                'contact': ['contact', 'get-in-touch', 'reach-us'],
                'team': ['team', 'about', 'leadership', 'staff', 'executives', 'meet-the-team'],
                'services': ['services', 'what-we-do', 'offerings', 'programs']
            }
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                for category, terms in keywords.items():
                    if any(term in href or term in text for term in terms):
                        full_url = urljoin(base_url, link['href'])
                        if full_url not in important_pages and urlparse(full_url).netloc == urlparse(base_url).netloc:
                            important_pages.append(full_url)
                            break
        
        except Exception as e:
            logger.warning(f"Error finding important pages: {e}")
        
        return important_pages
    
    def _get_linkedin_data(self, url: str, business_name: Optional[str]) -> Optional[Dict]:
        """Get LinkedIn company data (mock for now)"""
        # This would integrate with LinkedIn API in production
        return None
    
    def _ai_analyze(self, data: Dict) -> Dict:
        """AI analysis of business data"""
        try:
            client = OpenAI()
            
            prompt = f"""Analyze this business data and provide insights in JSON format:

Business: {data.get('business_name')}
Description: {data.get('description')}
Services: {data.get('services')}
Website: {data.get('url')}

Provide:
1. missing_services: List of 5 services they could offer
2. technology_gaps: List of 5 technology improvements needed
3. competitive_weaknesses: List of 5 competitive weaknesses
4. ideal_solution: One sentence describing ideal solution
5. urgency_score: Number 1-10 for urgency

Return only valid JSON."""
            
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return {}
    
    def _analyze_revenue_opportunities(self, data: Dict) -> Dict:
        """Analyze revenue opportunities"""
        opportunities = []
        total_loss = 0
        
        # Missing email
        if len(data.get('email', [])) == 0:
            opportunities.append({
                'type': 'missing_contact',
                'description': 'No email contact - missing online inquiries',
                'estimated_loss': 300
            })
            total_loss += 300
        
        # Missing services
        for service in data.get('missing_services', [])[:5]:
            opportunities.append({
                'type': 'missing_service',
                'description': f'Not offering: {service}',
                'estimated_loss': 500
            })
            total_loss += 500
        
        return {
            'total_opportunities_found': len(opportunities),
            'estimated_monthly_revenue_loss': total_loss,
            'opportunities': opportunities
        }
    
    def _merge_data(self, target: Dict, source: Dict):
        """Merge source data into target"""
        for key, value in source.items():
            if key in ['phone', 'email', 'address', 'services', 'executives']:
                if isinstance(value, list):
                    target.setdefault(key, []).extend(value)
                    target[key] = list(set(target[key]))[:15]
            elif key == 'social_media' and isinstance(value, dict):
                target.setdefault(key, {}).update(value)
            elif key == 'executives' and value:
                target.setdefault('key_decision_makers', []).extend(value)
                if not target.get('business_owner_name') and value:
                    first_exec = value[0]
                    if 'CEO' in first_exec or 'President' in first_exec or 'Founder' in first_exec:
                        parts = first_exec.split('-')
                        if len(parts) >= 2:
                            target['business_owner_name'] = parts[0].strip()
                            target['business_owner_title'] = parts[1].strip()
            elif not target.get(key) and value:
                target[key] = value
    
    def _calculate_completeness(self, data: Dict) -> int:
        """Calculate data completeness percentage"""
        fields = {
            'business_name': 10,
            'phone': 15,
            'email': 15,
            'description': 10,
            'services': 10,
            'social_media': 10,
            'business_owner_name': 15,
            'revenue_opportunities': 15
        }
        
        score = 0
        for field, weight in fields.items():
            value = data.get(field)
            if value:
                if isinstance(value, (list, dict)):
                    if len(value) > 0:
                        score += weight
                else:
                    score += weight
        
        return score
