#!/usr/bin/env python3
"""Build a beautifully formatted Six Nations Fantasy Doc"""

import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load credentials
creds_path = os.path.expanduser("~/.google_workspace_mcp/credentials/hectorcb101@gmail.com.json")
with open(creds_path) as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data['token'],
    refresh_token=token_data.get('refresh_token'),
    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
    client_id=token_data.get('client_id'),
    client_secret=token_data.get('client_secret')
)

docs_service = build('docs', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

DOC_ID = "1iBoI_8bb6P0jx9qIggXNs6yLzKseOggmFoSQkspNjik"

# Build the document content
requests = []

def add_text(text, bold=False, heading=None, color=None):
    """Add styled text"""
    start_index = requests[-1]['endIndex'] if requests and 'endIndex' in requests[-1] else 1
    
    # Insert text
    requests.append({
        'insertText': {
            'location': {'index': start_index},
            'text': text
        }
    })
    
    end_index = start_index + len(text)
    
    # Style it
    style = {}
    if bold:
        style['bold'] = True
    if color:
        style['foregroundColor'] = {'color': {'rgbColor': color}}
    
    if style:
        requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start_index, 'endIndex': end_index},
                'textStyle': style,
                'fields': ','.join(style.keys())
            }
        })
    
    if heading:
        requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start_index, 'endIndex': end_index},
                'paragraphStyle': {'namedStyleType': heading},
                'fields': 'namedStyleType'
            }
        })
    
    return end_index

# Clear existing content first
doc = docs_service.documents().get(documentId=DOC_ID).execute()
content = doc.get('body', {}).get('content', [])
if len(content) > 1:
    end_idx = content[-1].get('endIndex', 1) - 1
    if end_idx > 1:
        requests.append({
            'deleteContentRange': {
                'range': {'startIndex': 1, 'endIndex': end_idx}
            }
        })

