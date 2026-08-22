import re
import os

def clean_remaining_snippets():
    replacements = [
        # 113 Math Q5(二)
        (r'\* \*\*(二)\*\* 試求一向量函數[\s\S]*?S x\s*y\s*z\s*=\s*9\s*S[\s\S]*?。（10 分）',
         r'* **(二)** 試求一向量函數 $\mathbf{F} = 7x\mathbf{i} + 3y\mathbf{j} - z\mathbf{k}$ 之面積分 $\iint_S \mathbf{F} \cdot \mathbf{n} dA$，其中 $\mathbf{n}$ 為 $dA$ 指向外的法線方向單位向量，且此有界封閉曲面的表示式為 $S: x^2 + y^2 + z^2 = 9$。（10 分）'),
        (r'\* \*\*(二)\*\* 試求一向量函數[\s\S]*?=\s*。（10 分）',
         r'* **(二)** 試求一向量函數 $\mathbf{F} = 7x\mathbf{i} + 3y\mathbf{j} - z\mathbf{k}$ 之面積分 $\iint_S \mathbf{F} \cdot \mathbf{n} dA$，其中 $\mathbf{n}$ 為 $dA$ 指向外的法線方向單位向量，且此有界封閉曲面的表示式為 $S: x^2 + y^2 + z^2 = 9$。（10 分）'),
        (r'E\{\s*X3Y2\s*\}', r'$E\{X^3 Y^2\}$'),
        (r'E\{\s*Y\s*\}', r'$E\{Y\}$'),
        (r'k 值', r'$k$ 值'),
        (r'#### 五、\\n\\n\* \*\*(一)\*\*', r'#### 五、\n\n* **(一)**'),
        (r'\$y\\\'\\\'\(t\)', r'$y\'\'(t)'),
        (r'\$y\\\'\(t\)', r'$y\'(t)'),
    ]

    for root, dirs, files in os.walk('依考科分類'):
        for file in files:
            if file.endswith('.md'):
                fpath = os.path.join(root, file)
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pat, repl in replacements:
                    content = re.sub(pat, lambda m: repl, content)

                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)

clean_remaining_snippets()
print('Remaining snippets cleaned successfully!')
