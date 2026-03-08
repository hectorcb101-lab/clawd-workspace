#!/usr/bin/env python3
"""
Direct Google Workspace API client — bypasses mcporter/MCP entirely.
Uses the same credentials as check_emails.py with auto-refresh.

Usage:
    google_direct.py docs create "Title" [--content file.md] [--share email]
    google_direct.py docs list [--query "search terms"]
    google_direct.py docs read <doc_id>
    google_direct.py calendar list [--days N]
    google_direct.py calendar create "Title" --start "2026-02-20T10:00" --end "2026-02-20T11:00"
    google_direct.py drive list [--query "search terms"] [--folder folder_id]
    google_direct.py drive upload <file_path> [--folder folder_id] [--mime type]
    google_direct.py sheets create "Title" [--data file.csv]
    google_direct.py sheets read <sheet_id> [--range "Sheet1!A1:Z100"]
"""

import json
import sys
import os
import argparse
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_FILE = "/home/ubuntu/.google_workspace_mcp/credentials/hectorcb101@gmail.com.json"


def get_creds():
    """Load and auto-refresh Google credentials."""
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
        if hasattr(creds, 'expiry') and creds.expiry:
            token_data['expiry'] = creds.expiry.isoformat()
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)

    return creds


def get_service(api, version):
    return build(api, version, credentials=get_creds())


# ─── Google Docs ───────────────────────────────────────────────────

def docs_create(title, content_file=None, share_email=None):
    """Create a Google Doc, optionally with markdown content and sharing."""
    docs = get_service('docs', 'v1')
    drive = get_service('drive', 'v3')

    # Create empty doc
    doc = docs.documents().create(body={'title': title}).execute()
    doc_id = doc['documentId']
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    # Insert content if provided
    if content_file:
        if content_file == '-':
            content = sys.stdin.read()
        elif os.path.exists(content_file):
            with open(content_file, 'r') as f:
                content = f.read()
        else:
            content = content_file  # Treat as raw text

        if content.strip():
            requests = markdown_to_docs_requests(content)
            if requests:
                docs.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

    # Share if requested
    if share_email:
        drive.permissions().create(
            fileId=doc_id,
            body={'type': 'user', 'role': 'writer', 'emailAddress': share_email},
            sendNotificationEmail=False
        ).execute()

    print(json.dumps({
        'success': True,
        'documentId': doc_id,
        'title': title,
        'url': doc_url,
        'shared_with': share_email
    }, indent=2))


def markdown_to_docs_requests(md_text):
    """Convert markdown to Google Docs API requests with formatting."""
    requests = []
    lines = md_text.split('\n')
    current_index = 1  # Docs API uses 1-based index

    for line in lines:
        # Determine heading level
        heading_style = None
        text = line
        if line.startswith('### '):
            heading_style = 'HEADING_3'
            text = line[4:]
        elif line.startswith('## '):
            heading_style = 'HEADING_2'
            text = line[3:]
        elif line.startswith('# '):
            heading_style = 'HEADING_1'
            text = line[2:]

        # Clean up basic markdown formatting markers (bold/italic)
        clean_text = text.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
        insert_text = clean_text + '\n'

        # Insert the text
        requests.append({
            'insertText': {
                'location': {'index': current_index},
                'text': insert_text
            }
        })

        # Apply heading style
        if heading_style:
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': current_index,
                        'endIndex': current_index + len(insert_text)
                    },
                    'paragraphStyle': {'namedStyleType': heading_style},
                    'fields': 'namedStyleType'
                }
            })

        # Apply bold formatting
        bold_ranges = find_markdown_ranges(text, '**')
        for start, end in bold_ranges:
            abs_start = current_index + start
            abs_end = current_index + end
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': abs_start, 'endIndex': abs_end},
                    'textStyle': {'bold': True},
                    'fields': 'bold'
                }
            })

        current_index += len(insert_text)

    return requests


def find_markdown_ranges(text, marker):
    """Find ranges of text wrapped in markdown markers (e.g. **bold**)."""
    ranges = []
    search_text = text
    offset = 0
    while marker in search_text:
        start = search_text.index(marker)
        remaining = search_text[start + len(marker):]
        if marker not in remaining:
            break
        end = remaining.index(marker)
        # Calculate positions in cleaned text (without markers)
        clean_start = start - (len(ranges) * len(marker) * 2)
        clean_end = clean_start + end
        ranges.append((clean_start, clean_end))
        search_text = remaining[end + len(marker):]
        offset = start + len(marker) + end + len(marker)
    return ranges


