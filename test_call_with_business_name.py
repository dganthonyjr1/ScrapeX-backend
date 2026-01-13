#!/usr/bin/env python3
"""
Test call with dynamic business name
"""

import os
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RETELL_API_KEY = os.getenv("RETELL_API_KEY")
RETELL_API_BASE = "https://api.retellai.com"
AGENT_ID = "agent_4959fa89dc042dd9518fc1eb59"
TEST_NUMBER = "+18562001869"  # User's number

def make_test_call_with_business_name():
    """Make a test call mentioning DGA Management Group"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Create call with dynamic variables for business name
    call_config = {
        "from_number": "+16099084403",
        "to_number": TEST_NUMBER,
        "agent_id": AGENT_ID,
        "metadata": {
            "business_name": "DGA Management Group",
            "test_call": "true"
        },
        "dynamic_variables": [
            {
                "name": "business_name",
                "value": "DGA Management Group"
            }
        ]
    }
    
    print(f"Making test call to {TEST_NUMBER}...")
    print(f"Business name: DGA Management Group")
    
    response = requests.post(
        f"{RETELL_API_BASE}/v2/create-phone-call",
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        call_data = response.json()
        call_id = call_data.get('call_id')
        print(f"\n✓ Call created successfully!")
        print(f"Call ID: {call_id}")
        print(f"\nThe agent will call {TEST_NUMBER} and mention 'DGA Management Group'")
        print(f"\nYou can answer and test:")
        print(f"1. Does the agent mention DGA Management Group?")
        print(f"2. Language selection works?")
        print(f"3. Natural conversation flow?")
        return call_id
    else:
        print(f"\n✗ Failed to create call: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    print("=" * 70)
    print("TEST CALL WITH BUSINESS NAME")
    print("=" * 70)
    
    call_id = make_test_call_with_business_name()
    
    if call_id:
        print(f"\n✓ Test call initiated!")
        print(f"\nPlease answer the call and verify:")
        print(f"  - Agent mentions 'DGA Management Group'")
        print(f"  - All languages work correctly")
        print(f"  - Conversation flows naturally")
    else:
        print(f"\n✗ Test call failed")
