# -*- coding: utf-8 -*-
"""
pristine_math_and_table_repair.py
=================================
Repairs all corrupted LaTeX escape characters, broken table splits,
and malformed math across all markdown files in the repository.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def clean_file_content(content):
    # 1. Clean control characters and replace with correct LaTeX
    # Form-feed \x0c
    content = content.replace('\x0crac', r'\frac')
    content = content.replace('\x0c', '')
    
    # Bell \x07
    content = content.replace('\x07pprox', r'\approx')
    content = content.replace('\x07lpha', r'\alpha')
    content = content.replace('\x07', '')
    
    # Backspace \x08
    content = content.replace('\x08eta', r'\beta')
    content = content.replace('\x08f', r'\mathbf')
    content = content.replace('\x08', '')
    
    # Vertical Tab \x0b
    content = content.replace('\x0bec', r'\vec')
    content = content.replace('\x0b', '')
    
    # Tab \t corruptions in math
    content = content.replace('\tan\t', r'\tan ')
    content = content.replace('\t\tan', r'\tan')
    content = content.replace('\tan', r'\tan')  # normalize
    content = content.replace('\t\theta', r'\theta')
    content = content.replace('\t\tau', r'\tau')
    content = content.replace('\t\times', r'\times')
    content = content.replace('\t\text', r'\text')

    # Specific corrupted sequences where \t + word occurred
    content = re.sub(r'[\t]an(\b|[\s0-9\(\\_])', r'\\tan\1', content)
    content = re.sub(r'[\t]heta(\b|[\s0-9\(\\_])', r'\\theta\1', content)
    content = re.sub(r'[\t]au(\b|[\s0-9\(\\_])', r'\\tau\1', content)
    content = re.sub(r'[\t]imes(\b|[\s0-9\(\\_])', r'\\times\1', content)
    content = re.sub(r'[\t]ext\{', r'\\text{', content)
    content = re.sub(r'[\t]riangle(\b|[\s0-9\(\\_])', r'\\triangle\1', content)
    content = re.sub(r'[\t]ilde(\b|[\s0-9\(\\_])', r'\\tilde\1', content)
    
    # Replace broken string artifacts where leading backslash was eaten
    content = re.sub(r'(?<!\\)rac\{', r'\\frac{', content)
    content = re.sub(r'(?<!\\)pprox\b', r'\\approx', content)
    content = re.sub(r'(?<!\\)\blpha\b', r'\\alpha', content)

    # Clean double/triple backslashes if accidentally created
    content = content.replace(r'\\\frac', r'\frac')
    content = content.replace(r'\\\approx', r'\approx')
    content = content.replace(r'\\\alpha', r'\alpha')
    content = content.replace(r'\\\times', r'\times')
    content = content.replace(r'\\\text', r'\text')
    content = content.replace(r'\\\tan', r'\tan')
    content = content.replace(r'\\\theta', r'\theta')

    # 2. Fix broken Markdown tables split by WARNING blocks
    # e.g., "| :--- | :---: | :---: | :---\n\n> [!WARNING]...\n\n---\n: |\n| **row..."
    table_broken_pattern = re.compile(
        r'(\|(?:\s*:[-\s]+:?\s*\|)+\s*)\n+(\s*>\s*\[!WARNING\][\s\S]*?>\s*3\.[^\n]+\n+---\n+:?\s*\|)\n+(\|\s*\*\*[^\n]+)',
        re.MULTILINE
    )
    
    # Let's fix this specifically if found
    if ': |' in content and '> [!WARNING]' in content:
        # Extract the warning block
        warn_match = re.search(r'(>\s*\[!WARNING\][\s\S]*?>\s*3\.[^\n]+)', content)
        if warn_match:
            warn_text = warn_match.group(1).strip()
            # Remove the broken injection and the stray ': |' or '---'
            # First remove the warning block from its broken position
            content = re.sub(r'\n+>\s*\[!WARNING\][\s\S]*?>\s*3\.[^\n]+\n+---\n+:?\s*\|', '', content)
            # Ensure the table header is complete
            # If the table header row was broken (e.g. ends with ':---' without '|'), close it
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.strip().startswith('| :---') and not line.strip().endswith('|'):
                    line = line.strip() + ' :---|'
                new_lines.append(line)
            content = '\n'.join(new_lines)
            
            # Now append the warning cleanly before the final footer/conclusion or at the very end
            if warn_text not in content:
                content = content.rstrip() + '\n\n---\n\n' + warn_text + '\n'

    return content

def main():
    files = sorted(glob.glob(os.path.join(WORKSPACE, '**', '*.md'), recursive=True))
    repaired_count = 0
    
    for f in files:
        if '.git' in f or 'node_modules' in f:
            continue
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            orig = fp.read()
        
        cleaned = clean_file_content(orig)
        if cleaned != orig:
            with open(f, 'w', encoding='utf-8') as fp:
                fp.write(cleaned)
            repaired_count += 1
            print(f"✅ Repaired: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Total repaired markdown files: {repaired_count}")

if __name__ == '__main__':
    main()
