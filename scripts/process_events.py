#!/usr/bin/env python3
"""
Event Processing Script
Reads a Google Sheet, processes events, logs to file, updates status, pushes to GitHub.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration
SPREADSHEET_ID = "1ptHSLEHCzI5GeCHMbMvxwhF6DzqGwDE9COgWGp-Wh68"
CREDS_PATH = os.path.expanduser("~/.google_workspace_mcp/credentials/hectorcb101@gmail.com.json")
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / f"event_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def load_credentials():
    """Load OAuth credentials from workspace-mcp format."""
    print(f"[INFO] Loading credentials from {CREDS_PATH}")
    
    with open(CREDS_PATH, 'r') as f:
        cred_data = json.load(f)
    
    creds = Credentials(
        token=cred_data['token'],
        refresh_token=cred_data.get('refresh_token'),
        token_uri=cred_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=cred_data['client_id'],
        client_secret=cred_data['client_secret'],
        scopes=cred_data.get('scopes', [])
    )
    
    print(f"[INFO] Credentials loaded. Token expires: {cred_data.get('expiry', 'unknown')}")
    return creds

def read_sheet(service):
    """Read all rows from the sheet."""
    print(f"[INFO] Reading sheet {SPREADSHEET_ID}")
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="A1:C100"
    ).execute()
    
    rows = result.get('values', [])
    print(f"[INFO] Found {len(rows)} rows (including header)")
    return rows

def process_events(rows, log_file):
    """Process events and log them."""
    processed = []
    
    # Skip header row
    for i, row in enumerate(rows[1:], start=2):
        if len(row) < 3:
            continue
            
        timestamp, event, status = row[0], row[1], row[2]
        
        if status.lower() == 'pending':
            log_entry = f"[{datetime.now().isoformat()}] Processing row {i}: {timestamp} | {event} | {status}"
            print(log_entry)
            log_file.write(log_entry + "\n")
            processed.append(i)
    
    return processed

def update_sheet(service, processed_rows):
    """Mark processed rows as 'processed'."""
    if not processed_rows:
        print("[INFO] No rows to update")
        return
    
    print(f"[INFO] Updating {len(processed_rows)} rows to 'processed'")
    
    # Build batch update
    data = []
    for row_num in processed_rows:
        data.append({
            'range': f'C{row_num}',
            'values': [['processed']]
        })
    
    body = {
        'valueInputOption': 'RAW',
        'data': data
    }
    
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=body
    ).execute()
    
    print(f"[INFO] Updated {result.get('totalUpdatedCells', 0)} cells")

def git_push(log_file_path):
    """Commit and push the log file to GitHub."""
    repo_dir = Path(__file__).parent.parent
    
    print(f"[INFO] Adding log file to git: {log_file_path}")
    
    # Add the log file
    subprocess.run(['git', 'add', str(log_file_path)], cwd=repo_dir, check=True)
    
    # Commit
    commit_msg = f"Add event processing log {log_file_path.name}"
    result = subprocess.run(
        ['git', 'commit', '-m', commit_msg],
        cwd=repo_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
            print("[INFO] Nothing to commit")
            return
        print(f"[ERROR] Git commit failed: {result.stderr}")
        raise Exception(f"Git commit failed: {result.stderr}")
    
    print(f"[INFO] Committed: {commit_msg}")
    
    # Push
    result = subprocess.run(
        ['git', 'push', 'origin', 'HEAD'],
        cwd=repo_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"[ERROR] Git push failed: {result.stderr}")
        raise Exception(f"Git push failed: {result.stderr}")
    
    print("[INFO] Pushed to GitHub successfully")

def main():
    print("=" * 60)
    print("EVENT PROCESSING SCRIPT")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load credentials
        creds = load_credentials()
        
        # Build Sheets service
        print("[INFO] Building Sheets API service")
        service = build('sheets', 'v4', credentials=creds)
        
        # Read sheet
        rows = read_sheet(service)
        
        # Process events and log
        print(f"[INFO] Writing log to {LOG_FILE}")
        with open(LOG_FILE, 'w') as log_file:
            log_file.write(f"Event Processing Log - {datetime.now().isoformat()}\n")
            log_file.write("=" * 60 + "\n\n")
            
            processed_rows = process_events(rows, log_file)
            
            log_file.write(f"\n{'=' * 60}\n")
            log_file.write(f"Total processed: {len(processed_rows)} events\n")
        
        # Update sheet
        update_sheet(service, processed_rows)
        
        # Git push
        git_push(LOG_FILE)
        
        print("\n" + "=" * 60)
        print("COMPLETE!")
        print(f"- Processed: {len(processed_rows)} events")
        print(f"- Log file: {LOG_FILE}")
        print(f"- Sheet updated: Yes")
        print(f"- Pushed to GitHub: Yes")
        print("=" * 60)
        
    except HttpError as e:
        print(f"[ERROR] Google API error: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        raise

if __name__ == "__main__":
    main()
