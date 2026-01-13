"""Get call transcript to see what the agent is actually saying"""

import requests
import json
import time

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"

# Get the last call ID
with open("/home/ubuntu/scrapex-backend/last_call_id.txt", "r") as f:
    call_id = f.read().strip()

print(f"Getting transcript for call: {call_id}")
print("Waiting 10 seconds for call to complete...")
time.sleep(10)

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(
    f"{RETELL_API_BASE}/v2/get-call/{call_id}",
    headers=headers
)

if response.status_code == 200:
    call_data = response.json()
    
    print("\n" + "="*70)
    print("CALL TRANSCRIPT")
    print("="*70)
    
    print(f"\nCall Status: {call_data.get('call_status')}")
    print(f"Duration: {call_data.get('call_duration_ms', 0) / 1000} seconds")
    
    transcript = call_data.get('transcript', '')
    if transcript:
        print(f"\nFull Transcript:")
        print("-"*70)
        print(transcript)
        print("-"*70)
    else:
        print("\nNo transcript available yet. Call may still be processing.")
    
    # Save full call data
    with open("/home/ubuntu/scrapex-backend/last_call_data.json", "w") as f:
        json.dump(call_data, f, indent=2)
    
    print(f"\nFull call data saved to: last_call_data.json")
    
else:
    print(f"Failed to get call: {response.status_code}")
    print(response.text)
