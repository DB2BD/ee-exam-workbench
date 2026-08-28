# -*- coding: utf-8 -*-
import os
import re
import json

subjects = [
    ('01', '電路學', '', '#4a7c8f', '依考科分類/01_電路學.md', '依考科分類/01_電路學'),
    ('02', '電子學（含電力電子）', '', '#686b8f', '依考科分類/02_電子學_含電力電子.md', '依考科分類/02_電子學_含電力電子'),
    ('03', '工程數學', '', '#54826b', '依考科分類/03_工程數學.md', '依考科分類/03_工程數學'),
    ('04', '電機機械', '', '#a17846', '依考科分類/04_電機機械.md', '依考科分類/04_電機機械'),
    ('05', '電力系統', '', '#a85858', '依考科分類/05_電力系統.md', '依考科分類/05_電力系統'),
    ('06', '工業配電', '', '#7d6382', '依考科分類/06_工業配電.md', '依考科分類/06_工業配電'),
]

num_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}

# Build automatic dedicated notes dictionary for all solution files in 📝 個人題解與錯題本/
dedicated_notes = {}

# Scan all solution files in 📝 個人題解與錯題本/
for root, dirs, files in os.walk('📝 個人題解與錯題本'):
    for f in files:
        if f.endswith('_全卷完整詳細題解.md'):
            match = re.match(r'(\d{3})年_([^_]+)_全卷完整詳細題解\.md', f)
            if match:
                yr = int(match.group(1))
                sname = match.group(2)
                if '電路' in sname:
                    sid = '01'
                elif '電子' in sname:
                    sid = '02'
                elif '數學' in sname:
                    sid = '03'
                elif '機械' in sname:
                    sid = '04'
                elif '電力' in sname:
                    sid = '05'
                elif '配電' in sname:
                    sid = '06'
                else:
                    sid = '01'
                rel_path = os.path.join(root, f).replace('\\', '/')
                
                # Assign all questions (up to 9) for this year
                for qn in range(1, 10):
                    qid = f'EE-{yr}-{sid}-{qn}'
                    dedicated_notes[qid] = rel_path

# Add individual standalone questions (if any specific standalone notes exist)
if os.path.exists('📝 個人題解與錯題本/03_工程數學/114年_工程數學_第五題_線性系統完整解與零空間.md'):
    dedicated_notes['EE-114-03-5'] = '📝 個人題解與錯題本/03_工程數學/114年_工程數學_第五題_線性系統完整解與零空間.md'
if os.path.exists('📝 個人題解與錯題本/03_工程數學/114年_工程數學_第三題_二階線性ODE.md'):
    dedicated_notes['EE-114-03-3'] = '📝 個人題解與錯題本/03_工程數學/114年_工程數學_第三題_二階線性ODE.md'

all_questions = []
subject_counts = {}

from difficulty_evaluator import evaluate_question_difficulty

def estimate_difficulty(sid, topic, q_body):
    stars, raw_score, breakdown = evaluate_question_difficulty(sid, topic, q_body)
    return stars


def extract_formula_tags(topic, q_body):
    ftags = []
    if '戴維寧' in q_body or '諾頓' in q_body:
        ftags.append('戴維寧等效')
    if '相量' in q_body or '功率因數' in q_body or '複數功率' in q_body:
        ftags.append('S = VI*')
    if 'Buck' in q_body:
        ftags.append('Vo = D Vd')
    if 'Boost' in q_body:
        ftags.append('Vo = Vd/(1-D)')
    if 'SVD' in q_body or '奇異值' in q_body:
        ftags.append('A = U Σ V^T')
    if '特徵值' in q_body or '對角化' in q_body:
        ftags.append('det(A - λI) = 0')
    if '自耦' in q_body:
        ftags.append('S_auto = [VH/(VH-VX)] S2w')
    if '轉差率' in q_body or '感應' in q_body:
        ftags.append('s = (Ns - N)/Ns')
    if '故障' in q_body or '接地' in q_body or 'SLG' in q_body:
        ftags.append('Ia1 = Vf / (Z1+Z2+Z0)')
    if '短路容量' in q_body or '啟斷' in q_body:
        ftags.append('Ssc = Sbase / Xpu')
    if '壓降' in q_body:
        ftags.append('ΔV = √3 I (R cosθ + X sinθ)')
    if '搖擺' in q_body or '等面積' in q_body:
        ftags.append('M d^2δ/dt^2 = Pm - Pe')
    return ftags[:3]

