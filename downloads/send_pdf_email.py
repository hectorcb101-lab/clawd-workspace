#!/usr/bin/env python3
"""
Send PDF via Gmail API with attachment support
"""

import os
import sys
import json
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def send_email_with_attachment(
    to_email: str,
    subject: str,
    body_text: str,
    attachment_path: str,
    sender_name: str = "Atlas",
    sender_email: str = "hectorcb101@gmail.com"
):
    """Send email with PDF attachment using Gmail API."""
    
    # Load credentials
    token_path = Path.home() / ".workspace-mcp" / "token_hectorcb101@gmail.com.json"
    
    if not token_path.exists():
        print(f"Error: Token file not found at {token_path}", file=sys.stderr)
        return False
    
    # Get client credentials from environment
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Error: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set", file=sys.stderr)
        return False
    
    # Load token
    with open(token_path) as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data.get("access_token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/gmail.send"]
    )
    
    # Refresh token if needed
    if creds.expired or not creds.valid:
        creds.refresh(Request())
        # Update token file
        token_data["access_token"] = creds.token
        with open(token_path, "w") as f:
            json.dump(token_data, f, indent=2)
    
    # Build the service
    service = build('gmail', 'v1', credentials=creds)
    
    # Create message
    message = MIMEMultipart()
    message['From'] = f"{sender_name} <{sender_email}>"
    message['To'] = to_email
    message['Subject'] = subject
    
    # Add body
    message.attach(MIMEText(body_text, 'plain'))
    
    # Add attachment
    if attachment_path and os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)
        with open(attachment_path, 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='pdf')
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            message.attach(attachment)
    else:
        print(f"Warning: Attachment not found: {attachment_path}", file=sys.stderr)
    
    # Encode and send
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw}
    
    try:
        result = service.users().messages().send(userId='me', body=body).execute()
        print(f"✓ Email sent successfully! Message ID: {result['id']}")
        return True
    except Exception as e:
        print(f"✗ Error sending email: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    # Send the probability answers PDF
    success = send_email_with_attachment(
        to_email="wfmckie@gmail.com",
        subject="Week 4 Stats — Probability Answers (Fixed Layout)",
        body_text="""Hi Finn,

Updated version with fixed layout — all content should now be fully visible on every page.

Key fixes applied:
• Wider margins (2cm instead of 2.5cm)
• Breakable coloured boxes across pages
• Better text wrapping and spacing
• Unicode characters replaced with proper LaTeX symbols

Best,
Atlas""",
        attachment_path="/home/ubuntu/clawd/downloads/Week4_Stats_Probability_Answers.pdf"
    )
    
    sys.exit(0 if success else 1)
