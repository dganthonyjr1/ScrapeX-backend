"""
Add SMS payment link capability to the Retell AI agent
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.environ.get("RETELL_API_KEY")
LLM_ID = "llm_c934afcf3083aa0bd590693df4cc"
AGENT_ID = "agent_05e8f725879b2997086400e39f"

# Stripe payment links
CHAMBER_PAYMENT_LINK = "https://buy.stripe.com/7sY8wRaUt8tK4woazL"
REGULAR_PAYMENT_LINK = "https://buy.stripe.com/28E14p4w5aBS4wo4bn"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

# Step 1: Update LLM with new prompt that includes SMS capability
print("[1] Updating LLM with SMS payment link capability...")
with open("/home/ubuntu/scrapex-backend/enhanced_llm_prompt_with_sms.txt", "r") as f:
    new_prompt = f.read()

llm_data = {
    "general_prompt": new_prompt
}

llm_response = requests.patch(
    f"https://api.retellai.com/update-retell-llm/{LLM_ID}",
    headers=headers,
    json=llm_data
)

if llm_response.status_code == 200:
    print("✓ LLM updated with SMS capability")
else:
    print(f"✗ LLM update failed: {llm_response.status_code}")
    print(llm_response.text)
    exit(1)

# Step 2: Add send_payment_link function to the agent
print("\n[2] Adding send_payment_link function to agent...")

# First, get the current agent configuration
agent_response = requests.get(
    f"https://api.retellai.com/get-agent/{AGENT_ID}",
    headers=headers
)

if agent_response.status_code != 200:
    print(f"✗ Failed to get agent config: {agent_response.status_code}")
    print(agent_response.text)
    exit(1)

current_agent = agent_response.json()
print(f"✓ Retrieved current agent configuration")

# Add the send_payment_link function
send_payment_link_function = {
    "name": "send_payment_link",
    "description": "Send a payment link via SMS to the customer's phone number. Only call this when the customer explicitly asks for a payment link or asks how to sign up.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_type": {
                "type": "string",
                "enum": ["chamber", "regular"],
                "description": "Type of customer: 'chamber' for Chamber of Commerce or Tourism board, 'regular' for regular business"
            }
        },
        "required": ["customer_type"]
    }
}

# Get existing functions or create new list
existing_functions = current_agent.get("function_call_config", {}).get("functions", [])

# Check if send_payment_link already exists
function_exists = any(f.get("name") == "send_payment_link" for f in existing_functions)

if not function_exists:
    existing_functions.append(send_payment_link_function)
    print("✓ Added send_payment_link function")
else:
    # Update existing function
    for i, f in enumerate(existing_functions):
        if f.get("name") == "send_payment_link":
            existing_functions[i] = send_payment_link_function
    print("✓ Updated existing send_payment_link function")

# Update agent with new function
agent_update_data = {
    "function_call_config": {
        "functions": existing_functions
    }
}

agent_update_response = requests.patch(
    f"https://api.retellai.com/update-agent/{AGENT_ID}",
    headers=headers,
    json=agent_update_data
)

if agent_update_response.status_code == 200:
    print("✓ Agent updated with send_payment_link function")
else:
    print(f"✗ Agent update failed: {agent_update_response.status_code}")
    print(agent_update_response.text)
    exit(1)

print("\n" + "="*60)
print("✓ SMS PAYMENT LINK CAPABILITY ADDED SUCCESSFULLY")
print("="*60)
print(f"\nAgent ID: {AGENT_ID}")
print(f"LLM ID: {LLM_ID}")
print("\nThe agent now has:")
print("  ✓ Multi-lingual support (English, Spanish, French, Mandarin, Portuguese, German)")
print("  ✓ Data validation (repeats contact info slowly)")
print("  ✓ SMS payment link capability (hidden feature)")
print("\nPayment Links:")
print(f"  - Chamber/Tourism: {CHAMBER_PAYMENT_LINK}")
print(f"  - Regular Business: {REGULAR_PAYMENT_LINK}")
print("\nHow it works:")
print("  1. Agent NEVER mentions payment link proactively")
print("  2. Only sends when customer asks 'Can you send me a payment link?'")
print("  3. Agent asks: 'Are you with a Chamber of Commerce or Tourism board?'")
print("  4. Sends appropriate link via SMS based on answer")
print("\nNext step: Configure SMS sending in Retell dashboard")
print("  Go to: https://dashboard.retellai.com/phone-numbers")
print("  Enable SMS on phone number: +16099084403")
