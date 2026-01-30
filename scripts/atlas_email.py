#!/usr/bin/env python3
"""
Atlas Email - Send emails with proper sender name via Gmail API
Uses 🏛️ emoji as logo - simple and reliable
"""
import json
import base64
import argparse
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Config - secrets from environment, not hardcoded
TOKEN_FILE = "/home/ubuntu/.workspace-mcp/token_hectorcb101@gmail.com.json"
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SENDER_NAME = "Atlas"
SENDER_EMAIL = "hectorcb101@gmail.com"

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment")

def get_credentials():
    """Load and refresh credentials."""
    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data.get('access_token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=token_data.get('scopes', ['https://mail.google.com/'])
    )
    
    if creds.expired or not creds.valid:
        creds.refresh(Request())
        token_data['access_token'] = creds.token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f)
    
    return creds

def build_templated_body(content: str, greeting: str = "Finn,", footer: str = "Sent by Atlas") -> str:
    """Build a clean email body with 🏛️ logo."""
    date_str = datetime.now().strftime("%d %B %Y")
    
    return f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background-color:#f5f5f5;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f5f5f5">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="max-width:600px; width:100%; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
          
          <!-- Header bar -->
          <tr><td style="height: 4px; background: linear-gradient(90deg, #1e3a5f 0%, #b8860b 100%);"></td></tr>
          
          <!-- Header with emoji logo -->
          <tr>
            <td align="center" style="padding: 28px 40px 24px 40px; border-bottom: 1px solid #eee;">
              <div style="font-size: 48px; margin-bottom: 8px;">🏛️</div>
              <span style="font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 24px; font-weight: bold; color: #1e3a5f; letter-spacing: 3px;">ATLAS</span>
              <p style="font-size: 11px; color: #999; font-family: -apple-system, sans-serif; margin: 8px 0 0 0;">{date_str}</p>
            </td>
          </tr>
          
          <!-- Content -->
          <tr>
            <td style="padding: 28px 40px 32px 40px;">
              <p style="font-family: Georgia, serif; font-size: 18px; color: #1a1a1a; margin: 0 0 16px 0;">{greeting}</p>
              {content}
              <p style="font-family: Georgia, serif; font-size: 16px; color: #1e3a5f; margin: 24px 0 0 0;">— Atlas 🏛️</p>
            </td>
          </tr>
          
        </table>
        
        <!-- Footer -->
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px; width:100%; margin-top: 16px;">
          <tr>
            <td align="center" style="font-size: 11px; color: #999; font-family: -apple-system, sans-serif;">
              {footer}
            </td>
          </tr>
        </table>
        
      </td>
    </tr>
  </table>
</body>
</html>'''

def send_email(to: str, subject: str, body: str, html: bool = True):
    """Send email with Atlas as sender name."""
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    if html:
        message = MIMEMultipart('alternative')
        message.attach(MIMEText(body, 'html'))
    else:
        message = MIMEText(body, 'plain')
    
    message['to'] = to
    message['from'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    message['subject'] = subject
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    result = service.users().messages().send(
        userId='me',
        body={'raw': raw}
    ).execute()
    
    print(f"Email sent! Message ID: {result['id']}")
    return result

def send_templated_email(to: str, subject: str, content: str, greeting: str = "Finn,", footer: str = "Sent by Atlas"):
    """Convenience function to send a templated Atlas email."""
    body = build_templated_body(content, greeting, footer)
    return send_email(to, subject, body)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send email as Atlas')
    parser.add_argument('--to', required=True, help='Recipient email')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--body', help='Email body (HTML) - use this OR --content')
    parser.add_argument('--content', help='Email content (uses Atlas template)')
    parser.add_argument('--greeting', default='Finn,', help='Greeting line')
    parser.add_argument('--footer', default='Sent by Atlas', help='Footer text')
    parser.add_argument('--plain', action='store_true', help='Send as plain text')
    
    args = parser.parse_args()
    
    if args.content:
        send_templated_email(args.to, args.subject, args.content, args.greeting, args.footer)
    elif args.body:
        send_email(args.to, args.subject, args.body, html=not args.plain)
    else:
        print("Error: Either --body or --content is required")
        exit(1)
