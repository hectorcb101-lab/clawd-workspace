#!/usr/bin/env python3
"""
Drive utilities - Create folders, move files
"""
import json
import argparse
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_FILE = "/home/ubuntu/.workspace-mcp/token_hectorcb101@gmail.com.json"
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment")

def get_credentials():
    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data.get('access_token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=token_data.get('scopes', ['https://www.googleapis.com/auth/drive'])
    )
    
    if creds.expired or not creds.valid:
        creds.refresh(Request())
        token_data['access_token'] = creds.token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f)
    
    return creds

def create_folder(name: str, parent_id: str = None):
    """Create a folder in Drive."""
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        metadata['parents'] = [parent_id]
    
    folder = service.files().create(body=metadata, fields='id,name,webViewLink').execute()
    print(f"Created folder: {folder['name']}")
    print(f"Folder ID: {folder['id']}")
    print(f"Link: {folder.get('webViewLink', 'N/A')}")
    return folder

def move_file(file_id: str, folder_id: str):
    """Move a file to a folder."""
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    # Get current parents
    file = service.files().get(fileId=file_id, fields='parents').execute()
    previous_parents = ",".join(file.get('parents', []))
    
    # Move file
    file = service.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents=previous_parents,
        fields='id, name, parents, webViewLink'
    ).execute()
    
    print(f"Moved file: {file['name']}")
    print(f"New link: {file.get('webViewLink', 'N/A')}")
    return file

def upload_file(file_path: str, folder_id: str = None, file_name: str = None):
    """Upload a file to Drive."""
    from googleapiclient.http import MediaFileUpload
    import os
    
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    if not file_name:
        file_name = os.path.basename(file_path)
    
    # Determine mime type
    ext = os.path.splitext(file_path)[1].lower()
    mime_types = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.txt': 'text/plain',
    }
    mime_type = mime_types.get(ext, 'application/octet-stream')
    
    metadata = {'name': file_name}
    if folder_id:
        metadata['parents'] = [folder_id]
    
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    file = service.files().create(body=metadata, media_body=media, fields='id,name,webViewLink').execute()
    
    print(f"Uploaded: {file['name']}")
    print(f"File ID: {file['id']}")
    print(f"Link: {file.get('webViewLink', 'N/A')}")
    return file

def share_folder(folder_id: str, email: str = None, anyone: bool = False):
    """Share a folder."""
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    if anyone:
        permission = {'type': 'anyone', 'role': 'reader'}
    else:
        permission = {'type': 'user', 'role': 'writer', 'emailAddress': email}
    
    service.permissions().create(fileId=folder_id, body=permission).execute()
    
    # Get shareable link
    file = service.files().get(fileId=folder_id, fields='webViewLink').execute()
    print(f"Shared! Link: {file.get('webViewLink')}")
    return file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    
    # Create folder
    create_p = subparsers.add_parser('create-folder')
    create_p.add_argument('--name', required=True)
    create_p.add_argument('--parent', default=None)
    
    # Move file
    move_p = subparsers.add_parser('move')
    move_p.add_argument('--file-id', required=True)
    move_p.add_argument('--folder-id', required=True)
    
    # Share
    share_p = subparsers.add_parser('share')
    share_p.add_argument('--folder-id', required=True)
    share_p.add_argument('--email', default=None)
    share_p.add_argument('--anyone', action='store_true')
    
    # Upload
    upload_p = subparsers.add_parser('upload')
    upload_p.add_argument('--file', required=True)
    upload_p.add_argument('--folder-id', default=None)
    upload_p.add_argument('--name', default=None)
    
    args = parser.parse_args()
    
    if args.command == 'create-folder':
        create_folder(args.name, args.parent)
    elif args.command == 'move':
        move_file(args.file_id, args.folder_id)
    elif args.command == 'share':
        share_folder(args.folder_id, args.email, args.anyone)
    elif args.command == 'upload':
        upload_file(args.file, args.folder_id, args.name)