for sid, sname, icon, color, md_file, pdf_dir in subjects:
    if not os.path.exists(md_file):
        continue
    with open(md_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    count_for_subj = 0
    year_sections = re.split(r'\n##\s+(\d+)\s*年', text)
    if len(year_sections) > 1:
        for i in range(1, len(year_sections), 2):
            yr = int(year_sections[i])
            sec_content = year_sections[i+1]
            
            q_blocks = re.split(r'\n####\s+([一二三四五六七八九十]+)[、\.]\s*', sec_content)
            if len(q_blocks) > 1:
                for j in range(1, len(q_blocks), 2):
                    q_chinese = q_blocks[j]
                    q_num = num_map.get(q_chinese, 1)
                    q_body = q_blocks[j+1].strip()
                    
                    clean_body = re.sub(r'###\s+📷\s+官方試卷[\s\S]*?(?=\n####|\n##|\Z)', '', q_body)
                    clean_body = re.sub(r'!\[\[.*?\]\]', '', clean_body)
                    clean_body = re.sub(r'!\[.*?\]\(.*?\)', '', clean_body)
                    clean_body = re.sub(r'\[⬆\s+回到目錄導覽\].*', '', clean_body).strip()
                    topic = clean_body if clean_body else f'{sname} 第 {q_num} 題'
                        
                    tags = [sname.split('（')[0]]
                    if any(w in q_body for w in ['定理', '定律', '諾頓', '戴維寧']):
                        tags.append('等效定理')
                    if any(w in q_body for w in ['矩陣', '特徵值', '對角化', 'SVD', '零空間']):
                        tags.append('線性代數')
                    if any(w in q_body for w in ['功率', '相量', '阻抗', '三相', '負載', '功角']):
                        tags.append('交流相量')
                    if any(w in q_body for w in ['故障', '短路', '接地', '保護']):
                        tags.append('故障分析')
                    if any(w in q_body for w in ['暫態', 'ODE', '微分', '拉氏', 'Fourier', '穩定度']):
                        tags.append('暫態穩定')
                    if any(w in q_body for w in ['變壓器', '感應', '電動機', '同步', '磁路', '轉矩']):
                        tags.append('電機機械')
                    if any(w in q_body for w in ['諧波', '電容', '契約', '需量', '配電', '壓降']):
                        tags.append('配電設計')
                    if any(w in q_body for w in ['Buck', 'Boost', '轉換器', 'PWM', 'BJT', 'MOSFET', '變流器']):
                        tags.append('電力電子')
                    
                    qid = f'EE-{yr}-{sid}-{q_num}'
                    
                    pdf_file = ''
                    if os.path.exists(pdf_dir):
                        for pf in os.listdir(pdf_dir):
                            if pf.startswith(f'{yr}年') and pf.endswith('.pdf'):
                                pdf_file = f'{pdf_dir}/{pf}'
                                break
                    if not pdf_file:
                        pdf_file = f'{pdf_dir}/{yr}年_電機工程技師.pdf'
                        
                    has_dedicated = False
                    if qid in dedicated_notes:
                        solLink = dedicated_notes[qid]
                        has_dedicated = True
                        v_status = 'verified'
                    else:
                        solLink = f'{md_file}#{yr}年'
                        v_status = 'in_progress'
                        
                    difficulty = estimate_difficulty(sid, topic, q_body)
                    ftags = extract_formula_tags(topic, q_body)
                    
                    all_questions.append([
                        qid, sid, yr, q_num, topic, list(set(tags)), solLink, pdf_file,
                        difficulty, v_status, ftags, has_dedicated
                    ])
                    count_for_subj += 1
                    
    subject_counts[sid] = count_for_subj

# Sort questions by year descending, then subject id ascending, then question number ascending
all_questions.sort(key=lambda q: (-q[2], q[1], q[3]))

# Seven Layers with 100% verified existing files
sevenLayers = [
    { "id": "L1", "title": "歷屆考題總目錄", "desc": "依考科分類（電路、電子、工數、機械、電力、配電）總攬 11 年試題", "link": "依考科分類/01_電路學.md" },
    { "id": "L2", "title": "歷年考題全真索引", "desc": "104 ~ 114 年 11 個年度 66 份考卷時間、代號與 PDF 下載", "link": "依年度分類/114年/README.md" },
    { "id": "L3", "title": "核心考點觀念庫", "desc": "6 大考科高頻公式彙整、SOP 解題標準程序與理論推導", "link": "🧠 核心考點知識庫/README.md" },
    { "id": "L4", "title": "6 大考科考點頻率統計", "desc": "104~114 年 330 道大題考點頻率雷達、佔比統計與 80/20 命中率分析", "link": "🧠 核心考點知識庫/📊_電機工程技師_6大考科11年高頻考點統計與命中率分析.md" },
    { "id": "L5", "title": "E-MORE fx-127 計算機寶典", "desc": "相量直角/極座標一鍵互轉、免開根號求幅值與實體按鍵秒殺指引", "link": "📝 個人題解與錯題本/🧮_EMORE_fx127_國考計算機電類相量與複數秒殺操作寶典.md" },
    { "id": "L6", "title": "看到題目發呆破局指南", "desc": "考場拿到題目 5 秒內精準識別題型、決定解題步驟與公式 SOP", "link": "📝 個人題解與錯題本/💡_電機技師看到題目發呆破局指南與秒解SOP.md" },
    { "id": "L7", "title": "職涯與資產總藍圖", "desc": "重工業工程設計躍升 ➔ 技師優利融資 ➔ 30 歲突破 300 萬資產終極藍圖", "link": "💼 個人職涯發展與國際戰略/🌟_電機工程師職涯躍升與資產質押複利_終極整合總藍圖.md" }
]

subject_meta_list = []
for sid, sname, icon, color, _, _ in subjects:
    subject_meta_list.append({
        "id": sid,
        "name": sname,
        "icon": icon,
        "color": color,
        "count": subject_counts.get(sid, 0)
    })

db_content = f"""// ⚡ 電機工程技師 歷屆試題與詳解知識庫 — 核心資料庫 (104 ~ 114 年)
// 全自動編譯：收錄 6 大考科 × 11 個年度共 {len(all_questions)} 道題目

const DB_DATA = {{
  meta: {{
    title: "⚡ 電機工程技師 歷屆試題與知識庫儀表板 (104–114 年)",
    years: [114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104],
    totalExams: 66,
    totalQuestions: {len(all_questions)},
    subjects: {json.dumps(subject_meta_list, ensure_ascii=False, indent=6)}
  }},

  questions: {json.dumps(all_questions, ensure_ascii=False, indent=2)},

  sevenLayers: {json.dumps(sevenLayers, ensure_ascii=False, indent=2)}
}};

console.log("Loaded complete exam database with", DB_DATA.questions.length, "question records.");
"""

with open('dashboard-data.js', 'w', encoding='utf-8') as f:
    f.write(db_content)

print(f'✅ dashboard-data.js generated with {len(all_questions)} questions.')

# Now compile solutions-bundle.js with all clean Markdown files and Image Mapping
bundle = {}
img_map = {}

for root, dirs, files in os.walk('.'):
    if '.git' in root or '.agents' in root or 'node_modules' in root or '.system_generated' in root:
        continue
    for f in files:
        rel_path = os.path.relpath(os.path.join(root, f), '.').replace(os.sep, '/')
        if f.endswith('.md'):
            with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fp:
                bundle[rel_path] = fp.read()
        elif f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp')):
            import urllib.parse
            img_map[f] = rel_path
            img_map[rel_path] = rel_path
            img_map['./' + rel_path] = rel_path
            img_map[urllib.parse.quote(f)] = rel_path
            img_map[urllib.parse.quote(rel_path)] = rel_path
            # Also map any subpath after 'images/'
            if 'images/' in rel_path:
                sub_img = rel_path.split('images/')[-1]
                img_map[sub_img] = rel_path
                img_map['./images/' + sub_img] = rel_path
                img_map['images/' + sub_img] = rel_path

bundle_js = 'const BUNDLED_MD = ' + json.dumps(bundle, ensure_ascii=False) + ';\n'
bundle_js += 'const IMAGE_MAP = ' + json.dumps(img_map, ensure_ascii=False) + ';\n'

with open('solutions-bundle.js', 'w', encoding='utf-8') as out:
    out.write(bundle_js)

print(f'✅ solutions-bundle.js refreshed with {len(bundle)} markdown files and {len(img_map)} image mappings.')
