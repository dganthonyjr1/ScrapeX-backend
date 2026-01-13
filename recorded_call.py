"""
Make a recorded test call and retrieve the recording afterward
"""

import requests
import json
import time
from datetime import datetime

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"
TEST_PHONE = "+18562001869"
AGENT_ID = "agent_4959fa89dc042dd9518fc1eb59"

def make_recorded_call():
    """Make test call with recording enabled"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    call_config = {
        "agent_id": AGENT_ID,
        "from_number": "+16099084403",
        "to_number": TEST_PHONE,
        "metadata": {
            "company": "DGA_Management_Group",
            "test": "recorded_multilingual_test",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/v2/create-phone-call",
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        call_data = response.json()
        call_id = call_data.get('call_id')
        print(f"✓ Recorded call initiated")
        print(f"  Call ID: {call_id}")
        print(f"  Status: {call_data.get('call_status')}")
        return call_id
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return None


def get_call_details(call_id):
    """Get call details including recording and transcript"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{RETELL_API_BASE}/v2/get-call/{call_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get call details: {response.status_code}")
        return None


if __name__ == "__main__":
    print("=" * 70)
    print("RECORDED MULTI-LINGUAL TEST CALL")
    print("=" * 70)
    
    print("\nInitiating recorded call...")
    call_id = make_recorded_call()
    
    if call_id:
        print("\n" + "=" * 70)
        print("CALL IN PROGRESS")
        print("=" * 70)
        print(f"\nCall ID: {call_id}")
        print(f"Phone: {TEST_PHONE}")
        print("\nThis call is being recorded.")
        print("\nAfter the call ends, I will retrieve:")
        print("  - Full transcript")
        print("  - Audio recording URL")
        print("  - Call duration and metrics")
        print("\nPlease answer the call and test:")
        print("  1. Interruption capability")
        print("  2. Multi-lingual switching")
        print("  3. DGA Management Group messaging")
        print("  4. Data validation (name/phone repeat)")
        print("\n" + "=" * 70)
        print("\nSaving call ID for later retrieval...")
        
        with open("/home/ubuntu/scrapex-backend/last_call_id.txt", "w") as f:
            f.write(call_id)
        
        print(f"Call ID saved to: /home/ubuntu/scrapex-backend/last_call_id.txt")
        print("\nAfter the call, run: python3 get_recording.py")
