import glob
import re
import os

def clean_math_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 1. Fuel cost formulas
    text = re.sub(r'C1\s*=\s*400\s*\+\s*6\.0\s*P1\s*\+\s*0\.004\s*\$?P1\^2\$?', lambda m: r'$C_1 = 400 + 6.0 P_1 + 0.004 P_1^2$', text)
    text = re.sub(r'C2\s*=\s*400\s*\+\s*6\.8\s*P2\s*\+\s*0\.002\s*\$?P2\^2\$?', lambda m: r'$C_2 = 400 + 6.8 P_2 + 0.002 P_2^2$', text)
    text = re.sub(r'\bP1\b', lambda m: r'$P_1$', text)
    text = re.sub(r'\bP2\b', lambda m: r'$P_2$', text)
    
    # 2. Voltage, Current, and Phasor equations
    text = re.sub(r'v\(t\)\s*=\s*\$?\\sqrt\{2\}\\times\$?\s*100\s*cos\s*[\(（]\s*(?:\\omega|ω)\s*t\s*\+\s*(?:\$\\alpha\$|\\alpha|α)\s*[\)）]\s*伏特[，,]\s*其相量為\s*100[∠\\angle]+(?:\$\\alpha\$|\\alpha|α)',
                  lambda m: r'$v(t) = \sqrt{2} \times 100 \cos(\omega t + \alpha)\text{ V}$，其相量為 $\mathbf{V} = 100\angle \alpha$', text)
    text = re.sub(r'i\(t\)\s*=\s*\$?\\sqrt\{2\}\$?Irmscos\s*[\(（]\s*(?:\\omega|ω)\s*t\s*\+\s*\$?60\^\\circ\$?\s*[\)）]\s*安培[，,]\s*其相量為\s*\$?Irms\\angle 60\^\\circ\$?',
                  lambda m: r'$i(t) = \sqrt{2} I_{\text{rms}} \cos(\omega t + 60^\circ)\text{ A}$，其相量為 $\mathbf{I} = I_{\text{rms}}\angle 60^\circ$', text)
    text = re.sub(r'Irms', lambda m: r'$I_{\text{rms}}$', text)
    
    # 3. Subscripts for electrical parameters
    text = re.sub(r'\bE1\s*=\s*', lambda m: r'$E_1 = $', text)
    text = re.sub(r'\bE2\b', lambda m: r'$E_2$', text)
    text = re.sub(r'\by12\s*=\s*', lambda m: r'$y_{12} = $', text)
    text = re.sub(r'\\delta\s*2\b', lambda m: r'\\delta_2', text)
    text = re.sub(r'\|\s*E2\s*\|', lambda m: r'$|E_2|$', text)
    
    # 4. Clean double dollars or broken nested dollars
    text = re.sub(r'\${2,}', lambda m: r'$$', text)
    text = re.sub(r'\$\s*\$', lambda m: r'', text)
    text = re.sub(r'\$\s*([^\$\n]+?)\s*\$', lambda m: f"${m.group(1)}$", text)
    text = re.sub(r'\$\s*\$', lambda m: r'', text)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(text)

for fpath in glob.glob('依考科分類/**/*.md', recursive=True) + glob.glob('依考科分類/*.md'):
    clean_math_file(fpath)

print('Cleaned math formatting across all subject files.')
