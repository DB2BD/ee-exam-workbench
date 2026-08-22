# -*- coding: utf-8 -*-
"""
全資料庫深度 Code Review — 四軸全掃描
1. 對稱成分短路故障計算數值
2. KaTeX 矩陣與公式語法
3. 防坑提醒 (Warning) 充足度
4. 圖片引用異常偵測
"""
import os, re, json

BASE = '.'
SOLUTION_ROOT = '📝 個人題解與錯題本'

# ─── Collectors ───
katex_issues = []       # (file, line, content, issue_type)
image_issues = []       # (file, line, content, issue_type)
warning_stats = {}      # file -> bool
fault_files = []        # (file, has_seq_model, has_warning)
all_md = []

# ── Obsidian image pattern: ![[filename]] or ![[filename|size]] ──
obsidian_img_re = re.compile(r'!\[\[([^\]]+?)\]\]')
# ── Standard markdown image: ![alt](path) ──
std_img_re = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
# ── Unclosed inline $ (not $$ and not \$) ──
unclosed_dollar_re = re.compile(r'(?<!\$)(?<!\\)\$(?!\$)')

for root, dirs, files in os.walk(BASE):
    # Skip irrelevant dirs
    if any(skip in root for skip in ['.git', 'node_modules', '.agents', '.system_generated', 'libs', '__pycache__']):
        continue
    for f in files:
        if not f.endswith('.md'):
            continue
        fpath = os.path.join(root, f)
        all_md.append(fpath)
        
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
            lines = fp.readlines()
        content = ''.join(lines)
        
        in_code_block = False
        in_math_block = False
        
        for lno, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Track code blocks
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            
            # ── KaTeX Checks ──
            # 1. Unclosed inline $
            dollars = unclosed_dollar_re.findall(line)
            dollar_count = len(dollars)
            if dollar_count % 2 != 0 and '$$' not in line:
                # Exclude currency-like patterns
                if not re.search(r'(NT\$|\$\d+[MBK]|\$/)', line):
                    katex_issues.append((fpath, lno, stripped[:100], 'unclosed_dollar'))
            
            # 2. Bare LaTeX without $$ delimiters (common mistake)
            if not in_math_block and re.match(r'\s*(\\mathbf|\\frac|\\begin|\\end|\\text|\\left|\\right|\\sqrt)', stripped):
                if not stripped.startswith('$') and not stripped.startswith('> '):
                    katex_issues.append((fpath, lno, stripped[:100], 'bare_latex'))
            
            # 3. Track $$ block state
            if stripped == '$$':
                in_math_block = not in_math_block
            
            # ── Image Checks ──
            # Obsidian-style ![[image]]
            obs_matches = obsidian_img_re.findall(line)
            for img_ref in obs_matches:
                img_name = img_ref.split('|')[0].strip()
                # Search for image file
                found = False
                for iroot, idirs, ifiles in os.walk(BASE):
                    if any(skip in iroot for skip in ['.git', 'node_modules', '.system_generated']):
                        continue
                    if img_name in ifiles:
                        found = True
                        break
                if not found:
                    image_issues.append((fpath, lno, img_name, 'obsidian_missing'))
            
            # Standard markdown ![alt](path)
            std_matches = std_img_re.findall(line)
            for alt, path in std_matches:
                if path.startswith('http'):
                    continue  # skip external URLs
                # Resolve relative path
                abs_img = os.path.normpath(os.path.join(os.path.dirname(fpath), path))
                if not os.path.exists(abs_img):
                    image_issues.append((fpath, lno, path, 'std_missing'))

# ── Fault calculation check ──
fault_keywords = ['對稱成分', '單相接地', '線間短路', 'SLG', '2LG', '零序', '負序', '正序', '故障電流', '短路容量', 'Fortescue']
for fpath in all_md:
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
        content = fp.read()
    if any(kw in content for kw in fault_keywords):
        has_seq = any(kw in content for kw in ['Z_1', 'X_1', 'I_{a1}', 'I_{a0}', 'V_{a2}'])
        has_warn = '> [!WARNING]' in content or '⚠️' in content
        fault_files.append((fpath, has_seq, has_warn))

# ── Warning coverage in solution files ──
warn_missing = []
for fpath in all_md:
    if '_全卷完整詳細題解.md' in fpath:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
        if '> [!WARNING]' not in content:
            warn_missing.append(fpath)

# ═══════════════════════ OUTPUT ═══════════════════════
print("=" * 70)
print("🔍 全資料庫 /code-review 四軸深度審查報告")
print("=" * 70)

print(f"\n📁 掃描 Markdown 總數: {len(all_md)} 篇")

print(f"\n{'─'*70}")
print(f"[1] 對稱成分與短路故障計算審查 ({len(fault_files)} 份含故障分析)")
print(f"{'─'*70}")
for fp, has_seq, has_warn in fault_files:
    seq_icon = '✅' if has_seq else '⚠️'
    warn_icon = '✅' if has_warn else '⚠️'
    print(f"  {seq_icon} 序網路模型 | {warn_icon} Warning | {fp}")

print(f"\n{'─'*70}")
print(f"[2] KaTeX 公式語法排查 ({len(katex_issues)} 處異常)")
print(f"{'─'*70}")
for fp, lno, txt, itype in katex_issues:
    type_label = {'unclosed_dollar': '未閉合 $', 'bare_latex': '裸露 LaTeX'}.get(itype, itype)
    print(f"  ⚠️ [{type_label}] {fp}:{lno}")
    print(f"     {txt}")

print(f"\n{'─'*70}")
print(f"[3] 防坑 Warning 覆蓋率 (缺少: {len(warn_missing)} 篇)")
print(f"{'─'*70}")
if warn_missing:
    for wm in warn_missing:
        print(f"  ⚠️ {wm}")
else:
    print("  ✅ 所有全卷題解均已具備 > [!WARNING] 防坑卡片")

print(f"\n{'─'*70}")
print(f"[4] 圖片引用異常偵測 ({len(image_issues)} 處)")
print(f"{'─'*70}")
if image_issues:
    for fp, lno, img, itype in image_issues:
        type_label = {'obsidian_missing': 'Obsidian 圖片遺失', 'std_missing': '標準圖片遺失'}.get(itype, itype)
        print(f"  ❌ [{type_label}] {fp}:{lno}")
        print(f"     → {img}")
else:
    print("  ✅ 所有圖片引用均正常")

# Dump structured JSON for follow-up
results = {
    'total_md': len(all_md),
    'katex_issues': [(fp, lno, txt, it) for fp, lno, txt, it in katex_issues],
    'image_issues': [(fp, lno, img, it) for fp, lno, img, it in image_issues],
    'warn_missing': warn_missing,
    'fault_files_count': len(fault_files),
}
with open('scripts/_review_results.json', 'w', encoding='utf-8') as jf:
    json.dump(results, jf, ensure_ascii=False, indent=2)

print(f"\n{'='*70}")
print(f"📊 結構化審查結果已儲存至 scripts/_review_results.json")
print(f"{'='*70}")
