#!/usr/bin/env python3
"""Download attachments from a Gmail message."""
import os
import sys
import base64
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDS_PATH = os.path.expanduser('~/.google_workspace_mcp/credentials/hectorcb101@gmail.com.json')
OUTPUT_DIR = '/home/ubuntu/clawd/obsidian-vault/QMUL MSc AI/Modules/Machine Learning'

def get_credentials():
    with open(CREDS_PATH, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return creds

def download_attachments(message_id):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    # Get the message
    message = service.users().messages().get(userId='me', id=message_id).execute()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    downloaded = []
    
    def process_parts(parts):
        for part in parts:
            filename = part.get('filename')
            if filename and part.get('body', {}).get('attachmentId'):
                att_id = part['body']['attachmentId']
                att = service.users().messages().attachments().get(
                    userId='me', messageId=message_id, id=att_id
                ).execute()
                
                data = base64.urlsafe_b64decode(att['data'])
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(data)
                
                downloaded.append(filepath)
                print(f"Downloaded: {filename}")
            
            # Recurse into nested parts
            if 'parts' in part:
                process_parts(part['parts'])
    
    if 'payload' in message:
        parts = message['payload'].get('parts', [])
        process_parts(parts)
    
    return downloaded

if __name__ == '__main__':
    message_id = sys.argv[1] if len(sys.argv) > 1 else '19c06c6df8158319'
    files = download_attachments(message_id)
    print(f"\nTotal downloaded: {len(files)} files")
    for f in files:
        print(f"  → {f}")
