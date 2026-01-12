"""
Retell AI Integration Module
Handles autonomous calls using Retell AI platform
Includes TCPA compliance, consent tracking, and webhook handling
"""

import json
import logging
import os
import requests
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConsentStatus(Enum):
    """Consent status for calls"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REVOKED = "revoked"


class CallOutcome(Enum):
    """Possible call outcomes"""
    COMPLETED = "completed"
    NO_ANSWER = "no_answer"
    VOICEMAIL = "voicemail"
    DECLINED = "declined"
    FAILED = "failed"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"


class RetellAIIntegration:
    """
    Manages integration with Retell AI for autonomous calling
    Includes TCPA compliance, consent management, and call tracking
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Retell AI integration
        
        Args:
            api_key: Retell AI API key (defaults to RETELL_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('RETELL_API_KEY')
        self.base_url = "https://api.retellai.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            logger.warning("Retell AI API key not provided. Calls will be simulated.")
        
        # Call tracking
        self.call_records = {}
        self.consent_records = {}

    def create_agent(self, facility_name: str, call_script: str) -> Dict:
        """
        Create a Retell AI agent for a specific facility
        
        Args:
            facility_name: Name of the healthcare facility
            call_script: AI-generated call script
            
        Returns:
            Agent configuration dictionary
        """
        
        agent_config = {
            "agent_name": f"ScrapeX-{facility_name.replace(' ', '-')}",
            "agent_role": "Healthcare Sales Representative",
            "language": "en-US",
            "model": "gpt-4",
            "voice_id": "default",
            "system_prompt": self._generate_system_prompt(facility_name),
            "initial_message": call_script,
            "temperature": 0.7,
            "max_call_duration": 600,  # 10 minutes
            "enable_recording": True,
            "enable_transcription": True,
        }
        
        if self.api_key:
            try:
                response = requests.post(
                    f"{self.base_url}/agents",
                    headers=self.headers,
                    json=agent_config
                )
                response.raise_for_status()
                agent_data = response.json()
                logger.info(f"Agent created for {facility_name}: {agent_data.get('agent_id')}")
                return agent_data
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to create agent: {str(e)}")
                return {"error": str(e), "agent_id": None}
        else:
            # Simulated agent creation
            agent_data = {
                "agent_id": f"agent_{facility_name.replace(' ', '_')}_{datetime.now().timestamp()}",
                "agent_name": agent_config["agent_name"],
                "status": "created"
            }
            return agent_data

    def _generate_system_prompt(self, facility_name: str) -> str:
        """Generate system prompt for the AI agent"""
        
        return f"""You are a professional healthcare sales representative calling {facility_name}.

Your goal is to:
1. Introduce yourself and ScrapeX
2. Identify decision-makers and their pain points
3. Explain how ScrapeX can help their organization
4. Qualify the lead and schedule a follow-up call if interested

IMPORTANT COMPLIANCE REQUIREMENTS:
- You are calling on behalf of ScrapeX, a healthcare lead generation platform
- The recipient has consented to receive this call
- Be professional, courteous, and respectful
- If the recipient asks to be added to the Do Not Call list, honor that request immediately
- Do not be aggressive or pushy
- If the recipient is not interested, thank them and end the call
- Record all important information about the conversation

Keep responses concise and natural. Listen carefully to the recipient's responses."""

    def initiate_call(self, facility_name: str, phone_number: str, 
                     agent_id: str, consent_status: str = "pending") -> Dict:
        """
        Initiate a call to a healthcare facility
        
        Args:
            facility_name: Name of the facility
            phone_number: Phone number to call
            agent_id: Retell AI agent ID
            consent_status: TCPA consent status
            
        Returns:
            Call initiation response
        """
        
        # Check consent
        if consent_status != "accepted":
            return {
                "success": False,
                "error": "TCPA consent not accepted",
                "call_id": None
            }
        
        call_payload = {
            "agent_id": agent_id,
            "phone_number": phone_number,
            "from_number": os.getenv('RETELL_FROM_NUMBER', '+1234567890'),
            "webhook_url": os.getenv('WEBHOOK_URL', 'https://your-domain.com/webhook/retell'),
            "metadata": {
                "facility_name": facility_name,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        if self.api_key:
            try:
                response = requests.post(
                    f"{self.base_url}/calls",
                    headers=self.headers,
                    json=call_payload
                )
                response.raise_for_status()
                call_data = response.json()
                
                # Store call record
                call_id = call_data.get('call_id')
                self.call_records[call_id] = {
                    "facility_name": facility_name,
                    "phone_number": phone_number,
                    "agent_id": agent_id,
                    "initiated_at": datetime.now().isoformat(),
                    "status": "initiated",
                    "consent_status": consent_status
                }
                
                logger.info(f"Call initiated to {facility_name}: {call_id}")
                return {
                    "success": True,
                    "call_id": call_id,
                    "status": "initiated",
                    "facility_name": facility_name
                }
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to initiate call: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "call_id": None
                }
        else:
            # Simulated call
            call_id = f"call_{facility_name.replace(' ', '_')}_{datetime.now().timestamp()}"
            self.call_records[call_id] = {
                "facility_name": facility_name,
                "phone_number": phone_number,
                "agent_id": agent_id,
                "initiated_at": datetime.now().isoformat(),
                "status": "initiated",
                "consent_status": consent_status
            }
            return {
                "success": True,
                "call_id": call_id,
                "status": "initiated",
                "facility_name": facility_name,
                "note": "Simulated call (Retell API key not configured)"
            }

    def get_call_status(self, call_id: str) -> Dict:
        """
        Get the status of a call
        
        Args:
            call_id: Retell AI call ID
            
        Returns:
            Call status information
        """
        
        if self.api_key:
            try:
                response = requests.get(
                    f"{self.base_url}/calls/{call_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                call_data = response.json()
                return call_data
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to get call status: {str(e)}")
                return {"error": str(e)}
        else:
            # Return simulated status
            if call_id in self.call_records:
                return self.call_records[call_id]
            return {"error": "Call not found"}

    def get_call_recording(self, call_id: str) -> Dict:
        """
        Get the recording URL for a call
        
        Args:
            call_id: Retell AI call ID
            
        Returns:
            Recording URL and metadata
        """
        
        if self.api_key:
            try:
                response = requests.get(
                    f"{self.base_url}/calls/{call_id}/recording",
                    headers=self.headers
                )
                response.raise_for_status()
                recording_data = response.json()
                return recording_data
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to get recording: {str(e)}")
                return {"error": str(e)}
        else:
            # Simulated recording
            return {
                "recording_url": f"https://recordings.retellai.com/{call_id}.mp3",
                "duration": 180,
                "note": "Simulated recording URL"
            }

    def get_call_transcript(self, call_id: str) -> Dict:
        """
        Get the transcript of a call
        
        Args:
            call_id: Retell AI call ID
            
        Returns:
            Call transcript
        """
        
        if self.api_key:
            try:
                response = requests.get(
                    f"{self.base_url}/calls/{call_id}/transcript",
                    headers=self.headers
                )
                response.raise_for_status()
                transcript_data = response.json()
                return transcript_data
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to get transcript: {str(e)}")
                return {"error": str(e)}
        else:
            # Simulated transcript
            return {
                "transcript": "Agent: Hello, this is ScrapeX calling...\nRecipient: Hi, how can I help?",
                "duration": 180,
                "note": "Simulated transcript"
            }

    def record_consent(self, phone_number: str, consent_type: str, 
                      accepted: bool, timestamp: Optional[str] = None) -> Dict:
        """
        Record TCPA consent for a phone number
        
        Args:
            phone_number: Phone number
            consent_type: Type of consent (tcpa, recording, etc.)
            accepted: Whether consent was accepted
            timestamp: When consent was given
            
        Returns:
            Consent record
        """
        
        consent_record = {
            "phone_number": phone_number,
            "consent_type": consent_type,
            "accepted": accepted,
            "timestamp": timestamp or datetime.now().isoformat(),
            "status": ConsentStatus.ACCEPTED.value if accepted else ConsentStatus.DECLINED.value
        }
        
        # Store consent record
        if phone_number not in self.consent_records:
            self.consent_records[phone_number] = []
        self.consent_records[phone_number].append(consent_record)
        
        logger.info(f"Consent recorded for {phone_number}: {consent_type} - {accepted}")
        return consent_record

    def get_consent_status(self, phone_number: str) -> Dict:
        """
        Get consent status for a phone number
        
        Args:
            phone_number: Phone number to check
            
        Returns:
            Consent status information
        """
        
        if phone_number in self.consent_records:
            records = self.consent_records[phone_number]
            # Get the most recent consent record
            latest = records[-1] if records else None
            return {
                "phone_number": phone_number,
                "has_consent": latest['accepted'] if latest else False,
                "latest_consent": latest,
                "all_records": records
            }
        return {
            "phone_number": phone_number,
            "has_consent": False,
            "latest_consent": None,
            "all_records": []
        }

    def handle_webhook(self, webhook_data: Dict) -> Dict:
        """
        Handle incoming webhook from Retell AI
        
        Args:
            webhook_data: Webhook payload from Retell
            
        Returns:
            Webhook processing result
        """
        
        event_type = webhook_data.get('event_type')
        call_id = webhook_data.get('call_id')
        
        logger.info(f"Webhook received: {event_type} for call {call_id}")
        
        if event_type == "call_started":
            if call_id in self.call_records:
                self.call_records[call_id]['status'] = 'in_progress'
                self.call_records[call_id]['started_at'] = datetime.now().isoformat()
        
        elif event_type == "call_ended":
            if call_id in self.call_records:
                self.call_records[call_id]['status'] = 'completed'
                self.call_records[call_id]['ended_at'] = datetime.now().isoformat()
                self.call_records[call_id]['outcome'] = webhook_data.get('outcome', 'unknown')
                self.call_records[call_id]['duration'] = webhook_data.get('duration', 0)
        
        elif event_type == "recording_ready":
            if call_id in self.call_records:
                self.call_records[call_id]['recording_url'] = webhook_data.get('recording_url')
        
        elif event_type == "transcript_ready":
            if call_id in self.call_records:
                self.call_records[call_id]['transcript'] = webhook_data.get('transcript')
        
        return {
            "success": True,
            "event_type": event_type,
            "call_id": call_id,
            "processed_at": datetime.now().isoformat()
        }

    def get_all_calls(self) -> List[Dict]:
        """Get all call records"""
        return list(self.call_records.values())

    def get_call_analytics(self) -> Dict:
        """Get analytics for all calls"""
        
        calls = self.call_records.values()
        
        total_calls = len(calls)
        completed_calls = sum(1 for c in calls if c.get('status') == 'completed')
        total_duration = sum(c.get('duration', 0) for c in calls)
        
        outcomes = {}
        for call in calls:
            outcome = call.get('outcome', 'unknown')
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        return {
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": total_duration / completed_calls if completed_calls > 0 else 0,
            "outcomes": outcomes
        }
