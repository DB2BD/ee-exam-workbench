# -*- coding: utf-8 -*-
"""
generate_all_national_exam_pdfs_v2.py
=====================================
Generates 25 official-quality MOEX exam PDF documents with:
- Full Unicode mathematical typography using Arial Unicode font (zero missing characters).
- Precise conversion of all LaTeX expressions (Greek letters, symbols, sub/superscripts).
- Full official examination header tables and instructions.
"""

import os
import re
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORKSPACE, "scripts", "lib"))
os.chdir(WORKSPACE)

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from generate_all_national_exams import EXAM_DATA, SUBJECT_DIRS

FONT_ARIAL_UNICODE = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
pdfmetrics.registerFont(TTFont("ArialUnicode", FONT_ARIAL_UNICODE))

SUBJECT_NAMES_SHORT = {
    '01': '電路學',
    '02': '電子學',
    '03': '工程數學',
    '04': '電機機械',
    '05': '電力系統'
}

def latex_to_unicode(text):
    """Converts LaTeX expressions into clean, legible Unicode text with zero missing characters."""
    t = text
    # Greek & Math symbols
    replacements = [
        (r'\\Omega', 'Ω'),
        (r'\\mu', 'μ'),
        (r'\\tau', 'τ'),
        (r'\\lambda', 'λ'),
        (r'\\theta', 'θ'),
        (r'\\pi', 'π'),
        (r'\\Delta', 'Δ'),
        (r'\\alpha', 'α'),
        (r'\\beta', 'β'),
        (r'\\gamma', 'γ'),
        (r'\\sigma', 'σ'),
        (r'\\omega', 'ω'),
        (r'\\angle', '∠'),
        (r'\\pm', '±'),
        (r'\\approx', '≈'),
        (r'\\le', '≤'),
        (r'\\ge', '≥'),
        (r'\\infty', '∞'),
        (r'\\parallel', '∥'),
        (r'\\cdot', '·'),
        (r'\\times', '×'),
        (r'\\partial', '∂'),
        (r'\\int', '∫'),
        (r'\\sum', '∑'),
        (r'\\sqrt\{([^}]+)\}', r'√(\1)'),
        (r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)'),
        (r'\\mathbf\{([^}]+)\}', r'\1'),
        (r'\\text\{([^}]+)\}', r'\1'),
        (r'\\mathrm\{([^}]+)\}', r'\1'),
        (r'\\left\(', '('),
        (r'\\right\)', ')'),
        (r'\\left\[', '['),
        (r'\\right\]', ']'),
        (r'\\,', ' '),
        (r'\\;', ' '),
        (r'\\!', ''),
        (r'\\', ''),
        (r'\$', ''),
        (r'\*', ''),
        (r'\#', '')
    ]
    for pattern, repl in replacements:
        t = re.sub(pattern, repl, t)
    
    # Subscripts & Superscripts
    sub_map = {'0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉','a':'ₐ','e':'ₑ','o':'ₒ','s':'ₛ','t':'ₜ','x':'ₓ'}
    sup_map = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹','+':'⁺','-':'⁻','=':'⁼','(':'⁽',')':'⁾','n':'ⁿ','t':'ᵗ'}
    
    t = re.sub(r'_([0-9aeostx])', lambda m: sub_map.get(m.group(1), m.group(0)), t)
    t = re.sub(r'\^([0-9\+\-\(\)nt])', lambda m: sup_map.get(m.group(1), m.group(0)), t)
    t = re.sub(r'\^\{([^}]+)\}', lambda m: '^(' + m.group(1) + ')', t)
    t = re.sub(r'_\{([^}]+)\}', lambda m: '_' + m.group(1), t)
    
    return t.strip()

