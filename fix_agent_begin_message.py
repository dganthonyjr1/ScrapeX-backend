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

# Update agent with begin_message
data = {
    "begin_message": "Thank you for picking up. This is Sarah from DGA Management Group. Is this a good time to talk?"
}

response = requests.patch(f"https://api.retellai.com/update-agent/{AGENT_ID}", headers=headers, json=data)

print("Status Code:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2))
