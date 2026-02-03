#!/usr/bin/env python3
"""Check unread emails using Google API directly - bypasses mcporter auth issues"""
import json
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_FILE = "/home/ubuntu/.google_workspace_mcp/credentials/hectorcb101@gmail.com.json"

def get_unread_emails(max_results=10, query="is:unread"):
    try:
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
        
        # Refresh if needed
        if creds.expired or not creds.valid:
            creds.refresh(Request())
            token_data['token'] = creds.token
            with open(TOKEN_FILE, 'w') as f:
                json.dump(token_data, f, indent=2)
        
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        output = []
        for msg in messages:
            msg_detail = service.users().messages().get(
                userId='me', id=msg['id'], format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            headers = {h['name']: h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
            output.append({
                'id': msg['id'],
                'from': headers.get('From', 'Unknown'),
                'subject': headers.get('Subject', 'No subject'),
                'date': headers.get('Date', '')
            })
        
        return {'success': True, 'count': len(messages), 'emails': output}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    query = sys.argv[1] if len(sys.argv) > 1 else "is:unread"
    result = get_unread_emails(query=query)
    print(json.dumps(result, indent=2))
