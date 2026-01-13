import os
import requests
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.environ.get("RETELL_API_KEY")
LLM_ID = "llm_c934afcf3083aa0bd590693df4cc"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

# Define the SMS tool
sms_tool = {
    "type": "custom",
    "name": "send_payment_link",
    "description": "Send a payment link via SMS to the customer. Only use this when the customer explicitly asks for a payment link, pricing information via text, or to receive information by SMS. Never mention this capability unless asked.",
    "url": "https://scrapex-backend.onrender.com/send-payment-sms",
    "speak_after_execution": True,
    "speak_during_execution": False,
    "execution_message_description": "I'm sending that to your phone now.",
    "parameters": {
        "type": "object",
        "properties": {
            "to_number": {
                "type": "string",
                "description": "The phone number to send the SMS to, in E.164 format (e.g., +14155552671). This should be the number you are currently calling."
            },
            "is_chamber": {
                "type": "boolean",
                "description": "Set to true if the customer is a Chamber of Commerce or Tourism Board. Set to false for all other businesses (medical facilities, restaurants, etc.)."
            }
        },
        "required": ["to_number"]
    }
}

# Get current LLM configuration
print("Getting current LLM configuration...")
get_response = requests.get(f"https://api.retellai.com/get-retell-llm/{LLM_ID}", headers=headers)
current_llm = get_response.json()

# Add SMS tool to existing tools
current_tools = current_llm.get("general_tools", [])
current_tools.append(sms_tool)

# Update LLM with new tool
print("Adding SMS tool to agent...")
update_data = {
    "general_tools": current_tools
}

update_response = requests.patch(f"https://api.retellai.com/update-retell-llm/{LLM_ID}", headers=headers, json=update_data)

if update_response.status_code == 200:
    print("✓ SMS tool added successfully")
    print("\nThe agent can now:")
    print("  - Send payment links via SMS when asked")
    print("  - Automatically detect Chamber vs Regular business")
    print("  - Send appropriate Stripe link")
    print("\nThe agent will NEVER mention this capability unless the customer asks for it.")
else:
    print(f"✗ Failed to add SMS tool: {update_response.status_code}")
    print(update_response.text)
