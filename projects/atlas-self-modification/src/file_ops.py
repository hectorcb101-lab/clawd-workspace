"""
Safe file operations for Atlas Self-Modification System.

All modifications are:
1. Backed up before applying
2. Logged with full diffs
3. Reversible via rollback
4. Git-committed (if repo available)
"""

import os
import shutil
import subprocess
import difflib
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Backup directory
BACKUP_DIR = Path(__file__).parent.parent / "data" / "backups"

# Files that can NEVER be auto-modified (require human approval always)
PROTECTED_FILES = {
    'SOUL.md',      # Core identity - too sensitive
    'USER.md',      # User info - privacy concerns
}

# Maximum lines for auto-apply (larger changes require approval)
MAX_AUTO_APPLY_LINES = 15


def ensure_backup_dir() -> Path:
    """Ensure backup directory exists."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    return BACKUP_DIR


def create_backup(file_path: str) -> str:
    """
    Create a timestamped backup of a file.
    
    Returns:
        Path to the backup file
    """
    ensure_backup_dir()
    
    source = Path(file_path)
    if not source.exists():
        raise FileNotFoundError(f"Cannot backup non-existent file: {file_path}")
    
    # Create timestamped backup name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source.stem}_{timestamp}{source.suffix}"
    backup_path = BACKUP_DIR / backup_name
    
    # Copy file
    shutil.copy2(str(source), str(backup_path))
    
    return str(backup_path)


def read_file(file_path: str) -> str:
    """Read file contents."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """Write content to file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_diff(before: str, after: str, file_path: str) -> str:
    """Generate a unified diff between two contents."""
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
    )
    
    return ''.join(diff)


def find_section(content: str, section_name: str) -> Optional[Tuple[int, int]]:
    """
    Find a section in markdown content by header.
    
    Returns:
        (start_line, end_line) or None if not found
    """
    lines = content.split('\n')
    start = None
    start_level = None
    
    for i, line in enumerate(lines):
        # Check for markdown headers
        if line.startswith('#'):
            # Count header level
            level = 0
            for char in line:
                if char == '#':
                    level += 1
                else:
                    break
            
            header_text = line[level:].strip()
            
            if start is None:
                # Looking for section start
                if section_name.lower() in header_text.lower():
                    start = i
                    start_level = level
            else:
                # Found section, looking for end
                # End when we hit a header of same or higher level
                if level <= start_level:
                    return (start, i - 1)
    
    if start is not None:
        # Section goes to end of file
        return (start, len(lines) - 1)
    
    return None


def apply_append(content: str, new_content: str, section: Optional[str] = None) -> str:
    """
    Append content to file, optionally within a section.
    """
    if section:
        section_range = find_section(content, section)
        if section_range:
            lines = content.split('\n')
            start, end = section_range
            # Insert before end of section
            lines.insert(end + 1, new_content)
            return '\n'.join(lines)
        else:
            # Section not found - append to end with section header
            return f"{content}\n\n## {section}\n\n{new_content}"
    else:
        # Simple append to end
        return f"{content}\n\n{new_content}"


def apply_edit(content: str, old_text: str, new_text: str) -> str:
    """
    Replace specific text in content.
    """
    if old_text not in content:
        raise ValueError(f"Text to replace not found in file")
    
    return content.replace(old_text, new_text, 1)


def apply_delete(content: str, text_to_delete: str) -> str:
    """
    Delete specific text from content.
    """
    if text_to_delete not in content:
        raise ValueError(f"Text to delete not found in file")
    
    return content.replace(text_to_delete, '', 1)


def is_protected(file_path: str) -> bool:
    """Check if file is protected from auto-modification."""
    filename = Path(file_path).name
    return filename in PROTECTED_FILES


def git_commit(file_path: str, modification_id: str, reason: str) -> Optional[str]:
    """
    Git commit a modified file.
    
    Returns:
        Commit hash or None if not in a git repo
    """
    try:
        # Check if in git repo
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            cwd=Path(file_path).parent
        )
        
        if result.returncode != 0:
            return None
        
        # Stage the file
        subprocess.run(
            ['git', 'add', file_path],
            capture_output=True,
            check=True
        )
        
        # Commit with modification ID in message
        commit_msg = f"[atlas-mod] {modification_id}: {reason}"
        result = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Maybe nothing to commit
            return None
        
        # Get commit hash
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        
        return result.stdout.strip()
        
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        # Git not installed
        return None


def safe_modify(
    file_path: str,
    modification_type: str,
    content: str,
    section: Optional[str] = None,
    old_text: Optional[str] = None,
    modification_id: Optional[str] = None,
    reason: Optional[str] = None,
) -> Tuple[str, str, str, Optional[str]]:
    """
    Safely modify a file with backup.
    
    Args:
        file_path: Path to file to modify
        modification_type: append, edit, delete
        content: New content (for append/edit) or text to delete
        section: Optional section name for append
        old_text: Text to replace (for edit)
        modification_id: ID for git commit message
        reason: Reason for git commit message
    
    Returns:
        (before_content, after_content, diff, git_commit_hash)
    """
    # Read original content
    before_content = read_file(file_path)
    
    # Create backup
    backup_path = create_backup(file_path)
    
    try:
        # Apply modification
        if modification_type == 'append':
            after_content = apply_append(before_content, content, section)
        elif modification_type == 'edit':
            if old_text is None:
                raise ValueError("old_text required for edit operation")
            after_content = apply_edit(before_content, old_text, content)
        elif modification_type == 'delete':
            after_content = apply_delete(before_content, content)
        else:
            raise ValueError(f"Unknown modification type: {modification_type}")
        
        # Generate diff
        diff = generate_diff(before_content, after_content, file_path)
        
        # Write modified content
        write_file(file_path, after_content)
        
        # Git commit if possible
        git_hash = None
        if modification_id and reason:
            git_hash = git_commit(file_path, modification_id, reason)
        
        return before_content, after_content, diff, git_hash
        
    except Exception as e:
        # Restore from backup on any error
        shutil.copy2(backup_path, file_path)
        raise


def restore_from_backup(file_path: str, backup_path: str) -> str:
    """
    Restore a file from backup.
    
    Returns:
        The restored content
    """
    shutil.copy2(backup_path, file_path)
    return read_file(file_path)


def restore_from_content(file_path: str, content: str, modification_id: str, reason: str) -> Optional[str]:
    """
    Restore a file to specific content.
    
    Returns:
        Git commit hash or None
    """
    # Backup current state first
    create_backup(file_path)
    
    # Write the restored content
    write_file(file_path, content)
    
    # Git commit
    return git_commit(file_path, modification_id, f"ROLLBACK: {reason}")
