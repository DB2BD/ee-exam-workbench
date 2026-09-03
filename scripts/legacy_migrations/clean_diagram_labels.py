import glob
import re
import os

def clean_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
        
    lines = text.splitlines()
    clean_lines = []
    
    # Regex patterns for isolated diagram labels
    diagram_label_patterns = [
        r'^\s*\$[vViIeE]\d*\$\s*$',
        r'^\s*\$\d+(?:\.\d+)?\\(?:text\{\s*k\}|text\{\s*M\}|\s*)[ΩΩ]\$\s*$',
        r'^\s*\$\d+(?:\.\d+)?\\text\{\s*(?:mH|pF|kV|kVA|MVA|Mvar|kvar|rad/s|Hz|HP|mA|mW|kW|MW|H)\}\$\s*$',
        r'^\s*\$\d+(?:\.\d+)?\\ \\mu\\text\{\s*F\}\$\s*$',
        r'^\s*\$[vViI][a-zA-Z0-9_]*\([t\d\s\+-]*\)\$\s*$',
        r'^\s*\$[a-zA-Z0-9_]+\$\s*$',
        r'^\s*(?:圖[一二三四五六七八九十\d]+|圖\([一二三四五六七八九十\d]+\))\s*$',
        r'^\s*(?:[＋－+\-＝=]|v[123]|I|Vx|2 Vx|vo|vs|is|R1|R2|R3|RL|Zin)\s*$',
        r'^\s*(?:1|2|3|4|5|6|7|8|9|0|\[|\]|\{|\}|\||T|ω)\s*$'
    ]
    
    for l in lines:
        ls = l.strip()
        if not ls:
            clean_lines.append('')
            continue
            
        # Check if line matches any diagram label pattern
        is_label = False
        for pat in diagram_label_patterns:
            if re.match(pat, ls):
                is_label = True
                break
                
        if not is_label:
            clean_lines.append(l)
            
    # Collapse multiple blank lines
    result = '\n'.join(clean_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(result.strip() + '\n')
    print(f'Cleaned: {fpath}')

all_subject_mds = glob.glob('依考科分類/**/*.md', recursive=True) + glob.glob('依考科分類/*.md')
for f in set(all_subject_mds):
    clean_file(f)

print('Successfully cleaned all 6 subjects!')
