// ═══════════════════════════════════════════════════════════════════
// 🏛️ 國考同級參考題庫 — 獨立擴充資料庫
// ⚠️  此檔案完全獨立於 dashboard-data.js，零覆蓋、零污染
// Auto-compiled by scripts/compile_national_exams.py
// Total national exam questions: 0
// ═══════════════════════════════════════════════════════════════════

const NATIONAL_EXAMS_DATA = {
  version: "1.0.0",
  categories: [
    {
        "id": "PE",
        "name": "🏆 電機工程技師",
        "total": 318,
        "isPrimary": true
    },
    {
        "id": "GK",
        "name": "🏛️ 公務高考三級",
        "total": 0,
        "isPrimary": false
    },
    {
        "id": "RW",
        "name": "🚆 鐵路特考高員",
        "total": 0,
        "isPrimary": false
    },
    {
        "id": "LOC",
        "name": "🏙️ 地方特考三級",
        "total": 0,
        "isPrimary": false
    },
    {
        "id": "SOE",
        "name": "⚡ 國營事業聯招",
        "total": 0,
        "isPrimary": false
    }
],
  subjects: [
    {
        "id": "01",
        "name": "電路學",
        "icon": "⚡",
        "color": "#4a7c8f",
        "count": 0
    },
    {
        "id": "02",
        "name": "電子學（含電力電子）",
        "icon": "🔌",
        "color": "#686b8f",
        "count": 0
    },
    {
        "id": "03",
        "name": "工程數學",
        "icon": "📐",
        "color": "#54826b",
        "count": 0
    },
    {
        "id": "04",
        "name": "電機機械",
        "icon": "⚙️",
        "color": "#a17846",
        "count": 0
    },
    {
        "id": "05",
        "name": "電力系統",
        "icon": "🏢",
        "color": "#a85858",
        "count": 0
    },
    {
        "id": "06",
        "name": "工業配電",
        "icon": "🏭",
        "color": "#7d6382",
        "count": 0
    }
],
  questions: []
};

console.log("Loaded national exam cross-reference database with", NATIONAL_EXAMS_DATA.questions.length, "questions.");
