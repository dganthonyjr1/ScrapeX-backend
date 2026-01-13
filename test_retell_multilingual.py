"""
Test script for Retell AI multi-lingual agent configuration
Tests native voice quality, pronunciation, and dialect accuracy
"""

import os
import requests
import json
from datetime import datetime

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"

def create_multilingual_agent():
    """Create a multi-lingual agent with native-quality voices"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Multi-lingual agent configuration with native voices
    agent_config = {
        "agent_name": "ScrapeX Multi-Lingual Test Agent",
        "language": "multi",  # Enable auto language detection
        "voice_id": "11labs-multilingual",  # ElevenLabs multilingual voice
        "voice_temperature": 0.7,
        "voice_speed": 0.95,  # Slightly slower for clarity
        "responsiveness": 0.8,
        "interruption_sensitivity": 0.5,
        "llm_model": "gpt-4",
        "llm_temperature": 0.7,
        "general_prompt": """
You are a professional business development representative testing multi-lingual capabilities.

CRITICAL LANGUAGE INSTRUCTION:
- Automatically detect the language the person speaks when they answer
- Respond in the SAME language they use throughout the entire conversation
- Speak with proper pronunciation, dialect, and fluency
- Use culturally appropriate greetings and phrases

CONVERSATION FLOW FOR TEST:
1. Greet them warmly in their language
2. Introduce yourself: "My name is Sarah, and I'm calling from ScrapeX to test our multi-lingual system"
3. Ask: "What language would you like me to speak? I can communicate in English, Spanish, French, Mandarin, Portuguese, or German"
4. Switch to their requested language and have a brief conversation
5. Ask them to rate the pronunciation and fluency from 1-10
6. CRITICAL DATA VALIDATION: Slowly repeat back: "Let me confirm I have your information correct. Your name is... your phone number is... Is that correct?"
7. Thank them for helping test the system

TONE AND STYLE:
- Speak naturally like a native speaker
- Use proper pronunciation and dialect
- Be friendly and professional
- Speak clearly and at a moderate pace for clarity
""",
        "begin_message": "Hello, this is Sarah calling from ScrapeX. I'm testing our new multi-lingual system. Can you hear me clearly?",
        "enable_backchannel": True,
        "ambient_sound": "call-center",
        "boosted_keywords": ["ScrapeX", "multi-lingual", "pronunciation", "fluency"]
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/create-agent",
        headers=headers,
        json=agent_config
    )
    
    if response.status_code == 200:
        agent_data = response.json()
        print(f"✓ Multi-lingual agent created successfully")
        print(f"  Agent ID: {agent_data.get('agent_id')}")
        return agent_data.get('agent_id')
    else:
        print(f"✗ Failed to create agent: {response.status_code}")
        print(f"  Error: {response.text}")
        return None


def make_test_call(agent_id, phone_number):
    """Make a test call to verify multi-lingual capabilities"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    call_config = {
        "agent_id": agent_id,
        "to_number": phone_number,
        "from_number": None,  # Will use Retell's default number
        "metadata": {
            "purpose": "multi-lingual_test",
            "test_date": datetime.now().isoformat(),
            "languages_to_test": ["English", "Spanish", "French", "Mandarin", "Portuguese", "German"]
        }
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/create-phone-call",
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 200:
        call_data = response.json()
        print(f"\n✓ Test call initiated successfully")
        print(f"  Call ID: {call_data.get('call_id')}")
        print(f"  Status: {call_data.get('status')}")
        print(f"  To: {phone_number}")
        print(f"\nThe agent will call you shortly to test multi-lingual capabilities.")
        print(f"You can test any of these languages: English, Spanish, French, Mandarin, Portuguese, German")
        return call_data.get('call_id')
    else:
        print(f"\n✗ Failed to initiate call: {response.status_code}")
        print(f"  Error: {response.text}")
        return None


def get_agent_list():
    """Get list of existing agents"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{RETELL_API_BASE}/list-agents",
        headers=headers
    )
    
    if response.status_code == 200:
        agents = response.json()
        print(f"\nExisting agents:")
        # Handle both list and dict responses
        agent_list = agents if isinstance(agents, list) else agents.get('agents', [])
        for agent in agent_list:
            print(f"  - {agent.get('agent_name')} (ID: {agent.get('agent_id')})")
        return agent_list
    else:
        print(f"Failed to get agent list: {response.status_code}")
        return []


if __name__ == "__main__":
    print("=" * 60)
    print("ScrapeX Multi-Lingual Agent Test")
    print("=" * 60)
    
    # Check existing agents
    print("\n[1] Checking existing agents...")
    agents = get_agent_list()
    
    # Create new multi-lingual agent
    print("\n[2] Creating multi-lingual agent...")
    agent_id = create_multilingual_agent()
    
    if agent_id:
        # Make test call
        print("\n[3] Initiating test call...")
        test_phone = "+18562001869"
        call_id = make_test_call(agent_id, test_phone)
        
        if call_id:
            print("\n" + "=" * 60)
            print("TEST CALL INITIATED")
            print("=" * 60)
            print(f"\nAgent ID: {agent_id}")
            print(f"Call ID: {call_id}")
            print(f"Phone: {test_phone}")
            print(f"\nInstructions for testing:")
            print("1. Answer the call when it comes in")
            print("2. Listen to the English greeting")
            print("3. Request to speak in a specific language")
            print("4. Evaluate pronunciation, dialect, and fluency")
            print("5. Rate the quality from 1-10")
            print("\nLanguages available:")
            print("  - English (US)")
            print("  - Spanish (Spain/Mexico)")
            print("  - French (France)")
            print("  - Mandarin Chinese")
            print("  - Portuguese (Brazil/Portugal)")
            print("  - German")
    else:
        print("\n✗ Failed to create agent. Cannot proceed with test call.")
