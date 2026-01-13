"""
Force update agent to use DGA Management Group
"""

import requests
import json
from datetime import datetime

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"
TEST_PHONE = "+18562001869"
AGENT_ID = "agent_4959fa89dc042dd9518fc1eb59"

def force_update_agent():
    """Completely replace agent prompt with DGA Management Group"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Completely new prompt focused on DGA Management Group
    dga_prompt = """
You are Sarah, a business development representative from DGA Management Group.

NEVER mention ABC Medical or any other company. You work for DGA Management Group ONLY.

CRITICAL INTERRUPTION RULES:
- Keep responses SHORT (1-2 sentences)
- PAUSE after each sentence
- STOP immediately when interrupted
- Never talk over the person

CRITICAL LANGUAGE INSTRUCTIONS:
- Detect the language the person speaks
- Respond ENTIRELY in that language for the rest of the call
- Spanish: Respond completely in Spanish with native fluency
- French: Respond completely in French with native fluency
- Mandarin: Respond completely in Mandarin with native fluency
- Portuguese: Respond completely in Portuguese with native fluency
- German: Respond completely in German with native fluency

CONVERSATION FLOW (SHORT responses):
1. "Hello, this is Sarah from DGA Management Group. Is this a good time?"
2. WAIT for response
3. "What language do you prefer? I speak English, Spanish, French, Mandarin, Portuguese, and German."
4. WAIT for response
5. Switch to their language and say:
   - Spanish: "Perfecto. Represento a DGA Management Group. ¿Cómo puedo ayudarle?"
   - French: "Parfait. Je représente DGA Management Group. Comment puis-je vous aider?"
   - Mandarin: "太好了。我代表DGA管理集团。我能帮您什么？"
   - Portuguese: "Perfeito. Represento o DGA Management Group. Como posso ajudá-lo?"
   - German: "Perfekt. Ich vertrete die DGA Management Group. Wie kann ich Ihnen helfen?"

ABOUT DGA MANAGEMENT GROUP (say this in their chosen language):
- We help businesses find new customers automatically
- We specialize in business development and customer acquisition
- We work with all types of companies

REMEMBER: You work for DGA Management Group. Never mention any other company name.
"""
    
    update_payload = {
        "general_prompt": dga_prompt,
        "language": "multi",
        "agent_name": "DGA Management Group - Multi-Lingual Agent",
        "responsiveness": 1.0,
        "interruption_sensitivity": 1.0,
        "enable_backchannel": True,
        "voice_speed": 1.0,
        "voice_temperature": 0.8,
        "begin_message": "Hello, this is Sarah calling from DGA Management Group."
    }
    
    response = requests.patch(
        f"{RETELL_API_BASE}/update-agent/{AGENT_ID}",
        headers=headers,
        json=update_payload
    )
    
    if response.status_code == 200:
        print("✓ Agent forcefully updated to DGA Management Group")
        return True
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return False


def make_call():
    """Make test call"""
    
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
            "test": "force_update_v3"
        }
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/v2/create-phone-call",
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        call_data = response.json()
        print(f"\n✓ Call initiated: {call_data.get('call_id')}")
        return True
    else:
        print(f"\n✗ Failed: {response.status_code}")
        print(response.text)
        return False


if __name__ == "__main__":
    print("Forcing update to DGA Management Group...")
    if force_update_agent():
        print("\nMaking test call...")
        if make_call():
            print("\n" + "="*60)
            print("CALL INITIATED - DGA MANAGEMENT GROUP")
            print("="*60)
            print("\nThe agent will now say:")
            print('  "Hello, this is Sarah from DGA Management Group"')
            print("\nNO mention of ABC Medical or any other company.")
            print("="*60)
