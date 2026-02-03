#!/usr/bin/env python3
"""
Email Notification Daemon
Runs independently, monitors Gmail, sends Telegram alerts directly.
No dependency on Clawdbot sessions.
"""
import json
import os
import time
import requests
import logging
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Config
TOKEN_FILE = "/home/ubuntu/.google_workspace_mcp/credentials/hectorcb101@gmail.com.json"
STATE_FILE = "/home/ubuntu/clawd/.email_daemon_state.json"
LOG_FILE = "/home/ubuntu/clawd/logs/email_daemon.log"
FINN_EMAIL = "wfmckie@gmail.com"
FINN_TELEGRAM_ID = "6047368408"
TELEGRAM_BOT_TOKEN = "8309758074:AAE3vvKfsFvvfoKGqhPKTygQ1bexOEwo3Sc"
CHECK_INTERVAL = 120  # 2 minutes

# Setup logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"seen_ids": [], "last_check": None}

def save_state(state):
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def send_telegram(message):
    """Send message directly to Finn via Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": FINN_TELEGRAM_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info(f"Telegram sent: {message[:50]}...")
            return True
        else:
            logger.error(f"Telegram failed: {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False

def get_gmail_service():
    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes', [])
    )
    
    if creds.expired or not creds.valid:
        logger.info("Refreshing Gmail token...")
        creds.refresh(Request())
        token_data['token'] = creds.token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)
    
    return build('gmail', 'v1', credentials=creds)

def check_emails():
    """Check for new emails from Finn."""
    state = load_state()
    
    try:
        service = get_gmail_service()
        query = f"from:{FINN_EMAIL} is:unread"
        results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
        messages = results.get('messages', [])
        
        new_emails = []
        for msg in messages:
            if msg['id'] not in state['seen_ids']:
                msg_detail = service.users().messages().get(
                    userId='me', id=msg['id'], format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                headers = {h['name']: h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
                new_emails.append({
                    'id': msg['id'],
                    'subject': headers.get('Subject', 'No subject'),
                })
                state['seen_ids'].append(msg['id'])
        
        # Keep only last 200 IDs
        state['seen_ids'] = state['seen_ids'][-200:]
        save_state(state)
        
        return new_emails
    
    except Exception as e:
        logger.error(f"Gmail check failed: {e}")
        # Alert about auth failure
        if "authentication" in str(e).lower() or "credential" in str(e).lower():
            send_telegram("⚠️ Atlas: Gmail auth failed! Need to re-authenticate.")
        return []

def main():
    logger.info("📧 Email Notification Daemon starting...")
    send_telegram("🏛️ Atlas Email Monitor is now running. I'll alert you when you send emails to hectorcb101@gmail.com.")
    
    while True:
        try:
            new_emails = check_emails()
            
            if new_emails:
                # Send alert for each new email
                for email in new_emails:
                    msg = f"📬 <b>New email from you:</b>\n\n<i>{email['subject']}</i>"
                    send_telegram(msg)
                    logger.info(f"New email: {email['subject']}")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Daemon stopped by user")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
