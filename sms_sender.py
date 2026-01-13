import os
from twilio.rest import Client

# Twilio credentials (you'll need to add these to .env)
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "+16099084403")

# Payment links
CHAMBER_PAYMENT_LINK = "https://buy.stripe.com/7sY8wRaUt8tK4woazL2kw00"
REGULAR_PAYMENT_LINK = "https://buy.stripe.com/28E14p4w5aBS4wo4bn2kw01"

def send_payment_link_sms(to_number: str, is_chamber: bool = False):
    """
    Send payment link via SMS
    
    Args:
        to_number: Phone number to send to (E.164 format)
        is_chamber: True if Chamber/Tourism board, False for regular business
    
    Returns:
        dict with status and message_sid
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Select appropriate payment link
        payment_link = CHAMBER_PAYMENT_LINK if is_chamber else REGULAR_PAYMENT_LINK
        
        # Create SMS message
        message_body = f"Thank you for your interest in DGA Management Group. Here is your payment link: {payment_link}"
        
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        
        return {
            "status": "success",
            "message_sid": message.sid,
            "to": to_number
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
