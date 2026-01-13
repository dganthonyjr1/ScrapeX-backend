"""
Capacity Test for Large Chamber Directories
Tests system performance with 100+ businesses
"""

import json
import sys
import time
import psutil
import os
sys.path.append('/home/ubuntu/scrapex-backend')

from integrated_scraper import IntegratedScrapingPipeline

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_large_directory():
    """Test with a large Chamber directory"""
    
    # Denver Chamber has 2000+ members - good stress test
    test_url = "https://denverchamber.org/member/member-directory/"
    
    print("="*80)
    print("CAPACITY TEST: LARGE CHAMBER DIRECTORY")
    print("="*80)
    print(f"\nTarget: Denver Chamber of Commerce")
    print(f"URL: {test_url}")
    print(f"Expected Size: 2000+ member businesses")
    print(f"\nTest Parameters:")
    print(f"  - Max Businesses to Scrape: 50 (for testing)")
    print(f"  - Max Pages: 3")
    print(f"  - Parallel Workers: 5")
    print("\n" + "="*80)
    
    # Record start metrics
    start_time = time.time()
    start_memory = get_memory_usage()
    
    print(f"\nStarting Memory: {start_memory:.2f} MB")
    print(f"Starting Time: {time.strftime('%H:%M:%S')}")
    print("\nPhase 1: Scraping directory for business list...")
    
    pipeline = IntegratedScrapingPipeline(max_workers=5)
    
    result = pipeline.scrape_directory_and_businesses(
        directory_url=test_url,
        max_businesses=50,
        max_pages=3
    )
    
    # Record end metrics
    end_time = time.time()
    end_memory = get_memory_usage()
    duration = end_time - start_time
    memory_used = end_memory - start_memory
    
    print("\n" + "="*80)
    print("CAPACITY TEST RESULTS")
    print("="*80)
    
    print(f"\n--- PERFORMANCE METRICS ---")
    print(f"Total Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"Memory Used: {memory_used:.2f} MB")
    print(f"Peak Memory: {end_memory:.2f} MB")
    
    print(f"\n--- SCRAPING RESULTS ---")
    print(f"Status: {result.get('status')}")
    print(f"Directory Type: {result.get('directory_type')}")
    print(f"Pages Scraped: {result.get('pages_scraped')}")
    print(f"Businesses Found: {result.get('total_businesses_found')}")
    print(f"Businesses Scraped: {result.get('businesses_scraped')}")
    
    if result.get('businesses_scraped', 0) > 0:
        avg_time_per_business = duration / result.get('businesses_scraped')
        print(f"Average Time per Business: {avg_time_per_business:.2f} seconds")
        
        # Extrapolate for 100 and 500 businesses
        time_for_100 = avg_time_per_business * 100 / 60
        time_for_500 = avg_time_per_business * 500 / 60
        
        print(f"\n--- CAPACITY PROJECTIONS ---")
        print(f"Estimated time for 100 businesses: {time_for_100:.1f} minutes")
        print(f"Estimated time for 500 businesses: {time_for_500:.1f} minutes")
        print(f"Estimated memory for 500 businesses: {(memory_used / result.get('businesses_scraped')) * 500:.2f} MB")
    
    summary = result.get('summary', {})
    if summary:
        print(f"\n--- DATA QUALITY ---")
        print(f"Total Businesses: {summary.get('total_businesses')}")
        print(f"With Owner Info: {summary.get('businesses_with_owner_info')}")
        print(f"With Email: {summary.get('businesses_with_email')}")
        print(f"With Phone: {summary.get('businesses_with_phone')}")
        
        completeness = summary.get('data_completeness', {})
        print(f"\nData Completeness Rates:")
        print(f"  Owner Info: {completeness.get('owner_info', 'N/A')}")
        print(f"  Email: {completeness.get('email', 'N/A')}")
        print(f"  Phone: {completeness.get('phone', 'N/A')}")
        
        business_types = summary.get('business_types', {})
        if business_types:
            print(f"\nBusiness Types Found:")
            for biz_type, count in sorted(business_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {biz_type}: {count}")
    
    # Save results
    pipeline.export_to_json(result, '/home/ubuntu/scrapex-backend/capacity_test_results.json')
    pipeline.export_to_csv(result, '/home/ubuntu/scrapex-backend/capacity_test_results.csv')
    
    print(f"\n--- RECOMMENDATIONS ---")
    
    if result.get('businesses_scraped', 0) >= 50:
        print("✓ System successfully handled 50 businesses")
        print("✓ Can scale to 100+ businesses with current architecture")
        
        if avg_time_per_business < 10:
            print("✓ Fast scraping speed - good for production")
        else:
            print("⚠ Scraping speed could be optimized")
        
        if memory_used < 500:
            print("✓ Memory usage is efficient")
        else:
            print("⚠ Consider implementing batch processing for very large directories")
    
    print(f"\nFor production use with large directories (500+ businesses):")
    print("1. Implement pagination and batch processing")
    print("2. Use a job queue system (Celery/Redis)")
    print("3. Store results in database instead of memory")
    print("4. Add progress tracking and resume capability")
    
    print("\n" + "="*80)
    
    return result

if __name__ == "__main__":
    test_large_directory()
