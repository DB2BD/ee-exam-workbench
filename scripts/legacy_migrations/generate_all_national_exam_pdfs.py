# -*- coding: utf-8 -*-
"""
generate_all_national_exam_pdfs.py
==================================
Generates 25 official-style MOEX exam PDF documents for 110~114 National Exams.
Uses ReportLab with macOS system Songti font.
"""

import os
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORKSPACE, "scripts", "lib"))
os.chdir(WORKSPACE)

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from generate_all_national_exams import EXAM_DATA, SUBJECT_DIRS

# Register Songti font
FONT_PATH = "/System/Library/Fonts/Supplemental/Songti.ttc"
pdfmetrics.registerFont(TTFont("Songti", FONT_PATH, subfontIndex=0))
pdfmetrics.registerFont(TTFont("Songti-Bold", FONT_PATH, subfontIndex=1 if os.path.exists(FONT_PATH) else 0))

SUBJECT_NAMES_SHORT = {
    '01': '電路學',
    '02': '電子學',
    '03': '工程數學',
    '04': '電機機械',
    '05': '電力系統'
}

def draw_header_box(c, yr, title, code, time_str):
    # Outer frame
    width, height = A4
    c.setLineWidth(1.5)
    c.rect(36, 36, width - 72, height - 72)
    
    # Title
    c.setFont("Songti", 16)
    header_text = f"{yr} 年公務人員高等考試三級考試試題"
    c.drawCentredString(width / 2.0, height - 60, header_text)
    
    # Metadata Table
    c.setLineWidth(0.8)
    table_top = height - 75
    table_bottom = table_top - 60
    c.rect(46, table_bottom, width - 92, 60)
    
    # Grid lines
    c.line(46, table_top - 20, width - 46, table_top - 20)
    c.line(46, table_top - 40, width - 46, table_top - 40)
    c.line(140, table_top, 140, table_bottom)
    c.line(280, table_top, 280, table_bottom)
    c.line(380, table_top, 380, table_bottom)
    
    c.setFont("Songti", 9)
    # Row 1
    c.drawString(52, table_top - 14, "等　　別：高等考試三級")
    c.drawString(146, table_top - 14, "類　科：電力工程 / 電子工程")
    c.drawString(286, table_top - 14, f"科　目：{title}")
    c.drawString(386, table_top - 14, f"代　號：{code}")
    
    # Row 2
    c.drawString(52, table_top - 34, f"考試時間：{time_str}")
    c.drawString(146, table_top - 34, "座號：")
    c.drawString(286, table_top - 34, "※注意：禁止使用未經考選部核定之電子計算器。")
    
    # Row 3
    c.drawString(52, table_top - 54, "不必抄題，作答時請將試題題號及答案依照順序寫在申論試卷上，於本試題上作答者，不予計分。")
    
    c.line(46, table_bottom - 10, width - 46, table_bottom - 10)
    return table_bottom - 25

def wrap_text(text, max_chars=40):
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

def generate_exam_pdf(sid, yr):
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
        
        # Check remaining space for page break
        if y < 140:
            c.showPage()
            c.setLineWidth(1.5)
            c.rect(36, 36, width - 72, height - 72)
            c.setFont("Songti", 10)
            c.drawString(width / 2.0 - 40, height - 50, f"{yr} 年高考三級 {sname_short}（續頁）")
            y = height - 70
            
        c.setFont("Songti", 11)
        # Main question
        main_q_clean = main_q.replace("$", "").replace("\\", "").replace("text", "").replace("{", "").replace("}", "")
        lines = wrap_text(f"{num_str}、 {main_q_clean}", max_chars=44)
        for l in lines:
            c.drawString(50, y, l)
            y -= 18
            
        # Sub questions
        if sub_qs:
            for sub_idx, sub_q in enumerate(sub_qs):
                sub_num = ["一", "二", "三", "四", "五"][sub_idx]
                sub_clean = sub_q.replace("$", "").replace("\\", "").replace("text", "").replace("{", "").replace("}", "")
                sub_lines = wrap_text(f"({sub_num}) {sub_clean}", max_chars=40)
                for sl in sub_lines:
                    c.drawString(70, y, sl)
                    y -= 16
                    
        y -= 8  # spacing between questions
        
    c.showPage()
    c.save()
    print(f"  📄 Generated Official PDF: 依考科分類/🏛️_國考同級參考題庫/{sdir}/{pdf_filename}")

print("🚀 Generating 25 Official Exam PDFs (110~114 年)...")
for sid in ['01', '02', '03', '04', '05']:
    for yr in [110, 111, 112, 113, 114]:
        generate_exam_pdf(sid, yr)

print("\n🎉 All 25 National Exam PDFs successfully generated!")
