# modules/smtp_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

def send_email(to_email: str, subject: str, body: str) -> dict:
    """
    Sends an email using Gmail SMTP.
    Requires GMAIL_ADDRESS and GMAIL_APP_PASSWORD in your .env file.
    
    How to get Gmail App Password:
    1. Go to Google Account Settings
    2. Security → 2-Step Verification (must be ON)
    3. Search "App Passwords" → Create one for "Mail"
    4. Copy the 16-character password
    """
    from_email = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not from_email or not app_password:
        return {
            "success": False,
            "message": "❌ Gmail credentials not found in .env file. Add GMAIL_ADDRESS and GMAIL_APP_PASSWORD."
        }

    try:
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, app_password)
            server.send_message(msg)

        return {"success": True, "message": f"✅ Email sent successfully to {to_email}!"}

    except Exception as e:
        return {"success": False, "message": f"❌ Failed to send email: {str(e)}"}