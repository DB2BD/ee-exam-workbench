import glob
import re

for fpath in glob.glob('依考科分類/**/*.md', recursive=True) + glob.glob('依考科分類/*.md'):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix \ne (not equal)
    content = content.replace('\\beta \n e 0', '\\beta \\ne 0')
    content = content.replace('\\beta \ne 0', '\\beta \\ne 0')
    content = content.replace('\\beta\n e 0', '\\beta \\ne 0')

    # Fix 113 Math Q5
    q5_pat = r'\* \*\*(二)\*\* 試求一向量函數\n7[\s\S]*?=\s*。（10 分）'
    q5_rep = r'* **(二)** 試求一向量函數 $\mathbf{F} = 7x\mathbf{i} + 3y\mathbf{j} - z\mathbf{k}$ 之面積分 $\iint_S \mathbf{F} \cdot \mathbf{n} dA$，其中 $\mathbf{n}$ 為 $dA$ 指向外的法線方向單位向量，且此有界封閉曲面的表示式為 $S: x^2 + y^2 + z^2 = 9$。（10 分）'
    content = re.sub(q5_pat, lambda m: q5_rep, content)

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

print('Fixed LaTeX symbols and Q5 across all files!')
