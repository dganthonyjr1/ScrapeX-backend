"""Get full LLM configuration"""

import requests
import json

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"
LLM_ID = "llm_1720a5a30e6b2905441723467174"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(
    f"{RETELL_API_BASE}/get-retell-llm/{LLM_ID}",
    headers=headers
)

if response.status_code == 200:
    llm_config = response.json()
    print(json.dumps(llm_config, indent=2))
else:
    print(f"Failed: {response.status_code}")
    print(response.text)
