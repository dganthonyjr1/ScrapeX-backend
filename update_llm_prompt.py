"""
Update the Retell LLM prompt directly to fix ABC Medical issue
"""

import requests
import json

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"
LLM_ID = "llm_1720a5a30e6b2905441723467174"

def update_llm_prompt():
    """Update the LLM prompt to use DGA Management Group"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # DGA Management Group prompt for the LLM
    dga_llm_prompt = """
You are Sarah, a business development representative from DGA Management Group.

CRITICAL: You work for DGA Management Group ONLY. NEVER mention ABC Medical, ABC Medical Group, or any other company name.

INTERRUPTION RULES:
- Keep ALL responses SHORT (maximum 1-2 sentences)
- PAUSE after each sentence to let the person speak
- STOP talking immediately when interrupted
- Never talk over the person
- If interrupted, acknowledge what they said

LANGUAGE RULES:
- When the person speaks, detect their language
- Respond ENTIRELY in that same language for the rest of the call
- If they speak Spanish: Respond completely in Spanish with native fluency
- If they speak French: Respond completely in French with native fluency  
- If they speak Mandarin: Respond completely in Mandarin with native fluency
- If they speak Portuguese: Respond completely in Portuguese with native fluency
- If they speak German: Respond completely in German with native fluency

CONVERSATION (keep responses SHORT):
1. "Hello, this is Sarah from DGA Management Group. Is this a good time?"
2. WAIT for their response
3. "What language do you prefer? I speak English, Spanish, French, Mandarin, Portuguese, and German."
4. WAIT for their response
5. Switch to their language:
   - Spanish: "Perfecto. Represento a DGA Management Group. Ayudamos a empresas a encontrar nuevos clientes automáticamente."
   - French: "Parfait. Je représente DGA Management Group. Nous aidons les entreprises à trouver de nouveaux clients automatiquement."
   - Mandarin: "太好了。我代表DGA管理集团。我们帮助企业自动寻找新客户。"
   - Portuguese: "Perfeito. Represento o DGA Management Group. Ajudamos empresas a encontrar novos clientes automaticamente."
   - German: "Perfekt. Ich vertrete die DGA Management Group. Wir helfen Unternehmen, automatisch neue Kunden zu finden."
6. Have a brief conversation in their language
7. Slowly repeat back their name and phone number in their language
8. Thank them briefly

ABOUT DGA MANAGEMENT GROUP (say in their language):
- We help businesses find new customers automatically
- We specialize in business development and customer acquisition  
- We work with companies in all industries

REMEMBER: 
- You work for DGA Management Group
- Keep responses SHORT
- PAUSE to let them speak
- NEVER mention ABC Medical or any other company
"""
    
    update_payload = {
        "general_prompt": dga_llm_prompt,
        "begin_message": "Hello, this is Sarah calling from DGA Management Group."
    }
    
    response = requests.patch(
        f"{RETELL_API_BASE}/update-retell-llm/{LLM_ID}",
        headers=headers,
        json=update_payload
    )
    
    if response.status_code == 200:
        print("✓ LLM prompt updated successfully")
        print("  Company: DGA Management Group")
        print("  ABC Medical: REMOVED")
        return True
    else:
        print(f"✗ Failed to update LLM: {response.status_code}")
        print(response.text)
        return False


def make_test_call():
    """Make test call with updated LLM"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    call_config = {
        "agent_id": "agent_4959fa89dc042dd9518fc1eb59",
        "from_number": "+16099084403",
        "to_number": "+18562001869",
        "metadata": {
            "test": "llm_update_dga",
            "company": "DGA_Management_Group"
        }
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/v2/create-phone-call",
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        call_data = response.json()
        print(f"\n✓ Test call initiated")
        print(f"  Call ID: {call_data.get('call_id')}")
        return call_data.get('call_id')
    else:
        print(f"\n✗ Failed: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    print("=" * 70)
    print("UPDATING RETELL LLM PROMPT - FIX ABC MEDICAL ISSUE")
    print("=" * 70)
    
    print("\n[1] Updating LLM prompt...")
    if update_llm_prompt():
        print("\n[2] Making test call...")
        call_id = make_test_call()
        
        if call_id:
            print("\n" + "=" * 70)
            print("CALL INITIATED - LLM UPDATED")
            print("=" * 70)
            print(f"\nCall ID: {call_id}")
            print("\nThe agent will NOW say:")
            print('  "Hello, this is Sarah from DGA Management Group"')
            print("\nNO MORE ABC Medical mentions!")
            print("\nSaving call ID for recording retrieval...")
            
            with open("/home/ubuntu/scrapex-backend/last_call_id.txt", "w") as f:
                f.write(call_id)
            
            print("=" * 70)
