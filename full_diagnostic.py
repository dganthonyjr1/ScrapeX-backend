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

# Get agent configuration
print("=== AGENT CONFIGURATION ===")
agent_response = requests.get(f"https://api.retellai.com/get-agent/{AGENT_ID}", headers=headers)
agent_data = agent_response.json()
print(json.dumps(agent_data, indent=2))

# Get LLM configuration
llm_id = agent_data.get("llm_websocket_url")
if llm_id:
    print(f"\n=== LLM CONFIGURATION ({llm_id}) ===")
    llm_response = requests.get(f"https://api.retellai.com/get-retell-llm/{llm_id}", headers=headers)
    llm_data = llm_response.json()
    print(json.dumps(llm_data, indent=2))

# Check begin_message
print("\n=== BEGIN MESSAGE ===")
print(agent_data.get("begin_message", "NOT SET"))

# Check general_prompt
print("\n=== GENERAL PROMPT ===")
print(agent_data.get("general_prompt", "NOT SET"))
