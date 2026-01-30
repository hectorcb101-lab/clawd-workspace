#!/usr/bin/env python3
"""
Google Lean - Minimal Google Workspace tools for Atlas

Only the 15 tools I actually use, no bloat.
Uses existing credentials from ~/.google_workspace_mcp/credentials/

Usage:
    google_lean.py <command> [args...]

Commands:
    # Gmail
    gmail-search <query>
    gmail-read <message_id>
    gmail-read-batch <id1,id2,id3>
    gmail-labels <message_id> --add LABEL --remove LABEL
    gmail-send <to> <subject> <body>
    
    # Calendar
    cal-list
    cal-events [--calendar ID] [--days N]
    cal-create <summary> <start> <end> [--calendar ID]
    
    # Drive
    drive-search <query>
    drive-upload <local_path> [--folder ID] [--name NAME]
    drive-download <file_id> <output_path>
    drive-share <file_id> <email> [--role reader|writer]
    
    # Docs
    doc-create <title> [--content TEXT]
    doc-read <doc_id>
    
    # Sheets
    sheet-read <sheet_id> <range>
    sheet-write <sheet_id> <range> <values_json>
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

# Google API imports
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import base64

# Credentials location
CREDS_DIR = Path.home() / '.google_workspace_mcp' / 'credentials'
DEFAULT_EMAIL = 'hectorcb101@gmail.com'

# Scopes needed
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
]


def get_credentials(email: str = DEFAULT_EMAIL) -> Credentials:
    """Load credentials for the given email."""
    token_file = CREDS_DIR / f'{email}.json'
    if not token_file.exists():
        raise FileNotFoundError(f"No credentials found for {email}. Run google-workspace MCP auth first.")
    
    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
    return creds


def get_service(service_name: str, version: str, email: str = DEFAULT_EMAIL):
    """Get a Google API service."""
    creds = get_credentials(email)
    return build(service_name, version, credentials=creds)


# ==================== GMAIL ====================

def gmail_search(query: str, max_results: int = 10) -> Dict:
    """Search Gmail messages."""
    service = get_service('gmail', 'v1')
    results = service.users().messages().list(
        userId='me', q=query, maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    output = []
    for msg in messages:
        output.append({
            'id': msg['id'],
            'threadId': msg['threadId']
        })
    
    return {'count': len(output), 'messages': output}


def gmail_read(message_id: str) -> Dict:
    """Read a Gmail message."""
    service = get_service('gmail', 'v1')
    msg = service.users().messages().get(
        userId='me', id=message_id, format='full'
    ).execute()
    
    headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
    
    # Extract body
    body = ''
    if 'parts' in msg['payload']:
        for part in msg['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                break
    elif 'body' in msg['payload']:
        data = msg['payload']['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    
    # Extract attachments info
    attachments = []
    if 'parts' in msg['payload']:
        for part in msg['payload']['parts']:
            if part.get('filename'):
                attachments.append({
                    'filename': part['filename'],
                    'mimeType': part['mimeType'],
                    'size': part['body'].get('size', 0),
                    'attachmentId': part['body'].get('attachmentId')
                })
    
    return {
        'id': message_id,
        'subject': headers.get('Subject', ''),
        'from': headers.get('From', ''),
        'to': headers.get('To', ''),
        'date': headers.get('Date', ''),
        'body': body[:5000],  # Truncate long bodies
        'attachments': attachments
    }


def gmail_read_batch(message_ids: List[str]) -> List[Dict]:
    """Read multiple Gmail messages."""
    return [gmail_read(mid) for mid in message_ids]


def gmail_labels(message_id: str, add_labels: List[str] = None, remove_labels: List[str] = None) -> Dict:
    """Modify message labels."""
    service = get_service('gmail', 'v1')
    body = {}
    if add_labels:
        body['addLabelIds'] = add_labels
    if remove_labels:
        body['removeLabelIds'] = remove_labels
    
    result = service.users().messages().modify(
        userId='me', id=message_id, body=body
    ).execute()
    
    return {'success': True, 'labels': result.get('labelIds', [])}


def gmail_send(to: str, subject: str, body: str, html: bool = False) -> Dict:
    """Send an email."""
    import email.mime.text
    import email.mime.multipart
    
    service = get_service('gmail', 'v1')
    
    message = email.mime.multipart.MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    
    mime_type = 'html' if html else 'plain'
    message.attach(email.mime.text.MIMEText(body, mime_type))
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    result = service.users().messages().send(
        userId='me', body={'raw': raw}
    ).execute()
    
    return {'success': True, 'messageId': result['id']}


# ==================== CALENDAR ====================

def cal_list() -> Dict:
    """List calendars."""
    service = get_service('calendar', 'v3')
    results = service.calendarList().list().execute()
    
    calendars = []
    for cal in results.get('items', []):
        calendars.append({
            'id': cal['id'],
            'summary': cal.get('summary', ''),
            'primary': cal.get('primary', False)
        })
    
    return {'calendars': calendars}


def cal_events(calendar_id: str = 'primary', days: int = 7) -> Dict:
    """Get calendar events."""
    service = get_service('calendar', 'v3')
    
    now = datetime.now(timezone.utc)
    time_min = now.isoformat().replace('+00:00', 'Z')
    time_max = (now + timedelta(days=days)).isoformat().replace('+00:00', 'Z')
    
    results = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        maxResults=50,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = []
    for event in results.get('items', []):
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        events.append({
            'id': event['id'],
            'summary': event.get('summary', ''),
            'start': start,
            'end': end,
            'location': event.get('location', '')
        })
    
    return {'events': events}


def cal_create(summary: str, start: str, end: str, calendar_id: str = 'primary') -> Dict:
    """Create a calendar event."""
    service = get_service('calendar', 'v3')
    
    event = {
        'summary': summary,
        'start': {'dateTime': start, 'timeZone': 'Europe/London'},
        'end': {'dateTime': end, 'timeZone': 'Europe/London'},
    }
    
    result = service.events().insert(calendarId=calendar_id, body=event).execute()
    
    return {'success': True, 'eventId': result['id'], 'link': result.get('htmlLink')}


# ==================== DRIVE ====================

def drive_search(query: str, max_results: int = 20) -> Dict:
    """Search Drive files."""
    service = get_service('drive', 'v3')
    
    results = service.files().list(
        q=f"name contains '{query}' or fullText contains '{query}'",
        pageSize=max_results,
        fields="files(id, name, mimeType, modifiedTime, webViewLink)"
    ).execute()
    
    files = []
    for f in results.get('files', []):
        files.append({
            'id': f['id'],
            'name': f['name'],
            'mimeType': f['mimeType'],
            'modified': f.get('modifiedTime'),
            'link': f.get('webViewLink')
        })
    
    return {'files': files}


def drive_upload(local_path: str, folder_id: str = None, name: str = None) -> Dict:
    """Upload a file to Drive."""
    service = get_service('drive', 'v3')
    
    file_name = name or Path(local_path).name
    
    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    media = MediaFileUpload(local_path, resumable=True)
    
    result = service.files().create(
        body=file_metadata, media_body=media, fields='id, webViewLink'
    ).execute()
    
    return {'success': True, 'fileId': result['id'], 'link': result.get('webViewLink')}


def drive_download(file_id: str, output_path: str) -> Dict:
    """Download a file from Drive."""
    service = get_service('drive', 'v3')
    
    request = service.files().get_media(fileId=file_id)
    
    with open(output_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
    
    return {'success': True, 'path': output_path}


def drive_share(file_id: str, email: str, role: str = 'reader') -> Dict:
    """Share a Drive file."""
    service = get_service('drive', 'v3')
    
    permission = {
        'type': 'user',
        'role': role,
        'emailAddress': email
    }
    
    service.permissions().create(
        fileId=file_id, body=permission, sendNotificationEmail=False
    ).execute()
    
    return {'success': True, 'shared_with': email, 'role': role}


# ==================== DOCS ====================

def doc_create(title: str, content: str = '') -> Dict:
    """Create a Google Doc."""
    service = get_service('docs', 'v1')
    
    doc = service.documents().create(body={'title': title}).execute()
    doc_id = doc['documentId']
    
    if content:
        requests = [{'insertText': {'location': {'index': 1}, 'text': content}}]
        service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    
    return {'success': True, 'documentId': doc_id, 'link': f"https://docs.google.com/document/d/{doc_id}"}


def doc_read(doc_id: str) -> Dict:
    """Read a Google Doc."""
    service = get_service('docs', 'v1')
    
    doc = service.documents().get(documentId=doc_id).execute()
    
    # Extract text content
    content = ''
    for element in doc.get('body', {}).get('content', []):
        if 'paragraph' in element:
            for elem in element['paragraph'].get('elements', []):
                if 'textRun' in elem:
                    content += elem['textRun'].get('content', '')
    
    return {
        'title': doc.get('title'),
        'documentId': doc_id,
        'content': content[:10000]  # Truncate
    }


# ==================== SHEETS ====================

def sheet_read(sheet_id: str, range_name: str) -> Dict:
    """Read from a Google Sheet."""
    service = get_service('sheets', 'v4')
    
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=range_name
    ).execute()
    
    return {'values': result.get('values', [])}


def sheet_write(sheet_id: str, range_name: str, values: List[List]) -> Dict:
    """Write to a Google Sheet."""
    service = get_service('sheets', 'v4')
    
    body = {'values': values}
    
    result = service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    
    return {'success': True, 'updatedCells': result.get('updatedCells')}


# ==================== CLI ====================

def main():
    parser = argparse.ArgumentParser(description='Google Lean - Minimal Google Workspace tools')
    parser.add_argument('command', help='Command to run')
    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('--calendar', default='primary', help='Calendar ID')
    parser.add_argument('--days', type=int, default=7, help='Number of days for events')
    parser.add_argument('--folder', help='Drive folder ID')
    parser.add_argument('--name', help='File name')
    parser.add_argument('--role', default='reader', help='Share role')
    parser.add_argument('--add', action='append', help='Labels to add')
    parser.add_argument('--remove', action='append', help='Labels to remove')
    parser.add_argument('--content', help='Document content')
    parser.add_argument('--html', action='store_true', help='Send as HTML')
    
    args = parser.parse_args()
    
    try:
        result = None
        
        # Gmail
        if args.command == 'gmail-search':
            result = gmail_search(args.args[0] if args.args else '')
        elif args.command == 'gmail-read':
            result = gmail_read(args.args[0])
        elif args.command == 'gmail-read-batch':
            ids = args.args[0].split(',')
            result = gmail_read_batch(ids)
        elif args.command == 'gmail-labels':
            result = gmail_labels(args.args[0], args.add, args.remove)
        elif args.command == 'gmail-send':
            result = gmail_send(args.args[0], args.args[1], args.args[2], args.html)
        
        # Calendar
        elif args.command == 'cal-list':
            result = cal_list()
        elif args.command == 'cal-events':
            result = cal_events(args.calendar, args.days)
        elif args.command == 'cal-create':
            result = cal_create(args.args[0], args.args[1], args.args[2], args.calendar)
        
        # Drive
        elif args.command == 'drive-search':
            result = drive_search(args.args[0])
        elif args.command == 'drive-upload':
            result = drive_upload(args.args[0], args.folder, args.name)
        elif args.command == 'drive-download':
            result = drive_download(args.args[0], args.args[1])
        elif args.command == 'drive-share':
            result = drive_share(args.args[0], args.args[1], args.role)
        
        # Docs
        elif args.command == 'doc-create':
            result = doc_create(args.args[0], args.content or '')
        elif args.command == 'doc-read':
            result = doc_read(args.args[0])
        
        # Sheets
        elif args.command == 'sheet-read':
            result = sheet_read(args.args[0], args.args[1])
        elif args.command == 'sheet-write':
            values = json.loads(args.args[2])
            result = sheet_write(args.args[0], args.args[1], values)
        
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)
        
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
