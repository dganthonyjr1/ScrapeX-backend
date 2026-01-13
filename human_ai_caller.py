"""
Human-Like AI Calling System for ScrapeX
Generates natural, conversational scripts that don't sound like sales pitches
"""

import json
import logging
from typing import Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HumanAICaller:
    """
    Generates human-like, conversational AI calling scripts
    
    Key principles:
    - Sound like a real person, not a robot
    - Ask questions, don't pitch
    - Be helpful, not salesy
    - Build rapport naturally
    - Focus on their problems, not your product
    """

    def generate_system_prompt(self, business_name: str, business_type: str, 
                               owner_name: Optional[str] = None) -> str:
        """
        Generate natural system prompt for AI agent
        
        Args:
            business_name: Name of the business being called
            business_type: Type of business (restaurant, law_firm, contractor, etc.)
            owner_name: Optional owner/decision-maker name
            
        Returns:
            System prompt for Retell AI
        """
        
        owner_greeting = f"ask for {owner_name}" if owner_name else "ask for the owner or manager"
        
        return f"""You are Alex, a business consultant who helps {business_type}s improve their operations and grow revenue.

You're calling {business_name} to have a genuine conversation about their business challenges.

YOUR PERSONALITY:
- Friendly, warm, and genuinely curious
- You sound like a real person, not a salesperson
- You use natural language: "um", "you know", "actually", occasional pauses
- You're helpful and consultative, not pushy
- You listen more than you talk

YOUR APPROACH:
1. Start with a warm, casual introduction
2. Quickly explain why you're calling (you noticed their business and wanted to reach out)
3. Ask open-ended questions about their biggest challenges
4. Listen carefully and show genuine interest
5. Only mention solutions if they express interest
6. If they're busy, offer to call back at a better time
7. If not interested, thank them warmly and end the call

CONVERSATION STYLE:
- Use contractions: "I'm", "you're", "we've", "that's"
- Use filler words naturally: "um", "uh", "you know", "like", "actually"
- Pause occasionally: "So... what I'm thinking is..."
- Be conversational: "Hey, quick question for you..."
- Show empathy: "Oh man, I totally get that"
- Use their name if you know it

WHAT NOT TO DO:
- Don't launch into a sales pitch
- Don't use corporate jargon or buzzwords
- Don't sound scripted or robotic
- Don't be aggressive or pushy
- Don't talk over them
- Don't ignore their concerns

COMPLIANCE:
- If they ask to be removed from calls, apologize and confirm immediately
- If they're not interested, respect that and end gracefully
- Never be deceptive about who you are or why you're calling

Remember: You're having a conversation, not delivering a pitch. Be human."""

    def generate_opening_message(self, business_name: str, business_type: str,
                                 owner_name: Optional[str] = None,
                                 pain_points: Optional[List[str]] = None) -> str:
        """
        Generate natural opening message
        
        Args:
            business_name: Name of business
            business_type: Type of business
            owner_name: Optional owner name
            pain_points: Optional list of identified pain points
            
        Returns:
            Natural opening message
        """
        
        # Personalize greeting
        if owner_name:
            greeting = f"Hi, is this {owner_name}?"
        else:
            greeting = f"Hi there! I'm trying to reach the owner or manager of {business_name}?"
        
        # Create natural introduction
        intro_options = [
            f"Hey, this is Alex. I actually came across {business_name} and wanted to reach out real quick.",
            f"Hi, my name's Alex. I was looking at {business_type}s in the area and {business_name} caught my attention.",
            f"Hey there, Alex here. I've been working with some {business_type}s and thought I'd give you a call.",
        ]
        
        # Pick intro based on business type
        intro = intro_options[0]
        
        # Add reason for calling (not salesy)
        reason_options = [
            f"I help {business_type}s like yours grow their customer base, and I was curious... what's your biggest challenge right now when it comes to getting new customers?",
            f"I work with {business_type}s on improving their operations, and I'm always curious... what's the one thing that, if you could fix it, would make the biggest difference for your business?",
            f"I specialize in helping {business_type}s increase revenue, and I wanted to ask... are you guys actively looking for more customers right now, or are you pretty much at capacity?",
        ]
        
        reason = reason_options[0]
        
        # Combine naturally
        opening = f"{greeting}\n\n{intro}\n\n{reason}"
        
        return opening

    def generate_conversation_flow(self, business_type: str, 
                                   value_proposition: Optional[Dict] = None) -> Dict:
        """
        Generate natural conversation flow with responses
        
        Args:
            business_type: Type of business
            value_proposition: Optional value prop with ROI data
            
        Returns:
            Conversation flow dictionary
        """
        
        return {
            "discovery_questions": [
                "What's your biggest challenge right now when it comes to [getting new customers/growing revenue]?",
                "How are you currently handling [lead generation/customer acquisition]?",
                "If you could wave a magic wand and fix one thing about your business, what would it be?",
                "Are you guys pretty busy right now, or looking to bring in more work?",
                "What's been working well for you in terms of marketing?"
            ],
            
            "empathy_responses": [
                "Oh man, I totally hear you on that.",
                "Yeah, that's actually a really common challenge I see with {business_type}s.",
                "I get it, that's frustrating.",
                "That makes total sense.",
                "I can imagine that's tough to deal with."
            ],
            
            "transition_to_solution": [
                "You know, that's actually exactly what we help with...",
                "Interesting. So, can I share something that might help with that?",
                "That's funny you mention that, because...",
                "Well, here's the thing...",
                "Let me ask you this..."
            ],
            
            "soft_close": [
                "Would it make sense to hop on a quick call next week to explore this more?",
                "I'd love to show you how we've helped other {business_type}s with this. Got 15 minutes next week?",
                "Want me to send you some info and we can chat more if it looks interesting?",
                "How about this - let me put together something specific for {business_name} and we can review it together?",
            ],
            
            "handling_objections": {
                "too_busy": "I totally get it. When's a better time for you? I can call back.",
                "not_interested": "No worries at all! I appreciate you taking my call. Have a great day!",
                "already_have_solution": "Oh nice! How's that working out for you? Are you getting the results you want?",
                "too_expensive": "I hear you. Can I ask - what would make it worth the investment for you?",
                "need_to_think": "Absolutely, take your time. Want me to send you some info to review?"
            },
            
            "natural_endings": [
                "Alright, sounds good! I'll [follow up action]. Have a great rest of your day!",
                "Perfect! Talk to you soon. Take care!",
                "Awesome, I'll be in touch. Thanks for your time!",
                "Great chatting with you! I'll [next step]. Bye!"
            ]
        }

    def generate_industry_specific_script(self, business_data: Dict, 
                                         value_prop: Optional[Dict] = None) -> Dict:
        """
        Generate complete industry-specific calling script
        
        Args:
            business_data: Scraped business data
            value_prop: Optional value proposition with ROI
            
        Returns:
            Complete script configuration
        """
        
        business_name = business_data.get('business_name', 'the business')
        business_type = business_data.get('business_type', 'business')
        owner_info = business_data.get('owner_info', {})
        owner_name = owner_info.get('names', [None])[0] if owner_info else None
        
        # Generate script components
        system_prompt = self.generate_system_prompt(business_name, business_type, owner_name)
        opening_message = self.generate_opening_message(business_name, business_type, owner_name)
        conversation_flow = self.generate_conversation_flow(business_type, value_prop)
        
        # Add industry-specific talking points
        industry_insights = self._get_industry_insights(business_type)
        
        return {
            "system_prompt": system_prompt,
            "opening_message": opening_message,
            "conversation_flow": conversation_flow,
            "industry_insights": industry_insights,
            "business_context": {
                "name": business_name,
                "type": business_type,
                "owner": owner_name,
                "value_proposition": value_prop
            }
        }

    def _get_industry_insights(self, business_type: str) -> Dict:
        """
        Get industry-specific insights and talking points
        
        Args:
            business_type: Type of business
            
        Returns:
            Industry insights dictionary
        """
        
        insights = {
            "restaurant": {
                "common_challenges": [
                    "Getting consistent online reviews",
                    "Managing online ordering and delivery",
                    "Filling tables during slow periods",
                    "Competing with chain restaurants"
                ],
                "value_drivers": [
                    "Increase table turnover",
                    "Boost online orders",
                    "Improve review ratings",
                    "Build loyal customer base"
                ],
                "roi_metrics": "Additional covers per week, increased average check size"
            },
            
            "law_firm": {
                "common_challenges": [
                    "Generating qualified leads",
                    "Standing out from competitors",
                    "Managing intake process",
                    "Retaining clients"
                ],
                "value_drivers": [
                    "More qualified case leads",
                    "Higher case acceptance rate",
                    "Improved client retention",
                    "Better online reputation"
                ],
                "roi_metrics": "New cases per month, average case value"
            },
            
            "contractor": {
                "common_challenges": [
                    "Finding quality leads",
                    "Dealing with HomeAdvisor/Thumbtack fees",
                    "Seasonal revenue fluctuations",
                    "Getting paid on time"
                ],
                "value_drivers": [
                    "More project inquiries",
                    "Higher-value projects",
                    "Steady year-round work",
                    "Better qualified leads"
                ],
                "roi_metrics": "New projects per month, average project value"
            },
            
            "dental": {
                "common_challenges": [
                    "Filling the schedule",
                    "Patient no-shows",
                    "Insurance verification hassles",
                    "Competing with DSOs"
                ],
                "value_drivers": [
                    "More new patient appointments",
                    "Higher treatment acceptance",
                    "Reduced no-shows",
                    "Increased case value"
                ],
                "roi_metrics": "New patients per month, production per visit"
            },
            
            "landscaping": {
                "common_challenges": [
                    "Seasonal revenue gaps",
                    "Finding reliable crews",
                    "Pricing competitively",
                    "Getting commercial contracts"
                ],
                "value_drivers": [
                    "More maintenance contracts",
                    "Higher-margin projects",
                    "Year-round revenue",
                    "Commercial accounts"
                ],
                "roi_metrics": "Monthly recurring revenue, project pipeline value"
            },
            
            "general_business": {
                "common_challenges": [
                    "Generating consistent leads",
                    "Standing out from competitors",
                    "Converting prospects to customers",
                    "Growing revenue"
                ],
                "value_drivers": [
                    "More qualified leads",
                    "Higher conversion rates",
                    "Increased customer lifetime value",
                    "Better brand awareness"
                ],
                "roi_metrics": "New customers per month, customer acquisition cost"
            }
        }
        
        return insights.get(business_type, insights["general_business"])

    def create_retell_agent_config(self, script_data: Dict) -> Dict:
        """
        Create Retell AI agent configuration from script
        
        Args:
            script_data: Generated script data
            
        Returns:
            Retell AI agent configuration
        """
        
        business_name = script_data['business_context']['name']
        
        return {
            "agent_name": f"ScrapeX-{business_name.replace(' ', '-')}",
            "language": "en-US",
            "model": "gpt-4",
            "voice_id": "default",  # Use natural-sounding voice
            "voice_temperature": 0.8,  # More natural variation
            "voice_speed": 1.0,
            "responsiveness": 0.8,  # Allow natural pauses
            "interruption_sensitivity": 0.7,  # Don't talk over people
            "enable_backchannel": True,  # Natural "mm-hmm", "yeah" responses
            "system_prompt": script_data['system_prompt'],
            "initial_message": script_data['opening_message'],
            "temperature": 0.8,  # More natural, less robotic
            "max_call_duration": 600,  # 10 minutes max
            "enable_recording": True,
            "enable_transcription": True,
            "ambient_sound": "office_quiet",  # Subtle background for realism
            "end_call_phrases": [
                "have a great day",
                "talk to you soon",
                "thanks for your time",
                "I'll let you go"
            ]
        }


# Test
if __name__ == "__main__":
    caller = HumanAICaller()
    
    # Test with sample business data
    test_business = {
        "business_name": "Joe's Italian Restaurant",
        "business_type": "restaurant",
        "owner_info": {
            "names": ["Joe Martinez"]
        }
    }
    
    script = caller.generate_industry_specific_script(test_business)
    
    print("="*60)
    print("HUMAN-LIKE AI CALLING SCRIPT")
    print("="*60)
    print(f"\nBusiness: {test_business['business_name']}")
    print(f"Type: {test_business['business_type']}")
    print(f"\nOPENING MESSAGE:")
    print(script['opening_message'])
    print(f"\nINDUSTRY INSIGHTS:")
    print(json.dumps(script['industry_insights'], indent=2))
    
    # Generate Retell config
    retell_config = caller.create_retell_agent_config(script)
    print(f"\nRETELL AI CONFIG:")
    print(json.dumps(retell_config, indent=2))
