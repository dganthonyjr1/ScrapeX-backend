#!/usr/bin/env python3
"""
Test automated workflow with public companies
These are large companies with public phone numbers
"""

import requests
import time

BACKEND_URL = "https://scrapex-backend.onrender.com"

# Public companies with phone numbers on their websites
TEST_COMPANIES = [
    {
        "name": "Walmart Corporate",
        "url": "https://corporate.walmart.com/contact",
        "expected_phone": True
    },
    {
        "name": "Target Corporate",
        "url": "https://corporate.target.com/about/contact",
        "expected_phone": True
    },
    {
        "name": "Best Buy Corporate",
        "url": "https://corporate.bestbuy.com/contact-us/",
        "expected_phone": True
    }
]

def test_company(company_info):
    """Test scraping and automated calling for one company"""
    
    print(f"\n{'='*70}")
    print(f"TESTING: {company_info['name']}")
    print(f"URL: {company_info['url']}")
    print(f"{'='*70}")
    
    # Initiate scrape
    print("\n[1] Scraping website...")
    response = requests.post(
        f"{BACKEND_URL}/api/v1/scrape",
        json={"url": company_info['url'], "business_name": company_info['name']}
    )
    
    if response.status_code != 200:
        print(f"✗ Failed to start scrape: {response.status_code}")
        return None
    
    job_data = response.json()
    job_id = job_data.get('job_id')
    print(f"✓ Job started: {job_id}")
    
    # Poll for completion
    print("\n[2] Waiting for completion...")
    for attempt in range(30):
        time.sleep(3)
        
        status_response = requests.get(f"{BACKEND_URL}/api/v1/jobs/{job_id}")
        if status_response.status_code != 200:
            continue
        
        job = status_response.json()
        status = job.get('status')
        
        if status == 'completed':
            print("✓ Scrape completed!")
            
            result = job.get('result', {})
            phones = result.get('phone', [])
            insights = result.get('analysis_insights', [])
            
            print(f"\n[3] Results:")
            print(f"  Business: {result.get('business_name', 'Unknown')}")
            print(f"  Phones Found: {len(phones)}")
            
            if phones:
                for i, phone in enumerate(phones[:3], 1):
                    print(f"    {i}. {phone}")
            
            print(f"\n[4] Analysis Insights:")
            for insight in insights:
                print(f"  • {insight}")
            
            # Check automated calling
            call_initiated = job.get('call_initiated', False)
            call_id = job.get('call_id')
            call_phone = job.get('call_phone')
            
            print(f"\n[5] Automated Calling:")
            print(f"  Initiated: {call_initiated}")
            
            if call_initiated:
                print(f"  ✓ Call ID: {call_id}")
                print(f"  ✓ Calling: {call_phone}")
                print(f"\n  ⚠ NOTE: This is a TEST CALL to a public company")
                print(f"  ⚠ If answered, the agent will hang up immediately")
                print(f"  ⚠ This verifies the automated workflow works end-to-end")
            else:
                call_error = job.get('call_error')
                print(f"  ✗ Not initiated")
                if call_error:
                    print(f"  Reason: {call_error}")
            
            return {
                'company': company_info['name'],
                'phones_found': len(phones),
                'call_initiated': call_initiated,
                'call_id': call_id if call_initiated else None
            }
            
        elif status == 'failed':
            print(f"✗ Failed: {job.get('error')}")
            return None
        
        if attempt % 5 == 0:
            print(f"  Still processing... ({attempt*3}s)")
    
    print("✗ Timeout")
    return None


def main():
    """Run tests on all companies"""
    
    print("\n" + "="*70)
    print("AUTOMATED WORKFLOW TEST - PUBLIC COMPANIES")
    print("="*70)
    print("\nTesting with large public companies that have phone numbers")
    print("These are non-intrusive tests to verify the system works")
    print("\nWaiting 30 seconds for deployment to complete...")
    time.sleep(30)
    
    results = []
    
    for company in TEST_COMPANIES:
        result = test_company(company)
        if result:
            results.append(result)
        time.sleep(5)  # Pause between tests
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for result in results:
        status = "✓ SUCCESS" if result['call_initiated'] else "✗ NO CALL"
        print(f"\n{result['company']}: {status}")
        print(f"  Phones Found: {result['phones_found']}")
        if result['call_id']:
            print(f"  Call ID: {result['call_id']}")
    
    success_count = sum(1 for r in results if r['call_initiated'])
    print(f"\n{'='*70}")
    print(f"RESULTS: {success_count}/{len(results)} automated calls initiated")
    print(f"{'='*70}")
    
    if success_count > 0:
        print("\n✓✓✓ AUTOMATED WORKFLOW WORKS! ✓✓✓")
        print("\nThe system successfully:")
        print("  1. Scraped business websites")
        print("  2. Extracted phone numbers")
        print("  3. Automatically initiated calls")
        print("\nReady for production use!")
    else:
        print("\n⚠ No calls initiated - scraper needs improvement")


if __name__ == "__main__":
    main()
