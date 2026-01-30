#!/usr/bin/env python3
"""Convert Markdown to Google Docs with proper formatting"""
import re
import sys
import subprocess

def strip_markdown(text):
    """Remove markdown syntax, return plain text"""
    # Remove headers but keep text
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove italic  
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Remove code
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Convert lists
    text = re.sub(r'^-\s+', '• ', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    # Remove YAML frontmatter
    text = re.sub(r'^---\s*\n[\s\S]*?\n---\s*\n', '', text)
    # Clean multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def create_doc(title, content, user_email="hectorcb101@gmail.com"):
    """Create Google Doc and return doc ID"""
    result = subprocess.run([
        'mcporter', 'call', 'google-workspace.create_doc',
        f'user_google_email={user_email}',
        f'title={title}',
        f'content={content}'
    ], capture_output=True, text=True)
    
    output = result.stdout + result.stderr
    
    # Extract doc ID from output
    if match := re.search(r'ID:\s+([A-Za-z0-9_-]+)', output):
        return match.group(1)
    elif match := re.search(r'/d/([A-Za-z0-9_-]+)/', output):
        return match.group(1)
    
    print(f"Could not extract doc ID from: {output}")
    return None

def find_headers(markdown_text):
    """Find header positions in markdown"""
    headers = []
    lines = markdown_text.split('\n')
    pos = 0
    
    for line in lines:
        if match := re.match(r'^(#{1,6})\s+(.+)$', line):
            level = len(match.group(1))
            text = match.group(2)
            headers.append({
                'start': pos,
                'length': len(text),
                'level': level,
                'text': text
            })
        pos += len(line) + 1
    
    return headers

def apply_header_formatting(doc_id, headers, plain_text, user_email="hectorcb101@gmail.com"):
    """Apply header formatting to doc"""
    font_sizes = {1: 20, 2: 16, 3: 14, 4: 13}
    
    for header in headers:
        # Find header text in plain version
        text_pos = plain_text.find(header['text'])
        if text_pos == -1:
            continue
            
        size = font_sizes.get(header['level'], 12)
        end_pos = text_pos + header['length']
        
        print(f"Formatting header: '{header['text']}' at {text_pos}-{end_pos} (level {header['level']})")
        
        subprocess.run([
            'mcporter', 'call', 'google-workspace.modify_doc_text',
            f'user_google_email={user_email}',
            f'document_id={doc_id}',
            f'start_index={text_pos}',
            f'end_index={end_pos}',
            f'bold=true',
            f'font_size={size}'
        ], capture_output=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: md_to_gdoc.py <title> <markdown_file>")
        sys.exit(1)
    
    title = sys.argv[1]
    md_file = sys.argv[2]
    
    with open(md_file, 'r') as f:
        markdown = f.read()
    
    # Extract headers before stripping
    headers = find_headers(markdown)
    
    # Convert to plain text
    plain_text = strip_markdown(markdown)
    
    print(f"Creating doc: {title}")
    doc_id = create_doc(title, plain_text)
    
    if not doc_id:
        print("❌ Failed to create doc")
        sys.exit(1)
    
    print(f"✅ Doc created: {doc_id}")
    
    # Apply header formatting
    if headers:
        print(f"Applying {len(headers)} header formats...")
        apply_header_formatting(doc_id, headers, plain_text)
    
    print(f"\n✅ Success! https://docs.google.com/document/d/{doc_id}/edit")
