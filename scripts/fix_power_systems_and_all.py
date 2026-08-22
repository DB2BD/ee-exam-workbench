# -*- coding: utf-8 -*-
import re
import os

# 1. Fix 05_電力系統.md
power_file = '依考科分類/05_電力系統.md'
with open(power_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix currency dollar signs that break LaTeX
text = text.replace('其單位為$/h', '其單位為 $/h')
text = text.replace('$/h', r'\text{元/h}')
text = text.replace('$/hr', r'\text{元/h}')
text = text.replace('$/MWh', r'\text{元/MWh}')
text = text.replace('$/MW2h', r'\text{元/MW}^2\text{h}')
text = text.replace('增量成本λ為$8/MWh', r'增量成本 $\lambda = 8\text{ 元/MWh}$')
text = text.replace('λ為$10/MWh', r'$\lambda = 10\text{ 元/MWh}$')
text = text.replace('二座$800\\text{ MW}$', r'二座 $800\text{ MW}$')
text = text.replace('總功率需求為$550\\text{ MW}$', r'總功率需求為 $550\text{ MW}$')
text = text.replace('總功率需求為$1300\\text{ MW}$', r'總功率需求為 $1300\text{ MW}$')

# Fix split powers P1 2 -> P_1^2
text = re.sub(r'0\.004P1\s*2', r'0.004 P_1^2', text)
text = re.sub(r'0\.002P2\s*2', r'0.002 P_2^2', text)
text = re.sub(r'6\.0P1', r'6.0 P_1', text)
text = re.sub(r'6\.8P2', r'6.8 P_2', text)

with open(power_file, 'w', encoding='utf-8') as f:
    f.write(text)
print('✅ Fixed 05_電力系統.md currency and math expressions')

# 2. Fix 02_電子學_含電力電子.md
elec_file = '依考科分類/02_電子學_含電力電子.md'
with open(elec_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix fragmented variables
text = text.replace('Rs = $15\\text{ k}\\Omega$', '$R_s = 15\\text{ k}\\Omega$')
text = text.replace('Ra = $3\\text{ k}\\Omega$', '$R_a = 3\\text{ k}\\Omega$')
text = text.replace('Ca = $3\\text{ pF}$', '$C_a = 3\\text{ pF}$')
text = text.replace('Gm = $15\\text{ mA}$/V', '$G_m = 15\\text{ mA/V}$')
text = text.replace('RL =$1\\text{ k}\\Omega$', '$R_L = 1\\text{ k}\\Omega$')
text = text.replace('CL = $2\\text{ pF}$', '$C_L = 2\\text{ pF}$')
text = text.replace('L = $25\\text{ mH}$', '$L = 25\\text{ mH}$')
text = text.replace('R = 0.$5\\ \\Omega$', '$R = 0.5\\ \\Omega$')
text = text.replace('RC = RS = $2\\text{ k}\\Omega$', '$R_C = R_S = 2\\text{ k}\\Omega$')
text = text.replace('IS = $2\\text{ mA}$', '$I_S = 2\\text{ mA}$')

with open(elec_file, 'w', encoding='utf-8') as f:
    f.write(text)
print('✅ Fixed 02_電子學_含電力電子.md parameter formats')
