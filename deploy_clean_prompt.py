import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.environ.get("RETELL_API_KEY")
LLM_ID = "llm_f488632c143120f1076236e6682d"
AGENT_ID = "agent_a6f77fcd5883ee76ce0ef1bbe3"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

# Read the clean prompt
with open("/home/ubuntu/scrapex-backend/clean_llm_prompt.txt", "r") as f:
    clean_prompt = f.read()

# Update LLM with clean prompt and begin message
llm_data = {
    "general_prompt": clean_prompt,
    "begin_message": "Hello, this is Sarah calling from DGA Management Group. How are you today?"
}

print("Updating LLM...")
llm_response = requests.patch(f"https://api.retellai.com/update-retell-llm/{LLM_ID}", headers=headers, json=llm_data)
print("LLM Status:", llm_response.status_code)

if llm_response.status_code == 200:
    print("✓ LLM updated successfully")
else:
    print("✗ LLM update failed")
    print(llm_response.text)
    exit(1)

# Update agent with begin message
agent_data = {
    "begin_message": "Hello, this is Sarah calling from DGA Management Group. How are you today?"
}

print("\nUpdating Agent...")
agent_response = requests.patch(f"https://api.retellai.com/update-agent/{AGENT_ID}", headers=headers, json=agent_data)
print("Agent Status:", agent_response.status_code)

if agent_response.status_code == 200:
    print("✓ Agent updated successfully")
else:
    print("✗ Agent update failed")
    print(agent_response.text)
    exit(1)

print("\n✓ ALL UPDATES DEPLOYED SUCCESSFULLY")
print("\nNext step: Test with a call to verify it works")
