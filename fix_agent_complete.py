"""
Complete agent configuration: Link LLM and add send_payment_link function
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.environ.get("RETELL_API_KEY")
AGENT_ID = "agent_05e8f725879b2997086400e39f"
LLM_ID = "llm_c934afcf3083aa0bd590693df4cc"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

print("="*60)
print("FIXING AGENT CONFIGURATION")
print("="*60)

# Step 1: Link the LLM to the agent and add function
print("\n[1] Linking LLM and adding send_payment_link function...")

agent_update = {
    "llm_id": LLM_ID,
    "begin_message": "Hello, this is Sarah calling from DGA Management Group. How are you today?",
    "function_call_config": {
        "functions": [
            {
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
        ]
    }
}

update_response = requests.patch(
    f"https://api.retellai.com/update-agent/{AGENT_ID}",
    headers=headers,
    json=agent_update
)

if update_response.status_code == 200:
    print("✓ Agent updated successfully")
else:
    print(f"✗ Failed to update agent: {update_response.status_code}")
    print(update_response.text)
    exit(1)

# Step 2: Verify the configuration
print("\n[2] Verifying configuration...")
verify_response = requests.get(
    f"https://api.retellai.com/get-agent/{AGENT_ID}",
    headers=headers
)

if verify_response.status_code == 200:
    agent = verify_response.json()
    print(f"✓ Agent Name: {agent.get('agent_name')}")
    print(f"✓ LLM ID: {agent.get('llm_id')}")
    print(f"✓ Webhook URL: {agent.get('webhook_url')}")
    print(f"✓ Begin Message: {agent.get('begin_message')}")
    
    func_config = agent.get('function_call_config', {})
    functions = func_config.get('functions', [])
    print(f"✓ Functions: {len(functions)}")
    for func in functions:
        print(f"  - {func.get('name')}: {func.get('description')[:60]}...")
else:
    print(f"✗ Verification failed: {verify_response.status_code}")
    print(verify_response.text)
    exit(1)

print("\n" + "="*60)
print("✓ AGENT FULLY CONFIGURED")
print("="*60)
print(f"\nAgent ID: {AGENT_ID}")
print(f"LLM ID: {LLM_ID}")
print(f"Webhook: https://scrapex-backend.onrender.com/api/v1/retell/webhook")
print("\nCapabilities:")
print("  ✓ Multi-lingual (English, Spanish, French, Mandarin, Portuguese, German)")
print("  ✓ Data validation (repeats contact info slowly)")
print("  ✓ SMS payment link (hidden feature - only when customer asks)")
print("  ✓ Customer type detection (Chamber vs Regular Business)")
print("\nPayment Links:")
print("  - Chamber/Tourism: https://buy.stripe.com/7sY8wRaUt8tK4woazL")
print("  - Regular Business: https://buy.stripe.com/28E14p4w5aBS4wo4bn")
print("\n⚠️  IMPORTANT: Enable SMS on phone number +16099084403")
print("   Go to: https://dashboard.retellai.com/phone-numbers")
