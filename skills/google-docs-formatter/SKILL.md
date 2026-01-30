---
name: google-docs-formatter
description: Convert markdown content to properly formatted Google Docs with headers, bold, italic, and proper styling. Use when Finn requests documents - he wants Google Docs format, NOT raw markdown.
---

# Google Docs Formatter

Convert markdown to properly formatted Google Docs. **Finn does not want raw markdown syntax (##, **bold**, etc.) in Google Docs.**

## Critical Rule

**NEVER send markdown files to Finn. Always convert to properly formatted Google Docs.**

## Tools Available

```bash
# Create a folder in Google Drive
mcporter call google-workspace.create_drive_file \
  user_google_email="hectorcb101@gmail.com" \
  file_name="Folder Name" \
  mime_type="application/vnd.google-apps.folder"

# Create a Google Doc with plain text
mcporter call google-workspace.create_doc \
  user_google_email="hectorcb101@gmail.com" \
  title="Document Title" \
  content="Plain text content here"

# Apply formatting to specific ranges
mcporter call google-workspace.modify_doc_text \
  user_google_email="hectorcb101@gmail.com" \
  document_id="<doc_id>" \
  start_index=0 \
  end_index=10 \
  bold=true \
  font_size=20
```

## Conversion Strategy

### 1. Parse Markdown Structure

Identify:
- Headers (# ## ###)
- Bold (**text**)
- Italic (*text*)
- Code blocks (```)
- Lists (- or 1.)
- Links ([text](url))

### 2. Strip Markdown Syntax

Convert markdown to plain text:
- `# Heading` → `Heading`
- `**bold**` → `bold`
- `*italic*` → `italic`
- Remove all markdown syntax characters

### 3. Create Doc with Plain Text

```bash
mcporter call google-workspace.create_doc \
  user_google_email="hectorcb101@gmail.com" \
  title="Document Title" \
  content="<stripped_plain_text>"
```

Capture the document ID from response.

### 4. Apply Formatting

Build formatting operations:

**Headers:**
```bash
# H1: Font size 20pt, bold
mcporter call google-workspace.modify_doc_text \
  user_google_email="hectorcb101@gmail.com" \
  document_id="<doc_id>" \
  start_index=<start> \
  end_index=<end> \
  bold=true \
  font_size=20

# H2: Font size 16pt, bold  
font_size=16

# H3: Font size 14pt, bold
font_size=14
```

**Bold text:**
```bash
mcporter call google-workspace.modify_doc_text \
  user_google_email="hectorcb101@gmail.com" \
  document_id="<doc_id>" \
  start_index=<start> \
  end_index=<end> \
  bold=true
```

**Italic text:**
```bash
mcporter call google-workspace.modify_doc_text \
  ... \
  italic=true
```

**Code formatting:**
```bash
mcporter call google-workspace.modify_doc_text \
  ... \
  font_family="Courier New"
```

## Markdown to Google Docs Mapping

| Markdown | Google Docs Formatting |
|----------|------------------------|
| `# H1` | Font size 20pt, bold |
| `## H2` | Font size 16pt, bold |
| `### H3` | Font size 14pt, bold |
| `**bold**` | bold=true |
| `*italic*` | italic=true |
| `` `code` `` | font_family="Courier New" |
| Lists | Use bullet/number symbols |
| Links | Create hyperlink (if supported) |

## Index Calculation

Google Docs uses character indices (0-based):

```
Text: "Hello World\nThis is bold"
       ^^^^^          ^^^^ ^^ ^^^^
       0-5            12-16 20-24
```

Track positions carefully:
1. Build plain text string
2. Note start/end indices for each formatted section
3. Apply formatting in order

## Workflow Example

### Input (Markdown)
```markdown
# Learning Profile

**Name:** Finn
**Age:** 24

## Cognitive Strengths

- Pattern recognition
- Strategic thinking
```

### Step 1: Strip to Plain Text
```
Learning Profile

Name: Finn
Age: 24

Cognitive Strengths

• Pattern recognition
• Strategic thinking
```

### Step 2: Create Doc
```bash
mcporter call google-workspace.create_doc \
  user_google_email="hectorcb101@gmail.com" \
  title="Learning Profile" \
  content="Learning Profile\n\nName: Finn\nAge: 24\n\nCognitive Strengths\n\n• Pattern recognition\n• Strategic thinking"
```

Returns: `document_id: abc123`

### Step 3: Apply Formatting

**"Learning Profile" (H1):**
- Indices: 0-16
- Format: bold=true, font_size=20

**"Name:" (bold):**
- Indices: 18-22
- Format: bold=true

**"Age:" (bold):**
- Indices: 30-33
- Format: bold=true

**"Cognitive Strengths" (H2):**
- Indices: 38-56
- Format: bold=true, font_size=16

## Python Helper Script

```python
#!/usr/bin/env python3
import re
import subprocess
import json

def strip_markdown(text):
    """Remove markdown syntax, return plain text"""
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove italic
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Remove code
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Convert lists
    text = re.sub(r'^-\s+', '• ', text, flags=re.MULTILINE)
    return text

def find_headers(markdown_text):
    """Find header positions in original markdown"""
    headers = []
    lines = markdown_text.split('\n')
    pos = 0
    
    for line in lines:
        if match := re.match(r'^(#{1,6})\s+(.+)$', line):
            level = len(match.group(1))
            text = match.group(2)
            headers.append({
                'start': pos,
                'end': pos + len(text),
                'level': level,
                'text': text
            })
        pos += len(line) + 1  # +1 for newline
    
    return headers

def find_bold(markdown_text):
    """Find bold text positions"""
    bold_ranges = []
    for match in re.finditer(r'\*\*(.*?)\*\*', markdown_text):
        bold_ranges.append({
            'start': match.start(),
            'end': match.end(),
            'text': match.group(1)
        })
    return bold_ranges

def create_formatted_doc(title, markdown_content, user_email="hectorcb101@gmail.com"):
    """Create Google Doc with proper formatting"""
    
    # Strip markdown
    plain_text = strip_markdown(markdown_content)
    
    # Create doc
    result = subprocess.run([
        'mcporter', 'call', 'google-workspace.create_doc',
        f'user_google_email={user_email}',
        f'title={title}',
        f'content={plain_text}'
    ], capture_output=True, text=True)
    
    # Extract doc ID
    doc_id = extract_doc_id(result.stdout)
    
    # Find formatting sections
    headers = find_headers(markdown_content)
    bold_sections = find_bold(markdown_content)
    
    # Apply formatting
    for header in headers:
        font_size = {1: 20, 2: 16, 3: 14}.get(header['level'], 12)
        apply_formatting(user_email, doc_id, header['start'], header['end'], 
                        bold=True, font_size=font_size)
    
    for bold in bold_sections:
        apply_formatting(user_email, doc_id, bold['start'], bold['end'], bold=True)
    
    return doc_id

def apply_formatting(user_email, doc_id, start, end, **kwargs):
    """Apply formatting to doc range"""
    cmd = [
        'mcporter', 'call', 'google-workspace.modify_doc_text',
        f'user_google_email={user_email}',
        f'document_id={doc_id}',
        f'start_index={start}',
        f'end_index={end}'
    ]
    
    for key, value in kwargs.items():
        if isinstance(value, bool):
            cmd.append(f'{key}={str(value).lower()}')
        else:
            cmd.append(f'{key}={value}')
    
    subprocess.run(cmd)

# Usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: format_doc.py <title> <markdown_file>")
        sys.exit(1)
    
    title = sys.argv[1]
    with open(sys.argv[2]) as f:
        markdown = f.read()
    
    doc_id = create_formatted_doc(title, markdown)
    print(f"Created doc: {doc_id}")
```

Save as: `scripts/format_doc.py`

## Organizing Files in Drive

### Create Folder

```bash
mcporter call google-workspace.create_drive_file \
  user_google_email="hectorcb101@gmail.com" \
  file_name="Meta-Learning System - 2026-01-26" \
  mime_type="application/vnd.google-apps.folder"
```

Returns folder ID.

### Move Doc to Folder

After creating a doc, move it:

```bash
# Note: Use Drive API move operation
# (Check if workspace-mcp supports this)
```

Or create doc in folder directly by specifying folder_id in create operations.

## Best Practices

1. **Always ask Finn's preference** if unsure about formatting
2. **Name folders descriptively** with dates: "Project Name - YYYY-MM-DD"
3. **Test with small doc first** before converting large files
4. **Preserve document structure** (don't lose hierarchy)
5. **Use consistent formatting** (same header sizes, etc.)

## Common Mistakes to Avoid

❌ Sending raw markdown files to Finn  
❌ Using ## syntax in Google Docs  
❌ Forgetting to organize docs in folders  
❌ Not applying proper header formatting  
❌ Losing content during markdown stripping  

✅ Convert markdown to formatted Google Docs  
✅ Create organized folders  
✅ Apply proper styling (bold headers, etc.)  
✅ Test before sending to Finn  

## When to Use

- Finn requests documents
- Sending any documentation/reports
- Delivering structured content
- Any time markdown files would be sent

**Remember: Finn wants Google Docs, not markdown files!**
