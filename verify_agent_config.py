"""
Verify Retell AI agent configuration
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
print("AGENT CONFIGURATION VERIFICATION")
print("="*60)

# Get agent configuration
print(f"\n[1] Checking Agent: {AGENT_ID}")
agent_response = requests.get(
    f"https://api.retellai.com/get-agent/{AGENT_ID}",
    headers=headers
)

if agent_response.status_code == 200:
    agent = agent_response.json()
    print(f"✓ Agent Name: {agent.get('agent_name')}")
    print(f"✓ LLM ID: {agent.get('llm_id')}")
    print(f"✓ Webhook URL: {agent.get('webhook_url')}")
    print(f"✓ Voice: {agent.get('voice_id')}")
    print(f"✓ Begin Message: {agent.get('begin_message', 'Not set')[:100]}")
    
    # Check function calling config
    func_config = agent.get('function_call_config', {})
    functions = func_config.get('functions', [])
    print(f"\n✓ Functions configured: {len(functions)}")
    for func in functions:
        print(f"  - {func.get('name')}")
        print(f"    Description: {func.get('description')}")
        print(f"    Parameters: {json.dumps(func.get('parameters'), indent=6)}")
else:
    print(f"✗ Failed to get agent: {agent_response.status_code}")
    print(agent_response.text)

# Get LLM configuration
print(f"\n[2] Checking LLM: {LLM_ID}")
llm_response = requests.get(
    f"https://api.retellai.com/get-retell-llm/{LLM_ID}",
    headers=headers
)

if llm_response.status_code == 200:
    llm = llm_response.json()
    prompt = llm.get('general_prompt', '')
    print(f"✓ LLM Model: {llm.get('model')}")
    print(f"✓ Prompt length: {len(prompt)} characters")
    
    # Check if SMS capability is in prompt
    if 'send_payment_link' in prompt.lower():
        print("✓ SMS payment link capability found in prompt")
    else:
        print("✗ SMS payment link capability NOT found in prompt")
    
    # Check for multi-lingual support
    languages = ['Spanish', 'French', 'Mandarin', 'Portuguese', 'German']
    found_languages = [lang for lang in languages if lang in prompt]
    print(f"✓ Languages found in prompt: {', '.join(found_languages)}")
else:
    print(f"✗ Failed to get LLM: {llm_response.status_code}")
    print(llm_response.text)

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
