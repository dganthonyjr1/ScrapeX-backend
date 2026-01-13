"""
Multi-lingual AI Caller for ScrapeX
Automatically detects and responds in Spanish, French, Mandarin, Portuguese, and German
"""

import os
import logging
from typing import Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultilingualAICaller:
    """
    AI caller that automatically detects and responds in multiple languages
    
    Supported Languages:
    - English (en-US)
    - Spanish (es-ES, es-MX)
    - French (fr-FR)
    - Mandarin Chinese (zh-CN)
    - Portuguese (pt-BR, pt-PT)
    - German (de-DE)
    """

    # Language configurations
    SUPPORTED_LANGUAGES = {
        'en-US': {
            'name': 'English (US)',
            'greeting': 'Hello',
            'voice_id': 'elevenlabs-default-en',
            'tts_provider': 'elevenlabs'
        },
        'es-ES': {
            'name': 'Spanish (Spain)',
            'greeting': 'Hola',
            'voice_id': 'elevenlabs-default-es',
            'tts_provider': 'elevenlabs'
        },
        'es-MX': {
            'name': 'Spanish (Mexico)',
            'greeting': 'Hola',
            'voice_id': 'elevenlabs-default-es-mx',
            'tts_provider': 'elevenlabs'
        },
        'fr-FR': {
            'name': 'French',
            'greeting': 'Bonjour',
            'voice_id': 'elevenlabs-default-fr',
            'tts_provider': 'elevenlabs'
        },
        'zh-CN': {
            'name': 'Mandarin Chinese',
            'greeting': '你好',
            'voice_id': 'elevenlabs-default-zh',
            'tts_provider': 'elevenlabs'
        },
        'pt-BR': {
            'name': 'Portuguese (Brazil)',
            'greeting': 'Olá',
            'voice_id': 'elevenlabs-default-pt-br',
            'tts_provider': 'elevenlabs'
        },
        'pt-PT': {
            'name': 'Portuguese (Portugal)',
            'greeting': 'Olá',
            'voice_id': 'elevenlabs-default-pt',
            'tts_provider': 'elevenlabs'
        },
        'de-DE': {
            'name': 'German',
            'greeting': 'Guten Tag',
            'voice_id': 'elevenlabs-default-de',
            'tts_provider': 'elevenlabs'
        }
    }

    def __init__(self, retell_api_key: Optional[str] = None):
        """
        Initialize multi-lingual caller
        
        Args:
            retell_api_key: Retell AI API key (defaults to env variable)
        """
        self.retell_api_key = retell_api_key or os.getenv('RETELL_API_KEY')
        if not self.retell_api_key:
            logger.warning("Retell API key not found. Multi-lingual calling disabled.")

    def create_multilingual_agent_config(self, 
                                        company_name: str,
                                        value_proposition: str,
                                        industry: str = "general") -> Dict:
        """
        Create Retell AI agent configuration with multi-lingual support
        
        Args:
            company_name: Name of the company making the call
            value_proposition: What the company offers
            industry: Industry type for customization
            
        Returns:
            Agent configuration dict
        """
        
        # Multi-lingual prompt that instructs the agent to detect and respond in the caller's language
        multilingual_prompt = f"""
You are a professional business development representative calling on behalf of {company_name}.

CRITICAL LANGUAGE INSTRUCTION:
- Automatically detect the language the person speaks when they answer the phone
- Respond in the SAME language they use throughout the entire conversation
- If they speak Spanish, respond in Spanish
- If they speak French, respond in French  
- If they speak Mandarin, respond in Mandarin
- If they speak Portuguese, respond in Portuguese
- If they speak German, respond in German
- If they speak English, respond in English
- Never ask what language they prefer - just match their language automatically

YOUR ROLE:
You are calling to introduce {company_name} and explain how we help businesses like theirs.

WHAT WE OFFER:
{value_proposition}

CONVERSATION FLOW:
1. Greet them warmly in their language
2. Introduce yourself and {company_name} briefly
3. Ask if they have a moment to discuss how we help businesses in their industry
4. If yes, explain our value proposition in 2-3 sentences
5. Ask if they would be interested in learning more
6. If interested, offer to schedule a brief meeting or send information
7. CRITICAL DATA VALIDATION: Before ending the call, repeat back the contact's name, email, and phone number slowly and clearly to confirm you have the correct information. For example: 'So I have your name as... your email as... and your phone number as... Is that correct?'
8. Thank them for their time regardless of outcome

TONE AND STYLE:
- Be friendly, professional, and conversational
- Speak naturally like a real person, not a robot
- Be respectful of their time
- Listen actively and respond to their questions
- If they seem busy, offer to call back at a better time
- If they're not interested, thank them politely and end the call

IMPORTANT:
- Keep the call under 2 minutes unless they want to talk longer
- Focus on building rapport, not making a hard sell
- The goal is to book a meeting or send information, not close a deal on the phone
- Be culturally sensitive and adapt your approach to their communication style
"""

        # Agent configuration for Retell AI
        agent_config = {
            "agent_name": f"{company_name} - Multilingual Outreach Agent",
            "language": "multilingual",  # Enables automatic language detection
            "voice_id": "elevenlabs-default",  # Will auto-select based on detected language
            "voice_temperature": 0.7,  # Natural, conversational tone
            "voice_speed": 1.0,
            "responsiveness": 0.8,  # Balanced between listening and responding
            "interruption_sensitivity": 0.5,  # Allow natural conversation flow
            "llm_model": "gpt-4",  # Best for multi-lingual understanding
            "llm_temperature": 0.7,
            "general_prompt": multilingual_prompt,
            "general_tools": [],
            "begin_message": None,  # Let the agent detect language first
            "boosted_keywords": [
                company_name,
                "meeting",
                "appointment",
                "interested",
                "information"
            ],
            "enable_backchannel": True,  # Natural "uh-huh", "I see" responses
            "ambient_sound": "office",
            "language_detection": True,  # Enable automatic language detection
            "supported_languages": [
                "en-US", "es-ES", "es-MX", "fr-FR", 
                "zh-CN", "pt-BR", "pt-PT", "de-DE"
            ]
        }
        
        return agent_config

    def generate_language_specific_scripts(self) -> Dict[str, Dict]:
        """
        Generate conversation scripts for each supported language
        
        Returns:
            Dictionary of language-specific scripts
        """
        scripts = {
            'en-US': {
                'greeting': 'Hello, is this {contact_name}?',
                'introduction': 'My name is Sarah, and I\'m calling from {company_name}.',
                'value_prop': 'We help businesses like yours {value_proposition}.',
                'question': 'Would you be interested in learning more about how we can help your business?',
                'schedule': 'Great! Would you have 15 minutes this week for a quick call?',
                'closing': 'Thank you for your time. Have a great day!'
            },
            'es-ES': {
                'greeting': 'Hola, ¿hablo con {contact_name}?',
                'introduction': 'Mi nombre es Sarah y llamo de {company_name}.',
                'value_prop': 'Ayudamos a empresas como la suya {value_proposition}.',
                'question': '¿Le interesaría saber más sobre cómo podemos ayudar a su negocio?',
                'schedule': '¡Excelente! ¿Tendría 15 minutos esta semana para una llamada rápida?',
                'closing': 'Gracias por su tiempo. ¡Que tenga un buen día!'
            },
            'fr-FR': {
                'greeting': 'Bonjour, est-ce que je parle avec {contact_name}?',
                'introduction': 'Je m\'appelle Sarah et j\'appelle de {company_name}.',
                'value_prop': 'Nous aidons les entreprises comme la vôtre {value_proposition}.',
                'question': 'Seriez-vous intéressé à en savoir plus sur comment nous pouvons aider votre entreprise?',
                'schedule': 'Parfait! Auriez-vous 15 minutes cette semaine pour un appel rapide?',
                'closing': 'Merci pour votre temps. Bonne journée!'
            },
            'zh-CN': {
                'greeting': '你好，请问是{contact_name}吗？',
                'introduction': '我叫Sarah，来自{company_name}。',
                'value_prop': '我们帮助像您这样的企业{value_proposition}。',
                'question': '您有兴趣了解更多关于我们如何帮助您的业务吗？',
                'schedule': '太好了！您本周有15分钟时间进行快速通话吗？',
                'closing': '感谢您的时间。祝您有美好的一天！'
            },
            'pt-BR': {
                'greeting': 'Olá, falo com {contact_name}?',
                'introduction': 'Meu nome é Sarah e estou ligando da {company_name}.',
                'value_prop': 'Ajudamos empresas como a sua {value_proposition}.',
                'question': 'Você estaria interessado em saber mais sobre como podemos ajudar seu negócio?',
                'schedule': 'Ótimo! Você teria 15 minutos esta semana para uma ligação rápida?',
                'closing': 'Obrigado pelo seu tempo. Tenha um ótimo dia!'
            },
            'de-DE': {
                'greeting': 'Guten Tag, spreche ich mit {contact_name}?',
                'introduction': 'Mein Name ist Sarah und ich rufe von {company_name} an.',
                'value_prop': 'Wir helfen Unternehmen wie Ihrem {value_proposition}.',
                'question': 'Würden Sie daran interessiert sein, mehr darüber zu erfahren, wie wir Ihrem Unternehmen helfen können?',
                'schedule': 'Großartig! Hätten Sie diese Woche 15 Minuten Zeit für einen kurzen Anruf?',
                'closing': 'Vielen Dank für Ihre Zeit. Einen schönen Tag noch!'
            }
        }
        
        return scripts

    def create_call_request(self,
                          phone_number: str,
                          contact_name: str,
                          company_name: str,
                          business_type: str,
                          value_proposition: str,
                          preferred_language: Optional[str] = None) -> Dict:
        """
        Create a call request with multi-lingual support
        
        Args:
            phone_number: Phone number to call
            contact_name: Name of the contact
            company_name: Name of the business being called
            business_type: Type of business
            value_proposition: What you're offering
            preferred_language: Optional preferred language (will auto-detect if not provided)
            
        Returns:
            Call request dictionary
        """
        
        agent_config = self.create_multilingual_agent_config(
            company_name=company_name,
            value_proposition=value_proposition,
            industry=business_type
        )
        
        call_request = {
            'phone_number': phone_number,
            'agent_config': agent_config,
            'metadata': {
                'contact_name': contact_name,
                'company_name': company_name,
                'business_type': business_type,
                'preferred_language': preferred_language or 'auto-detect',
                'created_at': datetime.now().isoformat()
            }
        }
        
        logger.info(f"Created multi-lingual call request for {contact_name} at {company_name}")
        
        return call_request


