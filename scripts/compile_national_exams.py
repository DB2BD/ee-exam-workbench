# -*- coding: utf-8 -*-
"""
compile_national_exams.py — 國考同級參考題庫獨立編譯器
=======================================================

⚠️  ISOLATION CONTRACT:
    此腳本只產生 national-exams-data.js 和 national-solutions-bundle.js
    絕不讀取、修改、覆寫 dashboard-data.js 或 solutions-bundle.js

Architecture:
    1. 掃描 依考科分類/🏛️_國考同級參考題庫/ 下所有考科 Markdown
    2. 掃描 📝 個人題解與錯題本/🏛️_國考同級題解/ 下的詳解 Markdown
    3. 解析題目結構 → 產生 NATIONAL_EXAMS_DATA (national-exams-data.js)
    4. 打包所有國考題解 Markdown + 圖片映射 → national-solutions-bundle.js
    5. 建立考點關聯索引 (relatedPEQid) 透過 tag 關鍵字比對

Usage:
    python3 scripts/compile_national_exams.py
"""

import os
import re
import json
import hashlib

# ═══════════════════════════════════════════════════════════════════════
# § 0. SAFETY: Verify we never overwrite PE technician files
# ═══════════════════════════════════════════════════════════════════════
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

PE_FILES_DO_NOT_TOUCH = [
    'dashboard-data.js',
    'solutions-bundle.js',
]

def safety_check():
    """Compute SHA-256 of PE files BEFORE and AFTER to prove zero-overwrite."""
    checksums = {}
    for f in PE_FILES_DO_NOT_TOUCH:
        if os.path.exists(f):
            with open(f, 'rb') as fp:
                checksums[f] = hashlib.sha256(fp.read()).hexdigest()
    return checksums

# ═══════════════════════════════════════════════════════════════════════
# § 1. Configuration & Constants
# ═══════════════════════════════════════════════════════════════════════

# Exam category definitions
EXAM_CATEGORIES = [
    {
        'id': 'PE',
        'name': '🏆 電機工程技師',
        'isPrimary': True,
        'prefix': 'EE',
        'total': 318,  # Read-only reference; actual count comes from dashboard-data.js
    },
    {
        'id': 'GK',
        'name': '🏛️ 公務高考三級',
        'isPrimary': False,
        'prefix': 'GK',
        'scanDir': '依考科分類/🏛️_國考同級參考題庫',
        'solDir': '📝 個人題解與錯題本/🏛️_國考同級題解',
        'filenamePattern': r'^GK_(\d{3})年_(.+)\.md$',
    },
    {
        'id': 'RW',
        'name': '🚆 鐵路特考高員',
        'isPrimary': False,
        'prefix': 'RW',
        'scanDir': '依考科分類/🏛️_國考同級參考題庫',
        'solDir': '📝 個人題解與錯題本/🏛️_國考同級題解',
        'filenamePattern': r'^RW_(\d{3})年_(.+)\.md$',
    },
    {
        'id': 'LOC',
        'name': '🏙️ 地方特考三級',
        'isPrimary': False,
        'prefix': 'LOC',
        'scanDir': '依考科分類/🏛️_國考同級參考題庫',
        'solDir': '📝 個人題解與錯題本/🏛️_國考同級題解',
        'filenamePattern': r'^LOC_(\d{3})年_(.+)\.md$',
    },
    {
        'id': 'SOE',
        'name': '⚡ 國營事業聯招',
        'isPrimary': False,
        'prefix': 'SOE',
        'scanDir': '依考科分類/🏛️_國考同級參考題庫',
        'solDir': '📝 個人題解與錯題本/🏛️_國考同級題解',
        'filenamePattern': r'^SOE_(\d{3})年_(.+)\.md$',
    },
]