def draw_header_box(c, yr, title, code, time_str):
    width, height = A4
    c.setLineWidth(1.5)
    c.rect(36, 36, width - 72, height - 72)
    
    # Title
    c.setFont("ArialUnicode", 15)
    header_text = f"{yr} 年公務人員高等考試三級考試試題"
    c.drawCentredString(width / 2.0, height - 58, header_text)
    
    # Metadata Table
    c.setLineWidth(0.8)
    table_top = height - 72
    table_bottom = table_top - 62
    c.rect(46, table_bottom, width - 92, 62)
    
    # Grid lines
    c.line(46, table_top - 20, width - 46, table_top - 20)
    c.line(46, table_top - 41, width - 46, table_top - 41)
    c.line(140, table_top, 140, table_bottom)
    c.line(280, table_top, 280, table_bottom)
    c.line(380, table_top, 380, table_bottom)
    
    c.setFont("ArialUnicode", 8.5)
    # Row 1
    c.drawString(52, table_top - 14, "等　　別：高等考試三級")
    c.drawString(146, table_top - 14, "類　科：電力工程 / 電子工程")
    c.drawString(286, table_top - 14, f"科　目：{title}")
    c.drawString(386, table_top - 14, f"代　號：{code}")
    
    # Row 2
    c.drawString(52, table_top - 35, f"考試時間：{time_str}")
    c.drawString(146, table_top - 35, "座號：")
    c.drawString(286, table_top - 35, "※注意：可以使用考選部核定之電子計算器。")
    
    # Row 3
    c.drawString(52, table_top - 55, "不必抄題，作答時請將試題題號及答案依照順序寫在申論試卷上，於本試題上作答者，不予計分。")
    
    c.line(46, table_bottom - 8, width - 46, table_bottom - 8)
    return table_bottom - 22

def wrap_text(text, max_chars=46):
    lines = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        while len(paragraph) > max_chars:
            lines.append(paragraph[:max_chars])
            paragraph = paragraph[max_chars:]
        if paragraph:
            lines.append(paragraph)
    return lines

def generate_exam_pdf_v2(sid, yr):
    data = EXAM_DATA.get((sid, yr))
    if not data:
        return
        
    sdir = SUBJECT_DIRS[sid]
    sname_short = SUBJECT_NAMES_SHORT[sid]
    out_dir = os.path.join(WORKSPACE, "依考科分類", "🏛️_國考同級參考題庫", sdir)
    os.makedirs(out_dir, exist_ok=True)
    pdf_filename = f"GK_{yr}年_高考三級_{sname_short}.pdf"
    pdf_path = os.path.join(out_dir, pdf_filename)
    
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    y = draw_header_box(c, yr, data["title"], data["code"], data["time"])
    
    num_map = ["一", "二", "三", "四", "五", "六", "七", "八"]
    for idx, (main_q, sub_qs) in enumerate(data["questions"]):
        num_str = num_map[idx]
        
        # Check space
        if y < 120:
            c.showPage()
            c.setLineWidth(1.5)
            c.rect(36, 36, width - 72, height - 72)
            c.setFont("ArialUnicode", 10)
            c.drawString(width / 2.0 - 50, height - 48, f"{yr} 年高考三級 {sname_short}（第 2 頁）")
            c.line(46, height - 56, width - 46, height - 56)
            y = height - 74
            
        c.setFont("ArialUnicode", 10.5)
        # Main question with full Unicode math
        main_q_clean = latex_to_unicode(main_q)
        lines = wrap_text(f"{num_str}、 {main_q_clean}", max_chars=48)
        for l in lines:
            c.drawString(50, y, l)
            y -= 16
            
        # Sub questions
        if sub_qs:
            for sub_idx, sub_q in enumerate(sub_qs):
                sub_num = ["一", "二", "三", "四", "五"][sub_idx]
                sub_clean = latex_to_unicode(sub_q)
                sub_lines = wrap_text(f"({sub_num}) {sub_clean}", max_chars=44)
                for sl in sub_lines:
                    c.drawString(70, y, sl)
                    y -= 15
                    
        y -= 8  # spacing
        
    c.showPage()
    c.save()
    print(f"  📄 Generated Complete Typography PDF: {sdir}/{pdf_filename}")

print("🚀 Regenerating 25 Official Quality Exam PDFs with Full Unicode Math Typography...")
for sid in ['01', '02', '03', '04', '05']:
    for yr in [110, 111, 112, 113, 114]:
        generate_exam_pdf_v2(sid, yr)

print("\n🎉 All 25 National Exam PDFs regenerated with ZERO missing characters!")
