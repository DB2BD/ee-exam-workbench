# -*- coding: utf-8 -*-
import re
import os

print("Standardizing all question headings (#### 一、 ~ #### 五、) across all 6 subjects...")

# Define subject files
subj_files = [
    '依考科分類/01_電路學.md',
    '依考科分類/02_電子學_含電力電子.md',
    '依考科分類/03_工程數學.md',
    '依考科分類/04_電機機械.md',
    '依考科分類/05_電力系統.md',
    '依考科分類/06_工業配電.md'
]

num_list = ['一', '二', '三', '四', '五', '六', '七', '八']

def standardize_year_section(sec_text, yr):
    # Check if section has #### 一、
    q_matches = re.findall(r'####\s+([一二三四五六七八九十]+)[、\.]', sec_text)
    if len(q_matches) >= 4:
        return sec_text # Already well structured
    
    # Try finding questions by (一、/二、/三、/四、/五、) or paragraph blocks after "### 📝 試題內容"
    parts = re.split(r'###\s+📝\s*試題內容[^\n]*\n+', sec_text)
    if len(parts) < 2:
        return sec_text
    
    header_part = parts[0] + "### 📝 試題內容與數學公式編排（LaTeX）\n\n"
    body_and_footer = parts[1]
    
    footer_parts = re.split(r'###\s+📷\s*官方試卷', body_and_footer)
    body_part = footer_parts[0]
    footer_part = "### 📷 官方試卷" + footer_parts[1] if len(footer_parts) > 1 else ""
    
    # Check if body has explicit 一、 二、 三、 四、 五、
    # If not, split into 5 question chunks
    # Let's see if we can split by paragraph blocks or common question indicators
    chunks = [c.strip() for c in re.split(r'\n\s*\n(?=[一二三四五]、|第[一二三四五]題|[1-5]\.)', body_part) if c.strip()]
    
    if len(chunks) < 4:
        # Split by paragraphs that don't start with * (sub-questions)
        raw_paras = [p.strip() for p in body_part.split('\n\n') if p.strip()]
        chunks = []
        cur_chunk = []
        for p in raw_paras:
            if not p.startswith('*') and not p.startswith('!['):
                if cur_chunk:
                    chunks.append('\n\n'.join(cur_chunk))
                    cur_chunk = []
            cur_chunk.append(p)
        if cur_chunk:
            chunks.append('\n\n'.join(cur_chunk))
            
    # Filter out OCR noise like "全一張", "（請接背面）", "考試時間 ： 2 小時"
    cleaned_chunks = []
    for c in chunks:
        # if chunk is just header noise, skip
        lines = [l.strip() for l in c.splitlines() if l.strip()]
        meaningful_lines = [l for l in lines if not any(w in l for w in ['全一張', '請接背面', '背面', '正面', '考試時間', '代號：', '類科：', '科目：', '公職王', '考選部'])]
        if meaningful_lines:
            cleaned_chunks.append('\n'.join(meaningful_lines))
            
    new_body = ""
    for idx, c in enumerate(cleaned_chunks[:5]):
        q_num_char = num_list[idx] if idx < len(num_list) else str(idx+1)
        # Remove existing 一、 or 1. at beginning
        c_clean = re.sub(r'^(?:####\s*)?[一二三四五六七八九十0-9]+[、\.]\s*', '', c).strip()
        new_body += f"#### {q_num_char}、 {c_clean}\n\n"
        
    return header_part + new_body + footer_part

# Process each subject file
for fpath in subj_files:
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
        
    year_sections = re.split(r'\n(##\s+\d+\s*年[^\n]*)', text)
    if len(year_sections) > 1:
        new_text = year_sections[0]
        for i in range(1, len(year_sections), 2):
            y_head = year_sections[i]
            y_sec = year_sections[i+1]
            yr_match = re.search(r'(\d+)\s*年', y_head)
            yr = int(yr_match.group(1)) if yr_match else 0
            
            standardized_sec = standardize_year_section(y_sec, yr)
            new_text += "\n" + y_head + standardized_sec
            
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_text)
        print(f"✅ Processed {fpath}")

print("✨ Standardization complete!")
