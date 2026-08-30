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

# Optional question-level crop manifest.  The renderer treats this as an
# override for legacy page embeds (e.g. *_p1.png), so a solution can never
# silently fall back to the whole exam page once a crop is available.
QUESTION_CROP_MAP = {}
ENGINEERING_MATH_AUDIT_STATUS = {}
# Official crop corrections for legacy annual notes whose question statement
# was copied from a different year/question number.
ENGINEERING_MATH_TOPIC_OVERRIDES = {
    'EE-114-03-5': (
        '假設矩陣 A = [[0, -1, 0, 1], [0, 1, -1, 0]] 與 b = [0, 1]^T；'
        '求 Ax=b 的完整解與矩陣 A 的零空間 N(A)。'
    ),
}
PE_CROP_MANIFEST = 'data/pe-question-crops.json'
if os.path.exists(PE_CROP_MANIFEST):
    try:
        with open(PE_CROP_MANIFEST, 'r', encoding='utf-8') as f:
            crop_data = json.load(f)
        if isinstance(crop_data, dict) and isinstance(crop_data.get('questions'), dict):
            QUESTION_CROP_MAP.update(crop_data['questions'])
        elif isinstance(crop_data, dict) and isinstance(crop_data.get('entries'), list):
            for entry in crop_data['entries']:
                if not isinstance(entry, dict):
                    continue
                qid = entry.get('question_id') or entry.get('qid') or entry.get('id')
                crop = entry.get('question_crop') or entry.get('crop')
                if qid and crop:
                    QUESTION_CROP_MAP[str(qid)] = crop
                # PE crop manifests retain a stable provenance id and the
                # application id separately.  Prefer the app id as an alias
                # so legacy EE-* records resolve to their own crop even when
                # the source PDF has a different question count.
                app_qid = entry.get('app_question_id') or entry.get('app_qid')
                if app_qid and crop:
                    QUESTION_CROP_MAP[str(app_qid)] = crop
                for question in entry.get('questions', []) if isinstance(entry.get('questions'), list) else []:
                    if not isinstance(question, dict):
                        continue
                    qcrop = question.get('question_crop') or question.get('crop')
                    source_qid = question.get('question_id') or question.get('qid') or question.get('id')
                    application_qid = question.get('app_question_id') or question.get('app_qid')
                    if qcrop and source_qid:
                        QUESTION_CROP_MAP[str(source_qid)] = qcrop
                    if qcrop and application_qid:
                        QUESTION_CROP_MAP[str(application_qid)] = qcrop
        elif isinstance(crop_data, dict):
            QUESTION_CROP_MAP.update({str(k): v for k, v in crop_data.items() if isinstance(v, str)})
    except (OSError, ValueError, TypeError) as exc:
        print(f'⚠️ PE crop manifest ignored: {exc}')

# Engineering-math solutions are audited independently from the PE question
# compiler.  Never advertise a legacy/template solution as verified when the
# audit manifest has evidence to the contrary.
MATH_AUDIT_MANIFEST = 'data/engineering-math-audit.json'
if os.path.exists(MATH_AUDIT_MANIFEST):
    try:
        with open(MATH_AUDIT_MANIFEST, 'r', encoding='utf-8') as f:
            audit_data = json.load(f)
        for item in audit_data.get('entries', []):
            if isinstance(item, dict) and item.get('qid') and item.get('audit_status'):
                ENGINEERING_MATH_AUDIT_STATUS[str(item['qid'])] = str(item['audit_status'])
    except (OSError, ValueError, TypeError) as exc:
        print(f'⚠️ Engineering-math audit manifest ignored: {exc}')

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

# Canonical, question-level notes take precedence over legacy annual templates.
# This keeps the original files available while routing the UI to a verified
# per-question derivation as soon as one exists.
canonical_dir = '📝 個人題解與錯題本/03_工程數學/canonical'
if os.path.isdir(canonical_dir):
    for f in os.listdir(canonical_dir):
        match = re.match(r'(EE-\d{3}-03-\d+)\.md$', f)
        if match:
            dedicated_notes[match.group(1)] = os.path.join(canonical_dir, f).replace('\\', '/')

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
                    if qid in ENGINEERING_MATH_TOPIC_OVERRIDES:
                        topic = ENGINEERING_MATH_TOPIC_OVERRIDES[qid]
                    
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
                        v_status = ENGINEERING_MATH_AUDIT_STATUS.get(
                            qid, 'verified' if sid != '03' else 'pending'
                        )
                    else:
                        solLink = f'{md_file}#{yr}年'
                        v_status = 'in_progress'
                        
                    difficulty = estimate_difficulty(sid, topic, q_body)
                    ftags = extract_formula_tags(topic, q_body)
                    
                    all_questions.append([
                        qid, sid, yr, q_num, topic, sorted(set(tags)), solLink, pdf_file,
                        difficulty, v_status, ftags, has_dedicated
                    ])
                    count_for_subj += 1
                    
    subject_counts[sid] = count_for_subj

# Sort questions by year descending, then subject id ascending, then question number ascending
all_questions.sort(key=lambda q: (-q[2], q[1], q[3]))

# Seven-layer score-oriented study path. Each layer is actionable in the UI.
sevenLayers = [
    { "id": "L1", "title": "題型辨識與範圍盤點", "desc": "先用歷屆題建立出題輪廓，避免把時間耗在低命中率內容。", "objective": "建立考科與題型地圖", "action": "all" },
    { "id": "L2", "title": "核心公式與單位", "desc": "先能在無提示下寫出公式、符號意義與單位，再進入計算。", "objective": "降低公式與單位失分", "action": "formula" },
    { "id": "L3", "title": "標準題型 SOP", "desc": "使用完整推導題練習固定解題順序，建立可重複的得分步驟。", "objective": "把會觀念轉成可拿分步驟", "action": "dedicated" },
    { "id": "L4", "title": "錯題與高難陷阱", "desc": "優先處理曾答錯與高難度題，記錄錯因、判斷點及下一次的防錯動作。", "objective": "直接降低重複錯誤", "action": "review" },
    { "id": "L5", "title": "跨章節整合題", "desc": "練習同時使用多個考點的綜合題，補足從單一公式到完整推導的斷層。", "objective": "提升大題中後段得分率", "action": "top10" },
    { "id": "L6", "title": "到期複習閉環", "desc": "依 SM-2 到期清單複習；不追求全部重讀，只處理目前最容易遺忘的題目。", "objective": "把短期記憶轉成穩定回憶", "action": "due" },
    { "id": "L7", "title": "限時模考與考場輸出", "desc": "以 120 分鐘整卷演練驗證速度、取捨與書寫完整度，將知識轉成考場分數。", "objective": "在時間限制下穩定拿分", "action": "mock" }
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

// qid -> question-level official crop (when generated by the crop pipeline).
// Kept separate from the legacy 12-column PE tuples for compatibility.
const QUESTION_CROP_MAP = {json.dumps(QUESTION_CROP_MAP, ensure_ascii=False, indent=2)};

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
                img_map[urllib.parse.quote(sub_img)] = rel_path
                img_map[urllib.parse.quote('images/' + sub_img)] = rel_path

bundle_js = 'const BUNDLED_MD = ' + json.dumps(bundle, ensure_ascii=False) + ';\n'
bundle_js += 'const IMAGE_MAP = ' + json.dumps(img_map, ensure_ascii=False) + ';\n'

with open('solutions-bundle.js', 'w', encoding='utf-8') as out:
    out.write(bundle_js)

print(f'✅ solutions-bundle.js refreshed with {len(bundle)} markdown files and {len(img_map)} image mappings.')
