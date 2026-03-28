"""
SMS service for sending text messages via Twilio.
Used for technician notifications and verification codes.
"""

from typing import Optional
from app.core.config import settings


def get_twilio_client():
    """Get Twilio client if configured."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return None

    try:
        from twilio.rest import Client

        return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    except ImportError:
        print("[WARN] Twilio not installed")
        return None


async def send_sms(phone: str, message: str) -> Optional[str]:
    """
    Send SMS via Twilio.

    Args:
        phone: Phone number in E.164 format (e.g., +911234567890)
        message: Message text (max 160 characters)

    Returns:
        Message SID if successful, None otherwise
    """
    client = get_twilio_client()
    if not client:
        print(f"[WARN] Twilio not configured. Skipping SMS to {phone}")
        return None

    try:
        sms = client.messages.create(
            body=message, from_=settings.TWILIO_PHONE_NUMBER, to=phone
        )
        print(f"[OK] SMS sent to {phone} (SID: {sms.sid})")
        return sms.sid
    except Exception as e:
        print(f"[ERROR] Failed to send SMS to {phone}: {str(e)}")
        return None


async def send_technician_assignment_sms(
    technician_phone: str, service_name: str, customer_name: str
) -> Optional[str]:
    """Send technician assignment notification via SMS."""
    message = f"New service: {service_name} for {customer_name}. Log in to view details."
    return await send_sms(technician_phone, message)


async def send_verification_code_sms(phone: str, code: str) -> Optional[str]:
    """Send verification code via SMS."""
    message = f"Your Sevai Hub verification code is: {code}. Valid for 10 minutes."
    return await send_sms(phone, message)


async def send_service_update_sms(phone: str, service_id: int, status: str) -> Optional[str]:
    """Send service status update via SMS."""
    message = f"Service #{service_id} status: {status}"
    return await send_sms(phone, message)


async def send_technician_reminder_sms(
    technician_phone: str, service_name: str, time: str
) -> Optional[str]:
    """Send reminder SMS to technician."""
    message = f"Reminder: Service '{service_name}' scheduled at {time}"
    return await send_sms(technician_phone, message)
