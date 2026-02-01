#!/usr/bin/env python3
"""
Convert Markdown to PDF

Auto-evolved capability - implemented by Atlas.
"""

import subprocess
import sys
from pathlib import Path


def convert(input_path: str, output_path: str = None) -> str:
    """Convert markdown file to PDF using pandoc."""
    input_file = Path(input_path)
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if output_path is None:
        output_path = str(input_file.with_suffix('.pdf'))
    
    # Use pandoc for conversion (common tool, likely installed)
    try:
        subprocess.run([
            'pandoc', str(input_file),
            '-o', output_path,
            '--pdf-engine=wkhtmltopdf'
        ], check=True, capture_output=True)
        return output_path
    except FileNotFoundError:
        # Fallback: try with basic pandoc
        try:
            subprocess.run([
                'pandoc', str(input_file),
                '-o', output_path
            ], check=True, capture_output=True)
            return output_path
        except FileNotFoundError:
            raise RuntimeError("pandoc not installed. Run: sudo apt install pandoc")


def main():
    if len(sys.argv) < 2:
        print("Usage: convert_markdown_to_pdf.py <input.md> [output.pdf]")
        return
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = convert(input_path, output_path)
    print(f"✅ Created: {result}")


def test():
    """Test the conversion."""
    print("Testing convert_markdown_to_pdf...")
    # Check if pandoc exists
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
        print("✅ pandoc available")
        return True
    except FileNotFoundError:
        print("⚠️ pandoc not installed")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        main()
