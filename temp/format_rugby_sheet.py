#!/usr/bin/env python3
"""Format the Rugby Sponsorship Google Sheet with colors and proper spacing."""

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
    
    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return creds

def format_spreadsheet():
    """Apply formatting to the spreadsheet."""
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    # Color definitions (RGB 0-1 scale)
    navy = {'red': 0.118, 'green': 0.227, 'blue': 0.373}  # #1e3a5f
    gold = {'red': 0.722, 'green': 0.525, 'blue': 0.043}  # #b8860b
    light_gold = {'red': 0.965, 'green': 0.933, 'blue': 0.831}  # light gold
    light_blue = {'red': 0.878, 'green': 0.925, 'blue': 0.969}  # #e0ecf8
    green = {'red': 0.565, 'green': 0.792, 'blue': 0.565}  # #90ca90
    red = {'red': 0.957, 'green': 0.643, 'blue': 0.643}  # #f4a4a4
    white = {'red': 1, 'green': 1, 'blue': 1}
    light_gray = {'red': 0.95, 'green': 0.95, 'blue': 0.95}
    
    requests = []
    
    # Get sheet ID
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_id = sheet_metadata['sheets'][0]['properties']['sheetId']
    
    # 1. Format header row (Row 1) - Navy background, white text, bold
    requests.append({
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 13},
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
    
    # 2. Format data rows (2-11) - alternating colors
    for row in range(1, 11):
        bg_color = light_blue if row % 2 == 1 else white
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': row, 'endRowIndex': row + 1, 'startColumnIndex': 0, 'endColumnIndex': 13},
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
    
    # 3. Color code "UK-Based?" column (E) - Green for YES, Red for NO
    uk_based_col = 4  # Column E (0-indexed)
    yes_rows = [1, 3, 4, 5, 6, 8, 9, 10]  # YES rows (0-indexed)
    no_rows = [2, 7]  # NO rows
    
    for row in yes_rows:
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': row, 'endRowIndex': row + 1, 'startColumnIndex': uk_based_col, 'endColumnIndex': uk_based_col + 1},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': green,
                        'textFormat': {'bold': True},
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })
    
    for row in no_rows:
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': row, 'endRowIndex': row + 1, 'startColumnIndex': uk_based_col, 'endColumnIndex': uk_based_col + 1},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': red,
                        'textFormat': {'bold': True},
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })
    
    # 4. Format section headers (rows 14, 21, 32, 43, 58) - Gold background
    section_rows = [13, 20, 31, 42, 57]  # 0-indexed
    for row in section_rows:
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': row, 'endRowIndex': row + 1, 'startColumnIndex': 0, 'endColumnIndex': 13},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': gold,
                        'textFormat': {'bold': True, 'foregroundColor': white, 'fontSize': 12},
                        'horizontalAlignment': 'LEFT'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })
    
    # 5. Format sub-headers (rows 22, 33, 44) - Light gold background
    sub_header_rows = [21, 32, 43]  # 0-indexed
    for row in sub_header_rows:
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': row, 'endRowIndex': row + 1, 'startColumnIndex': 0, 'endColumnIndex': 13},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': light_gold,
                        'textFormat': {'bold': True, 'fontSize': 10},
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })
    
    # 6. Set column widths for better spacing
    column_widths = [
        (0, 180),   # A - Club
        (1, 220),   # B - Principal Sponsor
        (2, 180),   # C - Industry
        (3, 180),   # D - UK HQ Location
        (4, 100),   # E - UK-Based?
        (5, 250),   # F - CEO/MD
        (6, 200),   # G - Group CEO
        (7, 200),   # H - Parent Company
        (8, 160),   # I - Parent HQ
        (9, 160),   # J - Sponsorship Since
        (10, 220),  # K - Stadium
        (11, 350),  # L - Notes
        (12, 160),  # M - Website
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
    
    # 7. Set row heights for header
    requests.append({
        'updateDimensionProperties': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'ROWS',
                'startIndex': 0,
                'endIndex': 1
            },
            'properties': {'pixelSize': 50},
            'fields': 'pixelSize'
        }
    })
    
    # Set row heights for data rows
    requests.append({
        'updateDimensionProperties': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'ROWS',
                'startIndex': 1,
                'endIndex': 11
            },
            'properties': {'pixelSize': 35},
            'fields': 'pixelSize'
        }
    })
    
    # 8. Add borders to main table (rows 1-11)
    requests.append({
        'updateBorders': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 11, 'startColumnIndex': 0, 'endColumnIndex': 13},
            'top': {'style': 'SOLID', 'width': 2, 'color': navy},
            'bottom': {'style': 'SOLID', 'width': 2, 'color': navy},
            'left': {'style': 'SOLID', 'width': 2, 'color': navy},
            'right': {'style': 'SOLID', 'width': 2, 'color': navy},
            'innerHorizontal': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
            'innerVertical': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}}
        }
    })
    
    # 9. Freeze header row
    requests.append({
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'gridProperties': {'frozenRowCount': 1}
            },
            'fields': 'gridProperties.frozenRowCount'
        }
    })
    
    # 10. Add borders to league sponsors table (rows 22-30)
    requests.append({
        'updateBorders': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 21, 'endRowIndex': 30, 'startColumnIndex': 0, 'endColumnIndex': 6},
            'top': {'style': 'SOLID', 'width': 2, 'color': navy},
            'bottom': {'style': 'SOLID', 'width': 2, 'color': navy},
            'left': {'style': 'SOLID', 'width': 2, 'color': navy},
            'right': {'style': 'SOLID', 'width': 2, 'color': navy},
            'innerHorizontal': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
            'innerVertical': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}}
        }
    })
    
    # 11. Add borders to company details table (rows 33-41)
    requests.append({
        'updateBorders': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 32, 'endRowIndex': 41, 'startColumnIndex': 0, 'endColumnIndex': 8},
            'top': {'style': 'SOLID', 'width': 2, 'color': navy},
            'bottom': {'style': 'SOLID', 'width': 2, 'color': navy},
            'left': {'style': 'SOLID', 'width': 2, 'color': navy},
            'right': {'style': 'SOLID', 'width': 2, 'color': navy},
            'innerHorizontal': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
            'innerVertical': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}}
        }
    })
    
    # 12. Add borders to CEO table (rows 44-56)
    requests.append({
        'updateBorders': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 43, 'endRowIndex': 56, 'startColumnIndex': 0, 'endColumnIndex': 7},
            'top': {'style': 'SOLID', 'width': 2, 'color': navy},
            'bottom': {'style': 'SOLID', 'width': 2, 'color': navy},
            'left': {'style': 'SOLID', 'width': 2, 'color': navy},
            'right': {'style': 'SOLID', 'width': 2, 'color': navy},
            'innerHorizontal': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
            'innerVertical': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}}
        }
    })
    
    # 13. Format alternating rows for other tables
    # League sponsors table (rows 23-30)
    for row in range(22, 30):
        bg_color = light_blue if row % 2 == 0 else white
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': row, 'endRowIndex': row + 1, 'startColumnIndex': 0, 'endColumnIndex': 6},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': bg_color,
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,verticalAlignment)'
            }
        })
    
    # Company details table (rows 34-41)
    for row in range(33, 41):
        bg_color = light_blue if row % 2 == 1 else white
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': row, 'endRowIndex': row + 1, 'startColumnIndex': 0, 'endColumnIndex': 8},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': bg_color,
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,verticalAlignment)'
            }
        })
    
    # CEO table (rows 45-56)
    for row in range(44, 56):
        bg_color = light_blue if row % 2 == 0 else white
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': row, 'endRowIndex': row + 1, 'startColumnIndex': 0, 'endColumnIndex': 7},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': bg_color,
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,verticalAlignment)'
            }
        })
    
    # Execute all formatting requests
    body = {'requests': requests}
    response = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print(f"✅ Formatting applied successfully! {len(requests)} updates made.")
    return response

if __name__ == '__main__':
    format_spreadsheet()
