from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sms_sender import send_payment_link_sms

router = APIRouter()

class SMSRequest(BaseModel):
    to_number: str
    is_chamber: bool = False

@router.post("/send-payment-sms")
async def send_payment_sms(request: SMSRequest):
    """
    Send payment link via SMS
    Called by Retell AI agent when customer asks for payment link
    """
    result = send_payment_link_sms(request.to_number, request.is_chamber)
    
    if result["status"] == "success":
        return {
            "success": True,
            "message": "Payment link sent successfully",
            "message_sid": result["message_sid"]
        }
    else:
        raise HTTPException(status_code=500, detail=result["error"])
