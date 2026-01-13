"""
Test script for directory scraper
Tests on real Chamber of Commerce sites
"""

import json
import sys
sys.path.append('/home/ubuntu/scrapex-backend')

from directory_scraper import DirectoryScraper

def test_directory_scraper():
    """Test directory scraper on real sites"""
    
    scraper = DirectoryScraper()
    
    # Test on Tampa Bay Chamber (good example)
    test_url = "https://www.tampabaychamber.com/membership/"
    
    print("="*80)
    print(f"TESTING DIRECTORY SCRAPER")
    print("="*80)
    print(f"\nTarget: {test_url}")
    print(f"Type: Chamber of Commerce Member Directory")
    print("\nScraping...")
    
    result = scraper.scrape_directory(test_url)
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    
    print(f"\nStatus: {result.get('status')}")
    print(f"Directory Type: {result.get('directory_type')}")
    print(f"Scraping Method: {result.get('scraping_method')}")
    print(f"Total Businesses Found: {result.get('total_found', 0)}")
    print(f"Has More Pages: {result.get('has_more_pages', False)}")
    
    businesses = result.get('businesses', [])
    
    if businesses:
        print(f"\n--- SAMPLE BUSINESSES (First 5) ---\n")
        for i, business in enumerate(businesses[:5], 1):
            print(f"{i}. {business.get('business_name', 'N/A')}")
            print(f"   Website: {business.get('website', 'N/A')}")
            print(f"   Phone: {business.get('phone', 'N/A')}")
            print(f"   Category: {business.get('category', 'N/A')}")
            print()
    
    # Save full results
    with open('/home/ubuntu/scrapex-backend/test_directory_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nFull results saved to: test_directory_results.json")
    print("\n" + "="*80)
    
    return result

if __name__ == "__main__":
    test_directory_scraper()
