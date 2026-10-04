---
trigger: always_on
---

# ⚡ 電機工程技師 題解與知識庫維護標準規範

所有在建立、更新或解答專門職業及技術人員高等考試【電機工程技師】相關試題時，必須嚴格遵守以下準則：

1. **零推測、精確計算**：
   - 題解推導必須一步到位，列出完整的物理量符號、代入公式數值與計算結果。
   - 所有數值結果必須標註正確物理單位（如 $\Omega, \text{mH}, \mu\text{F}, \text{kW}, \text{MVA}, \angle\theta^\circ$）。
2. **LaTeX 規範**：
   - 矩陣一律使用 `\begin{bmatrix} ... \end{bmatrix}`。
   - 分段函數一律使用 `\begin{cases} ... \end{cases}`。
   - 嚴格避免破音字與 OCR 雜訊字（如 `30o`, `w=`, `ohm`）。
3. **題解架構標準**：
   - PE canonical 題解一律採 `AGENT-SOLVE.md` 的 `lean-v1` 版型：「已知與所求／考場標準作答／驗算／失分點」；短題可用 `compact: true` 精簡形式，必要時加「條件與疑義」；「計算機按法」只用於複數相量或矩陣題。
   - 同一答案只推導一次；正文不寫稽核歷程與 metadata。
4. **強制執行雙重對抗批判與 Python 獨立審計（Adversarial Audit）**：
   - 在剖析、回答或修改任何題目時，**嚴禁盲目相信舊筆記**，必須執行 `adversarial-audit` 技能：
     - **第一關（真題原圖核對）**：調用 `view_file` 查驗原卷圖檔或 PDF，嚴防數字、單位、基準值或接線條件抄錯。
     - **第二關（Python 獨立求解）**：在 `verification/pe/EE-YYY-SS-N.py` 撰寫可重跑的 NumPy/SymPy 腳本以第一原理求解並 `assert` 每個 boxed 答案。
     - **第三關（審稿官挑錯）**：嚴格檢查是否漏解任何子問、是否有 Y-$\Delta$ $30^\circ$ 相位旋轉、是否有中性點不接地阻斷零序。
     - **第四關（修訂與重編譯）**：發現錯誤只改 canonical 來源，再由主 session 執行 `AGENTS.md` 的編譯與測試流程；不手改生成檔。