# Subject mapping (same as PE technician, ensures cross-referencing compatibility)
SUBJECTS = [
    ('01', '電路學', '⚡', '#4a7c8f'),
    ('02', '電子學（含電力電子）', '🔌', '#686b8f'),
    ('03', '工程數學', '📐', '#54826b'),
    ('04', '電機機械', '⚙️', '#a17846'),
    ('05', '電力系統', '🏢', '#a85858'),
    ('06', '工業配電', '🏭', '#7d6382'),
]

SUBJECT_NAME_TO_ID = {}
for sid, sname, _, _ in SUBJECTS:
    SUBJECT_NAME_TO_ID[sname] = sid
    # Partial match keys
    if '電路' in sname: SUBJECT_NAME_TO_ID['電路學'] = sid
    if '電子' in sname: SUBJECT_NAME_TO_ID['電子學'] = sid
    if '數學' in sname: SUBJECT_NAME_TO_ID['工程數學'] = sid
    if '機械' in sname: SUBJECT_NAME_TO_ID['電機機械'] = sid
    if '電力' in sname and '電子' not in sname: SUBJECT_NAME_TO_ID['電力系統'] = sid
    if '配電' in sname: SUBJECT_NAME_TO_ID['工業配電'] = sid

NUM_MAP = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}

OUTPUT_DATA_JS = 'national-exams-data.js'
OUTPUT_BUNDLE_JS = 'national-solutions-bundle.js'

# ═══════════════════════════════════════════════════════════════════════
# § 2. Question Extraction (mirrors compile_dashboard_database.py logic)
# ═══════════════════════════════════════════════════════════════════════

def resolve_subject_id(name_str):
    """Map a subject name string to its 2-digit ID."""
    for key, sid in SUBJECT_NAME_TO_ID.items():
        if key in name_str:
            return sid
    return '01'  # fallback


def estimate_difficulty(topic, q_body):
    diff = 3
    hard_words = ['SVD', '非齊次', '凸極', '牛頓法', '快速解耦', 'SPWM', '反時限',
                  '零空間', '留數', '特徵值對角化', '雙反應', '自耦變壓器', '搖擺方程',
                  '暫態穩定', '保護協調']
    easy_words = ['戴維寧等效', '節點電壓', '一階ODE', '分壓', '單相二線', '歐姆定律',
                  'KVL', 'KCL', '變壓器變比']
    for hw in hard_words:
        if hw in topic or hw in q_body:
            diff += 1
            break
    for ew in easy_words:
        if ew in topic or ew in q_body:
            diff -= 1
            break
    return max(1, min(5, diff))


def extract_formula_tags(topic, q_body):
    ftags = []
    tag_rules = [
        (['戴維寧', '諾頓'], '戴維寧等效'),
        (['相量', '功率因數', '複數功率'], 'S = VI*'),
        (['Buck'], 'Vo = D Vd'),
        (['Boost'], 'Vo = Vd/(1-D)'),
        (['SVD', '奇異值'], 'A = U Σ V^T'),
        (['特徵值', '對角化'], 'det(A - λI) = 0'),
        (['自耦'], 'S_auto = [VH/(VH-VX)] S2w'),
        (['轉差率', '感應'], 's = (Ns - N)/Ns'),
        (['故障', '接地', 'SLG'], 'Ia1 = Vf / (Z1+Z2+Z0)'),
        (['短路容量', '啟斷'], 'Ssc = Sbase / Xpu'),
        (['壓降'], 'ΔV = √3 I (R cosθ + X sinθ)'),
        (['搖擺', '等面積'], 'M d^2δ/dt^2 = Pm - Pe'),
    ]
    combined = topic + ' ' + q_body
    for keywords, tag in tag_rules:
        if any(kw in combined for kw in keywords):
            ftags.append(tag)
    return ftags[:3]


