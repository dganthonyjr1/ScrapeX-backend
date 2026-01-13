"""
Update existing Retell AI agent with multi-lingual prompt and make test call
"""

import requests
import json
from datetime import datetime

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"
TEST_PHONE = "+18562001869"

# Use the first existing agent
AGENT_ID = "agent_4959fa89dc042dd9518fc1eb59"

def update_agent_for_multilingual():
    """Update agent with multi-lingual prompt"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Multi-lingual prompt
    multilingual_prompt = """
You are a professional business development representative testing multi-lingual capabilities for ScrapeX.

CRITICAL LANGUAGE INSTRUCTION:
- Automatically detect the language the person speaks when they answer
- Respond in the SAME language they use throughout the entire conversation
- Speak with proper pronunciation, dialect, and fluency
- Use culturally appropriate greetings and phrases

CONVERSATION FLOW FOR TEST:
1. Greet them warmly: "Hello, this is Sarah calling from ScrapeX. I'm testing our new multi-lingual system."
2. Ask: "What language would you like me to speak? I can communicate fluently in English, Spanish, French, Mandarin, Portuguese, or German."
3. Once they choose a language, switch to that language immediately
4. Have a brief conversation in their chosen language:
   - Introduce ScrapeX: "We help businesses find new customers automatically"
   - Ask: "Would you be interested in learning more?"
5. CRITICAL DATA VALIDATION: Slowly and clearly repeat back:
   - "Let me confirm I have your information correct"
   - "Your name is [NAME]" (speak slowly)
   - "Your phone number is [PHONE]" (speak each digit slowly)
   - "Is that correct?"
6. Ask them to rate the pronunciation and fluency from 1 to 10
7. Thank them for helping test the system

TONE AND STYLE:
- Speak naturally like a native speaker in each language
- Use proper pronunciation and dialect
- Be friendly and professional
- Speak clearly and at a moderate pace for clarity
- When repeating back information, speak VERY SLOWLY and CLEARLY

LANGUAGES YOU MUST SPEAK FLUENTLY:
- English (US) - native quality
- Spanish (Spain and Mexico) - native quality with proper dialect
- French (France) - native quality
- Mandarin Chinese - native quality with proper tones
- Portuguese (Brazil and Portugal) - native quality with proper dialect
- German - native quality
"""
    
    update_payload = {
        "general_prompt": multilingual_prompt,
        "language": "multi",  # Enable multi-lingual support
        "agent_name": "ScrapeX Multi-Lingual Test Agent"
    }
    
    response = requests.patch(
        f"{RETELL_API_BASE}/update-agent/{AGENT_ID}",
        headers=headers,
        json=update_payload
    )
    
    if response.status_code == 200:
        print("✓ Agent updated successfully with multi-lingual prompt")
        return True
    else:
        print(f"✗ Failed to update agent: {response.status_code}")
        print(f"  Error: {response.text}")
        return False


def make_test_call():
    """Make test call to verify multi-lingual capabilities"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    call_config = {
        "agent_id": AGENT_ID,
        "from_number": "+16099084403",  # Your Retell phone number
        "to_number": TEST_PHONE,
        "metadata": {
            "purpose": "multi_lingual_test",
            "test_date": datetime.now().isoformat(),
            "languages": ["English", "Spanish", "French", "Mandarin", "Portuguese", "German"]
        }
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/v2/create-phone-call",
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        call_data = response.json()
        print(f"\n✓ Test call initiated successfully")
        print(f"  Call ID: {call_data.get('call_id')}")
        print(f"  Status: {call_data.get('call_status')}")
        print(f"  To: {TEST_PHONE}")
        return call_data.get('call_id')
    else:
        print(f"\n✗ Failed to initiate call: {response.status_code}")
        print(f"  Error: {response.text}")
        return None


if __name__ == "__main__":
    print("=" * 70)
    print("ScrapeX Multi-Lingual Agent Test")
    print("=" * 70)
    
    print("\n[1] Updating agent with multi-lingual prompt...")
    if update_agent_for_multilingual():
        print("\n[2] Initiating test call...")
        call_id = make_test_call()
        
        if call_id:
            print("\n" + "=" * 70)
            print("TEST CALL INITIATED")
            print("=" * 70)
            print(f"\nAgent ID: {AGENT_ID}")
            print(f"Call ID: {call_id}")
            print(f"Phone: {TEST_PHONE}")
            print(f"\nThe call will arrive shortly. When you answer:")
            print("1. Listen to the English greeting")
            print("2. Request to speak in a specific language")
            print("3. Evaluate the pronunciation, dialect, and fluency")
            print("4. Listen for the data validation (name and phone repeated slowly)")
            print("5. Rate the quality from 1-10")
            print(f"\nLanguages to test:")
            print("  - English (US)")
            print("  - Spanish (Spain/Mexico)")
            print("  - French (France)")
            print("  - Mandarin Chinese")
            print("  - Portuguese (Brazil/Portugal)")
            print("  - German")
            print("\n" + "=" * 70)
