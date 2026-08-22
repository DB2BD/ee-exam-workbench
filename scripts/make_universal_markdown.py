import fitz
import glob
import os
import re

pua_map = {
    0xe129: '(一)', 0xe12a: '(二)', 0xe12b: '(三)', 0xe12c: '(四)', 0xe12d: '(五)', 0xe12e: '(六)',
    0xf020: ' ', 0xf02b: '+', 0xf02d: '-', 0xf03c: '<', 0xf03d: '=', 0xf03e: '>',
    0xf044: 'Δ', 0xf057: 'Ω', 0xf061: 'α', 0xf062: 'β', 0xf064: 'δ', 0xf066: 'φ',
    0xf068: 'θ', 0xf06a: 'φ', 0xf06c: 'λ', 0xf06d: 'μ', 0xf06f: 'ο', 0xf070: 'π',
    0xf071: 'θ', 0xf072: 'ρ', 0xf074: 'τ', 0xf076: 'ω', 0xf077: 'ω', 0xf081: ' ',
    0xf0a2: '≥', 0xf0a3: '≤', 0xf0a5: '∞', 0xf0b0: '°', 0xf0b1: '±', 0xf0b3: '≥',
    0xf0b4: '×', 0xf0b7: '·', 0xf0b9: '≠', 0xf0bb: '≈', 0xf0c2: '⊆', 0xf0d0: '∠',
    0xf0d1: '∇', 0xf0e6: '(', 0xf0e7: '(', 0xf0e8: '(', 0xf0e9: '[', 0xf0ea: ']',
    0xf0eb: ']', 0xf0ec: '{', 0xf0ed: '{', 0xf0ee: '{', 0xf0ef: '}', 0xf0f2: '∫',
    0xf0f6: '(', 0xf0f7: ')', 0xf0f8: ')', 0xf0f9: '[', 0xf0fa: ']', 0xf0fb: ']',
    0xf8eb: '(', 0xf8ec: ')', 0xf8ed: ')', 0xf8ee: '[', 0xf8ef: ']', 0xf8f0: ']',
    0xf8f6: '(', 0xf8f7: ')', 0xf8f8: ')', 0xf8f9: '[', 0xf8fa: ']', 0xf8fb: ']'
}

char_map = {
    '路': '路', '不': '不', '量': '量', '﹖': '？',
    'Ð': '∠', 'Ω': 'Ω', '∆': 'Δ', '−': '-',
    '⑴': '(一)', '⑵': '(二)', '⑶': '(三)', '⑷': '(四)',
    '①': '(1)', '②': '(2)', '③': '(3)',
    'ܣ': 's', 'ܥ': 'C', 'ܫ': 'I', 'ܲ': 'P', 'ܸ': 'E', 'ܺ': 'z',
    'ܾ': '>', 'ܿ': '<', '݁': '', '݂': '', '݃': '',
    '݅': 'i', '݆': 'j', 'ݐ': 't', 'ݑ': 'u', 'ݒ': 'v', 'ݔ': 'x', 'ݕ': 'y', 'ݖ': 'z',
    'ߙ': 'α', 'ߚ': 'θ', '߱': 'ω', 'ߛ': 'k', 'ߜ': 'm', 'ߨ': 'f',
    'ଵ': '1', 'ଶ': '2', 'ଷ': '3', 'ସ': '4', 'ି': 'i', '୭': '°',
    '௥': 'r', '௠': 'm', '௦': 's', '௩': '3', '௫': '5', '௭': '7', '௟': 'l',
    '஼': '', '்': '', '௏': '', 'ௗ': 'd', '௚': '', '௜': '',
    'ம': 'm', '೒': 'g', '೔': 'h', '೚': 'z', 'ೞ': 'L',
    '൤': '[', '൥': '[', '൨': ']', '൩': ']',
    'ቂ': '[', 'ቃ': ']', 'ቄ': '{', 'ቊ': '{',
    'ᇱ': "'",
    '𝐼': 'I', '𝑇': 'T', '𝑘': 'k', '𝑠': 's',
}