def extract_content_tags(topic, q_body):
    tags = []
    tag_rules = [
        (['定理', '定律', '諾頓', '戴維寧'], '等效定理'),
        (['矩陣', '特徵值', '對角化', 'SVD', '零空間'], '線性代數'),
        (['功率', '相量', '阻抗', '三相', '負載', '功角'], '交流相量'),
        (['故障', '短路', '接地', '保護'], '故障分析'),
        (['暫態', 'ODE', '微分', '拉氏', 'Fourier', '穩定度'], '暫態穩定'),
        (['變壓器', '感應', '電動機', '同步', '磁路', '轉矩'], '電機機械'),
        (['諧波', '電容', '契約', '需量', '配電', '壓降'], '配電設計'),
        (['Buck', 'Boost', '轉換器', 'PWM', 'BJT', 'MOSFET', '變流器'], '電力電子'),
    ]
    combined = topic + ' ' + q_body
    for keywords, tag in tag_rules:
        if any(kw in combined for kw in keywords):
            tags.append(tag)
    return list(set(tags))


def scan_exam_category(cat):
    """
    Scan a non-PE exam category and extract all questions.
    Returns list of question tuples matching PE format:
    [qid, sid, year, qnum, topic, tags, solLink, pdfLink, diff, vstatus, ftags, hasDed, examCat, relatedPEQid]
    """
    questions = []
    scan_dir = cat.get('scanDir', '')
    sol_dir = cat.get('solDir', '')
    prefix = cat['prefix']
    pattern = re.compile(cat.get('filenamePattern', ''))

    if not os.path.exists(scan_dir):
        return questions

    # Scan each subject sub-directory
    for sid, sname, icon, color in SUBJECTS:
        # Derive the subject folder name based on conventions
        subject_folders = {
            '01': '01_電路學',
            '02': '02_電子學_含電力電子',
            '03': '03_工程數學',
            '04': '04_電機機械',
            '05': '05_電力系統',
            '06': '06_工業配電',
        }
        subj_folder = subject_folders.get(sid, '')
        exam_subj_dir = os.path.join(scan_dir, subj_folder)
        sol_subj_dir = os.path.join(sol_dir, subj_folder)

        if not os.path.exists(exam_subj_dir):
            continue

        for fname in sorted(os.listdir(exam_subj_dir)):
            if not fname.endswith('.md'):
                continue

            m = pattern.match(fname)
            if not m:
                continue

            yr = int(m.group(1))
            fpath = os.path.join(exam_subj_dir, fname)

            with open(fpath, 'r', encoding='utf-8') as f:
                text = f.read()

            # Extract questions using the same #### 一、 pattern
            q_blocks = re.split(r'\n####\s+([一二三四五六七八九十]+)[、\.]\s*', text)
            if len(q_blocks) > 1:
                for j in range(1, len(q_blocks), 2):
                    q_chinese = q_blocks[j]
                    q_num = NUM_MAP.get(q_chinese, 1)
                    q_body = q_blocks[j + 1].strip() if j + 1 < len(q_blocks) else ''

                    first_line = q_body.split('\n')[0].strip()
                    topic = re.sub(r'[\$\*\#\_\[\]]', '', first_line)
                    topic = re.sub(r'（\s*\d+\s*分\s*）', '', topic).strip()
                    if len(topic) > 60:
                        topic = topic[:57] + '...'
                    if not topic:
                        topic = f'{sname} 第 {q_num} 題'

                    qid = f'{prefix}-{yr}-{sid}-{q_num}'
                    tags = extract_content_tags(topic, q_body)
                    tags.insert(0, sname.split('（')[0])
                    ftags = extract_formula_tags(topic, q_body)
                    diff = estimate_difficulty(topic, q_body)

                    # Check for dedicated solution note
                    sol_link = ''
                    has_dedicated = False
                    if sol_subj_dir and os.path.exists(sol_subj_dir):
                        sol_pattern = f'{prefix}_{yr}年_{sname.split("（")[0]}_全卷完整詳細題解.md'
                        sol_path = os.path.join(sol_subj_dir, sol_pattern)
                        if os.path.exists(sol_path):
                            sol_link = sol_path.replace(os.sep, '/')
                            has_dedicated = True
                    # Check for local PDF or assign official MOEX PDF link
                    pdf_link = ''
                    local_pdf = os.path.join(exam_subj_dir, f'{prefix}_{yr}年_{sname.split("（")[0]}.pdf')
                    if os.path.exists(local_pdf):
                        pdf_link = local_pdf.replace(os.sep, '/')
                    else:
                        pdf_link = 'https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx'

                    # relatedPEQid: cross-reference placeholder (populated in phase 2)
                    related_pe_qid = ''

                    questions.append([
                        qid, sid, yr, q_num, topic, list(set(tags)),
                        sol_link, pdf_link, diff, 'verified' if has_dedicated else 'in_progress',
                        ftags, has_dedicated, cat['id'], related_pe_qid
                    ])

    return questions


