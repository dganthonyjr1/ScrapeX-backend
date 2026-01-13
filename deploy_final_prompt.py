#!/usr/bin/env python3
"""
Deploy final corrected prompt - pitches TO businesses, no language mention
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
    """Update the LLM with final corrected prompt"""
    
    with open("final_sales_prompt.txt", "r") as f:
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
        "begin_message": "Hello, this is Sarah. I help businesses find new corporate clients and increase their revenue. Is this a good time to talk?"
    }
    
    response = requests.patch(
        f"{RETELL_API_BASE}/update-retell-llm/{LLM_ID}",
        headers=headers,
        json=llm_config
    )
    
    if response.status_code == 200:
        print("✓ LLM updated successfully with final corrected prompt!")
        print("\nKey changes:")
        print("  - Agent pitches services TO businesses (not from)")
        print("  - Agent does NOT mention language capabilities")
        print("  - Agent detects and responds in spoken language naturally")
        print("  - Focus on solving problems and ROI")
        print("  - No technology mentions")
        return True
    else:
        print(f"✗ Failed to update LLM: {response.status_code}")
        print(response.text)
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("DEPLOYING FINAL CORRECTED PROMPT")
    print("=" * 70)
    
    success = update_llm_prompt()
    
    if success:
        print("\n✓ Ready to test with corrected behavior!")
    else:
        print("\n✗ Update failed")
