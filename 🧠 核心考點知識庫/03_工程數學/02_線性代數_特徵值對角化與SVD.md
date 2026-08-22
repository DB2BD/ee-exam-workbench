# 📐 工程數學 核心考點 02 — 線性代數：特徵值與矩陣分解

## 📌 核心觀念與定義
1. **特徵值與特徵向量（Eigenvalues & Eigenvectors）**：
   - 特徵方程式：$\det(\mathbf{A} - \lambda \mathbf{I}) = 0$
   - 求解 $(\mathbf{A} - \lambda_i \mathbf{I})\mathbf{v}_i = \mathbf{0}$ 得到特徵向量 $\mathbf{v}_i$。
2. **矩陣對角化（Diagonalization）**：
   - 若 $n \times n$ 方陣 $\mathbf{A}$ 具有 $n$ 個線性獨立特徵向量，則令特徵向量矩陣 $\mathbf{P} = [\mathbf{v}_1 \ \mathbf{v}_2 \ \dots \ \mathbf{v}_n]$：
     $$\mathbf{P}^{-1} \mathbf{A} \mathbf{P} = \mathbf{D} = \begin{bmatrix} \lambda_1 & 0 & \dots \\ 0 & \lambda_2 & \dots \\ \vdots & \vdots & \ddots \end{bmatrix}$$
   - 矩陣次方：$\mathbf{A}^k = \mathbf{P} \mathbf{D}^k \mathbf{P}^{-1}$
3. **奇異值分解（Singular Value Decomposition, SVD）**：
   - 任何 $m \times n$ 矩陣 $\mathbf{A}$ 可分解為：$\mathbf{A} = \mathbf{U} \mathbf{\Sigma} \mathbf{V}^T$
   - 奇異值 $\sigma_i = \sqrt{\lambda_i(\mathbf{A}^T \mathbf{A})}$（按降序排列 $\sigma_1 \ge \sigma_2 \ge \dots \ge 0$）。
4. **二次型極值（Quadratic Form）**：
   - $\max_{\|\mathbf{x}\|=1} \mathbf{x}^T \mathbf{A} \mathbf{x} = \lambda_{\max}(\mathbf{A})$，$\min_{\|\mathbf{x}\|=1} \mathbf{x}^T \mathbf{A} \mathbf{x} = \lambda_{\min}(\mathbf{A})$。

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第五題**：線性方程組 $\mathbf{A}\mathbf{x} = \mathbf{b}$ 之完整解與零空間 $N(\mathbf{A})$。
- **113 年 第四題**：Lyapunov 方程式 $\mathbf{P}\mathbf{A} + \mathbf{A}^T\mathbf{P} = -\mathbf{I}$ 與特徵值。
- **111 年 第四題**：奇異值 SVD 與二次型 $\mathbf{x}^T \mathbf{A} \mathbf{x}$ 最大最小值。
- **108 年 第二題**：$3 \times 3$ 矩陣特徵值與特徵向量。
