#!/usr/bin/env python3
"""
Send HTML email via Gmail using the Gmail API
"""

import base64
import json
import os
import sys
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def create_message(sender, to, subject, html_content):
    """Create a message for an email."""
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    # Attach HTML content
    html_part = MIMEText(html_content, 'html')
    message.attach(html_part)
    
    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def send_via_clawdbot_message(to, subject, html_content):
    """Send email using clawdbot message tool (fallback to Telegram with HTML)."""
    print(f"📧 Sending briefing to {to}...")
    print(f"   Subject: {subject}")
    
    # For now, since we don't have direct Gmail API access configured,
    # we'll output the command needed and save the HTML for manual testing
    print("\n⚠️  Gmail API not yet configured.")
    print("   To send via Gmail, you would need to:")
    print("   1. Set up Google Cloud Project")
    print("   2. Enable Gmail API")
    print("   3. Configure OAuth 2.0 credentials")
    print("   4. Use google-auth and google-api-python-client")
    
    return False

def send_email(sender="hectorcb101@gmail.com", to="wfmckie@gmail.com", subject="Daily Intelligence Briefing", html_file=None):
    """Main send function."""
    
    if html_file is None:
        html_file = Path(__dirname) / ".." / "data" / "cache" / "email.html"
    
    html_file = Path(html_file)
    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    html_content = html_file.read_text()
    
    # Try to send
    success = send_via_clawdbot_message(to, subject, html_content)
    
    if not success:
        print(f"\n💡 For testing, the HTML email has been saved to:")
        print(f"   {html_file}")
        print(f"\n   You can:")
        print(f"   1. Open it in a browser: file://{html_file.absolute()}")
        print(f"   2. Send it manually via Gmail")
        print(f"   3. Set up Gmail API for automated delivery")
    
    return success

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Send intelligence briefing email')
    parser.add_argument('--to', default='wfmckie@gmail.com', help='Recipient email')
    parser.add_argument('--from', dest='sender', default='hectorcb101@gmail.com', help='Sender email')
    parser.add_argument('--subject', default='Daily Intelligence Briefing', help='Email subject')
    parser.add_argument('--html-file', help='Path to HTML file')
    
    args = parser.parse_args()
    
    send_email(
        sender=args.sender,
        to=args.to,
        subject=args.subject,
        html_file=args.html_file
    )
