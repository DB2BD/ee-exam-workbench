# -*- coding: utf-8 -*-
"""
fix_final_59_issues.py
======================
Direct, pristine surgical fixes for all remaining 59 line delimiter issues.
"""

import os
import re
import glob

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix_content(content):
    # 1. Industrial Distribution compiler files
    content = content.replace("$$69\\text{ kV}$/$3.3\\text{ kV}$", "$69\\text{ kV} / 3.3\\text{ kV}$")
    content = content.replace("22.8\\text{ kV}$/$3.3\\text{ kV}$", "$22.8\\text{ kV} / 3.3\\text{ kV}$")
    content = content.replace("3 相$161\\text{ kV}$/$33\\text{ kV}$，100\\text{ MVA}$", "3 相 $161\\text{ kV} / 33\\text{ kV}$，$100\\text{ MVA}$")
    content = content.replace("短路容量為 100\\text{ MVA}$", "短路容量為 $100\\text{ MVA}$")
    content = content.replace("分別為$2000\\text{ kVA}$、22.8\\text{ kV}/480\\text{ V}$", "分別為 $2000\\text{ kVA}$、$22.8\\text{ kV}/480\\text{ V}$")
    content = content.replace("主變壓器額定$2000\\text{ kVA}$，11.4\\text{ kV}/480\\text{ V}$", "主變壓器額定 $2000\\text{ kVA}$，$11.4\\text{ kV}/480\\text{ V}$")
    content = content.replace("次暫態電抗同為 25\\%，", "次暫態電抗同為 $25\\%$，")
    content = content.replace("已知矩陣 $A =", "已知矩陣 $A$：")
    content = content.replace("求矩陣 $A =", "求矩陣 $A$：")

    # 2. Circuit 104, 105, 107, 108, 113
    content = content.replace("（20 分）」$", "（20 分）」")
    content = content.replace("2 - $j1\\ \\Omega$", "2 - j1\\ \\Omega$")
    content = content.replace("2. I_1 = 0$ 使得", "2. $I_1 = 0$ 使得")
    content = content.replace("* V_1 = v + 6 = -8 + 6 = -2\\text{ V} \\implies$", "* $V_1 = v + 6 = -8 + 6 = -2\\text{ V} \\implies$")
    content = content.replace("* v_2 = V_4 - V_3 = -4 - 0 = -4\\text{ V} \\implies \\frac{3}{2}v_2 = -6\\text{ A}$$（向下流入地）。", "* $v_2 = V_4 - V_3 = -4 - 0 = -4\\text{ V} \\implies \\frac{3}{2}v_2 = -6\\text{ A}$（向下流入地）。")
    content = content.replace("(2 + j2)\\mathbf{V}_1 - j\\mathbf{V}_2 = 10 \\quad \\text{--- (式 1')}$$", "$$(2 + j2)\\mathbf{V}_1 - j\\mathbf{V}_2 = 10 \\quad \\text{--- (式 1')}$$")
    content = re.sub(r'-\s+g_{11}\s*=\s*\\left\.\\frac\{\\mathbf\{I\}_1\}\{\\mathbf\{V\}_1\}\\right\|_\{[^\}]+\},\s*\\quad\s*g_\{21\}\s*=\s*\\left\.\\frac\{\\mathbf\{V\}_2\}\{\\mathbf\{V\}_1\}\\right\|_\{[^\}]+\}\$\$（埠 2 開路條件）', r'- $g_{11} = \\left.\\frac{\\mathbf{I}_1}{\\mathbf{V}_1}\\right|_{\\mathbf{I}_2=0}, \\quad g_{21} = \\left.\\frac{\\mathbf{V}_2}{\\mathbf{V}_1}\\right|_{\\mathbf{I}_2=0}$（埠 2 開路條件）', content)
    content = re.sub(r'-\s+g_{12}\s*=\s*\\left\.\\frac\{\\mathbf\{I\}_1\}\{\\mathbf\{I\}_2\}\\right\|_\{[^\}]+\},\s*\\quad\s*g_\{22\}\s*=\s*\\left\.\\frac\{\\mathbf\{V\}_2\}\{\\mathbf\{I\}_2\}\\right\|_\{[^\}]+\}\$\$（埠 1 短路條件）', r'- $g_{12} = \\left.\\frac{\\mathbf{I}_1}{\\mathbf{I}_2}\\right|_{\\mathbf{V}_1=0}, \\quad g_{22} = \\left.\\frac{\\mathbf{V}_2}{\\mathbf{I}_2}\\right|_{\\mathbf{V}_1=0}$（埠 1 短路條件）', content)

    # 3. Electronics 113, 114
    content = content.replace("1. D_1$ 導通", "1. $D_1$ 導通")
    content = content.replace("2. D_2$ 導通", "2. $D_2$ 導通")
    content = content.replace("1. D_1$ 截止", "1. $D_1$ 截止")
    content = content.replace("> A_v(s) = \\frac{v_o}{v_s} \\approx A_{vo} \\frac{1 + \\frac{s}{\\omega_z}}{1 + \\frac{s}{\\omega_H}}$$", "> $$A_v(s) = \\frac{v_o}{v_s} \\approx A_{vo} \\frac{1 + \\frac{s}{\\omega_z}}{1 + \\frac{s}{\\omega_H}}$$")

    # 4. Eng Math 105, 106, 109, 110, 112, GK 112
    content = content.replace("## 一、 請求出矩陣 $\\mathbf{A}：", "## 一、 請求出矩陣 $\\mathbf{A}$：")
    content = content.replace("## 四、 假設矩陣 $\\mathbf{A}：", "## 四、 假設矩陣 $\\mathbf{A}$：")
    content = content.replace("：$$$\n\n---", "：\n\n---")
    content = content.replace(".$$\n\n---", ".\n\n---")
    content = content.replace("。$$$\n\n---", "。\n\n---")
    content = content.replace(", \\mathbf{x}(0) = \\begin{bmatrix} 1 \\\\ 2 \\end{bmatrix}，利用矩陣指數 $e^{At}$求解。（20 分）", "且 $\\mathbf{x}(0) = \\begin{bmatrix} 1 \\\\ 2 \\end{bmatrix}$，利用矩陣指數 $e^{At}$ 求解。（20 分）")

    # 5. Power 106, 112
    content = content.replace("- $$\\mathbf{Z}_{bus}$ 元素：", "- $\\mathbf{Z}_{bus}$ 元素：")
    content = content.replace("(\\delta_{cr} - \\delta_0) + \\cos\\delta_{cr} - \\cos\\delta_0 = 1.5625\\cos\\delta_{cr} - 1.5625\\cos\\delta", "$$(\\delta_{cr} - \\delta_0) + \\cos\\delta_{cr} - \\cos\\delta_0 = 1.5625\\cos\\delta_{cr} - 1.5625\\cos\\delta_0$$")

    # 6. Industrial Distribution 111, 114
    content = content.replace("選用標準品 **$200\\text{ AT} / 225\\text{ AF}$**$。", "選用標準品 **$200\\text{ AT} / 225\\text{ AF}$**。")
    content = content.replace("- 容量比（Capacity Ratio）：\\frac{S_V}{S_\\Delta} = \\frac{\\sqrt{3} S_{1\\phi}}{3 S_{1\\phi}} = \\frac{1}{\\sqr", "- 容量比（Capacity Ratio）：$\\frac{S_V}{S_\\Delta} = \\frac{\\sqrt{3} S_{1\\phi}}{3 S_{1\\phi}} = \\frac{1}{\\sqrt{3}} \\approx 57.7\\%$")
    content = content.replace("- 利用率（Utilization Factor）：\\frac{S_V}{2 S_{1\\phi}} = \\frac{\\sqrt{3} S_{1\\phi}}{2 S_{1\\phi}} = \\frac{", "- 利用率（Utilization Factor）：$\\frac{S_V}{2 S_{1\\phi}} = \\frac{\\sqrt{3} S_{1\\phi}}{2 S_{1\\phi}} = \\frac{\\sqrt{3}}{2} \\approx 86.6\\%$")
    content = content.replace("$$\\Delta V\\% =  \\frac{V_{斷弧} - V_{短路}}{V_{額定}} \\times 100\\%", "$$\\Delta V\\% = \\frac{V_{斷弧} - V_{短路}}{V_{額定}} \\times 100\\%$$")
    content = content.replace("$$I = 0 \\implies  V_{二次側} = 1.0\\text{ pu} \\implies \\text{壓降 } \\Delta V_{斷弧} = \\mathbf{0\\%}", "$$I = 0 \\implies V_{二次側} = 1.0\\text{ pu} \\implies \\text{壓降 } \\Delta V_{斷弧} = \\mathbf{0\\%}$$")

    # Clean any trailing $ after Chinese periods
    content = re.sub(r'([。，；：）])\$(?=[。，；：\s\n]|$)', r'\1', content)

    return content

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        orig = f.read()
    content = fix_content(orig)
    if content != orig:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = sorted(glob.glob(os.path.join(WORKSPACE, '**', '*.md'), recursive=True))
    count = 0
    for f in files:
        if '.git' in f or 'node_modules' in f:
            continue
        if fix_file(f):
            count += 1
            print(f"✨ Surgical Fix: {os.path.relpath(f, WORKSPACE)}")
            
    print(f"\n🎉 Cleaned {count} files.")

if __name__ == '__main__':
    main()
