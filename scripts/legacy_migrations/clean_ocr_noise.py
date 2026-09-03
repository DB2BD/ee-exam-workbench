import re
import os

def clean_ocr_lines(text):
    lines = text.split('\n')
    cleaned_lines = []
    
    # Precompiled regex
    noise_pattern = re.compile(
        r'^(圖[\(（]?[一二三四五六七八九十\d\w\)]+[\)）]?|'
        r'\$?[ RCLVIviRo\d\.\+\-\\\/\_\^\*\%]+\$?|'
        r'I\d+|v_?[os\d]|BW|\(t\)|t|vs|Vo|Vin|Vout|4I1|r ix|\+ \-|\+\-|\-\+|'
        r'(\$?[0-9\.]+\s*(?:\\text\{\s*)?(?:k\\Omega|\\Omega|\\mu F|mH|pF|H|F|V|A|kVA|MVA|kW|MW|Hz|kHz|rad/s|ms)\$?\}?))$'
    )
    
    for line in lines:
        l = line.strip()
        if not l:
            cleaned_lines.append('')
            continue
            
        # Keep structural elements
        if l.startswith('#') or l.startswith('>') or l.startswith('!') or l.startswith('|') or l.startswith('*') or l.startswith('-') or l.startswith('$$') or l.startswith('[['):
            cleaned_lines.append(line)
            continue
            
        # If line contains Chinese question sentence markers, keep it
        if any(c in l for c in ['，', '。', '？', '！', '：', '；', '（', '）', '求解', '試求', '求出', '如下圖', '如圖', '假設', '已知', '考慮', '其中', '設由', '試述', '說明', '請依', '定義', '計算', '分析', '試問', '請繪']):
            cleaned_lines.append(line)
            continue
            
        # Check if line is isolated schematic label noise
        if len(l) < 30 and noise_pattern.match(l):
            continue
            
        if len(l) <= 4 and re.match(r'^[a-zA-Z0-9\s\+\-\$\_]+$', l):
            continue
            
        cleaned_lines.append(line)
        
    res = '\n'.join(cleaned_lines)
    res = re.sub(r'\n{3,}', '\n\n', res)
    return res

# Process all subjects
for subj_file in sorted(os.listdir('依考科分類')):
    if subj_file.endswith('.md'):
        full_path = os.path.join('依考科分類', subj_file)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned = clean_ocr_lines(content)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
            
        print(f'✅ Cleaned OCR noise in {full_path}')
