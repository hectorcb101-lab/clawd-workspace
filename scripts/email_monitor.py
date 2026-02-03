#!/usr/bin/env python3
"""
Email Monitor - Checks for new emails from Finn and returns alert if found.
Designed to be called by cron job.
"""
import json
import os
import sys
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_FILE = "/home/ubuntu/.google_workspace_mcp/credentials/hectorcb101@gmail.com.json"
STATE_FILE = "/home/ubuntu/clawd/.email_monitor_state.json"
FINN_EMAIL = "wfmckie@gmail.com"

def load_state():
    """Load last checked message IDs."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"seen_ids": [], "last_check": None}

def save_state(state):
    """Save state."""
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_gmail_service():
    """Get authenticated Gmail service."""
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
        creds.refresh(Request())
        token_data['token'] = creds.token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)
    
    return build('gmail', 'v1', credentials=creds)

def check_new_emails():
    """Check for new unread emails from Finn."""
    state = load_state()
    service = get_gmail_service()
    
    # Query for unread emails from Finn
    query = f"from:{FINN_EMAIL} is:unread"
    results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
    messages = results.get('messages', [])
    
    # Find new messages we haven't seen
    new_messages = []
    for msg in messages:
        if msg['id'] not in state['seen_ids']:
            # Get message details
            msg_detail = service.users().messages().get(
                userId='me', id=msg['id'], format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            headers = {h['name']: h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
            new_messages.append({
                'id': msg['id'],
                'subject': headers.get('Subject', 'No subject'),
                'date': headers.get('Date', '')
            })
            state['seen_ids'].append(msg['id'])
    
    # Keep only last 100 seen IDs to prevent unbounded growth
    state['seen_ids'] = state['seen_ids'][-100:]
    save_state(state)
    
    return new_messages

def main():
    try:
        new_emails = check_new_emails()
        if new_emails:
            # Output alert for cron to pick up
            print(f"NEW_EMAILS:{len(new_emails)}")
            for email in new_emails:
                print(f"  - {email['subject']}")
            sys.exit(1)  # Exit code 1 = new emails found
        else:
            sys.exit(0)  # Exit code 0 = no new emails
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)  # Exit code 2 = error

if __name__ == '__main__':
    main()
