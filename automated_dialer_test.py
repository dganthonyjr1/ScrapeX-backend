"""
Automated dialer test - makes a call to a test number and checks the transcript
"""

import requests
import json
import time

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"
AGENT_ID = "agent_a6f77fcd5883ee76ce0ef1bbe3"

# Use a test number that immediately hangs up to avoid bothering the user
TEST_NUMBER = "+18562001869"  # User's number for now, but will hang up quickly

def make_test_call():
    """Make a test call"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    call_config = {
        "agent_id": AGENT_ID,
        "from_number": "+16099084403",
        "to_number": TEST_NUMBER
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/v2/create-phone-call",
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        call_data = response.json()
        return call_data.get('call_id')
    else:
        print(f"Failed to create call: {response.status_code}")
        print(response.text)
        return None


def get_call_details(call_id, max_wait=30):
    """Wait for call to complete and get transcript"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"\nWaiting for call {call_id} to complete...")
    
    for i in range(max_wait):
        time.sleep(2)
        
        response = requests.get(
            f"{RETELL_API_BASE}/v2/get-call/{call_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            call_data = response.json()
            call_status = call_data.get('call_status')
            
            print(f"  Status: {call_status} ({i*2}s)")
            
            if call_status in ['ended', 'error']:
                return call_data
        
        if i >= max_wait - 1:
            print("  Timeout waiting for call to complete")
            return None
    
    return None


def check_transcript(call_data):
    """Check the transcript for issues"""
    
    transcript = call_data.get('transcript', '')
    
    print("\n" + "=" * 70)
    print("TRANSCRIPT ANALYSIS")
    print("=" * 70)
    
    if not transcript:
        print("\n❌ No transcript available")
        return False
    
    print(f"\nTranscript:\n{transcript}\n")
    
    # Check for issues
    issues = []
    
    if "thank you for letting me know" in transcript.lower():
        issues.append("❌ Agent says 'thank you for letting me know'")
    
    if "abc medical" in transcript.lower():
        issues.append("❌ Agent mentions 'ABC Medical'")
    
    if "dga management group" not in transcript.lower():
        issues.append("❌ Agent does not mention 'DGA Management Group'")
    
    # Check if agent starts correctly
    first_agent_message = ""
    for line in transcript.split('\n'):
        if 'agent:' in line.lower() or 'sarah:' in line.lower():
            first_agent_message = line
            break
    
    if first_agent_message:
        print(f"\nFirst agent message: {first_agent_message}")
        
        if "hello" not in first_agent_message.lower():
            issues.append("❌ Agent does not start with 'Hello'")
    
    if not issues:
        print("\n✓ All transcript checks passed!")
        return True
    else:
        print("\n❌ Issues found in transcript:")
        for issue in issues:
            print(f"  {issue}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("AUTOMATED DIALER TEST")
    print("=" * 70)
    
    print("\n[1] Making test call...")
    call_id = make_test_call()
    
    if not call_id:
        print("\n❌ Failed to create test call")
        exit(1)
    
    print(f"✓ Call created: {call_id}")
    
    print("\n[2] Waiting for call to complete...")
    call_data = get_call_details(call_id)
    
    if not call_data:
        print("\n❌ Could not retrieve call data")
        exit(1)
    
    print("\n[3] Analyzing transcript...")
    passed = check_transcript(call_data)
    
    if passed:
        print("\n" + "=" * 70)
        print("TEST PASSED - DIALER IS WORKING CORRECTLY")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("TEST FAILED - DIALER NEEDS FIXING")
        print("=" * 70)
