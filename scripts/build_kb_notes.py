import os

# Base directory
base_kb = '🧠 核心考點知識庫'

kb_data = {
    '01_電路學': [
        {
            'file': '01_直流電路與戴維寧諾頓等效.md',
            'title': '直流電路分析、戴維寧定理與諾頓等效 SOP',
            'content': r'''# ⚡ 電路學 核心考點 01 — 直流電路與戴維寧／諾頓等效

## 📌 核心觀念與定義
1. **節點電壓法（Nodal Analysis）**：以基準節點（接地點）為 $0\text{ V}$，列寫非基準節點之 KCL 方程式：$\sum I_{\text{out}} = 0$。若節點間含獨立電壓源，則定義**超節點（Supernode）**。
2. **網目電流法（Mesh Analysis）**：以各網目之順時針迴路電流為變數，列寫 KVL 方程式：$\sum V = 0$。若網目間含獨立電流源，則定義**超網目（Supermesh）**。
3. **戴維寧等效電路（Thevenin Equivalent）**：
   - 戴維寧開路電壓 $V_{th} = V_{oc}$（端點 $a-b$ 開路電壓）。
   - 戴維寧等效阻抗 $R_{th}$：
     - 若電路**僅含獨立源**：將所有獨立電壓源短路、獨立電流源開路，求端點間等效電阻。
     - 若電路**含相依源**：方法一為外加測試電源 $V_{\text{test}} = 1\text{ V}$ 求 $I_{\text{test}}$，則 $R_{th} = \frac{V_{\text{test}}}{I_{\text{test}}}$；方法二為求短路電流 $I_{sc}$，則 $R_{th} = \frac{V_{oc}}{I_{sc}}$。
4. **最大功率轉移定理（Maximum Power Transfer）**：
   - 當負載電阻 $R_L = R_{th}$ 時，負載可獲得最大功率：
     $$P_{L,\max} = \frac{V_{th}^2}{4 R_{th}}$$

---

## 📐 必備考場核心公式
$$\begin{aligned}
\text{戴維寧等效：} \quad & V_{th} = V_{oc}, \quad R_{th} = \frac{V_{oc}}{I_{sc}} \\
\text{諾頓等效：} \quad & I_N = I_{sc}, \quad R_N = R_{th} \\
\text{最大功率轉移：} \quad & P_{\max} = \frac{V_{th}^2}{4 R_{th}} = \frac{I_N^2 R_N}{4}
\end{aligned}$$

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第一題、第二題**：節點電壓法與諾頓等效電路求解。
- **113 年 第一題**：含流控相依電流源之直流電路功率計算。
- **109 年 第一題**：含相依源之戴維寧等效電路與最大功率。
'''
        },
        {
            'file': '02_交流穩態相量與功率因數改善.md',
            'title': '交流穩態相量、複數功率與功率因數改善',
            'content': r'''# ⚡ 電路學 核心考點 02 — 交流穩態相量與功率因數改善

## 📌 核心觀念與定義
1. **相量表示法（Phasor Domain）**：
   - 時域弦波 $v(t) = V_m \cos(\omega t + \theta)$ $\rightarrow$ 相量 $\mathbf{V} = V_{\text{rms}} \angle \theta = \frac{V_m}{\sqrt{2}} \angle \theta$。
   - 電阻阻抗：$\mathbf{Z}_R = R$
   - 電感阻抗：$\mathbf{Z}_L = j\omega L = \omega L \angle 90^\circ$
   - 電容阻抗：$\mathbf{Z}_C = \frac{1}{j\omega C} = -j\frac{1}{\omega C} = \frac{1}{\omega C} \angle -90^\circ$
2. **複數功率（Complex Power $\mathbf{S}$）**：
   $$\mathbf{S} = \mathbf{V}_{\text{rms}} \mathbf{I}_{\text{rms}}^* = P + jQ = |\mathbf{S}| \angle \theta$$
   - **實功率（Average / Real Power $P$）**：$P = |\mathbf{V}| |\mathbf{I}| \cos(\theta_v - \theta_i) \quad [\text{W}]$
   - **虛功率（Reactive Power $Q$）**：$Q = |\mathbf{V}| |\mathbf{I}| \sin(\theta_v - \theta_i) \quad [\text{var}]$（電感性負載 $Q > 0$，電容性負載 $Q < 0$）
   - **視在功率（Apparent Power $S$）**：$S = |\mathbf{S}| = \sqrt{P^2 + Q^2} \quad [\text{VA}]$
   - **功率因數（Power Factor $PF$）**：$\text{PF} = \cos\theta = \frac{P}{S}$（滯後 Lagging: 電感性；超前 Leading: 電容性）
3. **功率因數改善（Power Factor Correction）**：
   - 將功率因數由 $\cos\theta_1$ 提升至 $\cos\theta_2$（$\theta_2 < \theta_1$），需並聯之電容器容量 $Q_C$：
     $$Q_C = P (\tan\theta_1 - \tan\theta_2) = \omega C V_{\text{rms}}^2$$
   - 並聯電容量：
     $$C = \frac{P (\tan\theta_1 - \tan\theta_2)}{\omega V_{\text{rms}}^2}$$

---

## 🎯 歷屆技師高頻出題年份
- **113 年 第二題**：交流穩態相量與時域響應轉換。
- **110 年 第二題**：三相負載之複數功率與功率因數補償計算。
- **108 年 第三題**：交流電路最大功率轉移（$\mathbf{Z}_L = \mathbf{Z}_{th}^*$）。
'''
        },
        {
            'file': '03_一階與二階RLC暫態響應.md',
            'title': '一階 RL/RC 與二階 RLC 暫態響應求解 SOP',
            'content': r'''# ⚡ 電路學 核心考點 03 — 一階與二階 RLC 暫態響應

## 📌 核心解題 SOP
1. **開關切換連續性定律**：
   $$i_L(0^+) = i_L(0^-), \quad v_C(0^+) = v_C(0^-)$$
2. **一階電路步階響應三要素公式**：
   $$x(t) = x(\infty) + [x(0^+) - x(\infty)] e^{-t/\tau}, \quad t \ge 0$$
   - $RC$ 電路時間常數：$\tau = R_{th} C$
   - $RL$ 電路時間常數：$\tau = \frac{L}{R_{th}}$
3. **二階 RLC 電路特徵根與響應分類**：
   - 特徵方程式：$s^2 + 2\alpha s + \omega_0^2 = 0 \implies s_{1,2} = -\alpha \pm \sqrt{\alpha^2 - \omega_0^2}$
   - **串聯 RLC**：$\alpha = \frac{R}{2L}, \quad \omega_0 = \frac{1}{\sqrt{LC}}$
   - **並聯 RLC**：$\alpha = \frac{1}{2RC}, \quad \omega_0 = \frac{1}{\sqrt{LC}}$
   - **阻尼狀態判定**：
     - $\alpha > \omega_0$：**過阻尼（Overdamped）**，$x(t) = A_1 e^{s_1 t} + A_2 e^{s_2 t} + x(\infty)$
     - $\alpha = \omega_0$：**臨界阻尼（Critically Damped）**，$x(t) = (A_1 + A_2 t) e^{-\alpha t} + x(\infty)$
     - $\alpha < \omega_0$：**欠阻尼（Underdamped）**，$x(t) = e^{-\alpha t} (A_1 \cos\omega_d t + A_2 \sin\omega_d t) + x(\infty)$，其中 $\omega_d = \sqrt{\omega_0^2 - \alpha^2}$。

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第三題**：開關切換一階/二階暫態初值與時域表示式。
- **112 年 第三題**：二階並聯 RLC 電路欠阻尼暫態響應。
- **107 年 第二題**：一階 RL 電路脈衝激勵響應。
'''
        }
    ],
    '03_工程數學': [
        {
            'file': '01_常微分方程ODE與尤拉柯西方程.md',
            'title': '常微分方程（一階、二階常係數線性 ODE、尤拉-柯西方程）',
            'content': r'''# 📐 工程數學 核心考點 01 — 常微分方程（ODE）

## 📌 核心解題 SOP
1. **一階線性常微分方程**：$y' + P(x) y = Q(x)$
   - 積分因子：$I(x) = e^{\int P(x) dx}$
   - 通解公式：$y(x) = \frac{1}{I(x)} \left[ \int I(x) Q(x) dx + C \right]$
2. **二階常係數齊次線性 ODE**：$y'' + a y' + b y = 0$
   - 特徵方程：$\lambda^2 + a\lambda + b = 0$
   - 實相異根 $\lambda_1 \ne \lambda_2 \implies y_h = c_1 e^{\lambda_1 x} + c_2 e^{\lambda_2 x}$
   - 重根 $\lambda_1 = \lambda_2 \implies y_h = (c_1 + c_2 x) e^{\lambda_1 x}$
   - 複數共軛根 $\lambda = \alpha \pm j\beta \implies y_h = e^{\alpha x} (c_1 \cos\beta x + c_2 \sin\beta x)$
3. **二階非齊次 ODE 特解求法（參數變異法 Method of Variation of Parameters）**：
   $$y_p(x) = -y_1(x) \int \frac{y_2(x) r(x)}{W(y_1, y_2)} dx + y_2(x) \int \frac{y_1(x) r(x)}{W(y_1, y_2)} dx$$
   其中朗斯基行列式（Wronskian）$W(y_1, y_2) = \begin{vmatrix} y_1 & y_2 \\ y_1' & y_2' \end{vmatrix} = y_1 y_2' - y_1' y_2$。
4. **尤拉-柯西方程（Euler-Cauchy Equation）**：
   $$x^2 y'' + a x y' + b y = 0$$
   令 $y = x^m \implies m(m-1) + a m + b = 0 \implies m^2 + (a-1)m + b = 0$。

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第三題**：$y'' + 4y' + 4y = 0$ 重根初始值問題。
- **113 年 第一題**：$y'' + 4y' + 5y = e^{-2x} \csc x$ 參數變異法求解。
- **111 年 第一題**：降階法（Reduction of Order）已知一解求通解。
- **109 年 第一題**：二階非齊次常係數 ODE 待定係數法。
'''
        },
        {
            'file': '02_線性代數_特徵值對角化與SVD.md',
            'title': '線性代數：特徵值、特徵向量、對角化與奇異值分解 SVD',
            'content': r'''# 📐 工程數學 核心考點 02 — 線性代數：特徵值與矩陣分解

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
'''
        },
        {
            'file': '03_複變函數與留數定理.md',
            'title': '複變函數：柯西積分公式、羅倫級數與留數定理',
            'content': r'''# 📐 工程數學 核心考點 03 — 複變函數與留數定理

## 📌 核心解題 SOP
1. **柯西-黎曼方程式（Cauchy-Riemann Equations）**：
   - $f(z) = u(x,y) + i v(x,y)$ 為解析函數的充要條件：
     $$\frac{\partial u}{\partial x} = \frac{\partial v}{\partial y}, \quad \frac{\partial u}{\partial y} = -\frac{\partial v}{\partial x}$$
2. **柯西積分公式（Cauchy\'s Integral Formula）**：
   $$\oint_C \frac{f(z)}{z - z_0} dz = 2\pi i f(z_0)$$
   $$\oint_C \frac{f(z)}{(z - z_0)^{n+1}} dz = \frac{2\pi i}{n!} f^{(n)}(z_0)$$
3. **留數定理（Residue Theorem）**：
   $$\oint_C f(z) dz = 2\pi i \sum_{k=1}^m \text{Res}(f, z_k)$$
   - 一階極點（Simple Pole）：$\text{Res}(f, z_0) = \lim_{z \to z_0} (z - z_0) f(z)$
   - $m$ 階極點（Pole of order $m$）：
     $$\text{Res}(f, z_0) = \frac{1}{(m-1)!} \lim_{z \to z_0} \frac{d^{m-1}}{dz^{m-1}} \left[ (z - z_0)^m f(z) \right]$$
   - 本性奇異點（Essential Singularity）：將函數展開為羅倫級數（Laurent Series），取 $\frac{1}{z - z_0}$ 之係數 $b_1$。

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第二題**：本性奇異點複數積分 $\oint_C e^{1/z^2} dz$。
- **113 年 第三題**：利用留數定理計算實數瑕積分 $\int_{-\infty}^\infty \frac{1}{x^4 + 16} dx$。
- **112 年 第二題**：柯西-黎曼方程式求解調和共軛函數 $v(x,y)$。
- **111 年 第三題**：逆時針封閉曲線路徑積分與柯西留數計算。
'''
        }
    ],
    '04_電機機械': [
        {
            'file': '01_變壓器等效電路與效率計算.md',
            'title': '變壓器等效電路參數、電壓調整率與全日效率',
            'content': r'''# ⚙️ 電機機械 核心考點 01 — 變壓器等效電路與效率分析

## 📌 核心解題 SOP
1. **等效電路參數試驗（Equivalent Circuit Tests）**：
   - **開路試驗（Open-Circuit Test, OC，低壓側加額定電壓）**：
     $$P_{oc} = \frac{V_{oc}^2}{R_c}, \quad I_{oc} = \sqrt{I_c^2 + I_m^2} \implies Q_{oc} = \frac{V_{oc}^2}{X_m}$$
     可測得鐵損電阻 $R_c$ 與激磁電抗 $X_m$。
   - **短路試驗（Short-Circuit Test, SC，高壓側通額定電流）**：
     $$R_{eq} = \frac{P_{sc}}{I_{sc}^2}, \quad Z_{eq} = \frac{V_{sc}}{I_{sc}}, \quad X_{eq} = \sqrt{Z_{eq}^2 - R_{eq}^2}$$
     可測得等效銅損電阻 $R_{eq}$ 與漏電抗 $X_{eq}$。
2. **電壓調整率（Voltage Regulation, VR）**：
   $$VR = \frac{|V_{NL}| - |V_{FL}|}{|V_{FL}|} \times 100\% \approx \frac{I_L (R_{eq} \cos\theta \pm X_{eq} \sin\theta)}{V_{FL}} \times 100\%$$
   （$+$: 滯後 Lagging 功因；$-$: 超前 Leading 功因）
3. **全日效率（All-Day Efficiency $\eta_{\text{all-day}}$）**：
   $$\eta_{\text{all-day}} = \frac{W_{\text{out}}}{W_{\text{out}} + W_{\text{loss}}} = \frac{\sum (P_{i} \times t_i)}{\sum (P_{i} \times t_i) + 24 \times P_{\text{core}} + \sum (P_{cu,i} \times t_i)} \times 100\%$$

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第一題**：三相變壓器接線（Y-Δ）與短路試驗參數折算。
- **112 年 第一題**：自耦變壓器容量提升比與效率計算。
- **110 年 第一題**：全日效率與最大效率條件（鐵損 = 銅損 $P_c = P_{cu}$）。
'''
        },
        {
            'file': '02_三相感應電動機轉矩轉差率與啟動.md',
            'title': '三相感應電動機：等效電路、轉矩-轉差率曲線與降壓啟動',
            'content': r'''# ⚙️ 電機機械 核心考點 02 — 三相感應電動機

## 📌 核心公式與解題 SOP
1. **同步轉速與轉差率（Slip $s$）**：
   $$n_s = \frac{120 f}{P} \quad [\text{rpm}], \quad \omega_s = \frac{4\pi f}{P} \quad [\text{rad/s}], \quad s = \frac{n_s - n_r}{n_s}$$
2. **轉子感應頻率與等效電路**：
   - 轉子頻率：$f_r = s f_e$
   - 轉子每相電阻分解：$\frac{R_2}{s} = R_2 + R_2 \left(\frac{1 - s}{s}\right)$（$R_2$ 為銅損，後者為轉化為機械功率之等效負載電阻）
3. **氣隙功率、轉子銅損與電磁轉矩**：
   $$P_{ag} : P_{cu2} : P_{conv} = 1 : s : (1 - s)$$
   $$T_{ind} = \frac{P_{conv}}{\omega_m} = \frac{P_{ag}}{\omega_s} = \frac{3 V_{th}^2 \frac{R_2}{s}}{\omega_s \left[ (R_{th} + \frac{R_2}{s})^2 + (X_{th} + X_2)^2 \right]}$$
4. **最大轉矩（Pull-out Torque $T_{\max}$）與最大轉差率 $s_{\max}$**：
   $$s_{\max} = \frac{R_2}{\sqrt{R_{th}^2 + (X_{th} + X_2)^2}} \approx \frac{R_2}{X_{th} + X_2}$$
   $$T_{\max} = \frac{3 V_{th}^2}{2\omega_s \left[ R_{th} + \sqrt{R_{th}^2 + (X_{th} + X_2)^2} \right]}$$
   > **重要觀念**：最大轉矩 $T_{\max}$ **與轉子電阻 $R_2$ 無關**，但達到最大轉矩之轉差率 $s_{\max}$ 與 $R_2$ 成正比！

---

## 🎯 歷屆技師高頻出題年份
- **113 年 第二題**：感應電動機堵轉/無載試驗與轉矩特性分析。
- **111 年 第二題**：Y-Δ 啟動與自耦變壓器降壓啟動之啟動電流與轉矩比值計算。
- **109 年 第二題**：繞線式感應電動機外加電阻提升啟動轉矩。
'''
        }
    ],
    '05_電力系統': [
        {
            'file': '01_標么系統與對稱成分故障分析.md',
            'title': '標么系統（Per-Unit）與對稱成分法故障分析',
            'content': r'''# ⚡ 電力系統 核心考點 01 — 標么系統與短路故障分析

## 📌 核心公式與計算 SOP
1. **標么值基準轉換（Base Conversion Formula）**：
   $$Z_{\text{pu}}^{\text{new}} = Z_{\text{pu}}^{\text{old}} \times \left( \frac{V_{\text{base}}^{\text{old}}}{V_{\text{base}}^{\text{new}}} \right)^2 \times \left( \frac{S_{\text{base}}^{\text{new}}}{S_{\text{base}}^{\text{old}}} \right)$$
2. **對稱成分變換矩陣（Fortescue Transformation）**：
   $$\begin{bmatrix} V_a \\ V_b \\ V_c \end{bmatrix} = \begin{bmatrix} 1 & 1 & 1 \\ 1 & a^2 & a \\ 1 & a & a^2 \end{bmatrix} \begin{bmatrix} V_{a0} \\ V_{a1} \\ V_{a2} \end{bmatrix}, \quad \text{其中 } a = 1\angle 120^\circ = -\frac{1}{2} + j\frac{\sqrt{3}}{2}$$
3. **各類短路故障序網路連接方式**：
   - **三相平衡短路（3-Phase Fault）**：僅含正序網路，$I_{a1} = \frac{V_f}{Z_1 + Z_f}, \quad I_{a0} = I_{a2} = 0$。
   - **單線接地故障（Single Line-to-Ground, SLG）**：正序、負序、零序**串聯**：
     $$I_{a0} = I_{a1} = I_{a2} = \frac{V_f}{Z_0 + Z_1 + Z_2 + 3Z_n + 3Z_f}, \quad I_f = 3 I_{a1}$$
   - **線間短路故障（Line-to-Line, L-L）**：正序與負序**並聯**（零序開路）：
     $$I_{a1} = -I_{a2} = \frac{V_f}{Z_1 + Z_2 + Z_f}, \quad I_{a0} = 0, \quad I_f = \sqrt{3} I_{a1}$$
   - **雙線接地故障（Double Line-to-Ground, DLG）**：正序、負序、零序**並聯**。

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第二題**：單線接地故障（SLG）序阻抗網路計算與故障電流求解。
- **113 年 第一題**：標么值系統建構與多匯流排三相短路容量。
- **110 年 第三題**：線間短路與非對稱故障電流相量圖。
'''
        },
        {
            'file': '02_電力系統穩定度與搖擺方程式.md',
            'title': '電力系統暫態穩定度：搖擺方程式與等面積準則',
            'content': r'''# ⚡ 電力系統 核心考點 02 — 電力系統穩定度

## 📌 核心公式與解題 SOP
1. **轉子搖擺方程式（Swing Equation）**：
   $$\frac{2H}{\omega_s} \frac{d^2 \delta}{dt^2} = P_m - P_e = P_a \quad [\text{pu}]$$
   - $H$：慣性常數（Inertia Constant，單位為 $\text{MJ/MVA}$ 或 $\text{s}$）。
   - $\delta$：功角（Power Angle，單位為 $\text{rad}$）。
   - $P_m$：機械輸入功率， $P_e = P_{\max} \sin\delta = \frac{|E'| |V|}{X} \sin\delta$ 為電磁輸出功率。
2. **等面積準則（Equal-Area Criterion）**：
   - 系統維持暫態穩定之條件為**加速面積等於減速面積**：
     $$A_1 = \int_{\delta_0}^{\delta_c} (P_m - P_{e1}) d\delta = A_2 = \int_{\delta_c}^{\delta_{\max}} (P_{e2} - P_m) d\delta$$
3. **臨界清除角（Critical Clearing Angle $\delta_{cr}$）求解**：
   - 若故障期間電磁功率降為 $0$（$P_{e,\text{fault}} = 0$），故障清除後恢復原網路（$P_{e,\text{post}} = P_{\max} \sin\delta$）：
     $$\cos\delta_{cr} = \frac{P_m}{P_{\max}} (\delta_{\max} - \delta_0) + \cos\delta_{\max}$$
     其中 $\delta_{\max} = \pi - \sin^{-1}\left(\frac{P_m}{P_{\max}}\right)$。

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第三題**：發電機搖擺方程式與暫態穩定度等面積準則。
- **112 年 第三題**：臨界清除時間（CCT）與雙迴線切除故障分析。
- **109 年 第四題**：無阻尼轉子小振盪自然震盪頻率 $f_n$ 計算。
'''
        }
    ]
}

# Generate KB
for subj, notes in kb_data.items():
    subj_kb_dir = os.path.join(base_kb, subj)
    os.makedirs(subj_kb_dir, exist_ok=True)
    for note in notes:
        fpath = os.path.join(subj_kb_dir, note['file'])
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(note['content'].strip() + '\n')
        print('Created KB note:', fpath)

print('All Core Knowledge Base notes created successfully!')
