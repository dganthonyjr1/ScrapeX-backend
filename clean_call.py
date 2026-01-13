"""
Make a completely clean call with no dynamic variables
"""

import requests
import json

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"

def make_clean_call():
    """Make call with absolutely no dynamic variables"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Minimal call configuration with NO dynamic variables
    call_config = {
        "agent_id": "agent_4959fa89dc042dd9518fc1eb59",
        "from_number": "+16099084403",
        "to_number": "+18562001869"
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/v2/create-phone-call",
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        call_data = response.json()
        call_id = call_data.get('call_id')
        print(f"✓ Clean call initiated: {call_id}")
        
        with open("/home/ubuntu/scrapex-backend/last_call_id.txt", "w") as f:
            f.write(call_id)
        
        return call_id
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    print("=" * 70)
    print("MAKING CLEAN CALL - NO DYNAMIC VARIABLES")
    print("=" * 70)
    
    call_id = make_clean_call()
    
    if call_id:
        print("\n" + "=" * 70)
        print("CALL INITIATED")
        print("=" * 70)
        print(f"\nCall ID: {call_id}")
        print("\nThis is a completely clean call with:")
        print("  - NO dynamic variables")
        print("  - NO metadata overrides")
        print("  - ONLY the LLM prompt")
        print("\nThe agent should say:")
        print('  "Hello, this is Sarah calling from DGA Management Group"')
        print("\nAnd give real revenue numbers:")
        print('  "$10,000 to $50,000 in new revenue"')
        print("\n" + "=" * 70)