# Build fresh content
full_content = """🏆 SIX NATIONS FANTASY RUGBY 2026
ATLAS WINNING STRATEGY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 COMPETITION INTEL
• Pot: £85 | 17 competitors
• Budget: 200 stars
• Deadline: Thursday 5th February

📈 BETTING ODDS
🇫🇷 France — 8/11 (HEAVY FAVOURITES)
🏴󠁧󠁢󠁥󠁮󠁧󠁿 England — 11/4 (11-game winning streak)
🇮🇪 Ireland — 5/1
🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland — 14/1
🏴󠁧󠁢󠁷󠁬󠁳󠁿 Wales — 100/1 (AVOID)
🇮🇹 Italy — 125/1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 ROUND 1 OPTIMAL SQUAD
Strategy: Stack England (vs Wales try-fest) + key France/Ireland picks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STARTING XV

15. THOMAS RAMOS 🇫🇷 (C) — 15★
    Toulouse | 71 pts in 2025 Six Nations
    CAPTAIN EVERY FRANCE GAME — double kicking points

14. LOUIS BIELLE-BIARREY 🇫🇷 — 13★
    Bordeaux | 8 tries in 2025 (RECORD)
    Scored in EVERY game | Player of Tournament 2025

13. TOMMY FREEMAN 🏴󠁧󠁢󠁥󠁮󠁧󠁿 — 12★
    Northampton | Prem Team of Season
    England vs Wales = try-fest incoming

12. TOMMASO MENONCELLO 🇮🇹 — 10★
    Benetton | Italy's best back
    Value pick — Six Nations POTT nominee 2025

11. IMMANUEL FEYI-WABOSO 🏴󠁧󠁢󠁥󠁮󠁧󠁿 — 12★
    Exeter | Electric pace
    Winger vs Wales weak defence

10. MARCUS SMITH 🏴󠁧󠁢󠁥󠁮󠁧󠁿 — 14★
    Harlequins | England first-choice 10
    Kicks + tries vs Wales

9. ANTOINE DUPONT 🇫🇷 — 16★
    Toulouse | World's best scrum-half
    POTM potential every game

8. BEN EARL 🏴󠁧󠁢󠁥󠁮󠁧󠁿 — 14★
    Saracens | Lions 2025, England's best
    Try-scoring 8 = 15 pts per try

7. JOSH VAN DER FLIER 🇮🇪 — 13★
    Leinster | Tackle machine
    Consistent floor, breakdown specialist

6. TADHG BEIRNE 🇮🇪 — 13★
    Munster | Lineout steals = 7 pts each!
    Six Nations Team of Tournament 2025

5. JAMES RYAN 🇮🇪 — 10★
    Leinster | Solid lock
    Ireland set piece dominance

4. DAFYDD JENKINS 🏴󠁧󠁢󠁷󠁬󠁳󠁿 — 9★
    Exeter | Budget lock pick
    Will make tackles vs England

3. TADHG FURLONG 🇮🇪 — 11★
    Leinster | Ireland anchor
    Scrummaging + carries

2. DAN SHEEHAN 🇮🇪 — 16★
    Leinster | 12 TRIES IN 9 GAMES
    Try-scoring hooker = 15 pts per try

1. SIMONE FERRARI 🇮🇹 — 8★
    Benetton | BARGAIN
    High tackle count for the price

TOTAL: 186★

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 SUPERSUB (TRIPLE POINTS!)

HENRY POLLOCK 🏴󠁧󠁢󠁥󠁮󠁧󠁿 — 10★
Northampton Saints | 20 years old

Stats:
• 6 Champions Cup tries in 6 games
• 15 turnovers won
• Prem Breakthrough Player of Season

Why: If he scores off the bench = 45 POINTS (15 × 3)
Check Friday team sheet — must be on BENCH, not starting.

TOTAL SQUAD: 196★ (4★ buffer)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ CRITICAL SQUAD NEWS

FRANCE 🇫🇷
❌ Damian Penaud DROPPED (40 tries in 59 caps)
❌ Gregory Alldritt DROPPED
❌ Gael Fickou DROPPED
✅ Dupont, Ramos, Bielle-Biarrey IN

ITALY 🇮🇹
❌ Ange Capuozzo OUT (finger fracture)
❌ Edoardo Todaro OUT (ACL injury)
✅ Menoncello only reliable pick

ENGLAND 🏴󠁧󠁢󠁥󠁮󠁧󠁿
✅ 11-GAME WINNING STREAK
✅ Full strength — Earl, Smith, Freeman, Feyi-Waboso

IRELAND 🇮🇪
❌ Andrew Porter injured
✅ Sheehan, Beirne, van der Flier fit

WALES 🏴󠁧󠁢󠁷󠁬󠁳󠁿
⚠️ Wooden spoon last 2 years — AVOID R1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 ROUND 1 FIXTURES (5-7 Feb)

🇫🇷 France vs Ireland 🇮🇪
→ Tight game — captain Ramos for kicks

🇮🇹 Italy vs Scotland 🏴󠁧󠁢󠁳󠁣󠁴󠁿
→ Scotland should score freely

🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENGLAND vs Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿
→ STACK ENGLAND — 4+ tries expected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏅 WINNING PRINCIPLES

1. CAPTAIN RAMOS EVERY FRANCE GAME
   Non-10 kicker = guaranteed double points on kicks

2. STACK TEAMS WITH EASY FIXTURES
   R1: England (vs Wales)
   R2/R3: France (vs Wales/Italy)

3. TARGET TRY-SCORING FORWARDS
   15 pts vs 10 pts for backs
   Sheehan + Earl = premium

4. LINEOUT STEAL SPECIALISTS
   7 pts per steal — Beirne, Itoje hidden value

5. USE UNLIMITED TRANSFERS
   Rebuild entire team each week
   No loyalty — follow the fixtures

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ FRIDAY CHECKLIST

□ Check all team sheet announcements
□ Verify 15 picks are STARTING
□ Confirm Pollock is on BENCH
□ Research any surprise selections
□ Lock team before deadline

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔮 PREDICTION

Title: France 🇫🇷 (8/11)
Wooden Spoon: Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿

Let's win that £85! 💰

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Compiled by Atlas 🏛️
1st February 2026
"""

# Insert the content
requests.append({
    'insertText': {
        'location': {'index': 1},
        'text': full_content
    }
})

# Apply heading styles
# Title
requests.append({
    'updateParagraphStyle': {
        'range': {'startIndex': 1, 'endIndex': 38},
        'paragraphStyle': {'namedStyleType': 'TITLE'},
        'fields': 'namedStyleType'
    }
})

# Make title bold and larger
requests.append({
    'updateTextStyle': {
        'range': {'startIndex': 1, 'endIndex': 38},
        'textStyle': {
            'bold': True,
            'fontSize': {'magnitude': 24, 'unit': 'PT'},
            'foregroundColor': {'color': {'rgbColor': {'red': 0.12, 'green': 0.23, 'blue': 0.37}}}
        },
        'fields': 'bold,fontSize,foregroundColor'
    }
})

# Execute
if requests:
    docs_service.documents().batchUpdate(
        documentId=DOC_ID,
        body={'requests': requests}
    ).execute()

# Share with Finn
drive_service.permissions().create(
    fileId=DOC_ID,
    body={
        'type': 'user',
        'role': 'writer',
        'emailAddress': 'wfmckie@gmail.com'
    },
    sendNotificationEmail=False
).execute()

print(f"✅ Document built and shared!")
print(f"📄 https://docs.google.com/document/d/{DOC_ID}")
