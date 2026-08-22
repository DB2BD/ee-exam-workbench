---
name: electrical-exam-solver
description: >-
  專業電機工程技師考試（高考專技）題解與推導專家技能。
  專精於：電路學、電子學（含電力電子）、工程數學、電機機械、電力系統、工業配電 6 大考科之標準解題 SOP、
  詳細步驟推導、陷阱提示、計算機操作要領與標準 LaTeX 題解筆記生成。
---

# ⚡ 電機工程技師 題解與推導專家技能 (Electrical Exam Solver)

本 Skill 提供專門職業及技術人員高等考試【電機工程技師】6 大考科的標準解題方法論、高頻題型 SOP、步驟式 LaTeX 排版規範與錯題本生成引擎。

---

## 🎯 6 大考科解題核心 SOP 與規範

### 1. ⚡ 01. 電路學 (Circuit Theory)
- **直流/交流穩態**：
  - 優先列出節點電壓方程式（KCL）或迴路電流方程式（KVL）。
  - 相量分析務必標註複數單位（$\mathbf{V} = |V|\angle\theta^\circ, \mathbf{I} = |I|\angle\phi^\circ$）。
  - 複數功率計算：$\mathbf{S} = \mathbf{V}\mathbf{I}^* = P + jQ$（記得共軛！）。
- **暫態分析 (RL, RC, RLC)**：
  - **步驟 1**：求解初始狀態 $i_L(0^-) = i_L(0^+), v_C(0^-) = v_C(0^+)$。
  - **步驟 2**：求解 $t \to \infty$ 之最終穩態值。
  - **步驟 3**：求解等效時間常數 $\tau = R_{th}C$ 或 $\tau = L/R_{th}$。
  - **步驟 4**：套用三要素公式 $f(t) = f(\infty) + [f(0^+) - f(\infty)] e^{-t/\tau}$。
- **S 域拉氏轉換**：
  - 電感等效：$sL$ 串聯電壓源 $L i(0^-)$ 或並聯電流源 $i(0^-)/s$。
  - 電容等效：$\frac{1}{sC}$ 串聯電壓源 $\frac{v(0^-)}{s}$ 或並聯電流源 $C v(0^-)$。

### 2. ⚡ 02. 電子學（含電力電子學） (Electronics & Power Electronics)
- **BJT / MOSFET 放大器**：
  - **DC 偏壓分析**：求直流工作點 $Q(I_C, V_{CE})$ 或 $Q(I_D, V_{DS})$，確認操作於主動區（Active）或飽和區（Saturation）。
  - **小訊號參數**：$g_m = \frac{I_C}{V_T}$ 或 $g_m = \sqrt{2k_n'(W/L)I_D}$，$r_\pi = \frac{\beta}{g_m}$，$r_o = \frac{V_A}{I_C}$。
  - **AC 小訊號等效電路**：畫出混合 $\pi$ 模型，求解 $A_v, R_{in}, R_{out}, f_H$。
- **DC-DC 電力電子轉換器 (Buck, Boost, Buck-Boost)**：
  - 嚴格使用「電感伏秒平衡（Volt-Second Balance）」推導電壓轉換比 $M(D) = \frac{V_o}{V_s}$。
  - 嚴格使用「電容安秒平衡（Charge Balance）」推導輸出漣波 $\Delta V_o$。
  - 判斷連續導通模式（CCM）與臨界電感 $L_{crit}$。

### 3. 📐 03. 工程數學 (Engineering Mathematics)
- **二階與高階 ODE**：
  - 特徵方程式求齊次解 $y_h(x)$。
  - 待定係數法或參數變異法（Wronskian 行列式）求特解 $y_p(x)$。
- **線性代數**：
  - 特徵值求解：$\det(\mathbf{A} - \lambda\mathbf{I}) = 0$。
  - 矩陣對角化：$\mathbf{A} = \mathbf{P}\mathbf{\Lambda}\mathbf{P}^{-1}$ 或正交對角化 $\mathbf{A} = \mathbf{Q}\mathbf{\Lambda}\mathbf{Q}^T$。
  - 奇異值分解：$\mathbf{A} = \mathbf{U}\mathbf{\Sigma}\mathbf{V}^T$。
- **複變函數與留數定理**：
  - 極點判別：單極點 $\text{Res}(f, z_0) = \lim_{z \to z_0} (z-z_0)f(z)$；$m$ 階極點 $\text{Res}(f, z_0) = \frac{1}{(m-1)!} \lim_{z \to z_0} \frac{d^{m-1}}{dz^{m-1}}[(z-z_0)^m f(z)]$。
  - 積分公式：$\oint_C f(z) dz = 2\pi i \sum \text{Res}$。

### 4. ⚙️ 04. 電機機械 (Electric Machinery)
- **變壓器**：
  - 開路試驗（求勵磁參數 $R_c, X_m$）與短路試驗（求等效阻抗 $R_{eq}, X_{eq}$）。
  - 電壓調整率：$\text{VR} = \frac{V_{NL} - V_{FL}}{V_{FL}} \times 100\% \approx \frac{I_2(R_{eq2}\cos\theta \pm X_{eq2}\sin\theta)}{V_{2,FL}} \times 100\%$。
  - 全日效率（All-day Efficiency）：$\eta_{\text{all-day}} = \frac{\text{總輸出能量 (kWh)}}{\text{總輸出能量} + \text{全日鐵損} + \text{全日銅損}}$。
- **三相感應電動機**：
  - 轉差率 $s = \frac{n_s - n_r}{n_s}$，氣隙功率 $P_{ag} = 3 I_2'^2 \frac{R_2'}{s}$。
  - 電磁轉矩 $T_{ind} = \frac{P_{ag}}{\omega_s}$，最大轉矩 $T_{max}$ 與對應轉差率 $s_{maxT} = \frac{R_2'}{\sqrt{R_{th}^2 + (X_{th} + X_2')^2}}$。

