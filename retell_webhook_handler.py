"""
Retell AI Webhook Handler for Function Calling
Handles send_payment_link function calls from the AI agent
"""
import os
import requests
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Stripe payment links
CHAMBER_PAYMENT_LINK = "https://buy.stripe.com/7sY8wRaUt8tK4woazL"
REGULAR_PAYMENT_LINK = "https://buy.stripe.com/28E14p4w5aBS4wo4bn"

class RetellWebhookHandler:
    """Handles Retell AI webhook events and function calls"""
    
    def __init__(self):
        self.retell_api_key = os.environ.get("RETELL_API_KEY")
        if not self.retell_api_key:
            logger.warning("RETELL_API_KEY not found. SMS functionality will be limited.")
    
    def handle_function_call(self, function_name: str, parameters: Dict, call_data: Dict) -> Dict:
        """
        Handle function calls from Retell AI agent
        
        Args:
            function_name: Name of the function being called
            parameters: Function parameters from the agent
            call_data: Full call data from Retell webhook
            
        Returns:
            Response to send back to Retell
        """
        if function_name == "send_payment_link":
            return self._handle_send_payment_link(parameters, call_data)
        else:
            logger.warning(f"Unknown function call: {function_name}")
            return {
                "success": False,
                "message": f"Unknown function: {function_name}"
            }
    
    def _handle_send_payment_link(self, parameters: Dict, call_data: Dict) -> Dict:
        """
        Handle send_payment_link function call
        
        Args:
            parameters: {"customer_type": "chamber" or "regular"}
            call_data: Full call data including phone number
            
        Returns:
            Response with SMS sending status
        """
        try:
            customer_type = parameters.get("customer_type", "regular")
            
            # Determine which payment link to send
            if customer_type == "chamber":
                payment_link = CHAMBER_PAYMENT_LINK
                link_type = "Chamber/Tourism Partnership (50% off + 15% revenue share)"
            else:
                payment_link = REGULAR_PAYMENT_LINK
                link_type = "Regular Business Pro Plan"
            
            # Get customer phone number from call data
            customer_phone = call_data.get("from_number") or call_data.get("to_number")
            
            if not customer_phone:
                logger.error("No phone number found in call data")
                return {
                    "success": False,
                    "message": "Could not determine customer phone number"
                }
            
            # Send SMS via Retell API
            sms_sent = self._send_sms_via_retell(
                to_number=customer_phone,
                message=f"Thank you for your interest in DGA Management Group! Complete your signup here: {payment_link}",
                call_id=call_data.get("call_id")
            )
            
            if sms_sent:
                logger.info(f"Payment link sent to {customer_phone} - Type: {link_type}")
                return {
                    "success": True,
                    "message": f"Payment link sent successfully",
                    "customer_type": customer_type,
                    "link_type": link_type
                }
            else:
                logger.error(f"Failed to send SMS to {customer_phone}")
                return {
                    "success": False,
                    "message": "Failed to send SMS"
                }
                
        except Exception as e:
            logger.error(f"Error handling send_payment_link: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    def _send_sms_via_retell(self, to_number: str, message: str, call_id: Optional[str] = None) -> bool:
        """
        Send SMS using Retell AI's SMS API
        
        Args:
            to_number: Recipient phone number
            message: SMS message content
            call_id: Optional call ID for context
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        try:
            if not self.retell_api_key:
                logger.error("Cannot send SMS: RETELL_API_KEY not configured")
                return False
            
            headers = {
                "Authorization": f"Bearer {self.retell_api_key}",
                "Content-Type": "application/json"
            }
            
            # Use Retell's SMS API endpoint
            # Note: This sends SMS from the agent's phone number
            payload = {
                "to_number": to_number,
                "message": message
            }
            
            if call_id:
                payload["call_id"] = call_id
            
            response = requests.post(
                "https://api.retellai.com/create-outbound-sms",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"SMS sent successfully to {to_number}")
                return True
            else:
                logger.error(f"SMS API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return False
    
    def handle_call_started(self, call_data: Dict) -> Dict:
        """
        Handle call started webhook
        
        Args:
            call_data: Call data from Retell
            
        Returns:
            Response data
        """
        logger.info(f"Call started: {call_data.get('call_id')}")
        return {"status": "acknowledged"}
    
    def handle_call_ended(self, call_data: Dict) -> Dict:
        """
        Handle call ended webhook
        
        Args:
            call_data: Call data from Retell
            
        Returns:
            Response data
        """
        call_id = call_data.get('call_id')
        duration = call_data.get('call_duration_seconds', 0)
        logger.info(f"Call ended: {call_id} - Duration: {duration}s")
        return {"status": "acknowledged"}


# Global instance
webhook_handler = RetellWebhookHandler()
