"""
Configure Retell AI agent to use webhook for function calling
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.environ.get("RETELL_API_KEY")
AGENT_ID = "agent_05e8f725879b2997086400e39f"
BACKEND_URL = "https://scrapex-backend.onrender.com"
WEBHOOK_URL = f"{BACKEND_URL}/api/v1/retell/webhook"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

print("="*60)
print("CONFIGURING RETELL AI AGENT WITH WEBHOOK")
print("="*60)

# Step 1: Get current agent configuration
print("\n[1] Retrieving current agent configuration...")
agent_response = requests.get(
    f"https://api.retellai.com/get-agent/{AGENT_ID}",
    headers=headers
)

if agent_response.status_code != 200:
    print(f"✗ Failed to get agent: {agent_response.status_code}")
    print(agent_response.text)
    exit(1)

current_agent = agent_response.json()
print(f"✓ Agent retrieved: {current_agent.get('agent_name')}")

# Step 2: Update agent with webhook URL
print(f"\n[2] Configuring webhook URL: {WEBHOOK_URL}")

agent_update = {
    "webhook_url": WEBHOOK_URL
}

update_response = requests.patch(
    f"https://api.retellai.com/update-agent/{AGENT_ID}",
    headers=headers,
    json=agent_update
)

if update_response.status_code == 200:
    print("✓ Webhook URL configured successfully")
else:
    print(f"✗ Failed to update agent: {update_response.status_code}")
    print(update_response.text)
    exit(1)

# Step 3: Verify configuration
print("\n[3] Verifying configuration...")
verify_response = requests.get(
    f"https://api.retellai.com/get-agent/{AGENT_ID}",
    headers=headers
)

if verify_response.status_code == 200:
    agent_config = verify_response.json()
    webhook_url = agent_config.get("webhook_url")
    functions = agent_config.get("function_call_config", {}).get("functions", [])
    
    print(f"✓ Webhook URL: {webhook_url}")
    print(f"✓ Functions configured: {len(functions)}")
    
    for func in functions:
        print(f"  - {func.get('name')}: {func.get('description')[:60]}...")
else:
    print(f"✗ Verification failed: {verify_response.status_code}")

print("\n" + "="*60)
print("✓ AGENT CONFIGURATION COMPLETE")
print("="*60)
print(f"\nAgent ID: {AGENT_ID}")
print(f"Webhook URL: {WEBHOOK_URL}")
print("\nHow it works:")
print("  1. Customer asks: 'Can you send me a payment link?'")
print("  2. Agent asks: 'Are you with a Chamber of Commerce or Tourism board?'")
print("  3. Agent calls send_payment_link function with customer_type")
print("  4. Retell sends webhook to your backend")
print("  5. Backend sends SMS with appropriate Stripe payment link")
print("  6. Customer receives SMS with payment link")
print("\nPayment Links:")
print("  - Chamber/Tourism: https://buy.stripe.com/7sY8wRaUt8tK4woazL")
print("  - Regular Business: https://buy.stripe.com/28E14p4w5aBS4wo4bn")
print("\n✓ Ready for testing!")
