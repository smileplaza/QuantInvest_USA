#!/usr/bin/env python3
"""
Fix yfinance.download() calls in Jupyter notebooks
to use multi_level_index=False, auto_adjust=False
"""

import json
import re
from pathlib import Path

def fix_yfinance_in_notebook(notebook_path):
    """Fix yfinance.download() calls in a notebook"""

    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    changes_made = 0

    for cell in notebook.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue

        source = cell.get('source', [])
        if isinstance(source, list):
            source = ''.join(source)

        # Check if cell contains yfinance.download or yf.download
        if 'yfinance.download' not in source and 'yf.download' not in source:
            continue

        # Pattern 1: yf.download(...) without options
        pattern1 = r'yf\.download\(([^)]+)\)(?!\s*,)'
        if re.search(pattern1, source):
            # Only add options if they don't exist
            if 'multi_level_index' not in source and 'auto_adjust' not in source:
                source = re.sub(
                    r'yf\.download\(([^)]+)\)(?!\s*,)',
                    r'yf.download(\1, multi_level_index=False, auto_adjust=False)',
                    source
                )
                changes_made += 1

        # Pattern 2: yfinance.download(...) without options
        pattern2 = r'yfinance\.download\(([^)]+)\)(?!\s*,)'
        if re.search(pattern2, source):
            if 'multi_level_index' not in source and 'auto_adjust' not in source:
                source = re.sub(
                    r'yfinance\.download\(([^)]+)\)(?!\s*,)',
                    r'yfinance.download(\1, multi_level_index=False, auto_adjust=False)',
                    source
                )
                changes_made += 1

        # Update cell source
        if isinstance(cell.get('source'), list):
            cell['source'] = source.split('\n')
            # Preserve newlines properly
            cell['source'] = [line + '\n' if i < len(cell['source']) - 1 else line
                            for i, line in enumerate(cell['source'])]
        else:
            cell['source'] = source

    if changes_made > 0:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, ensure_ascii=False, indent=1)
        return changes_made

    return 0


def main():
    """Process all notebooks"""
    notebook_dir = Path('samples')
    notebooks = list(notebook_dir.glob('**/*.ipynb'))

    total_changes = 0

    for notebook_path in sorted(notebooks):
        try:
            changes = fix_yfinance_in_notebook(notebook_path)
            if changes > 0:
                print(f"[OK] {notebook_path}: {changes} yfinance call(s) fixed")
                total_changes += changes
            else:
                print(f"[--] {notebook_path}: Already fixed or no yfinance calls")
        except Exception as e:
            print(f"[ERROR] {notebook_path}: Error - {e}")

    print(f"\n[TOTAL] Total fixes applied: {total_changes}")


if __name__ == '__main__':
    main()