### 5. ⚡ 05. 電力系統 (Power Systems)
- **標么系統 (Per-Unit System)**：
  - 基準值轉換：$Z_{pu}^{new} = Z_{pu}^{old} \times \left(\frac{V_{base}^{old}}{V_{base}^{new}}\right)^2 \times \left(\frac{S_{base}^{new}}{S_{base}^{old}}\right)$。
- **故障分析 (Fault Analysis)**：
  - 三相短路：$I_f = \frac{V_f}{Z_1}$。
  - 單線接地故障 (SLG)：$I_{a0} = I_{a1} = I_{a2} = \frac{V_f}{Z_0 + Z_1 + Z_2 + 3Z_f}, \quad I_f = 3 I_{a0}$。
  - 線間短路 (L-L)：$I_{a1} = -I_{a2} = \frac{V_f}{Z_1 + Z_2 + Z_f}, \quad I_f = \sqrt{3} I_{a1}$。
- **暫態穩定度**：
  - 搖擺方程式：$\frac{2H}{\omega_s} \frac{d^2\delta}{dt^2} = P_m - P_e$。
  - 等面積準則（Equal-Area Criterion）求解臨界清除角 $\delta_{cr}$。

### 6. ⚡ 06. 工業配電 (Industrial Power Distribution)
- **負載計算**：
  - 需量因數、日負載因數、參差因數 $\text{DivF} = \frac{\sum \text{個別最大需量}}{\text{綜合最大需量}} \ge 1$。
- **短路容量與斷路器選定**：
  - 標么法：$\text{SCMVA} = \frac{S_{base}}{Z_{pu}}$，對稱短路電流 $I_{sc} = \frac{S_{base}}{\sqrt{3} V_{base} Z_{pu}}$。
- **過電流電驛協調 (CO-8 / CO-11)**：
  - Tap 設定、Time Dial (TDS) 設定、協調時間差 $\text{CTI} \approx 0.3 \sim 0.4\text{ s}$。

---

## 📝 題解筆記生成工作流

當使用者指定年份與題號要求詳解時：
1. 建立筆記於 `📝 個人題解與錯題本/<考科>/<年份>年_<考科>_<題號>_<主題>.md`。
2. 包含 YAML Frontmatter（考科、年份、題號、考點、難易度、掌握狀態）。
3. 輸出包含：
   - **📌 題目原始陳述與已知條件**
   - **💡 核心觀念與破題關鍵**
   - **✏️ 完整步驟式推導（含純 LaTeX 數學式）**
   - **🎯 考場計算機按法與陷阱提示**
   - **🔗 關聯核心考點卡片鏈結**
