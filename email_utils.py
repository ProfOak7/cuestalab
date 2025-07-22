# email_utils.py

import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# If modifying SCOPES, delete the token.json file first
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Authenticate and return Gmail API service object."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def send_confirmation_email(to_email, student_name, slot, location):
    """Send confirmation email via Gmail API."""
    service = get_gmail_service()

    subject = "AT Lab Appointment Confirmation"
    body = f"""Hi {student_name},

Your appointment has been successfully booked for:

{slot} @ {location}

See you at the AT Lab!

- Cuesta College"""

    message = MIMEText(body)
    message["to"] = to_email
    message["from"] = "jonathan_okerblom@my.cuesta.edu"
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {"raw": raw}

    try:
        service.users().messages().send(userId="me", body=message_body).execute()
        print("✅ Email sent!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
