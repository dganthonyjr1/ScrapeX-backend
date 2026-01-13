import os
import requests
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.environ.get("RETELL_API_KEY")
AGENT_ID = "agent_a6f77fcd5883ee76ce0ef1bbe3"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "agent_id": AGENT_ID,
    "from_number": "+16099084403",
    "to_number": "+18562001869",
    "retell_llm_dynamic_variables": {
        "language": "Spanish"
    }
}

response = requests.post("https://api.retellai.com/v2/create-phone-call", headers=headers, json=data)

print(response.text)