def clean_text(text):
    for code, rep in pua_map.items():
        text = text.replace(chr(code), rep)
    for k, v in char_map.items():
        text = text.replace(k, v)
    return text

def advanced_latexify(text):
    text = re.sub(r'1\s*\n\s*V\s+與\s+2\s*\n\s*V', lambda m: r'$\mathbf{V}_1$ 與 $\mathbf{V}_2$', text)
    text = re.sub(r'\)\s*\n\s*\(\s*\n\s*1\s*t\s*\n\s*v', lambda m: r'$v_1(t)$', text)
    text = re.sub(r'\)\s*\n\s*\(\s*\n\s*2\s*t\s*\n\s*v', lambda m: r'$v_2(t)$', text)
    text = re.sub(r'(\d+)\s*\n\s*([R|L|C|M|Z])\s*=\s*[ΩΩ]', lambda m: f"${m.group(2)}_1 = {m.group(1)}\\ \\Omega$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*H\s*\n\s*([L|M])\s*=', lambda m: f"${m.group(2)} = {m.group(1)}\\text{{ H}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*rad/s\s*\n\s*ω\s*=', lambda m: f"$\\omega = {m.group(1)}\\text{{ rad/s}}$", text)
    text = re.sub(r'ω\s*=\s*\n?\s*(\d+(?:\.\d+)?)\s*rad/s', lambda m: f"$\\omega = {m.group(1)}\\text{{ rad/s}}$", text)
    
    # Units
    text = re.sub(r'(\d+)\s*[ΩΩ]', lambda m: f"${m.group(1)}\\ \\Omega$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*k[ΩΩ]', lambda m: f"${m.group(1)}\\text{{ k}}\\Omega$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*M[ΩΩ]', lambda m: f"${m.group(1)}\\text{{ M}}\\Omega$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*mH\b', lambda m: f"${m.group(1)}\\text{{ mH}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*[μu]F\b', lambda m: f"${m.group(1)}\\ \\mu\\text{{F}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*pF\b', lambda m: f"${m.group(1)}\\text{{ pF}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*kV\b', lambda m: f"${m.group(1)}\\text{{ kV}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*kVA\b', lambda m: f"${m.group(1)}\\text{{ kVA}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*MVA\b', lambda m: f"${m.group(1)}\\text{{ MVA}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*Mvar\b', lambda m: f"${m.group(1)}\\text{{ Mvar}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*kvar\b', lambda m: f"${m.group(1)}\\text{{ kvar}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*rad/s\b', lambda m: f"${m.group(1)}\\text{{ rad/s}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*Hz\b', lambda m: f"${m.group(1)}\\text{{ Hz}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*HP\b', lambda m: f"${m.group(1)}\\text{{ HP}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*mA\b', lambda m: f"${m.group(1)}\\text{{ mA}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*mW\b', lambda m: f"${m.group(1)}\\text{{ mW}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*kW\b', lambda m: f"${m.group(1)}\\text{{ kW}}$", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*MW\b', lambda m: f"${m.group(1)}\\text{{ MW}}$", text)
    
    # Phasors and angles
    text = re.sub(r'(\d+(?:\.\d+)?)\s*∠\s*([-\d\.]+)\s*°?', lambda m: f"${m.group(1)}\\angle {m.group(2)}^\\circ$", text)
    text = re.sub(r'([I|V|E|Z][\w\d_]*)\s*∠\s*([-\w\d\.\+]+)\s*°?', lambda m: f"${m.group(1)}\\angle {m.group(2)}^\\circ$", text)
    
    # Signals
    text = re.sub(r'\bvo\s*\(\s*t\s*\)', lambda m: r'$v_o(t)$', text)
    text = re.sub(r'\bvs\s*\(\s*t\s*\)', lambda m: r'$v_s(t)$', text)
    text = re.sub(r'\bis\s*\(\s*t\s*\)', lambda m: r'$i_s(t)$', text)
    text = re.sub(r'\biL\s*\(\s*t\s*\)', lambda m: r'$i_L(t)$', text)
    text = re.sub(r'\bvC\s*\(\s*t\s*\)', lambda m: r'$v_C(t)$', text)
    text = re.sub(r'\bu\s*\(\s*t\s*\)', lambda m: r'$u(t)$', text)
    text = re.sub(r'δ\s*\(\s*t\s*\)', lambda m: r'$\delta(t)$', text)
    
    # Variables
    text = re.sub(r'\bv1\b', lambda m: r'$v_1$', text)
    text = re.sub(r'\bv2\b', lambda m: r'$v_2$', text)
    text = re.sub(r'\bv3\b', lambda m: r'$v_3$', text)
    
    # Times
    text = re.sub(r'\bt\s*=\s*0\b', lambda m: r'$t = 0$', text)
    text = re.sub(r'\bt\s*>\s*0\b', lambda m: r'$t > 0$', text)
    text = re.sub(r'\bt\s*≥\s*0\b', lambda m: r'$t \ge 0$', text)
    text = re.sub(r'\bt\s*≤\s*0\b', lambda m: r'$t \le 0$', text)
    text = re.sub(r'\bt\s*<\s*0\b', lambda m: r'$t < 0$', text)
    
    # Filter diagram noise
    lines = text.splitlines()
    cleaned = []
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
            cleaned.append('')
            continue
        is_label = any(re.match(pat, ls) for pat in diagram_label_patterns)
        if not is_label:
            cleaned.append(l)
            
    return '\n'.join(cleaned)

def parse_exam_file(pdf_path, subject_folder, year_str):
    doc = fitz.open(pdf_path)
    full_text = ''
    for page in doc:
        full_text += clean_text(page.get_text()) + '\n'
    
    calc_rule = '可以使用電子計算器' if '可以使用電子計算器' in full_text else ('禁止使用電子計算器' if '禁止使用電子計算器' in full_text or '不得使用電子計算器' in full_text else '未特別註明')
    code_match = re.search(r'代號：(\d+)', full_text)
    exam_code = code_match.group(1) if code_match else '—'
    
    page_texts = []
    for p_idx, page in enumerate(doc):
        p_raw = clean_text(page.get_text())
        lines = p_raw.splitlines()
        clean_lines = []
        
        for line in lines:
            l = line.strip()
            if not l:
                continue
            if any(kw in l for kw in [
                '專門職業及技術人員', '高等考試', '類科技師', '技師考試分階段考試',
                '暨普通考試', '不動產經紀人', '記帳士考試', '驗光人員考試',
                '等別：', '類科：', '科目：', '考試時間：', '座號：',
                '※注意：', '可以使用電子計算器', '禁止使用電子計算器', '不得使用電子計算器',
                '不必抄題', '本科目除專門名詞', '代號：', '頁次：',
                '等\n別', '類\n科', '科\n目'
            ]):
                continue
            if re.match(r'^(?:等|別|類|科|目)[：:]', l) or l in [
                '等', '別', '類', '科', '目', '電機工程技師',
                '電路學', '電子學（包括電力電子學）', '工程數學', '工程數學（包括線性代數、微分方程、複變函數與機率）',
                '電機機械', '電力系統', '工業配電'
            ]:
                continue
            if re.match(r'^\(\w+\)(?:可以使用|禁止使用|不必抄題|本科目除)', l):
                continue
            clean_lines.append(l)
        
        page_texts.append('\n'.join(clean_lines))
    
    body = '\n\n'.join(page_texts).strip()
    body = re.sub(r'(?:^|\n)\s*(\([一二三四五六七八九十]+\))\s*', r'\n\n* **\1** ', body)
    body = re.sub(r'(?:^|\n)\s*([一二三四五六七八九十]+[、\.])\s*', r'\n\n#### \1 ', body)
    body = advanced_latexify(body)
    
    if subject_folder == '03_工程數學':
        if year_str == '114':
            body = re.sub(r'二、\s*計算∫e17మ[^\n]*\n[^\n]*dz[^\n]*',
                          r'二、 計算 $\\oint_C e^{1/z^2} dz$，其中路徑 $C$ 為下圖所示複數平面 $z = x+iy$ 上，圓心在原點 $O$ 之單位圓。（15 分）', body)
            body = re.sub(r'三、\s*求解以下初始值問題之常微分方程式[^\n]*',
                          r'三、 求解以下初始值問題之常微分方程式：$y\'\'(t) + 4y\'(t) + 4y(t) = 0, y(0) = 1, y\'(0) = 3$。（20 分）', body)
            body = re.sub(r'四、\s*假設週期函數\(x\)之週期為2f[^\n]*\nx[^\n]*\n[^\n]*',
                          r'四、 假設週期函數 $f(x)$ 之週期為 $2\\pi$：\n$$f(x) = \\begin{cases} 0, & -\\pi < x \\le 0 \\\\ x, & 0 < x \\le \\pi \\end{cases}$$\n計算 $f(x)$ 之傅立葉級數（Fourier Series）。（20 分）', body)
            body = re.sub(r'五、\s*假設矩陣A = \[0[\s\S]*?T。',
                          r'五、 假設矩陣 $\\mathbf{A} = \\begin{bmatrix} 0 & 1 \\\\ -1 & 0 \\\\ 0 & 1 \\\\ -1 & 0 \\end{bmatrix}$ 與 $\\mathbf{b} = \\begin{bmatrix} 0 \\\\ 1 \\end{bmatrix}^T$：', body)
        elif year_str == '113':
            body = re.sub(r'一、\s*試求常微分方程式[\s\S]*?之通解。（20 分）',
                          r'一、 試求常微分方程式 $y\'\' + 4y\' + 5y = e^{-2x} \\csc x$ 之通解。（20 分）', body)
            body = re.sub(r'二、\s*試求一時間函數[\s\S]*?換（Laplace Transform）F\(s\)。',
                          r'二、 試求一時間函數 $f(t) = \\frac{1}{2\\beta^3} (\\sin \\beta t - \\beta t \\cos \\beta t),\\ t \\ge 0,\\ \\beta \\ne 0$ 之拉普拉斯轉換（Laplace Transform）$F(s)$。（10 分）', body)
            body = re.sub(r'三、\s*試以剩值定理[\s\S]*?之值。（20 分）',
                          r'三、 試以留數定理（Residue Theorem）求 $\\int_{-\\infty}^\\infty \\frac{1}{x^4 + 16} dx$ 之值。（20 分）', body)
            body = re.sub(r'四、\s*一矩陣[\s\S]*?A\s*，其轉置矩陣[\s\S]*?T\s*A\s*。',
                          r'四、 矩陣 $\\mathbf{A} = \\begin{bmatrix} 0 & 1 \\\\ -5 & -6 \\end{bmatrix}$，其轉置矩陣 $\\mathbf{A}^T = \\begin{bmatrix} 0 & -5 \\\\ 1 & -6 \\end{bmatrix}$。', body)
            body = re.sub(r'滿足下列矩陣方程式，[\s\S]*?PA\s*A P\s*。',
                          r'滿足下列矩陣方程式：$\\mathbf{P}\\mathbf{A} + \\mathbf{A}^T\\mathbf{P} = -\\begin{bmatrix} 1 & 0 \\\\ 0 & 1 \\end{bmatrix}$。', body)
            body = re.sub(r'五、[\s\S]*?單位切線向量。（10 分）',
                          r'五、\n\n* **(一)** 一曲線 $C$，其表示式為 $\\mathbf{r}(t) = [3t^2, 4t, 8t^4]$，$t$ 為參數，試求其切線向量與單位切線向量。（10 分）', body)
            body = re.sub(r'\* \*\*(二)\*\* 試求一向量函數[\s\S]*?9\s*S[\s\S]*?（10 分）',
                          r'* **(二)** 試求一向量函數 $\\mathbf{F} = 7x\\mathbf{i} + 3y\\mathbf{j} - z\\mathbf{k}$ 之面積分 $\\iint_S \\mathbf{F} \\cdot \\mathbf{n} dA$，其中 $\\mathbf{n}$ 為 $dA$ 指向外的法線方向單位向量，且此有界封閉曲面的表示式為 $S: x^2 + y^2 + z^2 = 9$。（10 分）', body)
            body = re.sub(r'六、[\s\S]*?聯合機率密度函數[\s\S]*?p x y[\s\S]*?其他區域。',
                          r'六、 $X$ 與 $Y$ 為兩隨機變數（Random variables），其聯合機率密度函數（Joint probability density function）為：\n$$p(x,y) = \\begin{cases} k e^{-x - 2y}, & 0 \\le x < \\infty,\\ 0 \\le y < \\infty \\\\ 0, & \\text{其他區域} \\end{cases}$$\n', body)
        elif year_str == '112':
            body = re.sub(r'假設\(x\) = \{-2x, -2 ≤x< 0[\s\S]*?20\s*。（20 分）',
                          r'假設 $f(x) = \\begin{cases} -2x, & -2 \\le x < 0 \\\\ 2x, & 0 \\le x < 2 \\end{cases}$，週期為 $4$。（20 分）', body)
            body = re.sub(r"y\(0\)=\s*y'\s*\(0\)=0，其中\(t\) = \{[\s\S]*?其他",
                          r"$y(0) = y'(0) = 0$，其中 $g(t) = \\begin{cases} 1, & 5 \\le t < 20 \\\\ 0, & \\text{其他} \\end{cases}$", body)
            body = re.sub(r'假設A =\[\s*1\s*3\s*0\s*0\s*0\s*1\s*1\s*3\s*1\], b =\[\s*2\s*4\s*6\], c =\[\s*1\s*6\s*7\]',
                          r'假設 $\\mathbf{A} = \\begin{bmatrix} 1 & 0 & 1 \\\\ 3 & 0 & 3 \\\\ 0 & 1 & 1 \\end{bmatrix}$，$\\mathbf{b} = \\begin{bmatrix} 2 \\\\ 4 \\\\ 6 \\end{bmatrix}$，$\\mathbf{c} = \\begin{bmatrix} 1 \\\\ 6 \\\\ 7 \\end{bmatrix}$', body)
        elif year_str == '111':
            body = re.sub(r'一、\s*1y\s*x\s*=\s*為[\s\S]*?0\s*x\s*x\s*之一解，試求其通解。（15 分）',
                          r'一、 已知 $y_1(x) = \\frac{1}{x}$ 為微分方程式 $x^2 \\frac{d^2y}{dx^2} - 2x \\frac{dy}{dx} + (2 - x^2) y = 0$ 之一解，試求其通解。（15 分）', body)
            body = re.sub(r'四、\s*矩陣\s*1\s*1\s*1\s*3\s*\[\s*\]\s*=\s*\|\s*\|\s*\[\s*\]\s*A\s*。',
                          r'四、 矩陣 $\\mathbf{A} = \\begin{bmatrix} 1 & 1 \\\\ 1 & 3 \\end{bmatrix}$。', body)
        elif year_str == '110':
            body = re.sub(r'六、\s*3\s*0\s*2\s*0\s*2\s*0\s*2\s*0\s*0\s*A[\s\S]*?-\s*\[\s*\]',
                          r'六、 矩陣 $\\mathbf{A} = \\begin{bmatrix} 3 & 0 & -2 \\\\ 0 & 2 & 0 \\\\ -2 & 0 & 0 \\end{bmatrix}$', body)
            body = re.sub(r"二、\s*求\s*2\s*2x\s*y\s*y e-\s*'\s*=\s*的通解[^\n]*",
                          r"二、 求常微分方程 $y' = y^2 e^{-2x}$ 的通解（General Solution）。（10 分）", body)
        elif year_str == '109':
            body = re.sub(r'求以下微分方程式的通解[\s\S]*?75\s*20[\s\S]*?。（20 分）',
                          r'一、 求以下微分方程式的通解：$\\frac{d^2y}{dx^2} - 10\\frac{dy}{dx} + 25y = 75x + 20$。（20 分）', body)
            body = re.sub(r'矩陣\s*7\s*2\s*3\s*13\s*2\s*7\s*8\s*2\s*2\s*A[\s\S]*?找出A的反矩陣\s*1\s*A-\s*。（20 分）',
                          r'五、 矩陣 $\\mathbf{A} = \\begin{bmatrix} -7 & 2 & -3 \\\\ 13 & 2 & -7 \\\\ 8 & 2 & -2 \\end{bmatrix}$，找出 $\\mathbf{A}$ 的反矩陣 $\\mathbf{A}^{-1}$。（20 分）', body)
        elif year_str == '108':
            body = re.sub(r'二、\s*試求矩陣[\s\S]*?3\s*0\s*0\s*2\s*0\s*1\s*0\s*0\s*2\s*A[\s\S]*?特徵向量（Eigenvectors）。（10 分）',
                          r'二、 試求矩陣 $\\mathbf{A} = \\begin{bmatrix} 2 & 0 & 0 \\\\ 1 & 0 & 2 \\\\ 0 & 0 & 3 \\end{bmatrix}$ 的特徵值（Eigenvalues）與特徵向量（Eigenvectors）。（10 分）', body)
    
    body = re.sub(r'#{4,}\s*', r'#### ', body)
    lines = [line.strip() for line in body.splitlines()]
    final_lines = []
    for line in lines:
        if line:
            final_lines.append(line)
        elif final_lines and final_lines[-1] != '':
            final_lines.append('')
            
    return {
        'exam_code': exam_code,
        'calc_rule': calc_rule,
        'page_count': len(doc),
        'body': '\n'.join(final_lines)
    }

subj_info = {
    '01_電路學': {
        'title': '01. 電路學',
        'name': '電路學',
        'desc': '直流電路分析（節點與迴路分析、戴維寧與諾頓等效）、交流穩態電路（相量、複數阻抗、實功率/虛功率/視在功率、功率因數改善）、三相平衡與不平衡電路、一階與二階暫態響應（RL, RC, RLC、微分方程求解）、拉氏轉換應用（S域電路分析、轉移函數、步階與脈衝響應）、雙埠網路（z, y, h, ABCD 參數互換與串並聯）、濾波器與頻率響應（諧振電路、波德圖 Bode Plot）。'
    },
    '02_電子學_含電力電子': {
        'title': '02. 電子學（包括電力電子學）',
        'name': '電子學（包括電力電子學）',
        'desc': '二極體應用電路（整流、截波、箝位、穩壓）、BJT 與 MOSFET 放大器（直流偏壓穩定度、小訊號交流分析、共射/共源/共集/共閘/共基/共汲組態、高低頻頻率響應）、差動放大器（CMRR、主動負載）、運算放大器（Op-Amp 理想與非理想特性、負回授拓撲與穩定度補償）、電力電子開關元件（SCR, TRIAC, GTO, MOSFET, IGBT）、非隔離型 DC-DC 轉換器（Buck, Boost, Buck-Boost 連續與不連續導通模式 CCM/DCM）、單相與三相反流器（Inverter、PWM 調變技術）、相控整流電路。'
    },
    '03_工程數學': {
        'title': '03. 工程數學（含線性代數、微分方程、複變函數、機率）',
        'name': '工程數學',
        'desc': '常微分方程（一階 ODE、二階與高階常係數線性 ODE、尤拉-柯西方程、級數解）、拉氏轉換（Laplace Transform、初值與終值定理、卷積 Convolution）、傅立葉級數與傅立葉轉換、線性代數（矩陣運算、行列式、線性獨立、特徵值與特徵向量、矩陣對角化、二次型、奇異值分解 SVD）、複變函數（柯西-黎曼方程式、解析函數、柯西積分公式、羅倫級數 Laurent Series、留數定理 Residue Theorem）、機率統計（機率公理、條件機率、貝氏定理、離散/連續隨機變數、期望值與變異數、聯合機率密度函數、常態分佈、二項分佈、卜瓦松分佈）。'
    },
    '04_電機機械': {
        'title': '04. 電機機械',
        'name': '電機機械',
        'desc': '磁路定律（安培環路定律、法拉第定律、磁阻、鐵損與磁滯）、變壓器（理想變壓器、實體等效電路參數開路/短路試驗、電壓調整率、全日效率、三相變壓器接線 Y-Δ/Δ-Y/V-V 與並聯運轉條件、自耦變壓器）、三相感應電動機（旋轉磁場原理、等效電路、堵轉/無載試驗、轉矩-轉差率曲線、最大轉矩、起動方法、降壓啟動、調速控制）、同步電機（發電機與電動機工作原理、電樞反應、同步阻抗試驗與短路比 SCR、相量圖、功角特性曲線、V 形曲線、並聯運轉同步程序）、直流電機（發電機與電動機構造、電樞反應與補償繞組、轉矩與反電動勢常數、速度控制、起動與電氣制動）、特殊電機（永久磁鐵無刷直流電動機 BLDC、步進電動機、開關式磁阻電動機 SRM）。'
    },
    '05_電力系統': {
        'title': '05. 電力系統',
        'name': '電力系統',
        'desc': '標么系統（Per-Unit System、多電壓等級基準轉換）、輸電線路參數計算（GMD, GMR、電阻、電感、電容）與傳輸模型（短程、中程 π/T 型、長程雙曲函數分佈參數模型、突波阻抗負載 SIL）、電力潮流分析（匯流排分類 PQ/PV/Slack、節點導納矩陣 Ybus 建立、Gauss-Seidel 與 Newton-Raphson 疊代求解）、對稱成分法（Symmetrical Components、序網路阻抗）、電力系統故障分析（三相短路、單線接地 SLG、線間短路 L-L、雙線接地 DLG）、電力系統穩定度（轉子動力學、搖擺方程式 Swing Equation、等面積準則 Equal-Area Criterion、臨界清除角 CCT）、電力系統經濟調度（等微增燃料成本準則、考慮輸電線損失之協調方程式 Penalty Factor）、電壓控制與無效功率補償。'
    },
    '06_工業配電': {
        'title': '06. 工業配電',
        'name': '工業配電',
        'desc': '工廠配電系統架構（放射狀、環狀、主副選擇式）與受電電壓選擇、負載特性分析（需量因數、負載因數、參差因數、利用率、契約容量計算）、短路電流計算方法（標么法、歐姆法）與斷路器容量選定（對稱啟斷容量、啟斷時間、VCB, ACB, MCCB）、保護協調（過電流電驛 CO/LVP/OVR 標置曲線、時間乘率與始動電流、保護協調階梯圖）、功率因數改善（電力電容器容量計算、電容器組串聯電抗器抑制諧波、功因自動調整 APFR）、接地系統設計（系統接地、設備接地、接地電阻計算、跨步電壓與接觸電壓）、電動機配線設計（幹線與分路導線線徑選定、電動機過載保護與短路保護、Y-Δ 啟動與補償器啟動器）、變壓器容量選定與配線施工（PVC/EMT 配管、電纜槽）、諧波分析與抑制（電力品質、諧波標準 IEEE 519）。'
    }
}

for folder, meta in subj_info.items():
    subj_path = os.path.join('依考科分類', folder)
    if not os.path.isdir(subj_path):
        continue
    
    pdfs = sorted(glob.glob(f'{subj_path}/*.pdf'), reverse=True)
    years_data = []
    
    for pdf in pdfs:
        base = os.path.splitext(os.path.basename(pdf))[0]
        year_match = re.match(r'(\d+)年', base)
        year_str = year_match.group(1) if year_match else '—'
        pdf_fname = os.path.basename(pdf)
        
        parsed = parse_exam_file(pdf, folder, year_str)
        
        years_data.append({
            'year': year_str,
            'pdf_file': pdf_fname,
            'exam_code': parsed['exam_code'],
            'calc_rule': parsed['calc_rule'],
            'page_count': parsed['page_count'],
            'body': parsed['body'],
            'base_name': base
        })
    
    def generate_content(is_top_level=False):
        prefix_path = f'./{folder}/' if is_top_level else './'
        img_prefix = f'./{folder}/images/' if is_top_level else './images/'
        
        lines = []
        lines.append(f'# ⚡ 電機工程技師 歷屆試題彙編 — {meta["title"]}（104 ~ 114 年）\n')
        lines.append(f'> **考科核心範疇與常考重點**：\n> {meta["desc"]}\n')
        lines.append('> **說明**：本彙編完整收錄專門職業及技術人員高等考試電機工程技師自民國 104 年至 114 年（共 11 個年度，11 份完整官方試題）之試卷內容、考場規定、原版高解析度試卷圖檔對照與 PDF 原檔下載。\n')
        lines.append('---\n')
        
        # Table of Contents
        lines.append('<a id="toc"></a>\n')
        lines.append('## 📑 快速目錄導覽\n')
        lines.append('| 年度 | 考科名稱 | 試題代號 | 考試時間 | 計算器規範 | 快速跳轉試題 | 官方試卷 PDF |')
        lines.append('| :---: | :--- | :---: | :---: | :---: | :--- | :--- |')
        
        for data in years_data:
            y = data['year']
            pdf_link = f'{prefix_path}{data["pdf_file"]}'
            lines.append(f'| **{y} 年** | {meta["name"]} | `{data["exam_code"]}` | 2 小時 | {data["calc_rule"]} | [🔗 前往 {y} 年試題](#year-{y}) | [📄 {y}年 PDF]({pdf_link}) |')
        
        lines.append('\n---\n')
        
        # Content by year with explicit HTML anchors
        for data in years_data:
            y = data['year']
            bname = data['base_name']
            pdf_link = f'{prefix_path}{data["pdf_file"]}'
            
            lines.append(f'<a id="year-{y}"></a>\n')
            lines.append(f'## {y} 年 電機工程技師 — {meta["name"]}\n')
            lines.append(f'> **等別**：高等考試  ')
            lines.append(f'> **類科**：電機工程技師  ')
            lines.append(f'> **科目**：{meta["name"]}  ')
            lines.append(f'> **考試時間**：2 小時（120 分鐘）  ')
            lines.append(f'> **試題代號**：`{data["exam_code"]}`  ')
            lines.append(f'> **計算器規範**：{data["calc_rule"]}  ')
            lines.append(f'> **官方原始試題 PDF**：[📄 下載 {data["pdf_file"]}]({pdf_link})\n')
            
            lines.append('### 📝 試題內容與數學公式編排（LaTeX）\n')
            lines.append(data['body'])
            lines.append('\n')
            
            lines.append('### 📷 官方試卷與電路圖檔對照\n')
            
            p_count = data['page_count']
            if p_count == 1:
                img1 = f'{img_prefix}{bname}_p1.png'
                lines.append(f'![第1頁]({img1})\n')
            elif p_count == 2:
                img1 = f'{img_prefix}{bname}_p1.png'
                img2 = f'{img_prefix}{bname}_p2.png'
                lines.append(f'![第1頁]({img1})\n\n![第2頁]({img2})\n')
            elif p_count == 3:
                img1 = f'{img_prefix}{bname}_p1.png'
                img2 = f'{img_prefix}{bname}_p2.png'
                img3 = f'{img_prefix}{bname}_p3.png'
                lines.append(f'![第1頁]({img1})\n\n![第2頁]({img2})\n\n![第3頁]({img3})\n')
            
            lines.append('[⬆ 回到目錄導覽](#toc)\n')
            lines.append('---\n')
        
        return '\n'.join(lines)
    
    # Subject folder file
    subj_file = os.path.join(subj_path, f'{folder}_歷屆試題彙編_104-114年.md')
    with open(subj_file, 'w', encoding='utf-8') as f:
        f.write(generate_content(is_top_level=False))
    print(f'Updated: {subj_file}')
    
    # Top level file in 依考科分類/
    top_file = os.path.join('依考科分類', f'{folder}.md')
    with open(top_file, 'w', encoding='utf-8') as f:
        f.write(generate_content(is_top_level=True))
    print(f'Updated top-level: {top_file}')

print('All 6 subjects generated with Universal standard Markdown links, images, and HTML anchors!')
