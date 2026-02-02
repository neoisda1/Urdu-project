#!/usr/bin/env python3
"""
Remove all inline <span dir="ltr"> tags from markdown files.
These are unnecessary when text is already within <div dir="ltr"> blocks.
"""

import re
import os

def remove_inline_spans(content):
    """Remove all inline <span dir="ltr">...</span> tags."""
    # Pattern to match <span dir="ltr">content</span>
    pattern = r'<span dir="ltr">(.*?)</span>'
    
    # Replace with just the content
    cleaned = re.sub(pattern, r'\1', content, flags=re.DOTALL)
    
    return cleaned

def process_file(filepath):
    """Process a single markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        cleaned_content = remove_inline_spans(content)
        
        if cleaned_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"✓ Cleaned: {filepath}")
            return True
        else:
            print(f"  Skipped: {filepath} (no changes needed)")
            return False
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    # Process all basics chapters
    basics_dir = 'basics'
    modified_count = 0
    
    if os.path.exists(basics_dir):
        for filename in sorted(os.listdir(basics_dir)):
            if filename.endswith('.md'):
                filepath = os.path.join(basics_dir, filename)
                if process_file(filepath):
                    modified_count += 1
    
    # Process all stories
    stories_dir = 'کہانیاں'
    if os.path.exists(stories_dir):
        for filename in sorted(os.listdir(stories_dir)):
            if filename.endswith('.md'):
                filepath = os.path.join(stories_dir, filename)
                if process_file(filepath):
                    modified_count += 1
    
    print(f"\n✅ Complete! Modified {modified_count} files.")

if __name__ == '__main__':
    main()
