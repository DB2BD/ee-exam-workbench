# 📋 電機工程技師 知識庫規格與 Metadata 規範 (CLAUDE-SPEC.md)

本文件定義本知識庫的**檔案命名標準、目錄架構、題目 Metadata 欄位規範、KaTeX 數學排版規範與標籤分類法**。

---

## 🏷️ 一、題目識別碼 (QID) 命名標準

每道試題均有全域唯一之識別碼（QID），其格式嚴格定義如下：

\text{QID} = \mathbf{EE\text{-}[年份]\text{-}[考科代號]\text{-}[題號]}

- **`EE`**：Electrical Engineer（電機工程技師）
- **`[年份]`**：民國紀年（如 `104` ~ `114`）
- **`[考科代號]`**：兩位數字代碼
  - `01`：電路學
  - `02`：電子學（含電力電子）
  - `03`：工程數學
  - `04`：電機機械
  - `05`：電力系統
  - `06`：工業配電
- **`[題號]`**：阿拉伯數字（如 `1`, `2`, `3`, `4`, `5`, `6`）

**範例**：
- `EE-114-04-1` 代表「民國 114 年 電機機械 第 1 題」
- `EE-110-05-3` 代表「民國 110 年 電力系統 第 3 題」
- `EE-108-01-2` 代表「民國 108 年 電路學 第 2 題」

---

## 🗂️ 二、題目中繼資料 (Metadata Schema)

在 `dashboard-data.js` 與資料庫編譯時，每道試題之資料格式定義如下：

```typescript
interface QuestionMetadata {
  qid: string;                   // 'EE-114-04-1'
  subjectId: string;             // '01' ~ '06'
  year: number;                  // 104 ~ 114
  questionNum: number;           // 1 ~ 6
  topic: string;                 // 題目簡述或核心摘要
  tags: string[];                // ['電機機械', '變壓器', '等效電路', '標么值']
  difficulty: number;            // 1 ~ 5 (星級難度)
  verificationStatus: string;    // 'verified' | 'in_progress' | 'needs_review'
  solutionPath: string;          // '📝 個人題解與錯題本/04_電機機械/114年_電機機械_全卷完整詳細題解.md'
  pdfPath: string;               // '依考科分類/04_電機機械/114年_電機機械.pdf'
  formulaTags: string[];         // ['VR公式', '標么阻抗', '短路容量']
```

---

## 📐 三、KaTeX 數學公式排版規範

1. **行內公式 (Inline Math)**：使用單一美元符號 `$ ... $`。
   - 範例：`$V_o = D V_d$`、`$S = P + jQ$`。
   - 禁止在行內公式中使用未轉義的 HTML 字符（如 `<` 請用 `$<$` 或 `\lt`）。
2. **獨立塊狀公式 (Display Math)**：使用雙美元符號 `$$ ... $$`。
   - 範例：
     $$S_{\text{auto}} = \frac{V_H}{V_H - V_X} S_{2w}$$
3. **矩陣與行列式 (Matrices & Determinants)**：
   - 嚴格禁止使用 ASCII 方括號，必須使用 `\begin{bmatrix} ... \end{bmatrix}` 或 `\begin{pmatrix} ... \end{pmatrix}`。
   - 範例：
     $$\begin{bmatrix} V_1 \\ V_2 \end{bmatrix} = \begin{bmatrix} Z_{11} & Z_{12} \\ Z_{21} & Z_{22} \end{bmatrix} \begin{bmatrix} I_1 \\ I_2 \end{bmatrix}$$
4. **多行聯立方程式 (Aligned Equations)**：使用 `\begin{aligned} ... \end{aligned}`。
   - 範例：
     $$
     \begin{aligned}
       P &= \sqrt{3} V_L I_L \cos\theta \\
       Q &= \sqrt{3} V_L I_L \sin\theta
     \end{aligned}
     $$
5. **物理單位**：使用 `\text{...}` 或 `\ ` 分隔，例如 `$50\text{ kVA}$`、`$3.87\%$`、`$60\text{ Hz}$`。

---

## 🏷️ 四、考點標籤體系 (Taxonomy)

| 科目 | 標籤分類 (Tags) | 代表公式 / 關鍵字 |
| :--- | :--- | :--- |
| **01. 電路學** | `#交流相量`, `#三要素暫態`, `#三相電路`, `#雙埠網路`, `#戴維寧等效`, `#拉氏轉換` | $S=VI^*$, $x(t)=x(\infty)+[x(0+)-x(\infty)]e^{-t/\tau}$, 二瓦特計 |
| **02. 電子學** | `#電力電子`, `#Buck轉換器`, `#Boost轉換器`, `#運算放大器`, `#SPWM變流器`, `#小訊號分析` | 伏秒平衡, 虛接地, $g_m=I_C/V_T$, 密勒效應 |
| **03. 工程數學** | `#線性代數`, `#特徵值對角化`, `#SVD奇異值`, `#常微分方程ODE`, `#複變留數`, `#拉氏轉換` | $\det(A-\lambda I)=0$, $A=U\Sigma V^T$, $2\pi j \sum \text{Res}$ |
| **04. 電機機械** | `#變壓器`, `#自耦變壓器`, `#感應電動機`, `#同步電機`, `#直流機`, `#磁路定律` | $s_{max}=\frac{R_2'}{\sqrt{R_{th}^2+X_{eq}^2}}$, $E_f=V_\phi+I_a Z_s$, $SCR=1/X_s$ |
| **05. 電力系統** | `#對稱成分`, `#短路故障`, `#電力潮流`, `#Ybus導納`, `#搖擺方程`, `#經濟調度`, `#ABCD參數` | SLG $I_{a1}=\frac{V_f}{Z_1+Z_2+Z_0+3Z_n}$, $M\frac{d^2\delta}{dt^2}=P_m-P_{\max}\sin\delta$ |
| **06. 工業配電** | `#短路容量`, `#斷路器選定`, `#功因改善`, `#諧波抑制`, `#電壓降`, `#需量管理`, `#保護協調` | $S_{sc}=\frac{S_{base}}{X_{pu}}$, $Q_c=P(\tan\theta_1-\tan\theta_2)$, $\Delta V=\sqrt{3}I(R\cos\theta+X\sin\theta)$ |

---

## ✅ 五、題解驗證狀態碼 (Verification Status)

- **`verified` (已驗證)**：經人工逐步計算、逆向核對無誤，符合考選部標準答案，具備完整公式與防坑提示。
- **`in_progress` (推導中)**：基本推導完成，待補充圖表或第二種解法驗證。
- **`needs_review` (需審查)**：題意存有爭議或有多種解讀模型，需進一步查核學界教科書。
