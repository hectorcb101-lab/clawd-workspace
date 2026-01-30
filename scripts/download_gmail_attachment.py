#!/usr/bin/env python3
"""Download Gmail attachments using Google API credentials."""

import argparse
import base64
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDS_DIR = Path.home() / '.google_workspace_mcp' / 'credentials'

def get_credentials(email: str):
    """Load credentials for the given email."""
    token_file = CREDS_DIR / f'{email}.json'
    if not token_file.exists():
        raise FileNotFoundError(f"No credentials found for {email}")
    
    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
    return creds

def download_attachment(email: str, message_id: str, attachment_id: str, save_path: str):
    """Download an attachment from Gmail."""
    creds = get_credentials(email)
    service = build('gmail', 'v1', credentials=creds)
    
    attachment = service.users().messages().attachments().get(
        userId='me',
        messageId=message_id,
        id=attachment_id
    ).execute()
    
    data = base64.urlsafe_b64decode(attachment['data'])
    
    # Ensure directory exists
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(save_path, 'wb') as f:
        f.write(data)
    
    print(f"Downloaded: {save_path} ({len(data)} bytes)")
    return save_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download Gmail attachment')
    parser.add_argument('--email', required=True, help='Google account email')
    parser.add_argument('--message-id', required=True, help='Gmail message ID')
    parser.add_argument('--attachment-id', required=True, help='Attachment ID')
    parser.add_argument('--save-path', required=True, help='Path to save the file')
    
    args = parser.parse_args()
    download_attachment(args.email, args.message_id, args.attachment_id, args.save_path)
