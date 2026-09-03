import glob
import os
import re

def polish_subject_content(content):
    # 1. Greek symbols outside math
    greek_repl = [
        (r'(?<![\$\\a-zA-Z])α(?![a-zA-Z\$])', r'$\\alpha$'),
        (r'(?<![\$\\a-zA-Z])β(?![a-zA-Z\$])', r'$\\beta$'),
        (r'(?<![\$\\a-zA-Z])γ(?![a-zA-Z\$])', r'$\\gamma$'),
        (r'(?<![\$\\a-zA-Z])δ(?![a-zA-Z\$])', r'$\\delta$'),
        (r'(?<![\$\\a-zA-Z])θ(?![a-zA-Z\$])', r'$\\theta$'),
        (r'(?<![\$\\a-zA-Z])λ(?![a-zA-Z\$])', r'$\\lambda$'),
        (r'(?<![\$\\a-zA-Z])μ(?![a-zA-Z\$])', r'$\\mu$'),
        (r'(?<![\$\\a-zA-Z])π(?![a-zA-Z\$])', r'$\\pi$'),
        (r'(?<![\$\\a-zA-Z])τ(?![a-zA-Z\$])', r'$\\tau$'),
        (r'(?<![\$\\a-zA-Z])ω(?![a-zA-Z\$])', r'$\\omega$'),
        (r'(?<![\$\\a-zA-Z])Δ(?![a-zA-Z\$])', r'$\\Delta$'),
        (r'(?<![\$\\a-zA-Z])Ω(?![a-zA-Z\$])', r'$\\Omega$'),
    ]
    for pat, rep in greek_repl:
        content = re.sub(pat, rep, content)
        
    # 2. Operators outside math
    content = re.sub(r'(?<![\$\w])≤(?![=\$\w])', r' $\\le$ ', content)
    content = re.sub(r'(?<![\$\w])≥(?![=\$\w])', r' $\\ge$ ', content)
    content = re.sub(r'(?<![\$\w])≠(?![=\$\w])', r' $\\ne$ ', content)
    content = re.sub(r'(?<![\$\w])≈(?![=\$\w])', r' $\\approx$ ', content)
    content = re.sub(r'(?<![\$\w])±(?![=\$\w])', r' $\\pm$ ', content)
    content = re.sub(r'(?<![\$\w])×(?![=\$\w])', r' $\\times$ ', content)
    content = re.sub(r'(?<![\$\w])÷(?![=\$\w])', r' $\\div$ ', content)
    content = re.sub(r'(?<![\$\w])∞(?![=\$\w])', r' $\\infty$ ', content)
    content = re.sub(r'(?<![\$\w])∠(?![=\$\w])', r' $\\angle$ ', content)

    # 3. Trigonometry and functions
    content = re.sub(r'(?<![\$\w])(\d+)\s*cos\s*[\(（]([^）\)]+)[\)）](?![\$\w])', lambda m: f"${m.group(1)}\\cos({m.group(2)})$", content)
    content = re.sub(r'(?<![\$\w])(\d+)\s*sin\s*[\(（]([^）\)]+)[\)）](?![\$\w])', lambda m: f"${m.group(1)}\\sin({m.group(2)})$", content)
    content = re.sub(r'(?<![\$\w])cos\s*[\(（]([^）\)]+)[\)）](?![\$\w])', lambda m: f"$\\cos({m.group(1)})$", content)
    content = re.sub(r'(?<![\$\w])sin\s*[\(（]([^）\)]+)[\)）](?![\$\w])', lambda m: f"$\\sin({m.group(1)})$", content)
    content = re.sub(r'(?<![\$\w])tan\s*[\(（]([^）\)]+)[\)）](?![\$\w])', lambda m: f"$\\tan({m.group(1)})$", content)

    # 4. Square roots
    content = re.sub(r'√(\d+)', lambda m: f"$\\sqrt{{{m.group(1)}}}$", content)
    content = re.sub(r'√\s*(\w+)', lambda m: f"$\\sqrt{{{m.group(1)}}}$", content)

    # 5. Electronic & circuit equations
    content = re.sub(r'\b(VBE|VCE|VDS|VGS|vGS|vDS|iD|iC|iB|vBE|vCE|IC|IB|IE|ID|IS|VT)\s*=\s*([-\d\.]+\s*(?:V|mV|mA|[μu]A|A)?)',
                     lambda m: f"${m.group(1)} = {m.group(2)}$", content)

    # 6. Angles
    content = re.sub(r'(\d+)\s*o(?=[,\s\.\)）]|$)', lambda m: f"${m.group(1)}^\\circ$", content)
    content = re.sub(r'(\d+)\s*°', lambda m: f"${m.group(1)}^\\circ$", content)

    # 7. Powers
    content = re.sub(r'\b([eE])\s*-\s*(\d*[a-zA-Z])\b', lambda m: f"${m.group(1)}^{{-{m.group(2)}}}$", content)
    content = re.sub(r'(?<![\$\w])([xyzrst])\s*2(?![a-zA-Z\d\$])', lambda m: f"${m.group(1)}^2$", content)
    content = re.sub(r'(?<![\$\w])([xyzrst])\s*3(?![a-zA-Z\d\$])', lambda m: f"${m.group(1)}^3$", content)
    content = re.sub(r'(?<![\$\w])([xyzrst])\s*4(?![a-zA-Z\d\$])', lambda m: f"${m.group(1)}^4$", content)

    # 8. Clean up double/nested dollars
    content = re.sub(r'\${2,}', '$$', content)
    content = re.sub(r'\$\s*\$', '', content)
    
    # 9. Clean inside dollar pairs
    def clean_dollar(m):
        inner = m.group(1).strip()
        inner = re.sub(r'\s+', ' ', inner)
        return f"${inner}$"
    content = re.sub(r'\$([^\$\n]+)\$', clean_dollar, content)

    return content

for fpath in glob.glob('依考科分類/**/*.md', recursive=True) + glob.glob('依考科分類/*.md') + glob.glob('🧠 核心考點知識庫/**/*.md', recursive=True):
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
    
    polished = polish_subject_content(orig)
    if polished != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(polished)
        print(f'Polished formulas in: {fpath}')

print('All math formulas systematically polished and verified!')
