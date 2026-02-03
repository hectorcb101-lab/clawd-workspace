#!/usr/bin/env python3
"""
Email Task Tracker
Tracks which emails have been processed to avoid duplicate work.

Uses:
1. Gmail labels (PROCESSED_BY_ATLAS) for persistence
2. Local JSON cache for quick checks
"""

import json
import os
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CONFIG = {
    "credentials_path": Path.home() / ".google_workspace_mcp/credentials/hectorcb101@gmail.com.json",
    "tracker_file": Path.home() / "clawd/projects/gmail-webhook/processed_emails.json",
    "label_name": "ATLAS_PROCESSED"
}


def load_credentials():
    """Load Google OAuth credentials."""
    with open(CONFIG["credentials_path"]) as f:
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
    
    return creds


def get_gmail_service():
    """Get Gmail API service."""
    return build('gmail', 'v1', credentials=load_credentials(), cache_discovery=False)


def load_tracker():
    """Load local tracker cache."""
    if CONFIG["tracker_file"].exists():
        with open(CONFIG["tracker_file"]) as f:
            return json.load(f)
    return {"processed": {}, "pending": {}}


def save_tracker(tracker):
    """Save local tracker cache."""
    CONFIG["tracker_file"].parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG["tracker_file"], "w") as f:
        json.dump(tracker, f, indent=2)


def get_or_create_label(service):
    """Get or create the ATLAS_PROCESSED label."""
    labels = service.users().labels().list(userId='me').execute()
    
    for label in labels.get('labels', []):
        if label['name'] == CONFIG["label_name"]:
            return label['id']
    
    # Create the label
    label_body = {
        'name': CONFIG["label_name"],
        'labelListVisibility': 'labelHide',
        'messageListVisibility': 'hide'
    }
    created = service.users().labels().create(userId='me', body=label_body).execute()
    return created['id']


def mark_processed(email_id: str, task_summary: str = None, notes: str = None):
    """Mark an email as processed."""
    tracker = load_tracker()
    service = get_gmail_service()
    label_id = get_or_create_label(service)
    
    # Add label to email
    service.users().messages().modify(
        userId='me',
        id=email_id,
        body={'addLabelIds': [label_id], 'removeLabelIds': ['UNREAD']}
    ).execute()
    
    # Update local tracker
    tracker["processed"][email_id] = {
        "processed_at": datetime.now().isoformat(),
        "task_summary": task_summary,
        "notes": notes
    }
    
    # Remove from pending if present
    if email_id in tracker.get("pending", {}):
        del tracker["pending"][email_id]
    
    save_tracker(tracker)
    print(f"✅ Marked {email_id} as processed")
    return True


def is_processed(email_id: str) -> bool:
    """Check if an email has been processed."""
    tracker = load_tracker()
    
    # Check local cache first
    if email_id in tracker.get("processed", {}):
        return True
    
    # Check Gmail label
    service = get_gmail_service()
    try:
        msg = service.users().messages().get(userId='me', id=email_id, format='minimal').execute()
        label_id = get_or_create_label(service)
        return label_id in msg.get('labelIds', [])
    except:
        return False


def add_pending(email_id: str, subject: str, sender: str, task_description: str = None):
    """Add an email to pending tasks."""
    tracker = load_tracker()
    
    tracker["pending"][email_id] = {
        "added_at": datetime.now().isoformat(),
        "subject": subject,
        "sender": sender,
        "task_description": task_description
    }
    
    save_tracker(tracker)
    print(f"📝 Added {email_id} to pending")


def list_pending():
    """List all pending email tasks."""
    tracker = load_tracker()
    pending = tracker.get("pending", {})
    
    if not pending:
        print("No pending email tasks")
        return []
    
    print(f"\n📬 Pending Email Tasks ({len(pending)}):\n")
    for email_id, info in pending.items():
        print(f"  [{email_id[:8]}...] {info.get('subject', 'No subject')}")
        if info.get('task_description'):
            print(f"           → {info['task_description']}")
    
    return list(pending.items())


def list_processed(limit: int = 10):
    """List recently processed emails."""
    tracker = load_tracker()
    processed = tracker.get("processed", {})
    
    # Sort by processed_at
    sorted_items = sorted(
        processed.items(),
        key=lambda x: x[1].get('processed_at', ''),
        reverse=True
    )[:limit]
    
    print(f"\n✅ Recently Processed ({len(sorted_items)}):\n")
    for email_id, info in sorted_items:
        print(f"  [{email_id[:8]}...] {info.get('task_summary', 'No summary')}")
        print(f"           @ {info.get('processed_at', 'Unknown')[:16]}")
    
    return sorted_items


def get_unprocessed_from_sender(sender_email: str, limit: int = 20):
    """Get unprocessed emails from a specific sender."""
    service = get_gmail_service()
    tracker = load_tracker()
    
    # Search for emails from sender
    results = service.users().messages().list(
        userId='me',
        q=f'from:{sender_email}',
        maxResults=limit
    ).execute()
    
    unprocessed = []
    for msg in results.get('messages', []):
        if msg['id'] not in tracker.get("processed", {}):
            # Get details
            details = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['Subject', 'Date']
            ).execute()
            
            headers = {h['name']: h['value'] for h in details.get('payload', {}).get('headers', [])}
            
            unprocessed.append({
                'id': msg['id'],
                'subject': headers.get('Subject', 'No subject'),
                'date': headers.get('Date', ''),
                'snippet': details.get('snippet', '')[:80]
            })
    
    return unprocessed


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Email Task Tracker")
        print("\nUsage:")
        print("  email_tracker.py pending              - List pending tasks")
        print("  email_tracker.py processed [n]        - List last n processed")
        print("  email_tracker.py mark <id> [summary]  - Mark email as processed")
        print("  email_tracker.py check <id>           - Check if processed")
        print("  email_tracker.py unprocessed <email>  - List unprocessed from sender")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "pending":
        list_pending()
    elif cmd == "processed":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_processed(limit)
    elif cmd == "mark":
        if len(sys.argv) < 3:
            print("Usage: email_tracker.py mark <email_id> [summary]")
            sys.exit(1)
        email_id = sys.argv[2]
        summary = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else None
        mark_processed(email_id, summary)
    elif cmd == "check":
        if len(sys.argv) < 3:
            print("Usage: email_tracker.py check <email_id>")
            sys.exit(1)
        result = is_processed(sys.argv[2])
        print(f"Processed: {'Yes ✅' if result else 'No ❌'}")
    elif cmd == "unprocessed":
        if len(sys.argv) < 3:
            print("Usage: email_tracker.py unprocessed <sender_email>")
            sys.exit(1)
        emails = get_unprocessed_from_sender(sys.argv[2])
        print(f"\n📬 Unprocessed from {sys.argv[2]} ({len(emails)}):\n")
        for e in emails:
            print(f"  [{e['id'][:8]}...] {e['subject']}")
            print(f"           {e['snippet']}...")
    else:
        print(f"Unknown command: {cmd}")
