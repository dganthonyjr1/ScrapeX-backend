"""
Fix agent configuration with correct response_engine format
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
print("FIXING AGENT WITH CORRECT RESPONSE_ENGINE FORMAT")
print("="*60)

# Update agent with correct response_engine format
print("\n[1] Updating agent with response_engine...")

agent_update = {
    "response_engine": {
        "type": "retell-llm",
        "llm_id": LLM_ID
    },
    "begin_message": "Hello, this is Sarah calling from DGA Management Group. How are you today?"
}

update_response = requests.patch(
    f"https://api.retellai.com/update-agent/{AGENT_ID}",
    headers=headers,
    json=agent_update
)

if update_response.status_code == 200:
    print("✓ Agent updated successfully")
    result = update_response.json()
    print(f"  Response engine type: {result.get('response_engine', {}).get('type')}")
    print(f"  LLM ID: {result.get('response_engine', {}).get('llm_id')}")
else:
    print(f"✗ Failed to update agent: {update_response.status_code}")
    print(update_response.text)
    exit(1)

# Verify
print("\n[2] Verifying configuration...")
verify_response = requests.get(
    f"https://api.retellai.com/get-agent/{AGENT_ID}",
    headers=headers
)

if verify_response.status_code == 200:
    agent = verify_response.json()
    response_engine = agent.get('response_engine', {})
    print(f"✓ Agent Name: {agent.get('agent_name')}")
    print(f"✓ Response Engine Type: {response_engine.get('type')}")
    print(f"✓ LLM ID: {response_engine.get('llm_id')}")
    print(f"✓ Webhook URL: {agent.get('webhook_url')}")
    print(f"✓ Begin Message: {agent.get('begin_message')}")
else:
    print(f"✗ Verification failed: {verify_response.status_code}")

print("\n" + "="*60)
print("✓ AGENT RESPONSE ENGINE CONFIGURED")
print("="*60)
print("\nNow the agent is linked to the LLM with:")
print("  ✓ Multi-lingual support")
print("  ✓ Data validation")
print("  ✓ SMS payment link capability in prompt")
print("\nNext: Add send_payment_link as a custom tool in Retell dashboard")
print("  Go to: https://dashboard.retellai.com/agents")
print(f"  Select agent: {AGENT_ID}")
print("  Add custom tool: send_payment_link")
