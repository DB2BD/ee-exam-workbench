# ADR-0005：官方原題溯源與逐題解答驗證閘門

* **狀態**：`已接受 (Accepted)`
* **日期**：2026-08-29
* **範圍**：公務高考三級原題、題目裁切、詳解發布與前端顯示

## 背景

檔案存在或文字可解析，不等於試題來自考選部，也不等於解答數值正確。PDF 文字抽取可能破壞數學符號與電路標籤；未經驗證的合成詳解會把錯誤答案帶入複習流程。

## 決策

1. 原題 PDF 只能由考選部 `wwwq.moex.gov.tw` 官方端點下載，並記錄官方網址、頁數與 SHA-256。
2. 每一題必須有獨立題目裁切；含圖題另存圖形裁切。裁切圖是文字抽取失真的最終判讀依據。
3. 詳解以題目 ID 綁定原題 PDF 雜湊與驗證狀態。只有列入 `validated_question_ids` 的題目，前端才顯示完整詳解連結。
4. 電路題至少執行兩種核對：解析推導與獨立數值／物理檢查，例如 KCL、KVL、功率平衡、初末值、連續性或等效電路。
5. 缺少官方原檔的欄位標記為 unavailable；禁止以自行排版 PDF 或通用答案模板補足官方題庫。

## 驗證命令

```text
python3 scripts/verify_moex_national_exams.py
python3 -m unittest discover -s tests -p 'test*.py' -v
python3 scripts/health_check_codebase.py
```

完整發布前另須通過：

```text
python3 scripts/verify_moex_national_exams.py --require-solutions
```
