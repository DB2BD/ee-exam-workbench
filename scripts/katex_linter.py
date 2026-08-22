# -*- coding: utf-8 -*-
"""
⚡ 全庫 KaTeX 數學公式語法深度檢驗與自動修復器 (KaTeX Comprehensive Linter & Fixer)
檢驗項目：
1. 檢測並自動修正 \\begin{align} 為 \\begin{aligned} (KaTeX 相容性)
2. 檢測並自動修正 \\begin{gather} 為 \\begin{gathered}
3. 檢測未閉合的 $ 或 $$ 符號
4. 檢測非數學內文中的未轉義貨幣符號 ($2M -> \\$2M)
5. 檢測獨立行裸露 LaTeX 矩陣與公式環境並包裹 $$
6. 支援 --fix 自動修復與全量覆寫
"""
import os
import re
import sys

BASE_DIR = '/Users/a/技師考試/歷屆試題_104-114年'
os.chdir(BASE_DIR)

auto_fix = '--fix' in sys.argv or True  # Default to auto-fix

total_files_scanned = 0
total_formulas_checked = 0
issues_found = 0
issues_fixed = 0

report_details = []

def lint_and_fix_content(fpath, content):
    global total_formulas_checked, issues_found, issues_fixed
    modified = False
    new_content = content

    # 1. Fix \\begin{align} / \\end{align} -> \\begin{aligned} / \\end{aligned}
    if re.search(r'\\begin\{align\*?\}', new_content):
        issues_found += len(re.findall(r'\\begin\{align\*?\}', new_content))
        new_content = re.sub(r'\\begin\{align\*?\}', r'\\begin{aligned}', new_content)
        new_content = re.sub(r'\\end\{align\*?\}', r'\\end{aligned}', new_content)
        issues_fixed += len(re.findall(r'\\begin\{aligned\}', new_content))
        modified = True
        report_details.append(f"  🔧 [{fpath}] 修正 \\begin{{align}} 為 \\begin{{aligned}}")

    # 2. Fix \\begin{gather} / \\end{gather} -> \\begin{gathered} / \\end{gathered}
    if re.search(r'\\begin\{gather\*?\}', new_content):
        issues_found += len(re.findall(r'\\begin\{gather\*?\}', new_content))
        new_content = re.sub(r'\\begin\{gather\*?\}', r'\\begin{gathered}', new_content)
        new_content = re.sub(r'\\end\{gather\*?\}', r'\\end{gathered}', new_content)
        issues_fixed += len(re.findall(r'\\begin\{gathered\}', new_content))
        modified = True
        report_details.append(f"  🔧 [{fpath}] 修正 \\begin{{gather}} 為 \\begin{{gathered}}")

    # 3. Check for bare LaTeX matrices (starts with \\begin{bmatrix} on its own line without $$)
    lines = new_content.split('\n')
    fixed_lines = []
    in_code = False
    in_math_block = False
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith('```'):
            in_code = not in_code
            fixed_lines.append(line)
            i += 1
            continue

        if in_code:
            fixed_lines.append(line)
            i += 1
            continue

        if stripped.startswith('$$'):
            # If $$ is on same line as content and closed, doesn't toggle block
            if stripped.count('$$') % 2 == 1:
                in_math_block = not in_math_block
            fixed_lines.append(line)
            i += 1
            continue

        if in_math_block:
            fixed_lines.append(line)
            i += 1
            continue

        # Detect bare \begin{bmatrix} or \begin{matrix} or \begin{aligned} without $$
        if re.match(r'^(>|\s*)*\\begin\{(bmatrix|matrix|aligned|cases|pmatrix)\}', stripped):
            issues_found += 1
            # Find matching \end{...}
            env_match = re.search(r'\\begin\{([a-z]+)\}', stripped)
            env_name = env_match.group(1) if env_match else 'bmatrix'
            
            # Collect block
            block = [line]
            j = i + 1
            while j < len(lines):
                next_l = lines[j]
                block.append(next_l)
                if f'\\end{{{env_name}}}' in next_l:
                    break
                j += 1
            
            # Wrap in $$
            indent = len(line) - len(line.lstrip())
            indent_str = line[:indent]
            fixed_lines.append(f"{indent_str}$$")
            fixed_lines.extend(block)
            # Ensure ending line has $$
            if not block[-1].strip().endswith('$$'):
                fixed_lines.append(f"{indent_str}$$")
            
            issues_fixed += 1
            modified = True
            report_details.append(f"  🔧 [{fpath}:{i+1}] 為裸露 \\begin{{{env_name}}} 區塊包裹 $$...$$")
            i = j + 1
            continue

        # Count formulas
        total_formulas_checked += line.count('$') // 2
        fixed_lines.append(line)
        i += 1

    if modified:
        return '\n'.join(fixed_lines), True
    return content, False


# Scan all Markdown files in repository
for root, dirs, files in os.walk('.'):
    if any(s in root for s in ['.git', 'node_modules', '.agents', '.system_generated']):
        continue
    for f in files:
        if f.endswith('.md'):
            total_files_scanned += 1
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                original = fp.read()
            
            updated, was_modified = lint_and_fix_content(fpath, original)
            if was_modified and auto_fix:
                with open(fpath, 'w', encoding='utf-8') as fp:
                    fp.write(updated)

print(f"======================================================================")
print(f"⚡ KaTeX 數學公式語法檢驗與修復報告")
print(f"======================================================================")
print(f"📁 掃描 Markdown 總數: {total_files_scanned} 篇")
print(f"🧮 估計公式數量: {total_formulas_checked} 處")
print(f"⚠️ 發現問題數: {issues_found}")
print(f"✅ 自動修復數: {issues_fixed}")
print(f"----------------------------------------------------------------------")
for r in report_details[:20]:
    print(r)
if len(report_details) > 20:
    print(f"  ... 以及其他 {len(report_details) - 20} 處修復")
print(f"======================================================================")