def docs_list(query=None):
    """List Google Docs."""
    drive = get_service('drive', 'v3')
    q = "mimeType='application/vnd.google-apps.document'"
    if query:
        q += f" and name contains '{query}'"
    q += " and trashed=false"

    results = drive.files().list(
        q=q, pageSize=20,
        fields="files(id, name, modifiedTime, webViewLink)",
        orderBy="modifiedTime desc"
    ).execute()

    files = results.get('files', [])
    print(json.dumps({'success': True, 'count': len(files), 'documents': files}, indent=2))


def docs_read(doc_id):
    """Read a Google Doc's content."""
    docs = get_service('docs', 'v1')
    doc = docs.documents().get(documentId=doc_id).execute()

    # Extract text content
    content = ''
    for element in doc.get('body', {}).get('content', []):
        if 'paragraph' in element:
            for elem in element['paragraph'].get('elements', []):
                if 'textRun' in elem:
                    content += elem['textRun']['content']

    print(json.dumps({
        'success': True,
        'documentId': doc_id,
        'title': doc.get('title', ''),
        'content': content
    }, indent=2))


# ─── Google Calendar ───────────────────────────────────────────────

def calendar_list(days=7):
    """List upcoming calendar events."""
    cal = get_service('calendar', 'v3')
    now = datetime.now(timezone.utc)
    time_max = now + timedelta(days=days)

    events_result = cal.events().list(
        calendarId='primary',
        timeMin=now.isoformat(),
        timeMax=time_max.isoformat(),
        maxResults=50,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    output = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        output.append({
            'id': event['id'],
            'summary': event.get('summary', 'No title'),
            'start': start,
            'end': end,
            'location': event.get('location', ''),
            'description': event.get('description', '')[:200] if event.get('description') else ''
        })

    print(json.dumps({'success': True, 'count': len(output), 'events': output}, indent=2))


def calendar_create(title, start, end, description=None, location=None):
    """Create a calendar event."""
    cal = get_service('calendar', 'v3')

    event = {
        'summary': title,
        'start': {'dateTime': start, 'timeZone': 'Europe/London'},
        'end': {'dateTime': end, 'timeZone': 'Europe/London'},
    }
    if description:
        event['description'] = description
    if location:
        event['location'] = location

    created = cal.events().insert(calendarId='primary', body=event).execute()
    print(json.dumps({
        'success': True,
        'eventId': created['id'],
        'summary': created['summary'],
        'htmlLink': created.get('htmlLink', '')
    }, indent=2))


# ─── Google Drive ──────────────────────────────────────────────────

def drive_list(query=None, folder_id=None):
    """List Drive files."""
    drive = get_service('drive', 'v3')
    q = "trashed=false"
    if query:
        q += f" and name contains '{query}'"
    if folder_id:
        q += f" and '{folder_id}' in parents"

    results = drive.files().list(
        q=q, pageSize=20,
        fields="files(id, name, mimeType, modifiedTime, webViewLink, size)",
        orderBy="modifiedTime desc"
    ).execute()

    files = results.get('files', [])
    print(json.dumps({'success': True, 'count': len(files), 'files': files}, indent=2))


def drive_upload(file_path, folder_id=None, mime_type=None):
    """Upload a file to Drive."""
    drive = get_service('drive', 'v3')

    if not mime_type:
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'

    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, mimetype=mime_type)
    uploaded = drive.files().create(
        body=file_metadata, media_body=media, fields='id, name, webViewLink'
    ).execute()

    print(json.dumps({
        'success': True,
        'fileId': uploaded['id'],
        'name': uploaded['name'],
        'url': uploaded.get('webViewLink', '')
    }, indent=2))


# ─── Google Sheets ─────────────────────────────────────────────────

