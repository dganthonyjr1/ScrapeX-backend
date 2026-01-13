"""
Update the CORRECT agent that's actually being used by the phone number
"""

import requests
import json

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"
CORRECT_AGENT_ID = "agent_a6f77fcd5883ee76ce0ef1bbe3"  # The one actually being used

def get_agent_config():
    """Get the current agent configuration"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{RETELL_API_BASE}/get-agent/{CORRECT_AGENT_ID}",
        headers=headers
    )
    
    if response.status_code == 200:
        config = response.json()
        print("Current agent configuration:")
        print(f"  Agent ID: {config.get('agent_id')}")
        print(f"  Agent Name: {config.get('agent_name')}")
        print(f"  Response Engine: {config.get('response_engine')}")
        return config
    else:
        print(f"Failed to get agent: {response.status_code}")
        return None


def update_agent_properly():
    """Update the agent with DGA Management Group prompt"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Clean, natural prompt for DGA Management Group
    prompt = """
You are Sarah, calling from DGA Management Group.

Keep responses extremely short. One sentence, then pause.

If interrupted, stop immediately.

Start: Hello, this is Sarah from DGA Management Group. Is this a good time?

Wait for response.

Ask: What language do you prefer? I speak English, Spanish, French, Mandarin, Portuguese, and German.

Wait for response.

When they choose a language, switch completely to that language.

Spanish: Perfecto. Represento a DGA Management Group. Ayudamos a empresas a encontrar diez mil a cincuenta mil dólares en nuevos ingresos en tres meses.

French: Parfait. Je représente DGA Management Group. Nous aidons les entreprises à trouver dix mille à cinquante mille euros de nouveaux revenus en trois mois.

Mandarin: 太好了。我代表DGA管理集团。我们帮助企业在三个月内找到七万到三十五万元的新收入。

Portuguese: Perfeito. Represento o DGA Management Group. Ajudamos empresas a encontrar dez mil a cinquenta mil reais em novas receitas em três meses.

German: Perfekt. Ich vertrete die DGA Management Group. Wir helfen Unternehmen, in drei Monaten zehntausend bis fünfzigtausend Euro an neuen Einnahmen zu finden.

Continue conversation in their language.

Before ending, slowly repeat their name and phone number.

Thank them.

Remember: DGA Management Group only. Short responses. Pause often.
"""
    
    update_payload = {
        "general_prompt": prompt,
        "agent_name": "DGA Management Group - Multi-Lingual",
        "language": "multi",
        "responsiveness": 1.0,
        "interruption_sensitivity": 1.0,
        "enable_backchannel": True,
        "begin_message": "Hello, this is Sarah from DGA Management Group."
    }
    
    response = requests.patch(
        f"{RETELL_API_BASE}/update-agent/{CORRECT_AGENT_ID}",
        headers=headers,
        json=update_payload
    )
    
    if response.status_code == 200:
        print("\n✓ Agent updated successfully")
        print("  Company: DGA Management Group")
        print("  Revenue: $10K-$50K mentioned")
        print("  Multi-lingual: Enabled")
        return True
    else:
        print(f"\n✗ Failed: {response.status_code}")
        print(response.text)
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("UPDATING THE CORRECT AGENT")
    print("=" * 70)
    
    print("\n[1] Getting current configuration...")
    get_agent_config()
    
    print("\n[2] Updating agent...")
    if update_agent_properly():
        print("\n" + "=" * 70)
        print("AGENT UPDATED - READY FOR TESTING")
        print("=" * 70)
        print("\nThe agent will now:")
        print("  ✓ Say 'DGA Management Group'")
        print("  ✓ Give revenue numbers ($10K-$50K)")
        print("  ✓ Keep responses SHORT")
        print("  ✓ Allow interruptions")
        print("  ✓ Switch to chosen language")
        print("\nReady to make test call.")
        print("=" * 70)