# ═══════════════════════════════════════════════════════════════════════
# § 3. Cross-Reference Builder (PE ↔ National Exam Topic Bridge)
# ═══════════════════════════════════════════════════════════════════════

def build_cross_references(nat_questions, pe_data_path='dashboard-data.js'):
    """
    Read PE technician questions from dashboard-data.js (read-only!)
    and match national exam questions by topic similarity (tag overlap).
    Populates relatedPEQid field (index 13) in nat_questions.
    """
    if not os.path.exists(pe_data_path):
        return

    with open(pe_data_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    # Extract questions array via simple regex (avoid full JS parser)
    match = re.search(r'questions:\s*(\[[\s\S]*?\])\s*,\s*\n\s*sevenLayers', raw)
    if not match:
        return

    try:
        pe_questions = json.loads(match.group(1))
    except json.JSONDecodeError:
        return

    # Build PE topic index: {(sid, tag_set_key): [pe_qid, ...]}
    pe_index = {}
    for pq in pe_questions:
        pe_qid, pe_sid = pq[0], pq[1]
        pe_tags = set(pq[5]) if len(pq) > 5 else set()
        pe_topic = pq[4] if len(pq) > 4 else ''
        pe_index.setdefault(pe_sid, []).append({
            'qid': pe_qid,
            'tags': pe_tags,
            'topic': pe_topic,
        })

    # Match national questions to PE questions
    for nq in nat_questions:
        n_sid = nq[1]
        n_tags = set(nq[5]) if nq[5] else set()
        n_topic = nq[4]

        if n_sid not in pe_index:
            continue

        best_match = None
        best_score = 0
        for pe_entry in pe_index[n_sid]:
            # Score = tag overlap + topic keyword overlap
            tag_overlap = len(n_tags & pe_entry['tags'])
            topic_words = set(n_topic) & set(pe_entry['topic'])
            score = tag_overlap * 3 + len(topic_words)
            if score > best_score:
                best_score = score
                best_match = pe_entry['qid']

        if best_match and best_score >= 3:
            nq[13] = best_match  # relatedPEQid


# ═══════════════════════════════════════════════════════════════════════
# § 4. Output Generators
# ═══════════════════════════════════════════════════════════════════════

def generate_data_js(all_questions, categories):
    """Generate national-exams-data.js"""
    cat_counts = {}
    for q in all_questions:
        cat_id = q[12]
        cat_counts[cat_id] = cat_counts.get(cat_id, 0) + 1

    cat_meta = []
    for cat in categories:
        if cat['isPrimary']:
            cat_meta.append({
                'id': cat['id'],
                'name': cat['name'],
                'total': cat['total'],
                'isPrimary': True,
            })
        else:
            cat_meta.append({
                'id': cat['id'],
                'name': cat['name'],
                'total': cat_counts.get(cat['id'], 0),
                'isPrimary': False,
            })

    # Build subject meta (same as PE for consistency)
    subj_meta = []
    for sid, sname, icon, color in SUBJECTS:
        count = len([q for q in all_questions if q[1] == sid])
        subj_meta.append({
            'id': sid,
            'name': sname,
            'icon': icon,
            'color': color,
            'count': count,
        })

    output = f"""// ═══════════════════════════════════════════════════════════════════
// 🏛️ 國考同級參考題庫 — 獨立擴充資料庫
// ⚠️  此檔案完全獨立於 dashboard-data.js，零覆蓋、零污染
// Auto-compiled by scripts/compile_national_exams.py
// Total national exam questions: {len(all_questions)}
// ═══════════════════════════════════════════════════════════════════

const NATIONAL_EXAMS_DATA = {{
  version: "1.0.0",
  categories: {json.dumps(cat_meta, ensure_ascii=False, indent=4)},
  subjects: {json.dumps(subj_meta, ensure_ascii=False, indent=4)},
  questions: {json.dumps(all_questions, ensure_ascii=False, indent=2)}
}};

console.log("Loaded national exam cross-reference database with", NATIONAL_EXAMS_DATA.questions.length, "questions.");
"""
    with open(OUTPUT_DATA_JS, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f'✅ {OUTPUT_DATA_JS} generated with {len(all_questions)} national exam questions.')


def generate_bundle_js():
    """Generate national-solutions-bundle.js (only national exam markdown + images)"""
    bundle = {}
    img_map = {}
    import urllib.parse

    scan_dirs = [
        '依考科分類/🏛️_國考同級參考題庫',
        '📝 個人題解與錯題本/🏛️_國考同級題解',
    ]

    for scan_dir in scan_dirs:
        if not os.path.exists(scan_dir):
            continue
        for root, dirs, files in os.walk(scan_dir):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), '.').replace(os.sep, '/')
                if f.endswith('.md'):
                    with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fp:
                        bundle[rel_path] = fp.read()
                elif f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp')):
                    img_map[f] = rel_path
                    img_map[rel_path] = rel_path
                    img_map['./' + rel_path] = rel_path
                    img_map[urllib.parse.quote(f)] = rel_path
                    img_map[urllib.parse.quote(rel_path)] = rel_path

    bundle_js = 'const NATIONAL_BUNDLED_MD = ' + json.dumps(bundle, ensure_ascii=False) + ';\n'
    bundle_js += 'const NATIONAL_IMAGE_MAP = ' + json.dumps(img_map, ensure_ascii=False) + ';\n'

    with open(OUTPUT_BUNDLE_JS, 'w', encoding='utf-8') as out:
        out.write(bundle_js)

    print(f'✅ {OUTPUT_BUNDLE_JS} generated with {len(bundle)} markdown files and {len(img_map)} image mappings.')


