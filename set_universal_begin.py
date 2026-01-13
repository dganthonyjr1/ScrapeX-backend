import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.environ.get("RETELL_API_KEY")
AGENT_ID = "agent_a6f77fcd5883ee76ce0ef1bbe3"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

# Universal begin message that works for all calls
universal_begin_message = "Hello, this is Sarah calling from DGA Management Group. How are you today?"

# Update agent
data = {
    "begin_message": universal_begin_message
}

response = requests.patch(f"https://api.retellai.com/update-agent/{AGENT_ID}", headers=headers, json=data)

print("Agent updated successfully!")
print("New begin message:", universal_begin_message)
print("\nAgent response:")
print(json.dumps(response.json(), indent=2))

# Also update the LLM to match
llm_data = {
    "begin_message": universal_begin_message
}

llm_response = requests.patch(f"https://api.retellai.com/update-retell-llm/llm_f488632c143120f1076236e6682d", headers=headers, json=llm_data)

print("\nLLM updated successfully!")
print("LLM response:")
print(json.dumps(llm_response.json(), indent=2))

# Make a test call
print("\n\nMaking test call...")
call_data = {
    "agent_id": AGENT_ID,
    "from_number": "+16099084403",
    "to_number": "+18562001869"
}

call_response = requests.post("https://api.retellai.com/v2/create-phone-call", headers=headers, json=call_data)
print("Call initiated!")
print(json.dumps(call_response.json(), indent=2))
