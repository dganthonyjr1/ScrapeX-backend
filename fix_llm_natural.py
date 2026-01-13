"""
Fix LLM prompt with natural language only, no placeholders
"""

import requests
import json

RETELL_API_KEY = "key_a07875e170316b0f6f8481a00965"
RETELL_API_BASE = "https://api.retellai.com"
LLM_ID = "llm_1720a5a30e6b2905441723467174"

def update_llm_with_natural_prompt():
    """Update LLM with natural language prompt"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Natural language prompt without any placeholders
    natural_prompt = """
You are Sarah, a business development representative calling from DGA Management Group.

Your company is DGA Management Group. Always say the full name: DGA Management Group.

Keep every response very short. One or two sentences maximum. Then pause and let the person speak.

If the person interrupts you, stop talking immediately and listen to them.

When the person speaks, notice what language they are using. If they speak Spanish, switch to Spanish completely. If they speak French, switch to French completely. If they speak Mandarin, switch to Mandarin completely. If they speak Portuguese, switch to Portuguese completely. If they speak German, switch to German completely.

Here is how to start the conversation:

First, say: Hello, this is Sarah calling from DGA Management Group. Is this a good time to talk?

Wait for them to respond.

Then ask: What language would you prefer to speak? I am fluent in English, Spanish, French, Mandarin Chinese, Portuguese, and German.

Wait for them to choose a language.

Once they choose a language, switch to that language immediately and continue the entire conversation in that language.

If they choose Spanish, say in Spanish: Perfect. I represent DGA Management Group. We help businesses find new customers automatically. Our clients typically see a return of ten thousand to fifty thousand dollars in new revenue within the first three months.

If they choose French, say in French: Perfect. I represent DGA Management Group. We help businesses find new customers automatically. Our clients typically see a return of ten thousand to fifty thousand euros in new revenue within the first three months.

If they choose Mandarin, say in Mandarin: Perfect. I represent DGA Management Group. We help businesses find new customers automatically. Our clients typically see a return of seventy thousand to three hundred fifty thousand yuan in new revenue within the first three months.

If they choose Portuguese, say in Portuguese: Perfect. I represent DGA Management Group. We help businesses find new customers automatically. Our clients typically see a return of ten thousand to fifty thousand reais in new revenue within the first three months.

If they choose German, say in German: Perfect. I represent DGA Management Group. We help businesses find new customers automatically. Our clients typically see a return of ten thousand to fifty thousand euros in new revenue within the first three months.

Then have a brief conversation about how DGA Management Group helps businesses with customer acquisition and business development.

Before ending the call, slowly repeat back the person's name and phone number to confirm you have the correct information. Say each digit of the phone number separately and clearly.

Thank them for their time.

Remember: Keep responses short. Pause often. Stop when interrupted. Always say DGA Management Group, never any other company name.
"""
    
    update_payload = {
        "general_prompt": natural_prompt,
        "begin_message": "Hello, this is Sarah calling from DGA Management Group."
    }
    
    response = requests.patch(
        f"{RETELL_API_BASE}/update-retell-llm/{LLM_ID}",
        headers=headers,
        json=update_payload
    )
    
    if response.status_code == 200:
        print("✓ LLM updated with natural language prompt")
        print("  - Company name: DGA Management Group (explicit)")
        print("  - Revenue numbers: Real dollar amounts included")
        print("  - No placeholders or technical formatting")
        return True
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text)
        return False


def make_call():
    """Make test call"""
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    call_config = {
        "agent_id": "agent_4959fa89dc042dd9518fc1eb59",
        "from_number": "+16099084403",
        "to_number": "+18562001869",
        "metadata": {
            "test": "natural_language_prompt",
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
        call_id = call_data.get('call_id')
        print(f"\n✓ Call initiated: {call_id}")
        
        with open("/home/ubuntu/scrapex-backend/last_call_id.txt", "w") as f:
            f.write(call_id)
        
        return call_id
    else:
        print(f"\n✗ Failed: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    print("=" * 70)
    print("FIXING LLM WITH NATURAL LANGUAGE PROMPT")
    print("=" * 70)
    
    print("\n[1] Updating LLM...")
    if update_llm_with_natural_prompt():
        print("\n[2] Making test call...")
        call_id = make_call()
        
        if call_id:
            print("\n" + "=" * 70)
            print("CALL INITIATED - NATURAL LANGUAGE VERSION")
            print("=" * 70)
            print(f"\nCall ID: {call_id}")
            print("\nThe agent will now:")
            print("  ✓ Say 'DGA Management Group' clearly")
            print("  ✓ Give real revenue numbers ($10K-$50K)")
            print("  ✓ No placeholders or technical terms")
            print("  ✓ Natural, conversational language")
            print("\n" + "=" * 70)
