# SMS Payment Link Implementation Summary

## ✓ COMPLETED WORK

### 1. Backend Webhook Handler
**File:** `/home/ubuntu/scrapex-backend/retell_webhook_handler.py`

Created a webhook handler that:
- Receives function calls from Retell AI agent
- Handles `send_payment_link` function with customer type detection
- Sends SMS via Retell's SMS API with appropriate Stripe payment link
- Logs all SMS sending activity

**Payment Links:**
- Chamber/Tourism: `https://buy.stripe.com/7sY8wRaUt8tK4woazL` (50% off + 15% revenue share)
- Regular Business: `https://buy.stripe.com/28E14p4w5aBS4wo4bn` (Pro Plan)

### 2. FastAPI Webhook Endpoint
**File:** `/home/ubuntu/scrapex-backend/main.py`

Added endpoint: `POST /api/v1/retell/webhook`

Handles:
- `function_call` events (send_payment_link)
- `call_started` events
- `call_ended` events

### 3. Agent LLM Prompt
**File:** `/home/ubuntu/scrapex-backend/enhanced_llm_prompt_with_sms.txt`

Updated agent prompt with:
- Multi-lingual support (English, Spanish, French, Mandarin, Portuguese, German)
- Data validation (repeats contact info slowly in each language)
- **SMS payment link capability (HIDDEN FEATURE)**
  - Agent NEVER mentions it proactively
  - Only sends when customer explicitly asks
  - Asks customer type before sending (Chamber vs Regular)

### 4. Agent Configuration
**Agent ID:** `agent_05e8f725879b2997086400e39f`
**LLM ID:** `llm_c934afcf3083aa0bd590693df4cc`
**Webhook URL:** `https://scrapex-backend.onrender.com/api/v1/retell/webhook`

✓ Agent linked to LLM with SMS capability
✓ Webhook URL configured
✓ Begin message set: "Hello, this is Sarah calling from DGA Management Group. How are you today?"

### 5. Deployment
✓ Backend code pushed to GitHub
✓ Auto-deployed to Render: `https://scrapex-backend.onrender.com`
✓ Webhook endpoint is live and ready

## ⚠️ REMAINING MANUAL STEPS

### Step 1: Add Custom Tool in Retell Dashboard

You need to add the `send_payment_link` function as a custom tool in the Retell dashboard:

1. Go to: https://dashboard.retellai.com/agents
2. Find agent: `DGA Management Group - Multi-Lingual (Fresh)`
3. Click "Edit Agent"
4. Scroll to "Custom Tools" or "Function Calling" section
5. Add new custom tool:

```json
{
  "name": "send_payment_link",
  "description": "Send a payment link via SMS to the customer's phone number. Only call this when the customer explicitly asks for a payment link or asks how to sign up.",
  "parameters": {
    "type": "object",
    "properties": {
      "customer_type": {
        "type": "string",
        "enum": ["chamber", "regular"],
        "description": "Type of customer: 'chamber' for Chamber of Commerce or Tourism board, 'regular' for regular business"
      }
    },
    "required": ["customer_type"]
  }
}
```

6. Save the agent

### Step 2: Enable SMS on Phone Number

Your phone number (+16099084403) needs SMS capabilities enabled:

1. Go to: https://dashboard.retellai.com/phone-numbers
2. Find phone number: +16099084403
3. Click "Enable SMS" or "Setup SMS"
4. Follow the A2P 10DLC registration process:
   - Business Profile (free)
   - Brand Registration ($4-45 one-time)
   - SMS Campaign ($15 one-time)
5. Wait for approval (2-3 weeks)

**Alternative:** If you already have SMS enabled on this number, skip this step.

## HOW IT WORKS

### Customer Flow:
1. Customer receives call from Sarah (AI agent)
2. Agent asks language preference
3. Agent pitches DGA Management Group services
4. **Customer asks:** "Can you send me a payment link?"
5. **Agent asks:** "Are you with a Chamber of Commerce or Tourism board?"
6. Customer answers: "Yes" or "No"
7. **Agent calls function:** `send_payment_link(customer_type="chamber" or "regular")`
8. **Retell sends webhook** to your backend
9. **Backend sends SMS** with appropriate Stripe payment link
10. **Customer receives SMS** within seconds

### Technical Flow:
```
Customer asks for link
    ↓
Agent invokes send_payment_link function
    ↓
Retell AI sends webhook to:
https://scrapex-backend.onrender.com/api/v1/retell/webhook
    ↓
Backend determines payment link based on customer_type
    ↓
Backend calls Retell SMS API:
POST https://api.retellai.com/create-outbound-sms
    ↓
Customer receives SMS with payment link
```

## TESTING

Once you complete the manual steps above, you can test by:

1. Making a test call to the agent
2. Saying: "Can you send me a payment link?"
3. When asked, say either:
   - "Yes, I'm with a Chamber of Commerce" → Gets Chamber link
   - "No, I'm a regular business" → Gets Regular Business link
4. Check your phone for SMS with Stripe payment link

## FILES CREATED

- `retell_webhook_handler.py` - Webhook handler for function calls
- `enhanced_llm_prompt_with_sms.txt` - Updated agent prompt
- `add_sms_payment_link.py` - Script to configure agent
- `configure_agent_webhook.py` - Script to set webhook URL
- `fix_agent_response_engine.py` - Script to link LLM to agent
- `verify_agent_config.py` - Verification script

## NEXT STEPS

1. Complete manual Step 1 (Add custom tool in dashboard)
2. Complete manual Step 2 (Enable SMS on phone number)
3. Test the functionality with a live call
4. Monitor webhook logs in Render dashboard
5. Verify SMS delivery and correct payment links

## SUPPORT

If you encounter issues:
- Check Render logs: https://dashboard.render.com/
- Check Retell dashboard: https://dashboard.retellai.com/
- Verify webhook is receiving requests
- Check SMS is enabled on phone number
