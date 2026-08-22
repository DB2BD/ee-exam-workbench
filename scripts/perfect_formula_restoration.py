import glob
import os
import re

def deep_restore_exam_text(content):
    # 1. Multi-line split powers like P1 \n 2 or x \n 2 or s \n 2
    content = re.sub(r'([P|Q|S|V|I|E|x|y|z|s|t]\d?)\s*\n\s*2(?=[，,、\s\.\)）]|$)', lambda m: f"${m.group(1)}^2$", content)
    content = re.sub(r'([P|Q|S|V|I|E|x|y|z|s|t]\d?)\s*\n\s*3(?=[，,、\s\.\)）]|$)', lambda m: f"${m.group(1)}^3$", content)
    content = re.sub(r'([P|Q|S|V|I|E|x|y|z|s|t]\d?)\s*\n\s*4(?=[，,、\s\.\)）]|$)', lambda m: f"${m.group(1)}^4$", content)

    # 2. Fuel cost equations in power systems
    content = re.sub(r'C1\s*=\s*400\s*\+\s*6\.0P1\s*\+\s*0\.004P1\^2', lambda m: r'$C_1 = 400 + 6.0 P_1 + 0.004 P_1^2$', content)
    content = re.sub(r'C2\s*=\s*400\s*\+\s*6\.8P2\s*\+\s*0\.002P2\^2', lambda m: r'$C_2 = 400 + 6.8 P_2 + 0.002 P_2^2$', content)
    content = re.sub(r'C1\s*=\s*400\s*\+\s*6\.0P1\s*\+\s*0\.004P1\s*2', lambda m: r'$C_1 = 400 + 6.0 P_1 + 0.004 P_1^2$', content)
    content = re.sub(r'C2\s*=\s*400\s*\+\s*6\.8P2\s*\+\s*0\.002P2\s*2', lambda m: r'$C_2 = 400 + 6.8 P_2 + 0.002 P_2^2$', content)

    # 3. Voltage and Current phasors
    content = re.sub(r'v\(t\)\s*=\s*(?:\\sqrt\{2\}|\$?\\sqrt\{2\}\$?)\s*(?:\\times|\$?\\times\$?)\s*100\s*cos\s*[\(（]\s*(?:\\omega|ω)\s*t\s*\+\s*(?:\\alpha|α)\s*[\)）]\s*伏特[，,]\s*其相量為\s*100[∠\\angle]+\s*(?:\\alpha|α)',
                     lambda m: r'$v(t) = \sqrt{2} \times 100 \cos(\omega t + \alpha)\text{ V}$，其相量為 $\mathbf{V} = 100\angle \alpha$', content)
    content = re.sub(r'i\(t\)\s*=\s*(?:\\sqrt\{2\}|\$?\\sqrt\{2\}\$?)\s*Irmscos\s*[\(（]\s*(?:\\omega|ω)\s*t\s*\+\s*60[^\)）]*[\)）]\s*安培[，,]\s*其相量為\s*\$?Irms\\angle 60\^\\circ\$?',
                     lambda m: r'$i(t) = \sqrt{2} I_{\text{rms}} \cos(\omega t + 60^\circ)\text{ A}$，其相量為 $\mathbf{I} = I_{\text{rms}}\angle 60^\circ$', content)
    content = re.sub(r'實功率P\(real power\)\s*=\s*500(?:\\sqrt\{3\}|\$?\\sqrt\{3\}\$?)\s*W[，,]\s*虛功率Q\s*\(reactive power\)\s*=\s*500\s*Var',
                     lambda m: r'實功率 $P = 500\sqrt{3}\text{ W}$，虛功率 $Q = 500\text{ Var}$', content)

    # 4. Electronic parameters
    content = re.sub(r'Q1\s*=\s*Q2[，,]\s*β\s*=\s*40[，,]\s*ro\s*=\s*∞', lambda m: r'$Q_1 = Q_2, \beta = 40, r_o = \infty$', content)
    content = re.sub(r'VS\s*=\s*5\s*V[，,]\s*E\s*=\s*10\s*V[。.]\s*定義時間常數τ\s*=\s*L/R[，,]\s*請算0\s*≤\s*t\s*≤\s*1\s*ms',
                     lambda m: r'$V_S = 5\text{ V}, E = 10\text{ V}$。定義時間常數 $\tau = L/R$，請計算 $0 \le t \le 1\text{ ms}$', content)
    content = re.sub(r'β\s*=\s*100[、,]\s*VBE\s*=\s*0\.7V[。.]\s*VA\s*=\s*∞[、,]\s*Cπ\s*=\s*\$?10\\text\{ pF\}\$?[、,]\s*Cμ\s*=\s*\$?1\\text\{ pF\}\$?',
                     lambda m: r'$\beta = 100, V_{BE} = 0.7\text{ V}, V_A = \infty, C_\pi = 10\text{ pF}, C_\mu = 1\text{ pF}$', content)

    # 5. Clean stray diagram lines like 圖二匯流排之電力系統
    content = re.sub(r'(?m)^\s*圖[一二三四五六七八九十\d]+.*$\n?', '', content)

    # 6. Clean and harmonize math delimiters
    content = re.sub(r'\${3,}', '$$', content)

    return content

for fpath in glob.glob('依考科分類/**/*.md', recursive=True) + glob.glob('依考科分類/*.md'):
    with open(fpath, 'r', encoding='utf-8') as f:
        orig = f.read()
    
    restored = deep_restore_exam_text(orig)
    if restored != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(restored)
        print(f'Restored equations in: {fpath}')

print('Completed deep restoration of formulas across all subjects!')
