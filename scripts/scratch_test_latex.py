import re

def latexify_circuit(text):
    # Common circuit notation
    text = re.sub(r'(\d+)\s*[ΩΩ]', r'$\1\\ \\Omega$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*k[ΩΩ]', r'$\1\\text{ k}\\Omega$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*M[ΩΩ]', r'$\1\\text{ M}\\Omega$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*mH', r'$\1\\text{ mH}$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*[μu]F', r'$\1\\ \\mu\\text{F}$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*pF', r'$\1\\text{ pF}$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*kV', r'$\1\\text{ kV}$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*kVA', r'$\1\\text{ kVA}$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*MVA', r'$\1\\text{ MVA}$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*Mvar', r'$\1\\text{ Mvar}$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*kvar', r'$\1\\text{ kvar}$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*rad/s', r'$\1\\text{ rad/s}$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*Hz', r'$\1\\text{ Hz}$', text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*HP', r'$\1\\text{ HP}$', text)
    
    # Phasors and angles
    text = re.sub(r'(\d+(?:\.\d+)?)\s*∠\s*([-\d\.]+)\s*°?', r'$\1\\angle \2^\\circ$', text)
    text = re.sub(r'([I|V|E|Z][\w\d_]*)\s*∠\s*([-\w\d\.\+]+)\s*°?', r'$\1\\angle \2^\\circ$', text)
    
    # Time domain signals
    text = re.sub(r'\bvo\s*\(\s*t\s*\)', r'$v_o(t)$', text)
    text = re.sub(r'\bvo\b', r'$v_o$', text)
    text = re.sub(r'\bv1\b', r'$v_1$', text)
    text = re.sub(r'\bv2\b', r'$v_2$', text)
    text = re.sub(r'\bv3\b', r'$v_3$', text)
    text = re.sub(r'\bvs\s*\(\s*t\s*\)', r'$v_s(t)$', text)
    text = re.sub(r'\bis\s*\(\s*t\s*\)', r'$i_s(t)$', text)
    text = re.sub(r'\biL\s*\(\s*t\s*\)', r'$i_L(t)$', text)
    text = re.sub(r'\bvC\s*\(\s*t\s*\)', r'$v_C(t)$', text)
    text = re.sub(r'\bu\s*\(\s*t\s*\)', r'$u(t)$', text)
    text = re.sub(r'δ\s*\(\s*t\s*\)', r'$\\delta(t)$', text)
    text = re.sub(r'\bt\s*=\s*0\b', r'$t = 0$', text)
    text = re.sub(r'\bt\s*>\s*0\b', r'$t > 0$', text)
    text = re.sub(r'\bt\s*≥\s*0\b', r'$t \\ge 0$', text)
    text = re.sub(r'\bt\s*≤\s*0\b', r'$t \\le 0$', text)
    
    return text

print('Test latexify circuit:')
print(latexify_circuit('電流I = ?，節點電壓v1、v2、v3 分別為何？vo(t)在t > 0 時，is = 10 u(t) A，L = 25 mH，R = 0.5 Ω，34.5 kVrms，24 MVA，120∠20° Vrms'))
