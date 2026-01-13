import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.environ.get("RETELL_API_KEY")
OLD_AGENT_ID = "agent_a6f77fcd5883ee76ce0ef1bbe3"
OLD_LLM_ID = "llm_f488632c143120f1076236e6682d"
PHONE_NUMBER = "+16099084403"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

# Step 1: Delete old agent
print("Step 1: Deleting old agent...")
delete_agent_response = requests.delete(f"https://api.retellai.com/delete-agent/{OLD_AGENT_ID}", headers=headers)
if delete_agent_response.status_code == 200:
    print("✓ Old agent deleted")
else:
    print(f"⚠ Agent deletion status: {delete_agent_response.status_code}")

# Step 2: Delete old LLM
print("\nStep 2: Deleting old LLM...")
delete_llm_response = requests.delete(f"https://api.retellai.com/delete-retell-llm/{OLD_LLM_ID}", headers=headers)
if delete_llm_response.status_code == 200:
    print("✓ Old LLM deleted")
else:
    print(f"⚠ LLM deletion status: {delete_llm_response.status_code}")

# Step 3: Create new LLM with clean prompt
print("\nStep 3: Creating new LLM...")
with open("/home/ubuntu/scrapex-backend/clean_llm_prompt.txt", "r") as f:
    clean_prompt = f.read()

new_llm_data = {
    "general_prompt": clean_prompt,
    "begin_message": "Hello, this is Sarah calling from DGA Management Group. How are you today?",
    "model": "gpt-4.1",
    "general_tools": [{
        "type": "end_call",
        "name": "end_call",
        "description": "End the call when user has to leave or says goodbye."
    }]
}

create_llm_response = requests.post("https://api.retellai.com/create-retell-llm", headers=headers, json=new_llm_data)
if create_llm_response.status_code == 201:
    new_llm = create_llm_response.json()
    new_llm_id = new_llm["llm_id"]
    print(f"✓ New LLM created: {new_llm_id}")
else:
    print(f"✗ LLM creation failed: {create_llm_response.status_code}")
    print(create_llm_response.text)
    exit(1)

# Step 4: Create new agent
print("\nStep 4: Creating new agent...")
new_agent_data = {
    "agent_name": "DGA Management Group - Multi-Lingual (Fresh)",
    "response_engine": {
        "type": "retell-llm",
        "llm_id": new_llm_id
    },
    "language": "multi",
    "voice_id": "11labs-Grace",
    "begin_message": "Hello, this is Sarah calling from DGA Management Group. How are you today?",
    "interruption_sensitivity": 1,
    "responsiveness": 1,
    "enable_backchannel": True
}

create_agent_response = requests.post("https://api.retellai.com/create-agent", headers=headers, json=new_agent_data)
if create_agent_response.status_code == 201:
    new_agent = create_agent_response.json()
    new_agent_id = new_agent["agent_id"]
    print(f"✓ New agent created: {new_agent_id}")
else:
    print(f"✗ Agent creation failed: {create_agent_response.status_code}")
    print(create_agent_response.text)
    exit(1)

# Step 5: Update phone number to use new agent
print("\nStep 5: Updating phone number to use new agent...")
update_phone_data = {
    "outbound_agent_id": new_agent_id
}

update_phone_response = requests.patch(f"https://api.retellai.com/update-phone-number/{PHONE_NUMBER}", headers=headers, json=update_phone_data)
if update_phone_response.status_code == 200:
    print(f"✓ Phone number {PHONE_NUMBER} now uses new agent")
else:
    print(f"✗ Phone update failed: {update_phone_response.status_code}")
    print(update_phone_response.text)
    exit(1)

print("\n" + "="*50)
print("✓ ALL STEPS COMPLETED SUCCESSFULLY")
print("="*50)
print(f"\nNew Agent ID: {new_agent_id}")
print(f"New LLM ID: {new_llm_id}")
print(f"Phone Number: {PHONE_NUMBER}")
print("\nThe agent is ready for testing.")
