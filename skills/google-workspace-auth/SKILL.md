---
name: google-workspace-auth
description: Google Workspace OAuth authentication for workspace-mcp. Use when Google services fail with auth errors or when setting up new OAuth credentials.
---

# Google Workspace OAuth Authentication

This skill documents how to complete Google OAuth authentication for the workspace-mcp server.

## The Problem

When running workspace-mcp via mcporter in stdio mode on a remote server (e.g., AWS), the OAuth callback flow fails because:

1. Google redirects to `http://localhost:8000/oauth2callback`
2. This goes to the USER's local machine, not the server
3. The server can't receive the callback

## The Solution: Manual Token Exchange

Instead of relying on the callback server, we can manually:
1. Get the authorization code from the browser URL
2. Exchange it for tokens
3. Save tokens in the correct format

## Credential Storage Location

```
~/.google_workspace_mcp/credentials/{email}.json
```

## Credential File Format

workspace-mcp expects this EXACT format:

```json
{
  "token": "ya29.access_token_here",
  "refresh_token": "1//refresh_token_here",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "your_client_id.apps.googleusercontent.com",
  "client_secret": "GOCSPX-your_secret",
  "scopes": ["https://www.googleapis.com/auth/gmail.send", "..."],
  "expiry": "2026-01-25T20:20:18.692597"
}
```

**IMPORTANT:** The field names matter!
- `token` NOT `access_token`
- `scopes` as an array, NOT a space-separated string
- `expiry` as ISO format datetime string

## Step-by-Step OAuth Flow

### 1. Trigger OAuth Flow
```bash
mcporter call google-workspace.send_gmail_message user_google_email="hectorcb101@gmail.com" to="test@example.com" subject="Test" body="Test"
```
This will fail but generate an authorization URL.

### 2. User Clicks Authorization Link
User authorizes with their Google account. The browser will show "localhost refused to connect" - this is expected.

### 3. Copy the Callback URL
User copies the FULL URL from the browser address bar:
```
http://localhost:8000/oauth2callback?state=...&code=4/0ASc3gC0...
```

### 4. Run Token Exchange Script

```bash
python3 /tmp/complete_oauth.py "AUTHORIZATION_CODE_HERE"
```

Or manually:

```python
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta

# OAuth config
client_id = "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret = "GOCSPX-YOUR_SECRET_HERE"
auth_code = "4/0ASc3gC0..."  # From callback URL
redirect_uri = "http://localhost:8000/oauth2callback"

# Exchange code for tokens
data = urllib.parse.urlencode({
    'code': auth_code,
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': redirect_uri,
    'grant_type': 'authorization_code'
}).encode()

req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
response = json.loads(urllib.request.urlopen(req).read())

# Parse scopes
scopes = response.get('scope', '').split()

# Calculate expiry
expiry = datetime.utcnow() + timedelta(seconds=response.get('expires_in', 3599))

# Create credentials in correct format
creds = {
    "token": response["access_token"],
    "refresh_token": response.get("refresh_token"),
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": client_id,
    "client_secret": client_secret,
    "scopes": scopes,
    "expiry": expiry.isoformat()
}

# Save
creds_file = Path.home() / ".google_workspace_mcp" / "credentials" / "hectorcb101@gmail.com.json"
creds_file.parent.mkdir(parents=True, exist_ok=True)
with open(creds_file, 'w') as f:
    json.dump(creds, f, indent=2)

print(f"Saved credentials to {creds_file}")
```

## Configuration

The OAuth client credentials are stored in:
```
~/clawd/config/mcporter.json
```

Under `mcpServers.google-workspace.env`:
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `USER_GOOGLE_EMAIL` (default email)

## My Account

- **Email:** hectorcb101@gmail.com
- **Associated GitHub:** hectorcb101-lab

## Troubleshooting

### "NoneType is not iterable" Error
The credential file has wrong format. Check field names match the expected format above.

### "Cannot initiate OAuth flow - callback server unavailable"
Port 8000 conflict. Kill any process using it:
```bash
fuser -k 8000/tcp
```

### Credentials Expired
Tokens are automatically refreshed if `refresh_token` is present. If refresh fails, re-run the OAuth flow.

## Related Files

- Credentials: `~/.google_workspace_mcp/credentials/`
- Config: `~/clawd/config/mcporter.json`
- Script: `/tmp/complete_oauth.py`