# Test function
def test_multilingual_caller():
    """Test the multi-lingual caller"""
    caller = MultilingualAICaller()
    
    # Test agent configuration
    config = caller.create_multilingual_agent_config(
        company_name="ScrapeX",
        value_proposition="automate customer acquisition and fill your sales pipeline with qualified leads",
        industry="B2B services"
    )
    
    print("Multi-lingual Agent Configuration:")
    print(f"Agent Name: {config['agent_name']}")
    print(f"Language: {config['language']}")
    print(f"Supported Languages: {', '.join(config['supported_languages'])}")
    print(f"Language Detection: {config['language_detection']}")
    
    # Test language-specific scripts
    scripts = caller.generate_language_specific_scripts()
    print("\nSupported Languages:")
    for lang_code, lang_config in caller.SUPPORTED_LANGUAGES.items():
        print(f"  {lang_config['name']} ({lang_code}): {lang_config['greeting']}")
    
    # Test call request
    call_request = caller.create_call_request(
        phone_number="+1234567890",
        contact_name="Maria Garcia",
        company_name="Garcia Restaurant",
        business_type="restaurant",
        value_proposition="increase catering revenue through corporate partnerships"
    )
    
    print("\nSample Call Request Created:")
    print(f"Phone: {call_request['phone_number']}")
    print(f"Contact: {call_request['metadata']['contact_name']}")
    print(f"Language Detection: {call_request['metadata']['preferred_language']}")
    
    return config


if __name__ == "__main__":
    test_multilingual_caller()
