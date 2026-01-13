#!/usr/bin/env python3
"""
Test automated workflow with a real business website
"""

import requests
import time

BACKEND_URL = "https://scrapex-backend.onrender.com"
# Test with a real small business that has contact info on their website
TEST_URL = "https://www.joespizzaandpasta.com"  # Example pizza restaurant

def test_real_business():
    """Test with real business"""
    
    print("=" * 70)
    print("TESTING AUTOMATED WORKFLOW WITH REAL BUSINESS")
    print("=" * 70)
    
    print(f"\n[1] Testing with: {TEST_URL}")
    print("    This will scrape the website and automatically call if phone found")
    
    # Initiate scrape
    print("\n[2] Initiating scrape...")
    scrape_response = requests.post(
        f"{BACKEND_URL}/api/v1/scrape",
        json={"url": TEST_URL}
    )
    
    if scrape_response.status_code != 200:
        print(f"✗ Failed: {scrape_response.status_code}")
        print(scrape_response.text)
        return
    
    job_data = scrape_response.json()
    job_id = job_data.get('job_id')
    print(f"✓ Job started: {job_id}")
    
    # Poll for completion
    print("\n[3] Waiting for completion...")
    for attempt in range(30):
        time.sleep(2)
        
        status_response = requests.get(f"{BACKEND_URL}/api/v1/jobs/{job_id}")
        if status_response.status_code != 200:
            continue
        
        job = status_response.json()
        status = job.get('status')
        
        print(f"  Attempt {attempt + 1}: {status}")
        
        if status == 'completed':
            print("\n✓ Scrape completed!")
            
            # Check results
            result = job.get('result', {})
            contact_info = result.get('contact_info', {})
            phones = contact_info.get('phone_numbers', [])
            
            print(f"\n[4] Scraped Data:")
            print(f"  Business: {result.get('business_name', 'Unknown')}")
            print(f"  Phone Numbers Found: {len(phones)}")
            
            if phones:
                for i, phone in enumerate(phones[:3], 1):
                    print(f"    {i}. {phone}")
            
            # Check if call was initiated
            call_initiated = job.get('call_initiated', False)
            call_id = job.get('call_id')
            call_phone = job.get('call_phone')
            call_error = job.get('call_error')
            
            print(f"\n[5] Automated Call Status:")
            print(f"  Initiated: {call_initiated}")
            
            if call_initiated:
                print(f"  ✓ Call ID: {call_id}")
                print(f"  ✓ Calling: {call_phone}")
                print(f"\n✓✓✓ AUTOMATED WORKFLOW SUCCESSFUL! ✓✓✓")
                print(f"\nThe system automatically:")
                print(f"  1. Scraped {TEST_URL}")
                print(f"  2. Found phone: {call_phone}")
                print(f"  3. Initiated call: {call_id}")
                print(f"\nThe business will receive a call from +16099084403")
            else:
                print(f"  ✗ Call not initiated")
                if call_error:
                    print(f"  Reason: {call_error}")
                else:
                    print(f"  Reason: No phone numbers found")
            
            return job
            
        elif status == 'failed':
            print(f"\n✗ Failed: {job.get('error')}")
            return None
    
    print("\n✗ Timeout")
    return None


if __name__ == "__main__":
    result = test_real_business()
    
    print("\n" + "=" * 70)
    if result and result.get('call_initiated'):
        print("TEST PASSED - AUTOMATED WORKFLOW WORKS!")
    else:
        print("TEST INCOMPLETE - Check scraper or phone extraction")
    print("=" * 70)
