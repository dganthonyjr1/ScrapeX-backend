#!/usr/bin/env python3
"""
Test the complete automated workflow: scrape → analyze → call
"""

import requests
import time
import json

BACKEND_URL = "https://scrapex-backend.onrender.com"
# Using a test business with clear contact information
TEST_URL = "https://www.example-business.com"  # Will test with real business
TEST_PHONE = "+18562001869"  # Fallback for testing

def test_automated_workflow():
    """Test the complete automated workflow"""
    
    print("=" * 70)
    print("TESTING AUTOMATED WORKFLOW")
    print("=" * 70)
    
    # Step 1: Initiate scrape
    print("\n[1] Initiating scrape...")
    scrape_response = requests.post(
        f"{BACKEND_URL}/api/v1/scrape",
        json={
            "url": TEST_URL,
            "business_name": "DGA Management Group"
        }
    )
    
    if scrape_response.status_code != 200:
        print(f"✗ Failed to initiate scrape: {scrape_response.status_code}")
        print(scrape_response.text)
        return
    
    job_data = scrape_response.json()
    job_id = job_data.get('job_id')
    print(f"✓ Scrape initiated - Job ID: {job_id}")
    
    # Step 2: Poll for completion
    print("\n[2] Waiting for scrape to complete...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        time.sleep(2)
        attempt += 1
        
        status_response = requests.get(f"{BACKEND_URL}/api/v1/jobs/{job_id}")
        if status_response.status_code != 200:
            print(f"✗ Failed to get job status: {status_response.status_code}")
            continue
        
        job_status = status_response.json()
        status = job_status.get('status')
        
        print(f"  Attempt {attempt}: Status = {status}")
        
        if status == 'completed':
            print("✓ Scrape completed!")
            
            # Check if call was initiated
            call_initiated = job_status.get('call_initiated', False)
            call_id = job_status.get('call_id')
            call_phone = job_status.get('call_phone')
            call_error = job_status.get('call_error')
            
            print("\n[3] Automated Call Status:")
            print(f"  Call Initiated: {call_initiated}")
            
            if call_initiated:
                print(f"  ✓ Call ID: {call_id}")
                print(f"  ✓ Phone Number: {call_phone}")
                print(f"\n✓ AUTOMATED WORKFLOW SUCCESSFUL!")
                print(f"\nThe system automatically:")
                print(f"  1. Scraped {TEST_URL}")
                print(f"  2. Extracted phone number: {call_phone}")
                print(f"  3. Initiated call: {call_id}")
                print(f"\nYou should receive a call from +16099084403")
            else:
                print(f"  ✗ Call not initiated")
                if call_error:
                    print(f"  Error: {call_error}")
            
            # Display scraped data
            result = job_status.get('result', {})
            print("\n[4] Scraped Data Summary:")
            print(f"  Business Name: {result.get('business_name')}")
            
            contact_info = result.get('contact_info', {})
            phone_numbers = contact_info.get('phone_numbers', [])
            emails = contact_info.get('emails', [])
            
            print(f"  Phone Numbers: {len(phone_numbers)}")
            for phone in phone_numbers[:3]:
                print(f"    - {phone}")
            
            print(f"  Emails: {len(emails)}")
            for email in emails[:3]:
                print(f"    - {email}")
            
            return job_status
            
        elif status == 'failed':
            error = job_status.get('error')
            print(f"✗ Scrape failed: {error}")
            return None
    
    print(f"✗ Timeout waiting for scrape to complete")
    return None


if __name__ == "__main__":
    result = test_automated_workflow()
    
    if result:
        print("\n" + "=" * 70)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("TEST FAILED")
        print("=" * 70)
