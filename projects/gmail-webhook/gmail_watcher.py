#!/usr/bin/env python3
"""
Gmail Watcher Daemon
Real-time email notifications using Gmail API history tracking.

Efficient approach:
- Uses historyId to only fetch changes since last check
- Polls every 60 seconds (configurable)
- Notifies via Clawdbot when emails from watched senders arrive
"""

import json
import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Configuration
CONFIG = {
    "poll_interval": 60,  # seconds
    "watched_senders": ["wfmckie@gmail.com"],
    "credentials_path": Path.home() / ".google_workspace_mcp/credentials/hectorcb101@gmail.com.json",
    "state_file": Path.home() / "clawd/projects/gmail-webhook/state.json",
    "log_file": Path.home() / "clawd/projects/gmail-webhook/gmail_watcher.log",
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG["log_file"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_credentials():
    """Load and refresh Google OAuth credentials."""
    creds_path = CONFIG["credentials_path"]
    if not creds_path.exists():
        raise FileNotFoundError(f"Credentials not found: {creds_path}")
    
    with open(creds_path) as f:
        creds_data = json.load(f)
    
    creds = Credentials(
        token=creds_data.get("token"),
        refresh_token=creds_data.get("refresh_token"),
        token_uri=creds_data.get("token_uri"),
        client_id=creds_data.get("client_id"),
        client_secret=creds_data.get("client_secret"),
        scopes=creds_data.get("scopes")
    )
    
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed credentials
        creds_data["token"] = creds.token
        creds_data["expiry"] = creds.expiry.isoformat() if creds.expiry else None
        with open(creds_path, "w") as f:
            json.dump(creds_data, f, indent=2)
        logger.info("Credentials refreshed")
    
    return creds


def load_state():
    """Load watcher state (last historyId)."""
    state_file = CONFIG["state_file"]
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    return {"history_id": None, "last_check": None}


def save_state(state):
    """Save watcher state."""
    state_file = CONFIG["state_file"]
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def get_gmail_service(creds):
    """Build Gmail API service."""
    return build('gmail', 'v1', credentials=creds, cache_discovery=False)


def get_current_history_id(service):
    """Get current historyId from profile."""
    profile = service.users().getProfile(userId='me').execute()
    return profile['historyId']


def check_for_new_emails(service, state):
    """Check for new emails since last historyId."""
    history_id = state.get("history_id")
    
    if not history_id:
        # First run - just record current historyId
        current_id = get_current_history_id(service)
        logger.info(f"First run. Setting historyId to {current_id}")
        return [], current_id
    
    try:
        # Get history since last check
        results = service.users().history().list(
            userId='me',
            startHistoryId=history_id,
            historyTypes=['messageAdded']
        ).execute()
        
        new_history_id = results.get('historyId', history_id)
        
        if 'history' not in results:
            return [], new_history_id
        
        # Extract new message IDs
        new_message_ids = []
        for history_item in results['history']:
            if 'messagesAdded' in history_item:
                for msg in history_item['messagesAdded']:
                    new_message_ids.append(msg['message']['id'])
        
        return new_message_ids, new_history_id
        
    except Exception as e:
        if 'historyId' in str(e):
            # History expired, reset
            logger.warning(f"History expired, resetting: {e}")
            return [], get_current_history_id(service)
        raise


def get_message_details(service, message_id):
    """Get message details (sender, subject, snippet)."""
    msg = service.users().messages().get(
        userId='me',
        id=message_id,
        format='metadata',
        metadataHeaders=['From', 'Subject', 'Date']
    ).execute()
    
    headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
    
    return {
        'id': message_id,
        'from': headers.get('From', 'Unknown'),
        'subject': headers.get('Subject', 'No subject'),
        'date': headers.get('Date', ''),
        'snippet': msg.get('snippet', '')[:100]
    }


def notify_clawdbot(emails):
    """Send notification via Clawdbot cron wake."""
    if not emails:
        return
    
    # Format notification message
    msg_parts = ["📬 **New Email Alert**\n"]
    for email in emails:
        sender = email['from'].split('<')[0].strip() or email['from']
        msg_parts.append(f"• **{sender}**: {email['subject']}")
        if email['snippet']:
            msg_parts.append(f"  _{email['snippet'][:80]}..._")
    
    message = "\n".join(msg_parts)
    
    # Use cron wake to notify
    try:
        result = subprocess.run(
            ['clawdbot', 'cron', 'wake', '--text', message],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            logger.info(f"Notification sent: {len(emails)} email(s)")
        else:
            logger.error(f"Notification failed: {result.stderr}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")


def run_daemon():
    """Main daemon loop."""
    logger.info("Gmail Watcher starting...")
    
    creds = load_credentials()
    service = get_gmail_service(creds)
    state = load_state()
    
    # Initialize historyId if needed
    if not state.get("history_id"):
        state["history_id"] = get_current_history_id(service)
        state["last_check"] = datetime.now().isoformat()
        save_state(state)
        logger.info(f"Initialized with historyId: {state['history_id']}")
    
    logger.info(f"Watching for emails from: {CONFIG['watched_senders']}")
    logger.info(f"Poll interval: {CONFIG['poll_interval']}s")
    
    while True:
        try:
            # Check for new emails
            new_ids, new_history_id = check_for_new_emails(service, state)
            
            if new_ids:
                logger.info(f"Found {len(new_ids)} new message(s)")
                
                # Get details and filter by watched senders
                watched_emails = []
                for msg_id in new_ids:
                    details = get_message_details(service, msg_id)
                    sender_email = details['from'].lower()
                    
                    # Check if from watched sender
                    for watched in CONFIG['watched_senders']:
                        if watched.lower() in sender_email:
                            watched_emails.append(details)
                            logger.info(f"Watched email: {details['subject']} from {details['from']}")
                            break
                
                # Notify if relevant emails found
                if watched_emails:
                    notify_clawdbot(watched_emails)
            
            # Update state
            state["history_id"] = new_history_id
            state["last_check"] = datetime.now().isoformat()
            save_state(state)
            
        except Exception as e:
            logger.error(f"Error in check cycle: {e}")
            # Refresh credentials on auth errors
            if 'invalid_grant' in str(e).lower() or 'expired' in str(e).lower():
                try:
                    creds = load_credentials()
                    service = get_gmail_service(creds)
                except Exception as auth_e:
                    logger.error(f"Failed to refresh credentials: {auth_e}")
        
        time.sleep(CONFIG["poll_interval"])


def check_once():
    """Single check (for testing)."""
    creds = load_credentials()
    service = get_gmail_service(creds)
    state = load_state()
    
    new_ids, new_history_id = check_for_new_emails(service, state)
    
    print(f"History ID: {state.get('history_id')} -> {new_history_id}")
    print(f"New messages: {len(new_ids)}")
    
    for msg_id in new_ids[:5]:  # Show first 5
        details = get_message_details(service, msg_id)
        print(f"  - {details['from']}: {details['subject']}")
    
    # Update state
    state["history_id"] = new_history_id
    state["last_check"] = datetime.now().isoformat()
    save_state(state)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        check_once()
    else:
        run_daemon()