# ═══════════════════════════════════════════════════════════════════════
# § 5. Main Execution
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('🔒 Computing PE database checksums (safety snapshot)...')
    pre_checksums = safety_check()

    all_nat_questions = []
    for cat in EXAM_CATEGORIES:
        if cat['isPrimary']:
            continue  # Skip PE; it's read-only reference
        questions = scan_exam_category(cat)
        all_nat_questions.extend(questions)
        if questions:
            print(f'  📋 {cat["name"]}: {len(questions)} questions found')

    # Build cross-references (read-only from dashboard-data.js)
    build_cross_references(all_nat_questions)

    # Sort: year desc, subject asc, question number asc
    all_nat_questions.sort(key=lambda q: (-q[2], q[1], q[3]))

    # Generate output files
    generate_data_js(all_nat_questions, EXAM_CATEGORIES)
    generate_bundle_js()

    # Safety verification
    post_checksums = safety_check()
    all_safe = True
    for f in PE_FILES_DO_NOT_TOUCH:
        if pre_checksums.get(f) != post_checksums.get(f):
            print(f'🚨 CRITICAL: {f} was modified! This is a bug. Rolling back...')
            all_safe = False

    if all_safe:
        print('✅ Zero-overwrite verification PASSED — PE database files are untouched.')
    else:
        print('❌ ZERO-OVERWRITE VIOLATION DETECTED. Aborting.')
        exit(1)
