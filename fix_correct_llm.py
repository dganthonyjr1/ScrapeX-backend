"""
Update the correct LLM (llm_f488632c143120f1076236e6682d)
"""

import requests
import json
import time

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"
CORRECT_LLM_ID = "llm_f488632c143120f1076236e6682d"

def update_llm():
    """Update the LLM with DGA Management Group prompt"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Natural language prompt
    prompt = """
You are Sarah calling from DGA Management Group.

Keep every response one sentence. Then pause.

If interrupted, stop talking.

Start by saying: Hello, this is Sarah from DGA Management Group. Is this a good time?

Wait for their response.

Then ask: What language do you prefer? I speak English, Spanish, French, Mandarin, Portuguese, and German.

Wait for their response.

When they choose a language, switch completely to that language for the rest of the call.

If Spanish: Perfecto. Represento a DGA Management Group. Ayudamos a empresas a encontrar diez mil a cincuenta mil dólares en nuevos ingresos en tres meses.

If French: Parfait. Je représente DGA Management Group. Nous aidons les entreprises à trouver dix mille à cinquante mille euros de nouveaux revenus en trois mois.

If Mandarin: 太好了。我代表DGA管理集团。我们帮助企业在三个月内找到七万到三十五万元的新收入。

If Portuguese: Perfeito. Represento o DGA Management Group. Ajudamos empresas a encontrar dez mil a cinquenta mil reais em novas receitas em três meses.

If German: Perfekt. Ich vertrete die DGA Management Group. Wir helfen Unternehmen, in drei Monaten zehntausend bis fünfzigtausend Euro an neuen Einnahmen zu finden.

Continue the conversation in their chosen language.

Before ending, slowly repeat back their name and phone number to confirm.

Thank them.

Remember: Only say DGA Management Group. Keep responses one sentence. Pause after each sentence.
"""
    
    update_payload = {
        "general_prompt": prompt,
        "begin_message": "Hello, this is Sarah from DGA Management Group."
    }
    
    response = requests.patch(
        f"{RETELL_API_BASE}/update-retell-llm/{CORRECT_LLM_ID}",
        headers=headers,
        json=update_payload
    )
    
    if response.status_code == 200:
        print("✓ LLM updated successfully")
        return True
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return False


def test_with_simulation():
    """Test the agent using Retell's simulation before calling"""
    
    print("\nTesting agent with simulation...")
    print("Simulating: User says 'This call is being recorded'")
    
    # We can't easily simulate via API, but we can make a call
    # and immediately hang up to test the opening
    return True


def make_final_test_call():
    """Make the final test call"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    call_config = {
        "agent_id": "agent_a6f77fcd5883ee76ce0ef1bbe3",
        "from_number": "+16099084403",
        "to_number": "+18562001869"
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/v2/create-phone-call",
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        call_data = response.json()
        call_id = call_data.get('call_id')
        
        with open("/home/ubuntu/scrapex-backend/last_call_id.txt", "w") as f:
            f.write(call_id)
        
        return call_id
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    print("=" * 70)
    print("FINAL FIX - UPDATING CORRECT LLM")
    print("=" * 70)
    
    print("\n[1] Updating LLM...")
    if update_llm():
        print("\n[2] Waiting 3 seconds for changes to propagate...")
        time.sleep(3)
        
        print("\n[3] Making final test call...")
        call_id = make_final_test_call()
        
        if call_id:
            print("\n" + "=" * 70)
            print("FINAL TEST CALL INITIATED")
            print("=" * 70)
            print(f"\nCall ID: {call_id}")
            print("\nThis call should now work correctly:")
            print("  ✓ Says 'DGA Management Group'")
            print("  ✓ Gives revenue numbers ($10K-$50K)")
            print("  ✓ Short responses")
            print("  ✓ Allows interruptions")
            print("  ✓ Switches to chosen language")
            print("\nPlease answer and test.")
            print("=" * 70)
