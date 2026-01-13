"""
Test the dialer opening message by retrieving the LLM configuration
and verifying the begin_message is correct
"""

import requests
import json

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"
AGENT_ID = "agent_a6f77fcd5883ee76ce0ef1bbe3"
LLM_ID = "llm_f488632c143120f1076236e6682d"

def get_llm_config():
    """Get the current LLM configuration"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{RETELL_API_BASE}/get-retell-llm/{LLM_ID}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get LLM: {response.status_code}")
        print(response.text)
        return None


def check_opening_message(config):
    """Check if the opening message is correct"""
    
    begin_message = config.get('begin_message', '')
    general_prompt = config.get('general_prompt', '')
    
    print("\n" + "=" * 70)
    print("DIALER OPENING MESSAGE TEST")
    print("=" * 70)
    
    print(f"\nBegin Message: {begin_message}")
    print(f"\nGeneral Prompt (first 500 chars):\n{general_prompt[:500]}...")
    
    # Check for issues
    issues = []
    
    if "thank you for letting me know" in general_prompt.lower():
        issues.append("❌ Prompt contains 'thank you for letting me know'")
    
    if "abc medical" in general_prompt.lower():
        issues.append("❌ Prompt still mentions 'ABC Medical'")
    
    if "dga management group" not in general_prompt.lower():
        issues.append("❌ Prompt does not mention 'DGA Management Group'")
    
    if begin_message and "dga management group" not in begin_message.lower():
        issues.append("❌ Begin message does not mention 'DGA Management Group'")
    
    if "{" in general_prompt or "{{" in general_prompt:
        issues.append("❌ Prompt contains template variables")
    
    if not issues:
        print("\n✓ All checks passed!")
        return True
    else:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False


if __name__ == "__main__":
    config = get_llm_config()
    
    if config:
        passed = check_opening_message(config)
        
        if not passed:
            print("\n" + "=" * 70)
            print("DIALER NEEDS FIXING")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("DIALER IS READY")
            print("=" * 70)
