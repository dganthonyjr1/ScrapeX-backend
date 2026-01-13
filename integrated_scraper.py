"""
Integrated Scraping Pipeline for ScrapeX
Combines directory scraping with individual business scraping
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from directory_scraper import DirectoryScraper
from universal_scraper import UniversalBusinessScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedScrapingPipeline:
    """
    Complete scraping pipeline:
    1. Scrape directory to get list of businesses
    2. Scrape each individual business for detailed info
    3. Return comprehensive dataset ready for AI calling
    """

    def __init__(self, max_workers: int = 5):
        """
        Initialize pipeline
        
        Args:
            max_workers: Number of parallel workers for business scraping
        """
        self.directory_scraper = DirectoryScraper()
        self.business_scraper = UniversalBusinessScraper()
        self.max_workers = max_workers

    def scrape_directory_and_businesses(self, directory_url: str, 
                                       max_businesses: Optional[int] = None,
                                       max_pages: int = 10) -> Dict:
        """
        Complete pipeline: scrape directory, then scrape each business
        
        Args:
            directory_url: URL of business directory
            max_businesses: Optional limit on number of businesses to scrape
            max_pages: Maximum directory pages to scrape
            
        Returns:
            Dict with directory info and detailed business data
        """
        logger.info(f"Starting integrated scraping pipeline for: {directory_url}")
        
        # Step 1: Scrape directory to get business list
        logger.info("Step 1: Scraping directory for business listings...")
        directory_result = self.directory_scraper.scrape_multiple_pages(
            directory_url, 
            max_pages=max_pages
        )
        
        if directory_result.get('status') != 'success':
            return {
                'status': 'failed',
                'error': 'Failed to scrape directory',
                'directory_url': directory_url
            }
        
        businesses_from_directory = directory_result.get('businesses', [])
        logger.info(f"Found {len(businesses_from_directory)} businesses in directory")
        
        # Limit if requested
        if max_businesses:
            businesses_from_directory = businesses_from_directory[:max_businesses]
            logger.info(f"Limited to {max_businesses} businesses")
        
        # Step 2: Scrape each individual business
        logger.info("Step 2: Scraping individual businesses for detailed info...")
        detailed_businesses = self._scrape_businesses_parallel(businesses_from_directory)
        
        # Step 3: Combine and return results
        return {
            'status': 'success',
            'directory_url': directory_url,
            'directory_type': directory_result.get('directory_type'),
            'pages_scraped': directory_result.get('pages_scraped'),
            'total_businesses_found': len(businesses_from_directory),
            'businesses_scraped': len(detailed_businesses),
            'businesses': detailed_businesses,
            'scraped_at': datetime.now().isoformat(),
            'summary': self._generate_summary(detailed_businesses)
        }

    def _scrape_businesses_parallel(self, business_list: List[Dict]) -> List[Dict]:
        """
        Scrape multiple businesses in parallel
        
        Args:
            business_list: List of businesses from directory
            
        Returns:
            List of detailed business data
        """
        detailed_businesses = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scraping tasks
            future_to_business = {
                executor.submit(
                    self._scrape_single_business, 
                    business
                ): business 
                for business in business_list
            }
            
            # Collect results as they complete
            for i, future in enumerate(as_completed(future_to_business), 1):
                try:
                    result = future.result()
                    if result and result.get('status') == 'success':
                        detailed_businesses.append(result)
                        logger.info(f"Progress: {i}/{len(business_list)} - Scraped: {result.get('business_name')}")
                    else:
                        logger.warning(f"Progress: {i}/{len(business_list)} - Failed to scrape business")
                except Exception as e:
                    logger.error(f"Error scraping business: {e}")
        
        return detailed_businesses

    def _scrape_single_business(self, directory_business: Dict) -> Optional[Dict]:
        """
        Scrape a single business and combine with directory data
        
        Args:
            directory_business: Business data from directory
            
        Returns:
            Combined business data
        """
        website = directory_business.get('website')
        if not website:
            return None
        
        try:
            # Scrape the business website
            detailed_data = self.business_scraper.scrape_business(
                website,
                business_type=directory_business.get('category')
            )
            
            # Combine directory data with scraped data
            if detailed_data.get('status') == 'success':
                # Merge data, preferring scraped data but keeping directory data as fallback
                combined = {
                    **directory_business,  # Start with directory data
                    **detailed_data,  # Override with scraped data
                    'directory_listing': directory_business,  # Keep original directory data
                }
                
                # If business name wasn't found, use directory name
                if not combined.get('business_name'):
                    combined['business_name'] = directory_business.get('business_name')
                
                return combined
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to scrape {website}: {e}")
            return None

    def _generate_summary(self, businesses: List[Dict]) -> Dict:
        """Generate summary statistics"""
        if not businesses:
            return {}
        
        # Count businesses by type
        business_types = {}
        businesses_with_owner_info = 0
        businesses_with_email = 0
        businesses_with_phone = 0
        
        for business in businesses:
            # Count by type
            biz_type = business.get('business_type', 'unknown')
            business_types[biz_type] = business_types.get(biz_type, 0) + 1
            
            # Count contact info
            if business.get('owner_info', {}).get('names'):
                businesses_with_owner_info += 1
            if business.get('email'):
                businesses_with_email += 1
            if business.get('phone'):
                businesses_with_phone += 1
        
        return {
            'total_businesses': len(businesses),
            'business_types': business_types,
            'businesses_with_owner_info': businesses_with_owner_info,
            'businesses_with_email': businesses_with_email,
            'businesses_with_phone': businesses_with_phone,
            'data_completeness': {
                'owner_info': f"{(businesses_with_owner_info / len(businesses) * 100):.1f}%",
                'email': f"{(businesses_with_email / len(businesses) * 100):.1f}%",
                'phone': f"{(businesses_with_phone / len(businesses) * 100):.1f}%"
            }
        }

    def export_to_json(self, result: Dict, filename: str):
        """Export results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Results exported to {filename}")

    def export_to_csv(self, result: Dict, filename: str):
        """Export results to CSV file"""
        import csv
        
        businesses = result.get('businesses', [])
        if not businesses:
            logger.warning("No businesses to export")
            return
        
        # Define CSV columns
        columns = [
            'business_name', 'business_type', 'website', 'phone', 'email',
            'address', 'owner_names', 'owner_emails', 'owner_linkedin',
            'description', 'services'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            
            for business in businesses:
                owner_info = business.get('owner_info', {})
                
                row = {
                    'business_name': business.get('business_name', ''),
                    'business_type': business.get('business_type', ''),
                    'website': business.get('url', ''),
                    'phone': ', '.join(business.get('phone', [])),
                    'email': ', '.join(business.get('email', [])),
                    'address': business.get('address', ''),
                    'owner_names': ', '.join(owner_info.get('names', [])),
                    'owner_emails': ', '.join(owner_info.get('emails', [])),
                    'owner_linkedin': ', '.join(owner_info.get('linkedin', [])),
                    'description': business.get('description', ''),
                    'services': ', '.join(business.get('services', []))
                }
                
                writer.writerow(row)
        
        logger.info(f"Results exported to {filename}")


# Test
if __name__ == "__main__":
    pipeline = IntegratedScrapingPipeline(max_workers=3)
    
    # Test on a sample directory
    test_url = "https://example-chamber.com/members"
    
    print(f"Testing integrated pipeline on: {test_url}")
    result = pipeline.scrape_directory_and_businesses(
        test_url,
        max_businesses=10,  # Limit for testing
        max_pages=2
    )
    
    print(json.dumps(result.get('summary'), indent=2))
    print(f"\nScraped {result.get('businesses_scraped')} businesses")
    
    # Export results
    pipeline.export_to_json(result, 'scraped_businesses.json')
    pipeline.export_to_csv(result, 'scraped_businesses.csv')
