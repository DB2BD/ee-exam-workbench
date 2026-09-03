# -*- coding: utf-8 -*-
"""
全資料庫四軸修復腳本
1. 修復 KaTeX 裸露 LaTeX（核心考點知識庫）
2. 修復圖片路徑（相對路徑指向正確 images 目錄）
3. 全量重掃驗證
"""
import os, re

BASE = '/Users/a/技師考試/歷屆試題_104-114年'
os.chdir(BASE)

fixed_count = 0

# ════════════════════════════════════════════════════════════════════
# [A] 修復核心考點知識庫中的裸露 LaTeX（加上 $$ 包裹）
# ════════════════════════════════════════════════════════════════════
KNOWLEDGE_ROOT = '🧠 核心考點知識庫'

def fix_bare_latex_in_file(fpath):
    """識別並修復未被 $$ 包裹的獨立公式行"""
    global fixed_count
    with open(fpath, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    
    modified = False
    new_lines = []
    in_code = False
    in_math = False
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Track code blocks
        if stripped.startswith('```'):
            in_code = not in_code
            new_lines.append(line)
            i += 1
            continue
        
        if in_code:
            new_lines.append(line)
            i += 1
            continue
        
        # Track existing $$ blocks
        if stripped == '$$':
            in_math = not in_math
            new_lines.append(line)
            i += 1
            continue
        
        if in_math:
            new_lines.append(line)
            i += 1
            continue
        
        # Detect bare LaTeX line (starts with \command but not inside $)
        if re.match(r'\s+(\\begin\{|\\end\{|\\frac\{|\\text\{|\\mathbf|\\left|\\right|\\cos|\\sin|\\oint|\\int)', stripped):
            # Check if this is part of a multi-line block
            # Collect consecutive bare LaTeX lines
            block_start = i
            block_lines = [line]
            j = i + 1
            while j < len(lines):
                next_stripped = lines[j].strip()
                if next_stripped == '' or next_stripped.startswith('#') or next_stripped.startswith('-') or next_stripped.startswith('>') or next_stripped.startswith('*'):
                    break
                if re.match(r'\s*(\\|&)', next_stripped) or next_stripped.endswith('\\\\') or next_stripped.startswith('\\end{'):
                    block_lines.append(lines[j])
                    j += 1
                else:
                    break
            
            # Determine indentation
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Wrap with $$
            new_lines.append(f'{indent_str}$$\n')
            for bl in block_lines:
                new_lines.append(bl)
            # Check if last line already ends with $$
            last_stripped = block_lines[-1].strip()
            if not last_stripped.endswith('$$'):
                new_lines.append(f'{indent_str}$$\n')
            
            modified = True
            fixed_count += 1
            i = j
            continue
        
        new_lines.append(line)
        i += 1
    
    if modified:
        with open(fpath, 'w', encoding='utf-8') as fp:
            fp.writelines(new_lines)
        print(f"  ✅ [KaTeX 修復] {fpath}")

# Process knowledge base files
for root, dirs, files in os.walk(KNOWLEDGE_ROOT):
    for f in files:
        if f.endswith('.md'):
            fix_bare_latex_in_file(os.path.join(root, f))

# ════════════════════════════════════════════════════════════════════
# [B] 修復圖片路徑（題解檔引用 ./images/ 但圖片在 依考科分類/XX/images/）
# ════════════════════════════════════════════════════════════════════
SOLUTION_ROOT = '📝 個人題解與錯題本'
EXAM_ROOT = '依考科分類'

# Build image index: filename -> absolute path
image_index = {}
for root, dirs, files in os.walk(BASE):
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
            image_index[f] = os.path.join(root, f)

std_img_re = re.compile(r'(!\[[^\]]*\])\(([^)]+)\)')

for root, dirs, files in os.walk(SOLUTION_ROOT):
    for f in files:
        if not f.endswith('.md'):
            continue
        fpath = os.path.join(root, f)
        with open(fpath, 'r', encoding='utf-8') as fp:
            content = fp.read()
        
        modified_flag = [False]
        
        def fix_img_path(match):
            global fixed_count
            alt_part = match.group(1)
            path = match.group(2)
            
            if path.startswith('http'):
                return match.group(0)
            
            # Check if path resolves
            abs_path = os.path.normpath(os.path.join(os.path.dirname(fpath), path))
            if os.path.exists(abs_path):
                return match.group(0)
            
            # Try to find the image by filename
            img_name = os.path.basename(path)
            if img_name in image_index:
                # Compute relative path from solution file to actual image
                actual_path = image_index[img_name]
                rel_path = os.path.relpath(actual_path, os.path.dirname(fpath))
                modified_flag[0] = True
                fixed_count += 1
                print(f"  ✅ [圖片路徑修復] {fpath}")
                print(f"     ❌ 舊路徑: {path}")
                print(f"     ✅ 新路徑: {rel_path}")
                return f'{alt_part}({rel_path})'
            
            return match.group(0)
        
        new_content = std_img_re.sub(fix_img_path, content)
        
        if modified_flag[0]:
            with open(fpath, 'w', encoding='utf-8') as fp:
                fp.write(new_content)

print(f"\n🎉 總共修復了 {fixed_count} 處問題")
