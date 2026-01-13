"""
Update agent with three customer types support
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

RETELL_API_KEY = os.environ.get("RETELL_API_KEY")
LLM_ID = "llm_c934afcf3083aa0bd590693df4cc"

headers = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json"
}

print("="*60)
print("UPDATING AGENT FOR THREE CUSTOMER TYPES")
print("="*60)

# Update LLM with new prompt
print("\n[1] Updating LLM prompt...")
with open("/home/ubuntu/scrapex-backend/enhanced_llm_prompt_three_types.txt", "r") as f:
    new_prompt = f.read()

llm_data = {
    "general_prompt": new_prompt
}

llm_response = requests.patch(
    f"https://api.retellai.com/update-retell-llm/{LLM_ID}",
    headers=headers,
    json=llm_data
)

if llm_response.status_code == 200:
    print("✓ LLM updated with three customer types")
else:
    print(f"✗ LLM update failed: {llm_response.status_code}")
    print(llm_response.text)
    exit(1)

print("\n" + "="*60)
print("✓ UPDATE COMPLETE")
print("="*60)
print("\nThe agent now supports three customer types:")
print("  1. Chamber/Tourism → Special partnership pricing")
print("  2. Healthcare → Pro Plan")
print("  3. General Business → Pro Plan")
print("\nAgent asks: 'What type of organization are you with?'")
print("  - Chamber of Commerce or Tourism board")
print("  - Healthcare facility")
print("  - Another type of business")
print("\nPayment Links:")
print("  - Chamber/Tourism: https://buy.stripe.com/7sY8wRaUt8tK4woazL")
print("  - Healthcare: https://buy.stripe.com/28E14p4w5aBS4wo4bn")
print("  - General: https://buy.stripe.com/28E14p4w5aBS4wo4bn")