def sheets_create(title, data_file=None):
    """Create a Google Sheet, optionally with CSV data."""
    sheets = get_service('sheets', 'v4')
    drive = get_service('drive', 'v3')

    spreadsheet = sheets.spreadsheets().create(
        body={'properties': {'title': title}}
    ).execute()

    sheet_id = spreadsheet['spreadsheetId']
    sheet_url = spreadsheet['spreadsheetUrl']

    if data_file and os.path.exists(data_file):
        import csv
        with open(data_file, 'r') as f:
            reader = csv.reader(f)
            values = list(reader)

        if values:
            sheets.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range='Sheet1!A1',
                valueInputOption='USER_ENTERED',
                body={'values': values}
            ).execute()

    print(json.dumps({
        'success': True,
        'spreadsheetId': sheet_id,
        'title': title,
        'url': sheet_url
    }, indent=2))


def sheets_read(sheet_id, range_str='Sheet1!A1:Z100'):
    """Read a Google Sheet."""
    sheets = get_service('sheets', 'v4')
    result = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=range_str
    ).execute()

    values = result.get('values', [])
    print(json.dumps({
        'success': True,
        'spreadsheetId': sheet_id,
        'range': range_str,
        'rows': len(values),
        'values': values
    }, indent=2))


# ─── CLI ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Direct Google Workspace API client')
    subparsers = parser.add_subparsers(dest='service')

    # Docs
    docs_parser = subparsers.add_parser('docs')
    docs_sub = docs_parser.add_subparsers(dest='action')

    docs_create_p = docs_sub.add_parser('create')
    docs_create_p.add_argument('title')
    docs_create_p.add_argument('--content', help='Markdown file, raw text, or - for stdin')
    docs_create_p.add_argument('--share', help='Email to share with')

    docs_list_p = docs_sub.add_parser('list')
    docs_list_p.add_argument('--query', help='Search query')

    docs_read_p = docs_sub.add_parser('read')
    docs_read_p.add_argument('doc_id')

    # Calendar
    cal_parser = subparsers.add_parser('calendar')
    cal_sub = cal_parser.add_subparsers(dest='action')

    cal_list_p = cal_sub.add_parser('list')
    cal_list_p.add_argument('--days', type=int, default=7)

    cal_create_p = cal_sub.add_parser('create')
    cal_create_p.add_argument('title')
    cal_create_p.add_argument('--start', required=True)
    cal_create_p.add_argument('--end', required=True)
    cal_create_p.add_argument('--description')
    cal_create_p.add_argument('--location')

    # Drive
    drive_parser = subparsers.add_parser('drive')
    drive_sub = drive_parser.add_subparsers(dest='action')

    drive_list_p = drive_sub.add_parser('list')
    drive_list_p.add_argument('--query', help='Search query')
    drive_list_p.add_argument('--folder', help='Folder ID')

    drive_upload_p = drive_sub.add_parser('upload')
    drive_upload_p.add_argument('file_path')
    drive_upload_p.add_argument('--folder', help='Folder ID')
    drive_upload_p.add_argument('--mime', help='MIME type')

    # Sheets
    sheets_parser = subparsers.add_parser('sheets')
    sheets_sub = sheets_parser.add_subparsers(dest='action')

    sheets_create_p = sheets_sub.add_parser('create')
    sheets_create_p.add_argument('title')
    sheets_create_p.add_argument('--data', help='CSV file path')

    sheets_read_p = sheets_sub.add_parser('read')
    sheets_read_p.add_argument('sheet_id')
    sheets_read_p.add_argument('--range', default='Sheet1!A1:Z100')

    args = parser.parse_args()

    if not args.service:
        parser.print_help()
        sys.exit(1)

    if args.service == 'docs':
        if args.action == 'create':
            docs_create(args.title, args.content, args.share)
        elif args.action == 'list':
            docs_list(args.query)
        elif args.action == 'read':
            docs_read(args.doc_id)
    elif args.service == 'calendar':
        if args.action == 'list':
            calendar_list(args.days)
        elif args.action == 'create':
            calendar_create(args.title, args.start, args.end, args.description, args.location)
    elif args.service == 'drive':
        if args.action == 'list':
            drive_list(args.query, args.folder)
        elif args.action == 'upload':
            drive_upload(args.file_path, args.folder, args.mime)
    elif args.service == 'sheets':
        if args.action == 'create':
            sheets_create(args.title, args.data)
        elif args.action == 'read':
            sheets_read(args.sheet_id, getattr(args, 'range', 'Sheet1!A1:Z100'))


if __name__ == '__main__':
    main()
