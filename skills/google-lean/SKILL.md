---
name: google-lean
description: Lean Google Workspace tools - Gmail, Calendar, Drive, Docs, Sheets. Only 15 tools vs 92 in MCP.
---

# Google Lean

Minimal Google Workspace integration. 15 tools that cover 95% of usage.

## CLI: `~/clawd/scripts/google`

## Gmail

```bash
# Search emails
google gmail-search "from:wfmckie@gmail.com is:unread"

# Read a message
google gmail-read <message_id>

# Read multiple messages
google gmail-read-batch "id1,id2,id3"

# Modify labels
google gmail-labels <message_id> --add STARRED --remove UNREAD

# Send email (use atlas_email.py for proper From name)
google gmail-send "to@email.com" "Subject" "Body text"
```

## Calendar

```bash
# List calendars
google cal-list

# Get events (next N days)
google cal-events --days 7

# Create event
google cal-create "Meeting" "2026-01-30T10:00:00" "2026-01-30T11:00:00"
```

## Drive

```bash
# Search files
google drive-search "document name"

# Upload file
google drive-upload /path/to/file.pdf --folder FOLDER_ID --name "New Name.pdf"

# Download file
google drive-download FILE_ID /local/path.pdf

# Share file
google drive-share FILE_ID "email@example.com" --role writer
```

## Docs

```bash
# Create document
google doc-create "Title" --content "Initial content"

# Read document
google doc-read DOCUMENT_ID
```

## Sheets

```bash
# Read range
google sheet-read SHEET_ID "Sheet1!A1:C10"

# Write values (JSON array)
google sheet-write SHEET_ID "Sheet1!A1" '[["a","b"],["c","d"]]'
```

## Notes

- Uses credentials from `~/.google_workspace_mcp/credentials/`
- Default account: hectorcb101@gmail.com
- For emails with proper "Atlas" sender name, use `atlas_email.py` instead
- Output is always JSON

## Comparison

| Feature | google-lean | google-workspace MCP |
|---------|-------------|---------------------|
| Tools | 15 | 92 |
| Context overhead | Minimal | Heavy |
| Speed | Direct API | MCP protocol |
| Dependencies | Python only | uvx + MCP server |
