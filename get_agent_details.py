"""Get details of an existing agent to understand the structure"""

import requests
import json

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

# Get details of first agent
agent_id = "agent_4959fa89dc042dd9518fc1eb59"

response = requests.get(
    f"{RETELL_API_BASE}/get-agent/{agent_id}",
    headers=headers
)

if response.status_code == 200:
    agent = response.json()
    print(json.dumps(agent, indent=2))
else:
    print(f"Failed: {response.status_code}")
    print(response.text)
