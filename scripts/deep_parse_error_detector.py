# -*- coding: utf-8 -*-
"""
deep_parse_error_detector.py
============================
Exhaustive KaTeX and Math Parser Audit Engine.
Audits all markdown files for valid KaTeX grammar, unclosed brackets, unbalanced environments, and leaked macros.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class KaTeXSyntaxAuditor:
    SUPPORTED_ENVS = {'aligned', 'matrix', 'bmatrix', 'pmatrix', 'vmatrix', 'Vmatrix', 'cases', 'array', 'gathered', 'split'}

    def __init__(self):
        self.issues = []

    def audit_math_block(self, math_text, is_display, file_path, line_no):
        raw = math_text.strip()
        if not raw:
            return

        # Rule 1: Braces balance check (ignoring escaped \{ and \})
        clean_braces = re.sub(r'\\[\{\}]', '', raw)
        open_c = clean_braces.count('{')
        close_c = clean_braces.count('}')
        if open_c != close_c:
            self.issues.append({
                'file': file_path,
                'line': line_no,
                'type': 'Unbalanced braces',
                'detail': f"Found {open_c} '{{' vs {close_c} '}}'",
                'snippet': raw[:100]
            })

        # Rule 2: Unescaped % inside math (causes comment truncation & missing arguments in KaTeX)
        unescaped_pct = re.findall(r'(?<!\\)%', raw)
        if unescaped_pct:
            self.issues.append({
                'file': file_path,
                'line': line_no,
                'type': 'Unescaped % in math',
                'detail': f"{len(unescaped_pct)} unescaped '%' found",
                'snippet': raw[:100]
            })

        # Rule 3: Double subscripts (e.g., x_1_2 or a_b_c without braces)
        double_sub = re.findall(r'(?<!\\)_[0-9A-Za-z]+_[0-9A-Za-z]+', raw)
        if double_sub:
            self.issues.append({
                'file': file_path,
                'line': line_no,
                'type': 'Double subscript',
                'detail': f"Found: {double_sub}",
                'snippet': raw[:100]
            })

        # Rule 4: Double superscripts (e.g., x^2^3 or a^b^c without braces)
        double_sup = re.findall(r'(?<!\\)\^[0-9A-Za-z]+\^[0-9A-Za-z]+', raw)
        if double_sup:
            self.issues.append({
                'file': file_path,
                'line': line_no,
                'type': 'Double superscript',
                'detail': f"Found: {double_sup}",
                'snippet': raw[:100]
            })

        # Rule 5: \begin and \end balance
        begins = re.findall(r'\\begin\{([^\}]+)\}', raw)
        ends = re.findall(r'\\end\{([^\}]+)\}', raw)
        if begins != ends:
            self.issues.append({
                'file': file_path,
                'line': line_no,
                'type': 'Mismatched \\begin and \\end',
                'detail': f"Begins: {begins}, Ends: {ends}",
                'snippet': raw[:100]
            })

        # Rule 6: Unescaped & outside matrix/aligned environments
        if '&' in raw and not any(env in raw for env in self.SUPPORTED_ENVS):
            self.issues.append({
                'file': file_path,
                'line': line_no,
                'type': 'Unescaped & outside matrix/aligned',
                'detail': f"Found '&' without aligned/matrix environment",
                'snippet': raw[:100]
            })

        # Rule 7: Corrupted or unsupported macros
        bad_macros = [
            (r'\\phase\b', r'\phase (KaTeX does not support \phase, use \angle)'),
            (r'\\phasor\b', r'\phasor (KaTeX does not support \phasor)'),
            (r'\\boldmath\b', r'\boldmath (KaTeX does not support \boldmath, use \mathbf)'),
            (r'\\mbox\b', r'\mbox (use \text)'),
            (r'\\sfrac\b', r'\sfrac (use \frac)'),
            (r'\\unit\b', r'\unit (use \text)'),
            (r'\\rac\b', r'\rac (corrupted \frac)'),
            (r'\\pprox\b', r'\pprox (corrupted \approx)'),
            (r'\\lpha\b', r'\lpha (corrupted \alpha)'),
            (r'\\heta\b', r'\heta (corrupted \theta)'),
            (r'\\f\\frac', r'\f\frac (duplicate prefix)'),
            (r'\\a\\approx', r'\a\approx (duplicate prefix)'),
            (r'\\a\\alpha', r'\a\alpha (duplicate prefix)'),
            (r'\\b\\beta', r'\b\beta (duplicate prefix)'),
        ]
        for pat, desc in bad_macros:
            if re.search(pat, raw):
                self.issues.append({
                    'file': file_path,
                    'line': line_no,
                    'type': 'Unsupported/Corrupted Macro',
                    'detail': desc,
                    'snippet': raw[:100]
                })

    def audit_file(self, file_path):
        rel_path = os.path.relpath(file_path, WORKSPACE)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        content = "".join(lines)
        
        # Remove code blocks
        no_code = re.sub(r'```[\s\S]*?```', '', content)
        
        # Display math $$...$$
        display_math_blocks = []
        for m in re.finditer(r'\$\$([\s\S]*?)\$\$', no_code):
            display_math_blocks.append((m.group(1), m.start()))

        # Non-display text with display math removed (use letters, no underscores to avoid double subscript false positives)
        no_display = re.sub(r'\$\$[\s\S]*?\$\$', ' DISPLAYMATHMARKER ', no_code)

        # Inline math $...$
        inline_math_blocks = []
        for m in re.finditer(r'(?<!\\)\$([^\$\n]+?)(?<!\\)\$', no_display):
            inline_math_blocks.append((m.group(1), m.start()))

        # Non-math text
        pure_text = re.sub(r'(?<!\\)\$([^\$\n]+?)(?<!\\)\$', ' INLINEMATHMARKER ', no_display)

        # Audit display math blocks
        for block, pos in display_math_blocks:
            line_no = content[:pos].count('\n') + 1
            self.audit_math_block(block, True, rel_path, line_no)

        # Audit inline math blocks
        for block, pos in inline_math_blocks:
            line_no = content[:pos].count('\n') + 1
            self.audit_math_block(block, False, rel_path, line_no)

        # Audit pure text for leaked LaTeX macros (ignoring common words and markdown links)
        # We only flag macros when they clearly represent mathematical symbols in text that should be in $...$
        leaked_macros = re.findall(r'(?<![A-Za-z0-9\$\\])\\(?:Omega|tau|frac|sqrt|angle|approx)\b', pure_text)
        if leaked_macros:
            self.issues.append({
                'file': rel_path,
                'line': 1,
                'type': 'Leaked LaTeX macros outside math mode',
                'detail': f"{len(leaked_macros)} leaked macros: {set(leaked_macros)}",
                'snippet': f"Found outside math: {leaked_macros[:5]}"
            })


def main():
    auditor = KaTeXSyntaxAuditor()
    files = sorted(glob.glob(os.path.join(WORKSPACE, '**', '*.md'), recursive=True))
    
    print(f"🔬 Auditing {len(files)} markdown files for all possible KaTeX Parse Errors...")
    
    for f in files:
        if '.git' in f or 'node_modules' in f:
            continue
        auditor.audit_file(f)
        
    print(f"\n=======================================================")
    print(f"📊 Parse Error Audit Result: {len(auditor.issues)} total issues found across the repository.")
    print(f"=======================================================\n")
    
    by_type = {}
    for iss in auditor.issues:
        t = iss['type']
        by_type[t] = by_type.get(t, 0) + 1
        
    for t, count in by_type.items():
        print(f"  📌 {t}: {count} occurrences")
        
    if auditor.issues:
        print("\nDetailed list of issues:")
        for iss in auditor.issues[:50]:
            print(f"  ❌ [{iss['file']}:L{iss['line']}] {iss['type']} - {iss['detail']}")
            print(f"     Snippet: {iss['snippet']}")

if __name__ == '__main__':
    main()
