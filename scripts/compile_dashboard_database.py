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
PE_SOLUTION_AUDIT_STATUS = {}
# Actionable metadata for questions that deliberately remain outside the
# ``verified`` state.  Keep this separate from the positional question tuples
# so existing consumers remain compatible while the UI can explain blockers.
SOLUTION_REVIEW_METADATA = {}
# Canonical chapter evidence is compiled into a question-level map.  The
# review UI consumes this map before the legacy keyword classifier so a
# generic token (e.g.「功率」or「電晶體」) cannot move a question into a
# neighbouring textbook chapter.
QUESTION_TAXONOMY_MAP = {}
CANONICAL_TOPIC_METADATA = {}
# Official crop corrections for legacy annual notes whose question statement
# was copied from a different year/question number.
ENGINEERING_MATH_TOPIC_OVERRIDES = {
    'EE-108-03-5': '複變函數線積分：被積函數 1/(z²−1)，圓心 (±1,0)、半徑 1 的圓周。',
    'EE-109-03-3': '聯合機率密度：矩形區域 0≤x≤5、0≤y≤3，求 P(X>Y)。',
    'EE-110-03-3': '傅立葉級數：f(x)=x−x²（−π<x<π）的 2π 週期延拓。',
    'EE-111-03-3': '複變留數定理：C 為 |z|=2.5 的逆時針圓周，計算兩個留數積分。',
    'EE-114-03-5': (
        '假設矩陣 A = [[0, -1, 0, 1], [0, 1, -1, 0]] 與 b = [0, 1]^T；'
        '求 Ax=b 的完整解與矩陣 A 的零空間 N(A)。'
    ),
}
PE_TOPIC_OVERRIDES = {
    'EE-109-02-1': '如圖一 BJT 開關電路，已知 R_C=11 Ω、V_CC=200 V、V_B=10 V、V_CE(sat)=1.0 V、V_BE(sat)=1.5 V、β_F∈[8,40]。求 ODF=6 時的 R_B 與電晶體總功率損耗 P_T。（25 分）',
    'EE-109-02-2': '如圖二理想 Boost 轉換器，V_s=15 V、V_o=30 V、I_o=3 A、f=25 kHz、L=100 μH、C=200 μF。求導通率 D、電感漣波與峰值電流、電容漣波及臨界 L_c、C_c。（25 分）',
    'EE-109-02-3': '如圖三返馳式（Flyback）轉換器，N_p/N_s=4、R_L=0.8 Ω、V_o=24 V、V_d=0.7 V、V_t=1.2 V、f=1.5 kHz、D=0.75。求 Q 的平均／峰值電流、L_p 與效率 η。（25 分）',
    'EE-109-02-4': '增強型 n 通道 NMOS 於 V_GS=V_DS=12 V 時 I_D=6 mA，於 V_GS=V_DS=8 V 時 I_D=1.5 mA。求臨界電壓 V_t 與製程參數 β。（25 分）',
}
# A few OCR-heavy annual sections contain terms from neighbouring chapters
# (for example「功率」in a BJT loss question).  Keep their textbook chapter
# tags deterministic at the question boundary so the review DAG does not let
# generic words outweigh the device/converter keyword.
QUESTION_TAG_OVERRIDES = {
    'EE-109-02-1': ['電子學', 'BJT 偏壓'],
    'EE-109-02-2': ['電子學', '電力電子', 'Boost 轉換器'],
    'EE-109-02-3': ['電子學', '電力電子', 'Flyback 轉換器'],
    'EE-109-02-4': ['電子學', 'MOSFET 偏壓'],
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

PE_AUDIT_MANIFEST = 'data/pe-solution-audit.json'
if os.path.exists(PE_AUDIT_MANIFEST):
    try:
        with open(PE_AUDIT_MANIFEST, 'r', encoding='utf-8') as f:
            audit_data = json.load(f)
        for item in audit_data.get('entries', []):
            if isinstance(item, dict) and item.get('qid') and item.get('audit_status'):
                PE_SOLUTION_AUDIT_STATUS[str(item['qid'])] = str(item['audit_status'])
    except (OSError, ValueError, TypeError) as exc:
        print(f'⚠️ PE solution audit manifest ignored: {exc}')

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
def parse_canonical_note(path):
    """Return the small amount of chapter evidence needed by the taxonomy map."""
    try:
        with open(path, 'r', encoding='utf-8') as fp:
            raw = fp.read()
    except OSError:
        return None
    fields = {}
    if raw.startswith('---'):
        frontmatter = raw.split('---', 2)[1]
        for line in frontmatter.splitlines():
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            fields[key.strip()] = value.strip().strip("'\"")
    title = ''
    for line in raw.splitlines():
        if line.startswith('# '):
            title = line[2:].strip()
            break
    return {'chapter': fields.get('chapter', ''), 'title': title}


for subject_dir in (
    '01_電路學', '02_電子學_含電力電子', '03_工程數學',
    '04_電機機械', '05_電力系統', '06_工業配電',
):
    canonical_dir = os.path.join('📝 個人題解與錯題本', subject_dir, 'canonical')
    if not os.path.isdir(canonical_dir):
        continue
    for f in os.listdir(canonical_dir):
        match = re.match(r'(EE-\d{3}-\d{2}-\d+)\.md$', f)
        if match:
            qid = match.group(1)
            path = os.path.join(canonical_dir, f)
            dedicated_notes[qid] = path.replace('\\', '/')
            evidence = parse_canonical_note(path)
            if evidence:
                CANONICAL_TOPIC_METADATA[qid] = evidence


# A canonical note may use a descriptive chapter name rather than the exact
# DAG id.  These deterministic rules resolve the descriptive name to the
# closest textbook chapter.  Question-level exceptions below cover notes with
# missing frontmatter or a genuinely ambiguous multi-topic title.
CANONICAL_CHAPTER_RULES = {
    '01': [
        ('ct-max-power', ('最大功率',)),
        ('ct-thevenin-norton', ('戴維寧', '諾頓', '等效定理')),
        ('ct-two-port', ('雙埠', '二埠')),
        ('ct-mutual-inductance', ('互感', '耦合', '同名端')),
        ('ct-laplace-circuit', ('拉氏', '拉普拉斯', 's 域', 's域')),
        ('ct-second-order-rlc', ('二階', 'RLC', '帶通', '帶拒', '諧振')),
        ('ct-first-order-rc-rl', ('一階', '暫態', '狀態空間', '初始電流')),
        ('ct-three-phase', ('三相', 'Y–Y', 'Y 接', 'Δ 負載', '三相四線')),
        ('ct-complex-power', ('複數功率', '功率因數', '交流功率')),
        ('ct-superposition', ('重疊', '疊加', '對偶')),
        ('ct-phasor-ac', ('相量', '交流穩態', '正弦穩態')),
        ('ct-node-mesh', ('節點', '網目')),
        ('ct-divider-equiv', ('分壓', '分流', '電阻等效')),
        ('ct-ohm-kcl-kvl', ('歐姆', 'KCL', 'KVL')),
    ],
    '02': [
        ('el-pe-inverter-spwm', ('逆變器', '變頻器', '全橋逆變', '方波逆變')),
        ('el-pe-thyristor-rectifier', ('閘流體', 'thyristor')),
        ('el-pe-buck-boost', ('轉換器', 'Boost', 'Buck', '降升壓', '升壓型', 'SEPIC', 'Ćuk', '電源')),
        ('el-feedback-stability', ('回授', '負回授', '穩定度')),
        ('el-active-filter', ('頻率響應', '濾波器', '米勒', 'Miller', '高頻', '振盪器', '積分器')),
        ('el-diff-amp', ('差動',)),
        ('el-opamp-ideal', ('運算放大器', 'OPA', 'Schmitt', '觸發')),
        ('el-mosfet-bias-small-signal', ('MOSFET', 'NMOS', 'PMOS', 'MOS')),
        ('el-bjt-bias-small-signal', ('BJT', '電晶體')),
        ('el-zener-regulator', ('齊納',)),
        ('el-diode-rectifier', ('二極體', '二極管', '整流', '限幅', '箝位', 'PN 接面')),
    ],
    '03': [
        ('em-svd-linear-systems', ('奇異值', 'SVD', '零空間', 'Rayleigh')),
        ('em-pde-separation', ('偏微分', 'PDE')),
        ('em-probability-statistics', ('機率', '統計', '隨機', '分布', '動差', '期望', 'CDF', '抽樣', '命中率')),
        ('em-eigen-diagonal', ('特徵值', '特徵向量', '對角化', 'Lyapunov')),
        ('em-vector-analysis', ('向量', '散度', '通量', '曲率', '切線')),
        ('em-matrix-det-inv', ('矩陣', '線性代數', '反矩陣', '最小平')),
        ('em-fourier-series', ('傅立葉', '傅氏')),
        ('em-complex-cauchy-residue', ('複變', '複數', '留數', '柯西', 'De Moivre')),
        ('em-laplace-transform', ('拉氏', '拉普拉斯')),
        ('em-second-order-ode-nonhomogeneous', ('非齊次', '變參數', '降階', '共振')),
        ('em-second-order-ode-homogeneous', ('二階', '重根')),
        ('em-first-order-ode', ('一階', '常微分', 'Bernoulli', '可分離')),
    ],
    '04': [
        ('emach-synchronous-salient-pole', ('凸極', '雙反應', '磁阻電動機')),
        ('emach-synchronous-generator-round', ('同步發電機', '同步機', '同步電容', '同步馬達', '同步電動機')),
        ('emach-induction-motor-torque', ('最大轉矩', '轉矩', '轉差率', '轉差', '旋轉磁動勢')),
        ('emach-induction-motor-equiv', ('感應', '感應馬達', '感應電動機')),
        ('emach-three-phase-transformer', ('三相變壓器', '三相繞組')),
        ('emach-autotransformer', ('自耦',)),
        ('emach-single-phase-transformer', ('變壓器', '變壓', '磁化電流', '漏磁')),
        ('emach-dc-motor-generator', ('直流', '串激', '他激', '複激')),
        ('emach-magnetic-circuits', ('磁路', '磁通', '氣隙', '電磁鐵', '電感', '磁飽和', '磁化')),
    ],
    '05': [
        ('ps-state-estimation-wls', ('狀態估計', 'WLS')),
        ('ps-economic-dispatch', ('經濟調度', '增量成本', '發電協調', '燃料成本', '微增', 'KKT')),
        ('ps-load-flow-admittance', ('潮流', '導納矩陣', 'Ybus', '匯流排', '牛頓', '高斯', '分接頭')),
        ('ps-power-analysis', ('實功率', '虛功率', '複數功率', '相量', '負載相量')),
        ('ps-system-protection-relay', ('保護電驛', '保護協調', '差動保護')),
        ('ps-unsymmetrical-faults', ('不平衡', '不對稱', '線間', '單相接地', '同時故障')),
        ('ps-transient-stability-equal-area', ('暫態穩定', '等面積', '搖擺', '功角', '清除')),
        ('ps-symmetrical-components', ('對稱成分', '正序', '負序', '零序')),
        ('ps-three-phase-fault', ('三相短路', '三相故障', '短路故障')),
        ('ps-transmission-line-models', ('中程', '長程', 'ABCD', '電壓調整')),
        ('ps-transmission-line-params', ('輸電線', '導線', 'GMD', 'GMR', '束線')),
        ('ps-per-unit', ('標么', 'pu', '基準')),
    ],
    '06': [
        ('dist-arc-flash-ieee80', ('弧閃',)),
        ('dist-grounding-system', ('接地',)),
        ('dist-lighting-design', ('照明', '流明')),
        ('dist-distribution-equipment', ('配電變壓器', '供電', '接線', 'V-V', '開三角', '受電', 'CVT', '比壓器')),
        ('dist-motor-installation', ('電動機', '馬達', '啟動', '配線')),
        ('dist-harmonics-mitigation', ('諧波', '閃爍', '電弧爐')),
        ('dist-protection-coordination', ('保護', '電驛', 'CT', '比流器', 'CO-7')),
        ('dist-short-circuit-capacity', ('短路', '故障')),
        ('dist-power-factor-correction', ('功率因數', '電容', 'APFR')),
        ('dist-voltage-drop', ('壓降', '電壓降')),
        ('dist-load-characteristics', ('負載', '需量', '契約', '容量')),
    ],
}

# Canonical notes that intentionally lack a chapter field, or whose chapter
# wording is too broad for a safe substring rule.  The title is retained as
# evidence in the generated map so a later editor can review the decision.
CANONICAL_TAXONOMY_OVERRIDES = {
    # Circuit theory: topics absent from the original keyword rules.
    'EE-106-01-3': 'ct-node-mesh',
    'EE-106-01-4': 'ct-superposition',
    'EE-107-01-4': 'ct-max-power',
    'EE-109-01-1': 'ct-node-mesh',
    'EE-109-01-2': 'ct-laplace-circuit',
    'EE-108-01-1': 'ct-phasor-ac',
    # Electronics: device marker must beat generic frequency/feedback words.
    'EE-104-02-1': 'el-mosfet-bias-small-signal',
    'EE-105-02-4': 'el-active-filter',
    'EE-106-02-2': 'el-mosfet-bias-small-signal',
    'EE-106-02-3': 'el-bjt-bias-small-signal',
    'EE-108-02-3': 'el-feedback-stability',
    'EE-111-02-4': 'el-feedback-stability',
    'EE-110-02-1': 'el-bjt-bias-small-signal',
    'EE-112-02-1': 'el-bjt-bias-small-signal',
    'EE-112-02-2': 'el-opamp-ideal',
    # Engineering mathematics: canonical wording is already chapter-level.
    'EE-105-03-1': 'em-second-order-ode-homogeneous',
    'EE-108-03-1': 'em-second-order-ode-nonhomogeneous',
    'EE-113-03-4': 'em-matrix-det-inv',
    # Electric machinery notes without frontmatter.
    'EE-104-04-1': 'emach-magnetic-circuits',
    'EE-104-04-3': 'emach-dc-motor-generator',
    'EE-104-04-4': 'emach-induction-motor-equiv',
    'EE-104-04-5': 'emach-synchronous-generator-round',
    'EE-105-04-1': 'emach-magnetic-circuits',
    'EE-105-04-2': 'emach-single-phase-transformer',
    # Starting-resistor question is explicitly about the torque/slip curve,
    # not the steady-state equivalent circuit.
    'EE-105-04-3': 'emach-induction-motor-torque',
    'EE-105-04-4': 'emach-synchronous-generator-round',
    'EE-106-04-1': 'emach-magnetic-circuits',
    'EE-106-04-3': 'emach-dc-motor-generator',
    'EE-106-04-4': 'emach-induction-motor-equiv',
    'EE-106-04-5': 'emach-synchronous-generator-round',
    'EE-107-04-2': 'emach-dc-motor-generator',
    'EE-107-04-3': 'emach-induction-motor-equiv',
    'EE-108-04-2': 'emach-dc-motor-generator',
    'EE-109-04-3': 'emach-induction-motor-equiv',
    'EE-109-04-4': 'emach-induction-motor-equiv',
    'EE-109-04-5': 'emach-synchronous-salient-pole',
    'EE-110-04-4': 'emach-dc-motor-generator',
    'EE-113-04-4': 'emach-induction-motor-equiv',
    'EE-114-04-1': 'emach-magnetic-circuits',
    'EE-114-04-2': 'emach-single-phase-transformer',
    'EE-114-04-3': 'emach-induction-motor-equiv',
    'EE-114-04-4': 'emach-synchronous-generator-round',
    'EE-114-04-5': 'emach-synchronous-salient-pole',
    # Power-system notes without frontmatter.
    # Sequence networks are used here to solve an SLG/grounding fault; the
    # fault type is the primary review topic and must not fall back to the
    # generic symmetrical-components chapter.
    'EE-104-05-1': 'ps-unsymmetrical-faults',
    'EE-104-05-2': 'ps-power-analysis',
    'EE-105-05-1': 'ps-transmission-line-models',
    'EE-105-05-3': 'ps-unsymmetrical-faults',
    'EE-106-05-1': 'ps-transmission-line-models',
    'EE-106-05-2': 'ps-three-phase-fault',
    'EE-106-05-4': 'ps-system-protection-relay',
    'EE-107-05-1': 'ps-transmission-line-models',
    'EE-107-05-2': 'ps-three-phase-fault',
    'EE-107-05-3': 'ps-power-analysis',
    'EE-109-05-2': 'ps-transmission-line-models',
    'EE-109-05-3': 'ps-load-flow-admittance',
    'EE-109-05-6': 'ps-transient-stability-equal-area',
    'EE-110-05-1': 'ps-transient-stability-equal-area',
    'EE-110-05-2': 'ps-load-flow-admittance',
    'EE-110-05-4': 'ps-economic-dispatch',
    'EE-111-05-1': 'ps-transmission-line-models',
    'EE-111-05-2': 'ps-three-phase-fault',
    'EE-109-05-4': 'ps-symmetrical-components',
    'EE-110-05-3': 'ps-symmetrical-components',
    'EE-113-05-4': 'ps-transient-stability-equal-area',
    'EE-114-05-1': 'ps-power-analysis',
    'EE-114-05-2': 'ps-load-flow-admittance',
    'EE-114-05-3': 'ps-economic-dispatch',
    'EE-114-05-4': 'ps-three-phase-fault',
    'EE-114-05-5': 'ps-transient-stability-equal-area',
    'EE-108-04-5': 'emach-dc-motor-generator',
    'EE-109-05-1': 'ps-power-analysis',
    'EE-112-04-1': 'emach-magnetic-circuits',
    'EE-112-04-2': 'emach-single-phase-transformer',
    'EE-112-04-3': 'emach-synchronous-generator-round',
    'EE-112-04-4': 'emach-induction-motor-equiv',
    'EE-112-04-5': 'emach-dc-motor-generator',
    # Industrial distribution 114 notes are all frontmatter-free.
    'EE-114-06-1': 'dist-distribution-equipment',
    'EE-114-06-2': 'dist-harmonics-mitigation',
    'EE-114-06-3': 'dist-short-circuit-capacity',
    'EE-114-06-4': 'dist-motor-installation',
    'EE-114-06-5': 'dist-power-factor-correction',
    # Mixed-topic titles use the leading textbook concept as primary.
    'EE-110-06-1': 'dist-power-factor-correction',
    'EE-110-06-5': 'dist-short-circuit-capacity',
    'EE-112-06-4': 'dist-short-circuit-capacity',
    'EE-113-06-2': 'dist-voltage-drop',
    'EE-106-06-1': 'dist-short-circuit-capacity',
    # Canonical title evidence resolves two otherwise ambiguous generic
    # classifications.
    'EE-112-06-5': 'dist-protection-coordination',
    'EE-114-02-2': 'el-mosfet-bias-small-signal',
}


def resolve_canonical_taxonomy(qid, subject_id):
    """Resolve one canonical note to a DAG node using chapter evidence."""
    evidence = CANONICAL_TOPIC_METADATA.get(qid, {})
    chapter = str(evidence.get('chapter', '') or '')
    title = str(evidence.get('title', '') or '')
    if qid in CANONICAL_TAXONOMY_OVERRIDES:
        return CANONICAL_TAXONOMY_OVERRIDES[qid]
    haystack = f'{chapter} {title}'.lower()
    for chapter_id, terms in CANONICAL_CHAPTER_RULES.get(subject_id, []):
        if any(str(term).lower() in haystack for term in terms):
            return chapter_id
    return None


for qid, evidence in CANONICAL_TOPIC_METADATA.items():
    sid_match = re.match(r'EE-\d{3}-(\d{2})-', qid)
    if not sid_match:
        continue
    sid = sid_match.group(1)
    chapter_id = resolve_canonical_taxonomy(qid, sid)
    if chapter_id:
        QUESTION_TAXONOMY_MAP[qid] = {
            'primaryChapter': chapter_id,
            'source': 'canonical-title-override' if qid in CANONICAL_TAXONOMY_OVERRIDES else 'canonical-chapter',
            'canonicalChapter': evidence.get('chapter', ''),
            'noteTitle': evidence.get('title', ''),
        }

# Read the explicit review register written by annotate_manual_reviews.py.
# Only expose the three stable fields; the full Markdown remains the source of
# truth for the derivation itself.
for subject_dir in (
    '01_電路學', '02_電子學_含電力電子', '03_工程數學',
    '04_電機機械', '05_電力系統', '06_工業配電',
):
    canonical_dir = os.path.join('📝 個人題解與錯題本', subject_dir, 'canonical')
    if not os.path.isdir(canonical_dir):
        continue
    for f in os.listdir(canonical_dir):
        match = re.match(r'(EE-\d{3}-\d{2}-\d+)\.md$', f)
        if not match:
            continue
        path = os.path.join(canonical_dir, f)
        try:
            with open(path, 'r', encoding='utf-8') as fp:
                raw = fp.read()
        except OSError:
            continue
        if not raw.startswith('---'):
            continue
        frontmatter = raw.split('---', 2)[1]
        fields = {}
        for line in frontmatter.splitlines():
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            fields[key.strip()] = value.strip().strip("'\"")
        if fields.get('review_disposition'):
            review_meta = {
                'disposition': fields.get('review_disposition', ''),
                'blocker': fields.get('review_blocker', ''),
                'action': fields.get('review_action', ''),
                'evidence': fields.get('review_evidence', ''),
            }
            public_urls = fields.get('public_reference_urls', '')
            if public_urls:
                # The annotation script stores a semicolon-delimited list so
                # each URL remains a single frontmatter scalar.  Preserve the
                # list as an array for safe rendering in the browser.
                review_meta['publicReferenceUrls'] = [
                    url.strip() for url in public_urls.split(';')
                    if url.strip().startswith('https://')
                ]
            public_note = fields.get('public_reference_note', '')
            if public_note:
                review_meta['publicReferenceNote'] = public_note
            official_url = fields.get('official_source_url', '')
            if official_url:
                review_meta['officialSourceUrl'] = official_url
            SOLUTION_REVIEW_METADATA[match.group(1)] = review_meta

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
                    if qid in QUESTION_TAG_OVERRIDES:
                        tags = QUESTION_TAG_OVERRIDES[qid][:]
                    if qid in ENGINEERING_MATH_TOPIC_OVERRIDES:
                        topic = ENGINEERING_MATH_TOPIC_OVERRIDES[qid]
                    if qid in PE_TOPIC_OVERRIDES:
                        topic = PE_TOPIC_OVERRIDES[qid]
                    
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
                        if sid == '03':
                            v_status = ENGINEERING_MATH_AUDIT_STATUS.get(qid, 'pending')
                        else:
                            v_status = PE_SOLUTION_AUDIT_STATUS.get(qid, 'verified')
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

# Fail closed if a new/removed canonical note leaves the dashboard without a
# chapter mapping, or if a mapping crosses subject boundaries.  This turns a
# silent "待人工複核" regression into a build-time error.
taxonomy_nodes = {}
try:
    with open('data/taxonomy/alias-map.json', 'r', encoding='utf-8') as f:
        alias_map = json.load(f)
    for subject_id, subject in alias_map.get('subjects', {}).items():
        for chapter_id in subject.get('chapters', {}):
            taxonomy_nodes[chapter_id] = str(subject_id)
except (OSError, ValueError, TypeError) as exc:
    raise RuntimeError(f'Cannot load taxonomy node manifest: {exc}') from exc

active_qids = {row[0] for row in all_questions}
mapped_qids = set(QUESTION_TAXONOMY_MAP)
if mapped_qids != active_qids:
    missing = sorted(active_qids - mapped_qids)
    extra = sorted(mapped_qids - active_qids)
    raise RuntimeError(f'Question taxonomy coverage mismatch: missing={missing}, extra={extra}')
for qid, evidence in QUESTION_TAXONOMY_MAP.items():
    chapter_id = evidence.get('primaryChapter') if isinstance(evidence, dict) else evidence
    sid = qid.split('-')[2] if qid.count('-') >= 2 else ''
    if chapter_id not in taxonomy_nodes:
        raise RuntimeError(f'Question taxonomy references unknown DAG chapter: {qid} -> {chapter_id}')
    if taxonomy_nodes[chapter_id] != sid:
        raise RuntimeError(f'Question taxonomy crosses subject boundary: {qid} -> {chapter_id}')

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
// qid -> canonical textbook chapter evidence.  Manual labels and explicit
// TAXONOMY_OVERRIDES remain higher priority in the review UI; this map is the
// stable source for every question that has a canonical solution note.
const QUESTION_TAXONOMY_MAP = {json.dumps(QUESTION_TAXONOMY_MAP, ensure_ascii=False, indent=2)};
const SOLUTION_REVIEW_METADATA = {json.dumps(SOLUTION_REVIEW_METADATA, ensure_ascii=False, indent=2)};

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
