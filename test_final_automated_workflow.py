#!/usr/bin/env python3
"""
Final test of complete automated workflow
"""

import requests
import time

BACKEND_URL = "https://scrapex-backend.onrender.com"
TEST_URL = "https://www.ycombinator.com/companies"  # Known to have phone number

print("="*70)
print("FINAL AUTOMATED WORKFLOW TEST")
print("="*70)
print(f"\nTesting complete workflow:")
print(f"  1. Scrape website")
print(f"  2. Extract phone number")
print(f"  3. Automatically initiate call")
print(f"\nURL: {TEST_URL}")
print(f"\nNote: This will make a REAL CALL to verify the system works")
print(f"If someone answers, they will hear the agent pitch services")
print("="*70)

# Initiate scrape
print("\n[1] Initiating scrape...")
response = requests.post(
    f"{BACKEND_URL}/api/v1/scrape",
    json={"url": TEST_URL}
)

if response.status_code != 200:
    print(f"✗ Failed: {response.status_code}")
    print(response.text)
    exit(1)

job_data = response.json()
job_id = job_data['job_id']
print(f"✓ Job started: {job_id}")

# Poll for completion
print("\n[2] Waiting for completion...")
for attempt in range(30):
    time.sleep(2)
    
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
        
        print(f"\n[3] Scraped Data:")
        print(f"  Business: {result.get('business_name', 'Unknown')}")
        print(f"  Phones: {len(phones)}")
        if phones:
            for phone in phones:
                print(f"    - {phone}")
        
        print(f"\n[4] Analysis Insights:")
        for insight in insights:
            print(f"  • {insight}")
        
        # Check automated calling
        call_initiated = job.get('call_initiated', False)
        call_id = job.get('call_id')
        call_phone = job.get('call_phone')
        call_error = job.get('call_error')
        
        print(f"\n[5] Automated Calling:")
        print(f"  Initiated: {call_initiated}")
        
        if call_initiated:
            print(f"  ✓ Call ID: {call_id}")
            print(f"  ✓ Calling: {call_phone}")
            print(f"\n{'='*70}")
            print("✓✓✓ AUTOMATED WORKFLOW SUCCESSFUL! ✓✓✓")
            print(f"{'='*70}")
            print(f"\nThe system automatically:")
            print(f"  1. ✓ Scraped {TEST_URL}")
            print(f"  2. ✓ Found phone: {call_phone}")
            print(f"  3. ✓ Initiated call: {call_id}")
            print(f"\nA call is being placed to {call_phone} right now")
            print(f"From: +16099084403")
            print(f"\nAgent will say:")
            print(f'  "Hi, this is Sarah. I was looking at your business')
            print(f'   online and noticed something interesting. Do you')
            print(f'   have a quick minute?"')
            print(f"\n{'='*70}")
            print("READY TO PUSH TO PRODUCTION!")
            print(f"{'='*70}")
        else:
            print(f"  ✗ Not initiated")
            if call_error:
                print(f"  Error: {call_error}")
            print(f"\n{'='*70}")
            print("WORKFLOW INCOMPLETE")
            print(f"{'='*70}")
        
        break
        
    elif status == 'failed':
        print(f"✗ Failed: {job.get('error')}")
        break
    
    if attempt % 5 == 0:
        print(f"  Processing... ({attempt*2}s)")

print("\nTest complete.")
