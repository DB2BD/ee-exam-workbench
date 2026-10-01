# 電機工程技師考古題題解規範 (AGENT-SOLVE.md)

本文件定義 PE canonical 題解（`📝 個人題解與錯題本/0X_*/canonical/EE-YYY-SS-N.md`）的唯一版型 `lean-v1`、精確性條件與驗證方式。它提高推導的可追溯性與一致性，不宣稱任何題解等同官方標準答案或保證得分。背景與迭代流程見 `docs/WORKPLAN_題解精確化與去冗迭代_2026-10-01.md`。

## 零、來源與驗證邊界

- 題幹唯一來源是官方題目裁切圖（frontmatter `source_crop`）；裁切圖有缺漏或滲入時，先修 `scripts/crop_pe_questions.py`，不得以舊題解或參考書反推題幹。
- 參考書只作核對材料。已核對參考書但官方證據不足時用 `reference_book_verified`；題幹缺參數、圖形需估讀或來源衝突時保留 `needs_manual_review`，在「條件與疑義」寫出假設與分支。
- 狀態只能由主 session 依稽核結果變更；解題者只提出建議狀態。

## 一、精確性條件（全數成立才可為 `verified`）

| 代號 | 條件 |
| --- | --- |
| P1 | 已知數值、單位、接線、極性、方向與裁切圖逐項一致（必須實際開圖）。 |
| P2 | 每個子題（一）（二）…都有 `\boxed{}` 最終答案並帶單位。 |
| P3 | `verification/pe/EE-YYY-SS-N.py` 以 SymPy／NumPy 從題目已知量獨立求解，`assert` 每個 boxed 答案（相對誤差 ≤ 0.5% 或符號相等）；`python3 scripts/run_verify_scripts.py EE-…` 通過。 |
| P4 | 「驗算」使用與主解不同的方法：回代、KCL/KVL、功率守恆、極限／終值定理、tr／det、單位或量級檢查。 |
| P5 | 只有題幹真缺條件時才寫分支並明示假設；條件完整的題目不加分支。 |
| P6 | KaTeX 可渲染：數學一律在 `$…$`、`$$…$$`、`\(…\)`、`\[…\]` 內，指令不得遺失反斜線。 |

## 二、`lean-v1` 版型

```markdown
---
qid: EE-114-05-3
year: 114
subject: 電力系統
chapter: 經濟調度（忽略損失）
template: lean-v1
annual_sync: true            # 工程數學以外的科目
audit_status: verified
verified_at: 2026-10-01
method: equal_incremental_cost_independent_sympy
source_crop: 依考科分類/05_電力系統/images/questions/PE_114年_電力系統_Q03.png
---

# 114 年電力系統第 3 題｜經濟調度

![官方題目裁切圖](../../../依考科分類/05_電力系統/images/questions/PE_114年_電力系統_Q03.png)

## 已知與所求
## 考場標準作答
### （一）…
## 驗算
## 失分點
## 條件與疑義        ← 僅限題幹缺條件或 needs_manual_review
## 計算機按法        ← 僅限複數相量或矩陣運算，一到三行
```

「考場標準作答」沿用 2026-09-05 產品企劃的用語：考場時限內寫得完、可得分的完整作答。舊五段式的「得分點拆解」「完整教學推導」與作答重複，已併入此段或刪除（2026-10-02 使用者決定）。

**短題精簡形式**：總配分 ≤10 分、或一個公式即可解完的題目，frontmatter 加 `compact: true`，可只保留「考場標準作答」與「驗算」，「已知與所求」「失分點」僅在確有必要時保留。lint 會拒絕配分 >10 分且正文 >700 字的 compact 題。

保留其他既有 frontmatter 欄位（如 `review_*`、`reference_book_*`）；`year`／`subject` 取代舊的「年份／考科／題號」鍵。

## 三、去冗規則

1. **一次推導**：每個答案只推導一次；不再有「考場標準作答＋完整教學推導」雙份內容，也不另列「得分點拆解」。
2. **考場標準作答段**：每個子題依序寫出符號公式 → 代入 → `\boxed{答案 單位}`；理由用一句話交代，不寫教科書式導論。
3. **驗算段**：只寫獨立方法讓等式成立所需的最少行。
4. **失分點**：最多 3 條，每條必須指涉本題具體的量或步驟；泛用提醒（「注意單位」）刪除。
5. **不重述 metadata**：正文不寫 QID、驗證日期、裁切圖路徑、稽核歷程（「升級為 verified」「原詳解…」）。這些只屬於 frontmatter 與 `data/pe-solution-audit.json`。
6. 難度、預估時間、同型題與知識延伸由工作台資料與知識圖譜提供，題解內不重複。

## 四、檢核命令

```bash
python3 scripts/lint_canonical_notes.py EE-114-05-3 --strict
python3 scripts/run_verify_scripts.py EE-114-05-3
python3 -m unittest <.agents/protected_notes.json 列出的測試檔>
```

`.agents/protected_notes.json` 列出被測試直接引用的題解；精簡時不得刪除測試斷言的字串，需改斷言時交由主 session 處理。

## 五、範例（`lean-v1` 正文）

```markdown
## 已知與所求

\(C_1=400+6P_1+0.004P_1^2\)、\(C_2=400+6.8P_2+0.002P_2^2\)（\$/h，\(P\) 以 MW 計），兩機各 800 MW，需求 550 MW，忽略損失。求（一）\(P_1,P_2\)；（二）\(\lambda\)。

## 考場標準作答

### （一）最佳出力

等增量成本與功率平衡：
\[
6+0.008P_1=6.8+0.004P_2,\qquad P_1+P_2=550
\]
\[
6+0.008P_1=9-0.004P_1\Rightarrow \boxed{P_1=250\ \mathrm{MW}},\quad \boxed{P_2=300\ \mathrm{MW}}
\]
成本函數凸且解在 0–800 MW 內，故為全域最小。

### （二）增量成本

\[
\boxed{\lambda=6+0.008(250)=8\ \$/\mathrm{MWh}}
\]

## 驗算

\(6.8+0.004(300)=8\)，兩機增量成本相等；\(250+300=550\)。

## 失分點

- \(0.004P_1^2\) 微分為 \(0.008P_1\)；若誤寫成 \(0.004P_1\) 會得 \(P_1=375\)。
- 須與 \(P_1+P_2=550\) 聯立，不可平均分配為 275／275。
```
