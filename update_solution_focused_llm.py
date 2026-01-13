#!/usr/bin/env python3
"""
Update Retell AI LLM with solution-focused prompt that uses dynamic business name
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.getenv("RETELL_API_KEY")
RETELL_API_BASE = "https://api.retellai.com"
LLM_ID = "llm_1a3e6e8f6d7e4e6f0d8f1e3e"

def update_llm_prompt():
    """Update the LLM with solution-focused prompt"""
    
    with open("solution_focused_prompt.txt", "r") as f:
        prompt = f.read()
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    llm_config = {
        "general_prompt": prompt,
        "general_tools": [
            {
                "type": "end_call",
                "name": "end_call",
                "description": "End the call when the conversation is complete or the customer wants to hang up"
            },
            {
                "type": "custom",
                "name": "send_payment_link",
                "description": "Send a payment link via SMS to the customer's phone number. Only use when customer explicitly requests it.",
                "speak_during_execution": False,
                "speak_after_execution": True,
                "execution_message_description": "Sending payment link via text message",
                "url": "https://scrapex-backend.onrender.com/api/v1/retell/webhook",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_type": {
                            "type": "string",
                            "enum": ["chamber_tourism", "healthcare", "general"],
                            "description": "Type of customer: chamber_tourism for Chamber of Commerce or Tourism boards, healthcare for healthcare facilities, general for all other businesses"
                        }
                    },
                    "required": ["customer_type"]
                }
            }
        ],
        "begin_message": "Hello, I'm calling about {{business_name}}. I help businesses like yours find new corporate clients and increase revenue by ten thousand to fifty thousand dollars per month. I speak English, Spanish, French, Mandarin, Portuguese, and German. Which language would you prefer?",
        "inbound_dynamic_variables_webhook_url": None
    }
    
    response = requests.patch(
        f"{RETELL_API_BASE}/update-retell-llm/{LLM_ID}",
        headers=headers,
        json=llm_config
    )
    
    if response.status_code == 200:
        print("✓ LLM updated successfully with solution-focused prompt!")
        print("\nKey changes:")
        print("  - Agent now says 'calling about {{business_name}}'")
        print("  - Focus on solving problems and ROI")
        print("  - No technology mentions")
        print("  - Dynamic business name variable enabled")
        return True
    else:
        print(f"✗ Failed to update LLM: {response.status_code}")
        print(response.text)
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("UPDATING LLM WITH SOLUTION-FOCUSED PROMPT")
    print("=" * 70)
    
    success = update_llm_prompt()
    
    if success:
        print("\n✓ Ready to test with dynamic business names!")
    else:
        print("\n✗ Update failed")
