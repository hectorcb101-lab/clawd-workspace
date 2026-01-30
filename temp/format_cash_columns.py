#!/usr/bin/env python3
"""Format the new cash columns in the Rugby Sponsorship Google Sheet."""

import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SPREADSHEET_ID = '1id_VEKkZVsPHlirF4Igri9unXABnM26UnadD-ht6g6A'
TOKEN_PATH = '/home/ubuntu/.workspace-mcp/token_hectorcb101@gmail.com.json'

def get_credentials():
    """Get valid credentials for Google Sheets API."""
    with open(TOKEN_PATH, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data.get('access_token') or token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes', ['https://www.googleapis.com/auth/spreadsheets'])
    )
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return creds

def format_cash_columns():
    """Apply formatting to the new cash columns."""
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    # Color definitions
    navy = {'red': 0.118, 'green': 0.227, 'blue': 0.373}
    white = {'red': 1, 'green': 1, 'blue': 1}
    light_blue = {'red': 0.878, 'green': 0.925, 'blue': 0.969}
    light_green = {'red': 0.851, 'green': 0.918, 'blue': 0.827}
    
    requests = []
    
    # Get sheet ID
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_id = sheet_metadata['sheets'][0]['properties']['sheetId']
    
    # 1. Format new header columns (N1:O1) - Navy background, white text
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 13, 'endColumnIndex': 15},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': navy,
                    'textFormat': {'bold': True, 'foregroundColor': white, 'fontSize': 11},
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE',
                    'wrapStrategy': 'WRAP'
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy)'
        }
    })
    
    # 2. Format data rows for new columns - alternating colors
    for row in range(1, 11):
        bg_color = light_blue if row % 2 == 1 else white
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': row, 'endRowIndex': row + 1, 'startColumnIndex': 13, 'endColumnIndex': 15},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': bg_color,
                        'verticalAlignment': 'MIDDLE',
                        'wrapStrategy': 'WRAP'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,verticalAlignment,wrapStrategy)'
            }
        })
    
    # 3. Set column widths for new columns
    column_widths = [
        (13, 150),  # N - Cash/Cash Equiv
        (14, 300),  # O - Source/Notes
    ]
    
    for col_idx, width in column_widths:
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': col_idx,
                    'endIndex': col_idx + 1
                },
                'properties': {'pixelSize': width},
                'fields': 'pixelSize'
            }
        })
    
    # 4. Update borders to include new columns
    requests.append({
        'updateBorders': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 11, 'startColumnIndex': 0, 'endColumnIndex': 15},
            'top': {'style': 'SOLID', 'width': 2, 'color': navy},
            'bottom': {'style': 'SOLID', 'width': 2, 'color': navy},
            'left': {'style': 'SOLID', 'width': 2, 'color': navy},
            'right': {'style': 'SOLID', 'width': 2, 'color': navy},
            'innerHorizontal': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
            'innerVertical': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}}
        }
    })
    
    # 5. Highlight cash column with light green for positive values
    green_rows = [6, 10]  # Mattioli Woods (row 7) and StoneX (row 11)
    for row in green_rows:
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': row, 'endRowIndex': row + 1, 'startColumnIndex': 13, 'endColumnIndex': 14},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': light_green,
                        'textFormat': {'bold': True}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        })
    
    # Execute all formatting requests
    body = {'requests': requests}
    response = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f"✅ Cash columns formatted! {len(requests)} updates made.")
    return response

if __name__ == '__main__':
    format_cash_columns()
