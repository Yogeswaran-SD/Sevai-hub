"""
Email service for sending emails via SMTP.
Supports async email delivery.
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


async def send_email(
    email_to: str,
    subject: str,
    html_body: str,
    text_body: str = None
) -> bool:
    """
    Send an email via configured SMTP server.

    Args:
        email_to: Recipient email address
        subject: Email subject
        html_body: HTML email body
        text_body: Plain text fallback body

    Returns:
        True if sent successfully, False otherwise
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"[WARN] Email service not configured. Skipping email to {email_to}")
        return False

    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        message["To"] = email_to

        # Attach plain text version if provided
        if text_body:
            part_text = MIMEText(text_body, "plain", _charset="utf-8")
            message.attach(part_text)

        # Attach HTML version
        part_html = MIMEText(html_body, "html", _charset="utf-8")
        message.attach(part_html)

        # Send via SMTP
        async with aiosmtplib.SMTP(
            hostname=settings.SMTP_HOST, port=settings.SMTP_PORT
        ) as smtp:
            await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            await smtp.send_message(message)

        print(f"[OK] Email sent to {email_to}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to send email to {email_to}: {str(e)}")
        return False


async def send_password_reset_email(email_to: str, reset_token: str) -> bool:
    """Send password reset email."""
    reset_url = f"http://localhost:5173/reset-password?token={reset_token}"

    html_body = f"""
    <html>
        <body>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_url}">Reset Password</a>
            <p>This link expires in 1 hour.</p>
        </body>
    </html>
    """

    text_body = f"Reset your password here: {reset_url}\nThis link expires in 1 hour."

    return await send_email(
        email_to=email_to,
        subject="Password Reset Request - Sevai Hub",
        html_body=html_body,
        text_body=text_body,
    )


async def send_technician_assignment_email(
    technician_email: str, service_name: str, customer_name: str
) -> bool:
    """Send technician assignment notification."""
    html_body = f"""
    <html>
        <body>
            <h2>New Service Assignment</h2>
            <p>You have been assigned to a new service:</p>
            <ul>
                <li><strong>Service:</strong> {service_name}</li>
                <li><strong>Customer:</strong> {customer_name}</li>
            </ul>
            <p>Please log in to view details and accept/decline.</p>
        </body>
    </html>
    """

    text_body = f"""
    New Service Assignment
    Service: {service_name}
    Customer: {customer_name}
    Please log in to view details.
    """

    return await send_email(
        email_to=technician_email,
        subject=f"New Service Assignment - {service_name}",
        html_body=html_body,
        text_body=text_body,
    )
