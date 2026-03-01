from email.message import EmailMessage
import smtplib
import os
from celery import shared_task

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

@shared_task
def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg['Subject'] = "PlaceMe - Verification Code"
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg.set_content(f"Your PlaceMe verification code is: {otp}\n\nThis code is valid for 10 minutes. Do not share it with anyone.")

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)   # type: ignore
        server.send_message(msg)
        server.quit()
        return f"OTP successfully sent to {to_email}"

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False