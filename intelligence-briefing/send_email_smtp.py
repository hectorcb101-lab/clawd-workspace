#!/usr/bin/env python3
"""
Send HTML email via Gmail SMTP
Requires: Gmail App Password (not regular password)
Setup: https://support.google.com/accounts/answer/185833
"""

import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import os

def send_email_smtp(
    sender_email,
    sender_password,
    recipient_email,
    subject,
    html_content
):
    """Send HTML email via Gmail SMTP."""
    
    # Create message
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email
    
    # Add HTML content
    html_part = MIMEText(html_content, 'html')
    message.attach(html_part)
    
    try:
        # Connect to Gmail SMTP
        print(f"📧 Connecting to Gmail SMTP...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            print(f"✅ Logged in as {sender_email}")
            
            server.sendmail(sender_email, recipient_email, message.as_string())
            print(f"✅ Email sent to {recipient_email}")
            return True
            
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def main():
    # Configuration
    sender_email = os.getenv('GMAIL_ADDRESS', 'hectorcb101@gmail.com')
    sender_password = os.getenv('GMAIL_APP_PASSWORD', '')
    recipient_email = os.getenv('BRIEFING_RECIPIENT', 'wfmckie@gmail.com')
    
    # Get HTML file path
    html_file = Path(__file__).parent / 'data' / 'cache' / 'email.html'
    
    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        print("   Run: cd email-template && npx tsx render.ts --save")
        return 1
    
    if not sender_password:
        print("❌ Gmail App Password not configured")
        print()
        print("To set up Gmail delivery:")
        print("1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Generate an app password for 'Mail'")
        print("3. Set environment variable:")
        print("   export GMAIL_APP_PASSWORD='your-app-password'")
        print()
        print("💡 For now, the HTML email is saved at:")
        print(f"   {html_file}")
        print(f"   Open in browser: file://{html_file.absolute()}")
        return 1
    
    # Read HTML
    html_content = html_file.read_text()
    
    # Send
    subject = f"🌍 Intelligence Briefing - {Path(html_file).stem.split('_')[0]}"
    success = send_email_smtp(
        sender_email,
        sender_password,
        recipient_email,
        subject,
        html_content
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
