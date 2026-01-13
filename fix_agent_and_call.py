"""
Fix agent with proper interruption settings and improved multi-lingual prompt
"""

import requests
import json
from datetime import datetime

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"
TEST_PHONE = "+18562001869"
AGENT_ID = "agent_4959fa89dc042dd9518fc1eb59"

def update_agent_with_fixes():
    """Update agent with interruption support and improved multi-lingual prompt"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Improved multi-lingual prompt with explicit language instructions
    improved_prompt = """
You are Sarah, a professional business development representative from DGA Management Group testing our new multi-lingual outreach system.

CRITICAL INTERRUPTION RULES:
- Keep your responses SHORT (1-2 sentences maximum)
- PAUSE after each sentence to let the person speak
- LISTEN for interruptions and stop talking immediately when interrupted
- Never talk over the person
- If interrupted, acknowledge what they said before continuing

CRITICAL LANGUAGE INSTRUCTIONS:
- When the person speaks, detect their language
- If they speak Spanish, respond ENTIRELY in Spanish for the rest of the call
- If they speak French, respond ENTIRELY in French for the rest of the call
- If they speak Mandarin, respond ENTIRELY in Mandarin for the rest of the call
- If they speak Portuguese, respond ENTIRELY in Portuguese for the rest of the call
- If they speak German, respond ENTIRELY in German for the rest of the call
- Use proper pronunciation, native dialect, and fluency
- Use culturally appropriate greetings and phrases

CONVERSATION FLOW (Keep each response SHORT):
1. Greet briefly: "Hello, this is Sarah from DGA Management Group. Is this a good time to talk?"
2. WAIT for response
3. Ask: "What language would you prefer? I speak English, Spanish, French, Mandarin, Portuguese, and German."
4. WAIT for response
5. Once they choose, switch to that language IMMEDIATELY and say:
   - Spanish: "Perfecto. Hablo español con fluidez. ¿Cómo puedo ayudarle hoy?"
   - French: "Parfait. Je parle couramment français. Comment puis-je vous aider aujourd'hui?"
   - Mandarin: "太好了。我说流利的中文。今天我能帮您什么？"
   - Portuguese: "Perfeito. Falo português fluentemente. Como posso ajudá-lo hoje?"
   - German: "Perfekt. Ich spreche fließend Deutsch. Wie kann ich Ihnen heute helfen?"
6. Have a brief conversation about DGA Management Group in their language
7. DATA VALIDATION: Slowly repeat back their name and phone number in their language
8. Thank them briefly

ABOUT DGA MANAGEMENT GROUP:
- We help businesses find new customers automatically
- We specialize in business development and customer acquisition
- We work with companies across all industries

TONE:
- Friendly and professional
- Conversational, not robotic
- BRIEF responses only
- Always pause to let them speak
"""
    
    update_payload = {
        "general_prompt": improved_prompt,
        "language": "multi",  # Multi-lingual support
        "agent_name": "ScrapeX Multi-Lingual Test - DGA Management",
        "responsiveness": 1.0,  # Maximum responsiveness to interruptions
        "interruption_sensitivity": 1.0,  # Maximum sensitivity to interruptions
        "enable_backchannel": True,  # Allow natural conversation flow
        "voice_speed": 1.0,  # Normal speed
        "voice_temperature": 0.8  # Natural variation
    }
    
    response = requests.patch(
        f"{RETELL_API_BASE}/update-agent/{AGENT_ID}",
        headers=headers,
        json=update_payload
    )
    
    if response.status_code == 200:
        print("✓ Agent updated successfully")
        print("  - Interruption sensitivity: MAXIMUM")
        print("  - Response length: SHORT")
        print("  - Multi-lingual: IMPROVED")
        print("  - Company: DGA Management Group")
        return True
    else:
        print(f"✗ Failed to update agent: {response.status_code}")
        print(f"  Error: {response.text}")
        return False


def make_test_call():
    """Make test call with fixed agent"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    call_config = {
        "agent_id": AGENT_ID,
        "from_number": "+16099084403",
        "to_number": TEST_PHONE,
        "metadata": {
            "purpose": "multi_lingual_test_v2",
            "test_date": datetime.now().isoformat(),
            "company": "DGA Management Group",
            "fixes": ["interruption_support", "improved_multilingual", "short_responses"]
        }
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/v2/create-phone-call",
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        call_data = response.json()
        print(f"\n✓ Test call initiated")
        print(f"  Call ID: {call_data.get('call_id')}")
        print(f"  To: {TEST_PHONE}")
        return call_data.get('call_id')
    else:
        print(f"\n✗ Failed to initiate call: {response.status_code}")
        print(f"  Error: {response.text}")
        return None


if __name__ == "__main__":
    print("=" * 70)
    print("ScrapeX Multi-Lingual Agent - FIXED VERSION")
    print("=" * 70)
    
    print("\n[1] Updating agent with fixes...")
    if update_agent_with_fixes():
        print("\n[2] Initiating test call...")
        call_id = make_test_call()
        
        if call_id:
            print("\n" + "=" * 70)
            print("TEST CALL INITIATED - TESTING FIXES")
            print("=" * 70)
            print(f"\nCall ID: {call_id}")
            print(f"Phone: {TEST_PHONE}")
            print(f"\nWhat's different:")
            print("  ✓ Agent will keep responses SHORT (1-2 sentences)")
            print("  ✓ Agent will PAUSE to let you speak")
            print("  ✓ Agent will STOP immediately when interrupted")
            print("  ✓ Agent will talk about DGA Management Group")
            print("  ✓ Agent will switch to your chosen language completely")
            print(f"\nTest by:")
            print("  1. Try interrupting the agent mid-sentence")
            print("  2. Request a specific language")
            print("  3. Verify the agent responds ENTIRELY in that language")
            print("  4. Check pronunciation and fluency")
            print("\n" + "=" * 70)
