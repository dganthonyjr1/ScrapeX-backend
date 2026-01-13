"""
Test script for integrated scraping pipeline
Tests directory scraping + individual business scraping
"""

import json
import sys
sys.path.append('/home/ubuntu/scrapex-backend')

from integrated_scraper import IntegratedScrapingPipeline

def test_integrated_pipeline():
    """Test the complete pipeline"""
    
    # Use a smaller directory for testing
    test_url = "https://www.tampabaychamber.com/membership/"
    
    print("="*80)
    print(f"TESTING INTEGRATED SCRAPING PIPELINE")
    print("="*80)
    print(f"\nTarget Directory: {test_url}")
    print(f"Max Businesses: 5 (for testing)")
    print(f"Max Pages: 1")
    print("\nThis will:")
    print("1. Scrape the directory to get business URLs")
    print("2. Visit each business website")
    print("3. Extract owner info, emails, phones, etc.")
    print("\nStarting pipeline...")
    print("="*80)
    
    pipeline = IntegratedScrapingPipeline(max_workers=3)
    
    result = pipeline.scrape_directory_and_businesses(
        directory_url=test_url,
        max_businesses=5,  # Limit for testing
        max_pages=1
    )
    
    print("\n" + "="*80)
    print("PIPELINE RESULTS")
    print("="*80)
    
    print(f"\nStatus: {result.get('status')}")
    print(f"Directory Type: {result.get('directory_type')}")
    print(f"Pages Scraped: {result.get('pages_scraped')}")
    print(f"Businesses Found in Directory: {result.get('total_businesses_found')}")
    print(f"Businesses Successfully Scraped: {result.get('businesses_scraped')}")
    
    summary = result.get('summary', {})
    if summary:
        print(f"\n--- DATA QUALITY SUMMARY ---")
        print(f"Total Businesses: {summary.get('total_businesses')}")
        print(f"With Owner Info: {summary.get('businesses_with_owner_info')}")
        print(f"With Email: {summary.get('businesses_with_email')}")
        print(f"With Phone: {summary.get('businesses_with_phone')}")
        print(f"\nData Completeness:")
        completeness = summary.get('data_completeness', {})
        print(f"  Owner Info: {completeness.get('owner_info', 'N/A')}")
        print(f"  Email: {completeness.get('email', 'N/A')}")
        print(f"  Phone: {completeness.get('phone', 'N/A')}")
    
    businesses = result.get('businesses', [])
    if businesses:
        print(f"\n--- DETAILED BUSINESS DATA ---\n")
        for i, business in enumerate(businesses[:3], 1):
            print(f"{i}. {business.get('business_name', 'N/A')}")
            print(f"   Type: {business.get('business_type', 'N/A')}")
            print(f"   Website: {business.get('url', 'N/A')}")
            print(f"   Phone: {', '.join(business.get('phone', []))}")
            print(f"   Email: {', '.join(business.get('email', []))}")
            
            owner_info = business.get('owner_info', {})
            if owner_info.get('names'):
                print(f"   Owner Names: {', '.join(owner_info.get('names', []))}")
            if owner_info.get('emails'):
                print(f"   Owner Emails: {', '.join(owner_info.get('emails', []))}")
            if owner_info.get('linkedin'):
                print(f"   LinkedIn: {', '.join(owner_info.get('linkedin', []))}")
            
            print()
    
    # Save results
    pipeline.export_to_json(result, '/home/ubuntu/scrapex-backend/test_integrated_results.json')
    pipeline.export_to_csv(result, '/home/ubuntu/scrapex-backend/test_integrated_results.csv')
    
    print(f"\nResults saved to:")
    print(f"  - test_integrated_results.json")
    print(f"  - test_integrated_results.csv")
    print("\n" + "="*80)
    
    return result

if __name__ == "__main__":
    test_integrated_pipeline()
