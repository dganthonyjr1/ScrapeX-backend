import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.environ.get("RETELL_API_KEY")
NEW_LLM_ID = "llm_c934afcf3083aa0bd590693df4cc"
NEW_AGENT_ID = "agent_05e8f725879b2997086400e39f"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

# Read enhanced prompt
with open("/home/ubuntu/scrapex-backend/enhanced_llm_prompt.txt", "r") as f:
    enhanced_prompt = f.read()

# Update LLM with enhanced prompt
print("Updating LLM with enhanced prompt (includes data validation in all languages)...")
llm_data = {
    "general_prompt": enhanced_prompt
}

llm_response = requests.patch(f"https://api.retellai.com/update-retell-llm/{NEW_LLM_ID}", headers=headers, json=llm_data)

if llm_response.status_code == 200:
    print("✓ LLM updated successfully")
    print("\nThe agent now includes:")
    print("  - Spanish, French, Mandarin, Portuguese, and German support")
    print("  - Data validation (repeats name, email, phone slowly)")
    print("  - Natural conversation flow in each language")
else:
    print(f"✗ LLM update failed: {llm_response.status_code}")
    print(llm_response.text)
    exit(1)

print("\n✓ Agent is ready for testing")
print(f"Agent ID: {NEW_AGENT_ID}")
print(f"LLM ID: {NEW_LLM_ID}")
