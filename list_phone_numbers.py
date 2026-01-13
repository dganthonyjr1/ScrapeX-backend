"""List phone numbers in Retell AI account"""

import requests
import json

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(
    f"{RETELL_API_BASE}/list-phone-numbers",
    headers=headers
)

if response.status_code == 200:
    numbers = response.json()
    print("Phone numbers in your Retell account:")
    print(json.dumps(numbers, indent=2))
else:
    print(f"Failed: {response.status_code}")
    print(response.text)
