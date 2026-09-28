<!--
Each task description MUST state:
- the behavior or contract being delivered (what is observably true when the
  task is complete), and
- the verification target that proves completion (test, CLI invocation,
  analyzer check, manual assertion, or content review).

File paths are supporting context for locating the work, never the task
itself. "Edit file X" is not a valid task — it is missing both behavior and
verification.
-->

## 1. 官方來源彙編與舊生成器安全

- [x] 1.1 將五份 GK 考科彙編改為來源優先索引：110–114 年 25 個科目／年度位置，都必須連到 manifest 可追溯的官方年度原題頁與清楚標示狀態的 repo 題解，或明示官方連結不可用並連回考選部查詢頁；工程數學 113、114 年的 manifest 狀態是 `not_available_in_selected_exam_class`，不得呈現成官方試題。索引不得包含舊版複製題幹、虛構代號、題數或配分。將該兩年由 ReportLab 產生、目前誤放在 `data/official_pdfs/gk/` 的 PDF 移至 `_unverified_pre_moex`，保留位元組、記錄原／新路徑、SHA-256 與降級理由，並修正既有符號連結。以 `python3 -m unittest tests.test_national_subject_master_indexes tests.test_national_official_pdf_manifest`、`python3 scripts/build_master_national_subject_files.py --check` 驗證 25 格覆蓋、23 個官方來源連結、2 個不可用狀態、所有本地連結有效、官方 PDF 目錄與 manifest 雙向吻合，以及兩份替代 PDF 不再位於官方來源目錄。
- [x] 1.2 確保舊 GK 資料生成模組與所有會寫入舊 GK 題目／解答的入口都安全：匯入時不寫檔，呼叫已退役的生成器時不得覆寫或新增官方年度題目、題解或原始 PDF。須保護的入口為 `scripts/generate_all_national_exams.py`、`scripts/generate_all_national_exam_solutions.py`、`scripts/generate_all_national_exam_pdfs_v2.py`、`scripts/build_all_authentic_gk_solutions.py`、`scripts/generate_flagship_gk_diagrams_and_solutions.py`、`scripts/legacy_migrations/build_full_step_by_step_solutions.py`、`scripts/legacy_migrations/generate_all_national_exam_pdfs.py`。以隔離測試 `tests.test_legacy_gk_generators_are_safe` 驗證，並確認官方年度來源檔位元組完全不變。
- [x] 1.3 [after: 1.1] 讓 `scripts/compile_national_exams.py` 在重建 `national-solutions-bundle.js` 時排除所有 `_unverified_pre_moex` Markdown、圖片及經符號連結指向隔離區的別名；其他 23 份官方年度頁、官方 PDF 雜湊及 solution 狀態保持完整；PE bundles 不得變動。以 `python3 -m unittest tests.test_national_bundle_excludes_unverified_sources` 與 `python3 scripts/compile_national_exams.py` 驗證，並確認 bundle 不含未驗證路徑、題目或圖片映射，GK 官方記錄和 PE 輸出符合既有完整性測試。
