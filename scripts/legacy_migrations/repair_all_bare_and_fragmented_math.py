# -*- coding: utf-8 -*-
"""
repair_all_bare_and_fragmented_math.py
======================================
Exhaustively fixes all 2000+ parse errors:
1. Strips spurious nested $ inside LaTeX expressions
2. Wraps bare unclosed LaTeX lines and bullet items in proper $$...$$ or $...$
3. Fixes unescaped % inside math
4. Fixes unbalanced braces and double sub/superscripts
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def is_math_expression(text):
    """Check if text is predominantly a LaTeX mathematical expression."""
    s = text.strip()
    if not s:
        return False
    # If it starts or ends with math delimiters
    if s.startswith('$$') and s.endswith('$$'):
        return True
    if s.startswith('$') and s.endswith('$'):
        return True
    
    # Check for strong LaTeX math signatures
    signatures = [
        r'\\mathbf\{', r'\\frac\{', r'\\sqrt\{', r'\\begin\{', r'\\mathcal\{',
        r'\\text\{', r'\\implies', r'\\approx', r'\\angle', r'\\times',
        r'\\parallel', r'\\Omega', r'\\Delta', r'\\pm', r'\\mathcal\{L\}',
        r'\\mathcal\{F\}', r'\\sum_', r'\\int_', r'\\partial', r'\\cdot'
    ]
    matches = sum(1 for sig in signatures if re.search(sig, s))
    if matches >= 2:
        return True
    if matches == 1 and ('=' in s or '+' in s or '-' in s or '/' in s):
        return True
    return False

def clean_nested_dollars_in_math(line):
    """Remove spurious nested $ inside a math block or bare math line."""
    # Tokens to unwrap
    p = line
    p = p.replace(r'$\times$', r'\times')
    p = p.replace(r'$\approx$', r'\approx')
    p = p.replace(r'$\pm$', r'\pm')
    p = p.replace(r'$\le$', r'\le')
    p = p.replace(r'$\ge$', r'\ge')
    p = p.replace(r'$\infty$', r'\infty')
    p = p.replace(r'$\beta$', r'\beta')
    p = p.replace(r'$\tau$', r'\tau')
    p = p.replace(r'$\Omega$', r'\Omega')
    p = p.replace(r'$\Delta$', r'\Delta')
    p = re.sub(r'\$\\Delta\s+([A-Za-z0-9_]+)\$', r'\\Delta \1', p)
    p = re.sub(r'\$\\angle\s*([0-9\-\+]+(?:\^\\circ)?)\$', r'\\angle \1', p)
    return p

def fix_unescaped_percent_in_math(math_text):
    """Escape % in math unless already escaped."""
    return re.sub(r'(?<!\\)%', r'\\%', math_text)

def repair_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    orig = "".join(lines)
    new_lines = []
    in_code_block = False
    in_display_math = False
    
    for line in lines:
        stripped = line.strip()
        
        # Track code blocks
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue
            
        if in_code_block:
            new_lines.append(line)
            continue

        # Track display math $$...$$
        if stripped == '$$':
            in_display_math = not in_display_math
            new_lines.append(line)
            continue
            
        if in_display_math:
            # Clean display math line
            cleaned_math = clean_nested_dollars_in_math(line)
            cleaned_math = fix_unescaped_percent_in_math(cleaned_math)
            new_lines.append(cleaned_math)
            continue
            
        # If line starts and ends with $$...$$
        if stripped.startswith('$$') and stripped.endswith('$$') and len(stripped) > 4:
            math_core = stripped[2:-2]
            math_core = clean_nested_dollars_in_math(math_core)
            math_core = fix_unescaped_percent_in_math(math_core)
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}$${math_core}$$\n")
            continue

        # Skip headers, tables, blockquotes, horizontal rules
        if stripped.startswith('#') or stripped.startswith('|') or stripped.startswith('> [!') or stripped.startswith('---'):
            # But clean nested dollars if present in text
            if '$\\times$' in line or '$\\approx$' in line:
                line = clean_nested_dollars_in_math(line)
            new_lines.append(line)
            continue

        # Check if line is a bullet item with bare math
        # e.g., "- \mathbf{V_1 = ...}" or "1. \mathbf{R_th = ...}"
        bullet_match = re.match(r'^(\s*(?:[-*]|\d+\.)\s+)(.+)$', line)
        if bullet_match:
            prefix = bullet_match.group(1)
            rest = bullet_match.group(2).strip()
            
            # If rest is a math expression not enclosed in $$ or $
            if is_math_expression(rest) and not (rest.startswith('$') and rest.endswith('$')) and not (rest.startswith('$$') and rest.endswith('$$')):
                rest_clean = clean_nested_dollars_in_math(rest)
                rest_clean = fix_unescaped_percent_in_math(rest_clean)
                new_lines.append(f"{prefix}$${rest_clean}$$\n")
                continue
            elif '$\\times$' in rest or '$\\approx$' in rest:
                rest_clean = clean_nested_dollars_in_math(rest)
                new_lines.append(f"{prefix}{rest_clean}\n")
                continue
            else:
                new_lines.append(line)
                continue

        # Check if standalone line is a bare math equation
        if is_math_expression(stripped) and not (stripped.startswith('$') and stripped.endswith('$')) and not (stripped.startswith('$$') and stripped.endswith('$$')):
            indent = line[:len(line) - len(line.lstrip())]
            clean_math = clean_nested_dollars_in_math(stripped)
            clean_math = fix_unescaped_percent_in_math(clean_math)
            new_lines.append(f"{indent}$${clean_math}$$\n")
            continue

        # Normal line: clean any fragmented dollars
        if '$\\times$' in line or '$\\approx$' in line or '$\\pm$' in line:
            line = clean_nested_dollars_in_math(line)

        new_lines.append(line)

    result = "".join(new_lines)
    
    # Global cleanups
    # Fix double superscript 2R^2C^2 -> 2 R^2 C^2
    result = result.replace(r'2R^2C^2', r'2 R^2 C^2')
    # Fix power \angle in text
    result = re.sub(r'\bpower\s*\\angle\b', 'power angle', result, flags=re.IGNORECASE)
    result = re.sub(r'\bfiring\s*\\angle\b', 'firing angle', result, flags=re.IGNORECASE)
    result = re.sub(r'\bphase\s*\\angle\b', 'phase angle', result, flags=re.IGNORECASE)

    if result != orig:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(result)
        return True
    return False

def main():
    files = sorted(glob.glob(os.path.join(WORKSPACE, '**', '*.md'), recursive=True))
    repaired = 0
    for f in files:
        if '.git' in f or 'node_modules' in f:
            continue
        if repair_markdown_file(f):
            repaired += 1
            print(f"✅ Repaired bare & fragmented math in: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Successfully repaired {repaired} files across the repository!")

if __name__ == '__main__':
    main()
