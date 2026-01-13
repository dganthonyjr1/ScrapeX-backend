#!/usr/bin/env python3
"""
Make test call with corrected DGA Management Group prompt
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.getenv("RETELL_API_KEY")
RETELL_API_BASE = "https://api.retellai.com"
AGENT_ID = "agent_05e8f725879b2997086400e39f"
TEST_PHONE = "+18562001869"
FROM_NUMBER = "+16099084403"

def make_test_call():
    """Make a test call to verify DGA prompt"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    call_config = {
        "agent_id": AGENT_ID,
        "from_number": FROM_NUMBER,
        "to_number": TEST_PHONE,
        "metadata": {
            "test": "dga_sales_prompt",
            "timestamp": "2026-01-13"
        }
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/v2/create-phone-call",
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        call_data = response.json()
        call_id = call_data.get("call_id")
        print("✓ Test call initiated successfully!")
        print(f"\nCall Details:")
        print(f"  Call ID: {call_id}")
        print(f"  From: {FROM_NUMBER}")
        print(f"  To: {TEST_PHONE}")
        print(f"  Agent: {AGENT_ID}")
        print(f"\nExpected behavior:")
        print("  - Agent says: 'Hello, I'm calling from DGA Management Group'")
        print("  - Agent asks for language preference")
        print("  - Agent switches to chosen language")
        print("  - Agent focuses on solving problems and ROI")
        print("  - No technology mentions")
        return call_id
    else:
        print(f"✗ Failed to initiate call: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    print("=" * 70)
    print("TEST CALL - DGA MANAGEMENT GROUP SALES PROMPT")
    print("=" * 70)
    
    call_id = make_test_call()
    
    if call_id:
        print("\n" + "=" * 70)
        print("TEST CALL IN PROGRESS")
        print("=" * 70)
        print("\nPlease answer the call and test:")
        print("  1. Agent introduction (should say FROM DGA Management Group)")
        print("  2. Language selection (try Spanish, French, or Mandarin)")
        print("  3. Conversation flow in chosen language")
        print("  4. Data validation (agent repeats info back slowly)")
        print("\nCall ID for reference: " + call_id)
    else:
        print("\n✗ Test call failed")
