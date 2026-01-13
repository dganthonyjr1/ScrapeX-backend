#!/usr/bin/env python3
"""
Test automated calling by directly calling the backend with mock data
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.getenv("RETELL_API_KEY")
AGENT_ID = "agent_05e8f725879b2997086400e39f"
FROM_NUMBER = "+16099084403"
TEST_PHONE = "+18562001869"

def test_direct_call():
    """Test calling directly via Retell API"""
    
    print("=" * 70)
    print("TESTING AUTOMATED CALL DIRECTLY")
    print("=" * 70)
    
    headers = {
        'Authorization': f'Bearer {RETELL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    call_config = {
        'agent_id': AGENT_ID,
        'from_number': FROM_NUMBER,
        'to_number': TEST_PHONE,
        'metadata': {
            'business_name': 'Test Business',
            'source': 'automated_workflow_test',
            'test': True
        }
    }
    
    print(f"\n[1] Initiating call to {TEST_PHONE}...")
    print(f"    From: {FROM_NUMBER}")
    print(f"    Agent: {AGENT_ID}")
    
    response = requests.post(
        'https://api.retellai.com/v2/create-phone-call',
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        result = response.json()
        call_id = result.get('call_id')
        print(f"\n✓ Call initiated successfully!")
        print(f"  Call ID: {call_id}")
        print(f"\nYou should receive a call from {FROM_NUMBER}")
        print(f"The agent will say: 'Hi, this is Sarah. I was looking at your business online and noticed something interesting. Do you have a quick minute?'")
        return True
    else:
        print(f"\n✗ Call failed: {response.status_code}")
        print(response.text)
        return False


if __name__ == "__main__":
    print("\nThis test verifies the automated calling functionality works.")
    print("It will initiate a real call to your phone number.\n")
    
    success = test_direct_call()
    
    if success:
        print("\n" + "=" * 70)
        print("AUTOMATED CALLING WORKS!")
        print("=" * 70)
        print("\nNext step: Fix scraper to extract phone numbers correctly")
        print("Then the full automated workflow will work end-to-end")
    else:
        print("\n" + "=" * 70)
        print("CALL INITIATION FAILED")
        print("=" * 70)
