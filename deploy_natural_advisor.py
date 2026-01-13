#!/usr/bin/env python3
"""
Deploy natural advisor prompt - sounds human, helpful, not salesy
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.getenv("RETELL_API_KEY")
RETELL_API_BASE = "https://api.retellai.com"
LLM_ID = "llm_c934afcf3083aa0bd590693df4cc"

def update_llm_prompt():
    """Update the LLM with natural advisor prompt"""
    
    with open("natural_advisor_prompt.txt", "r") as f:
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
        "begin_message": "Hi, this is Sarah. I was looking at your business online and noticed something interesting. Do you have a quick minute?"
    }
    
    response = requests.patch(
        f"{RETELL_API_BASE}/update-retell-llm/{LLM_ID}",
        headers=headers,
        json=llm_config
    )
    
    if response.status_code == 200:
        print("✓ LLM updated successfully with natural advisor prompt!")
        print("\nKey changes:")
        print("  - Sounds like helpful advisor, not salesperson")
        print("  - Opening feels personal (did homework on business)")
        print("  - Leads with intriguing observation, not pitch")
        print("  - Asks permission before sharing solutions")
        print("  - Uses natural language, filler words, pauses")
        print("  - No pushy revenue claims without context")
        print("  - Completely human-sounding conversation")
        return True
    else:
        print(f"✗ Failed to update LLM: {response.status_code}")
        print(response.text)
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("DEPLOYING NATURAL ADVISOR PROMPT")
    print("=" * 70)
    
    success = update_llm_prompt()
    
    if success:
        print("\n✓ Ready to test with natural human-like conversation!")
    else:
        print("\n✗ Update failed")
