#!/usr/bin/env python3
"""
Send HTML email via Google Workspace MCP
"""

import subprocess
import sys
from pathlib import Path

def send_email(
    html_file,
    to="wfmckie@gmail.com",
    from_email="hectorcb101@gmail.com",
    subject="🌍 Daily Intelligence Briefing"
):
    """Send HTML email using Google Workspace MCP."""
    
    html_path = Path(html_file)
    if not html_path.exists():
        print(f"❌ HTML file not found: {html_path}")
        return False
    
    # Read HTML content
    html_content = html_path.read_text()
    
    # Escape for shell
    html_escaped = html_content.replace('"', '\\"').replace('$', '\\$')
    
    # Build mcporter command
    cmd = [
        'mcporter', 'call', 'google-workspace.send_gmail_message',
        f'user_google_email={from_email}',
        f'to={to}',
        f'subject={subject}',
        f'body={html_escaped}',
        'body_format=html'
    ]
    
    try:
        print(f"📧 Sending email to {to}...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ Email sent successfully!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Failed to send email: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Send intelligence briefing email')
    parser.add_argument('--html-file', required=True, help='Path to HTML file')
    parser.add_argument('--to', default='wfmckie@gmail.com', help='Recipient email')
    parser.add_argument('--from', dest='from_email', default='hectorcb101@gmail.com', help='Sender email')
    parser.add_argument('--subject', default='🌍 Daily Intelligence Briefing', help='Email subject')
    
    args = parser.parse_args()
    
    success = send_email(
        html_file=args.html_file,
        to=args.to,
        from_email=args.from_email,
        subject=args.subject
    )
    
    sys.exit(0 if success else 1)
