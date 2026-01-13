"""
Add send_payment_link custom tool to agent with three customer types
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.environ.get("RETELL_API_KEY")
AGENT_ID = "agent_05e8f725879b2997086400e39f"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

print("="*60)
print("ADDING CUSTOM TOOL WITH THREE CUSTOMER TYPES")
print("="*60)

# Add custom tool to agent
print("\n[1] Adding send_payment_link function with three types...")

# Define the custom tool
custom_tool = {
    "name": "send_payment_link",
    "description": "Send a payment link via SMS to the customer's phone number. Only call this when the customer explicitly asks for a payment link or asks how to sign up. The function will automatically determine which payment link to send based on the customer type.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_type": {
                "type": "string",
                "enum": ["chamber_tourism", "healthcare", "general"],
                "description": "Type of customer: 'chamber_tourism' for Chamber of Commerce or Tourism board, 'healthcare' for healthcare facilities, 'general' for any other business"
            }
        },
        "required": ["customer_type"]
    }
}

# Update agent with custom tool
agent_update = {
    "custom_tools": [custom_tool]
}

update_response = requests.patch(
    f"https://api.retellai.com/update-agent/{AGENT_ID}",
    headers=headers,
    json=agent_update
)

if update_response.status_code == 200:
    print("✓ Custom tool added successfully")
    result = update_response.json()
    print(f"  Agent: {result.get('agent_name')}")
    
    # Check if custom_tools is in the response
    if 'custom_tools' in result:
        tools = result.get('custom_tools', [])
        print(f"  Custom tools: {len(tools)}")
        for tool in tools:
            print(f"    - {tool.get('name')}")
    else:
        print("  Note: custom_tools field not in response (may need dashboard configuration)")
else:
    print(f"✗ Failed to add custom tool: {update_response.status_code}")
    print(update_response.text)
    
    # Try alternative approach with function_call_config
    print("\n[2] Trying alternative approach with function_call_config...")
    
    agent_update_alt = {
        "function_call_config": {
            "functions": [custom_tool]
        }
    }
    
    update_response_alt = requests.patch(
        f"https://api.retellai.com/update-agent/{AGENT_ID}",
        headers=headers,
        json=agent_update_alt
    )
    
    if update_response_alt.status_code == 200:
        print("✓ Function added via function_call_config")
    else:
        print(f"✗ Alternative approach also failed: {update_response_alt.status_code}")
        print(update_response_alt.text)

# Verify configuration
print("\n[3] Verifying agent configuration...")
verify_response = requests.get(
    f"https://api.retellai.com/get-agent/{AGENT_ID}",
    headers=headers
)

if verify_response.status_code == 200:
    agent = verify_response.json()
    print(f"✓ Agent: {agent.get('agent_name')}")
    print(f"✓ Webhook: {agent.get('webhook_url')}")
    
    # Check for custom tools
    if 'custom_tools' in agent:
        print(f"✓ Custom tools: {len(agent.get('custom_tools', []))}")
    
    # Check for function_call_config
    if 'function_call_config' in agent:
        func_config = agent.get('function_call_config', {})
        functions = func_config.get('functions', [])
        print(f"✓ Functions: {len(functions)}")
        for func in functions:
            print(f"  - {func.get('name')}")

print("\n" + "="*60)
print("CONFIGURATION STATUS")
print("="*60)
print("\nCustom Tool Definition:")
print(json.dumps(custom_tool, indent=2))
print("\nIf the tool wasn't added via API, you'll need to add it manually in the dashboard:")
print("  1. Go to: https://dashboard.retellai.com/agents")
print(f"  2. Select agent: {AGENT_ID}")
print("  3. Add the custom tool with the definition above")
