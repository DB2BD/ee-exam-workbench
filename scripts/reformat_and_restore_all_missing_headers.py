# -*- coding: utf-8 -*-
import re
import os

def fix_subject_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by year headers
    year_splits = re.split(r'(##\s*\d{3}\s*年[^\n]*)', content)
    
    new_parts = [year_splits[0]] # preamble
    
    for i in range(1, len(year_splits), 2):
        yr_header = year_splits[i]
        yr_body = year_splits[i+1]
        
        # Check if #### 一、 is present
        # If not, let's identify paragraph starts that represent questions
        # Typically separated by blank lines or paragraphs
        lines = yr_body.split('\n')
        new_lines = []
        q_idx = 1
        num_map = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八'}
        
        in_content = False
        for line in lines:
            l_str = line.strip()
            
            if '### 📝 試題內容' in line:
                in_content = True
                new_lines.append(line)
                continue
            if '### 📷' in line or '##' in line:
                in_content = False
                new_lines.append(line)
                continue
                
            if in_content:
                # If line already starts with #### 一、 or 一、
                m_existing = re.match(r'^(?:####\s*)?([一二三四五六七八九十]+)[、\.\s](.*)', l_str)
                if m_existing:
                    q_zh = m_existing.group(1)
                    rest = m_existing.group(2).strip()
                    new_lines.append(f'#### {q_zh}、 {rest}')
                    continue
                
                # If line represents a question start but missing header
                # (e.g. starts with 如圖, 一部, 一台, 某, 兩部, 三台, 如下圖, 設, 試求, 試述)
                # and preceded by empty line, and not a sub-bullet *(一)*
                if not l_str.startswith('*') and not l_str.startswith('>') and not l_str.startswith('!') and not l_str.startswith('|') and not l_str.startswith('$$') and len(l_str) > 10:
                    if any(l_str.startswith(w) for w in ['如圖', '如下圖', '圖', '一部', '一台', '一具', '某', '兩部', '三台', '三相', '有一', '設一', '設有', '試述', '試求', '求解', '請', '已知', '考慮', '若', '依據', '根據', '針對', '某部', '某一', '一特高壓', '一工廠', '一鋼鐵廠', '一石化廠', '一鋁材料', '一加工廠', '一阻抗', '一煉鋼廠', '一配電', '一商業', '一電子', '一表燈', '一座', '電力公司', '一電磁鐵', '一交流', '如果', '由電錶', '電容式']):
                        # Check if this could be the start of question q_idx
                        # Let's ensure it has points or question structure
                        if q_idx <= 8 and not any(f'#### {num_map.get(q_idx, "")}、' in nl for nl in new_lines[-5:]):
                            q_zh = num_map.get(q_idx, str(q_idx))
                            new_lines.append(f'#### {q_zh}、 {l_str}')
                            q_idx += 1
                            continue
            
            new_lines.append(line)
            
        new_parts.append(yr_header)
        new_parts.append('\n'.join(new_lines))
        
    full_res = ''.join(new_parts)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(full_res)
    print(f'✅ Processed {fpath}')

for subj in ['02_電子學_含電力電子', '04_電機機械', '05_電力系統', '06_工業配電']:
    fix_subject_file(f'依考科分類/{subj}.md')
