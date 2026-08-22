#!/usr/bin/env python3
import os

target_dir = "/Users/a/技師考試/歷屆試題_104-114年/依考科分類/01_電路學/images"
os.makedirs(target_dir, exist_ok=True)

# ----------------- 1. 104 年 第 1 題 -----------------
svg_104_q1 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 540" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="box-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="0.95"/><stop offset="100%" stop-color="#0f172a" stop-opacity="0.95"/>
    </linearGradient>
    <marker id="arr-cyan" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8"/>
    </marker>
    <marker id="arr-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#f59e0b"/>
    </marker>
  </defs>
  <style>
    .title { font-family: -apple-system, sans-serif; font-weight: 800; fill: #f8fafc; }
    .subtitle { font-family: -apple-system, sans-serif; font-size: 13px; fill: #94a3b8; }
    .val-cyan { font-family: monospace; font-size: 13px; font-weight: bold; fill: #38bdf8; }
    .val-amber { font-family: monospace; font-size: 13px; font-weight: bold; fill: #f59e0b; }
    .val-rose { font-family: monospace; font-size: 13px; font-weight: bold; fill: #f43f5e; }
    .val-emerald { font-family: monospace; font-size: 13px; font-weight: bold; fill: #10b981; }
    .wire { stroke: #94a3b8; stroke-width: 2.2; stroke-linecap: round; fill: none; }
    .box { stroke: #334155; stroke-width: 1.5; rx: 12; fill: url(#box-bg); }
  </style>

  <rect width="920" height="540" rx="16" fill="url(#bg)"/>
  <text x="460" y="38" text-anchor="middle" class="title" font-size="20">104 年 電路學 第一題：橋接電路戴維寧等效 (Rth &amp; Vth) 拓撲標定圖</text>
  <text x="460" y="60" text-anchor="middle" class="subtitle">分析特點：關閉獨立源後懸空支路判定 暨 節點電壓 KCL 精確推導</text>

  <!-- 左圖：Rth 分析 (關閉獨立源) -->
  <rect x="25" y="80" width="420" height="435" class="box"/>
  <text x="45" y="110" class="title" font-size="16" fill="#f59e0b">【圖 A】戴維寧電阻 Rth 求解 (9V短路, 1.8A開路)</text>
  <text x="45" y="130" font-family="sans-serif" font-size="12" fill="#94a3b8">1.8A 開路後 5Ω 與 25Ω 懸空無電流迴路 ⇒ Rth = 60 || (20 + 10)</text>

  <!-- 短路點與線路 -->
  <line x1="75" y1="210" x2="75" y2="440" class="wire" stroke="#38bdf8" stroke-width="3"/>
  <circle cx="75" cy="210" r="5" fill="#38bdf8"/><circle cx="75" cy="440" r="5" fill="#38bdf8"/>
  <text x="65" y="325" text-anchor="middle" class="val-cyan" transform="rotate(-90 65 325)">9V 短路點</text>

  <!-- 頂部 20Ω -->
  <path d="M 75 210 L 375 210" class="wire"/>
  <rect x="180" y="200" width="50" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="205" y="215" text-anchor="middle" class="val-amber">20 Ω</text>

  <!-- 底部 10Ω -->
  <path d="M 75 440 L 375 440" class="wire"/>
  <rect x="180" y="430" width="50" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="205" y="445" text-anchor="middle" class="val-amber">10 Ω</text>

  <!-- 中間懸空虛線 5Ω & 25Ω -->
  <path d="M 120 210 L 120 440" stroke="#64748b" stroke-width="1.8" stroke-dasharray="4,4" fill="none"/>
  <rect x="105" y="250" width="30" height="40" fill="#1e293b" stroke="#64748b" rx="3"/>
  <text x="120" y="275" text-anchor="middle" font-size="11" fill="#64748b">5Ω</text>
  <rect x="105" y="340" width="30" height="40" fill="#1e293b" stroke="#64748b" rx="3"/>
  <text x="120" y="365" text-anchor="middle" font-size="11" fill="#64748b">25Ω</text>
  <text x="120" y="320" text-anchor="middle" class="val-rose" font-size="11">懸空(無電流)</text>

  <!-- 右側 60Ω -->
  <path d="M 375 210 L 375 440" class="wire"/>
  <rect x="365" y="300" width="20" height="50" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="400" y="330" class="val-amber">60 Ω</text>

  <!-- a, b 端點 -->
  <circle cx="375" cy="210" r="5" fill="#f43f5e"/>
  <text x="390" y="215" class="val-rose" font-size="14">a</text>
  <circle cx="375" cy="440" r="5" fill="#38bdf8"/>
  <text x="390" y="445" class="val-cyan" font-size="14">b</text>

  <rect x="45" y="465" width="380" height="35" fill="#0f172a" stroke="#10b981" rx="6"/>
  <text x="235" y="488" text-anchor="middle" class="val-emerald" font-size="13">Rth = 60 || (20 + 10) = 60 || 30 = 20 Ω</text>

  <!-- 右圖：Voc 分析 (節點電壓法) -->
  <rect x="475" y="80" width="420" height="435" class="box"/>
  <text x="495" y="110" class="title" font-size="16" fill="#38bdf8">【圖 B】開路電壓 Vth 求解 (節點電壓 KCL)</text>
  <text x="495" y="130" font-family="sans-serif" font-size="12" fill="#94a3b8">設 Vb = 0V ⇒ 9V負端為 Vd ⇒ 9V正端為 Vd+9 ⇒ 聯立解得 Va</text>

  <!-- 9V 電源 -->
  <circle cx="525" cy="325" r="18" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="525" y="330" text-anchor="middle" class="val-cyan">9V</text>
  <text x="525" y="300" text-anchor="middle" class="val-cyan">+</text>
  <text x="525" y="355" text-anchor="middle" class="val-cyan">−</text>

  <!-- 頂部與 20Ω -->
  <path d="M 525 307 L 525 210 L 825 210" class="wire"/>
  <rect x="670" y="200" width="45" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="692" y="215" text-anchor="middle" class="val-amber" font-size="12">20 Ω</text>

  <!-- 中間 c 節點與 1.8A 電流源 -->
  <path d="M 590 210 L 590 440" class="wire"/>
  <rect x="578" y="235" width="24" height="35" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="560" y="258" class="val-amber" font-size="11">5Ω</text>
  
  <circle cx="590" cy="300" r="4" fill="#f59e0b"/>
  <text x="575" y="305" text-anchor="end" class="val-amber" font-size="12">Vc</text>
  
  <rect x="578" y="360" width="24" height="35" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="560" y="382" class="val-amber" font-size="11">25Ω</text>

  <!-- 1.8A 電流源向右進入 a -->
  <path d="M 590 300 L 825 300 L 825 210" class="wire"/>
  <circle cx="710" cy="300" r="15" fill="#1e293b" stroke="#f59e0b" stroke-width="1.8"/>
  <line x1="700" y1="300" x2="720" y2="300" stroke="#f59e0b" stroke-width="2" marker-end="url(#arr-amber)"/>
  <text x="710" y="280" text-anchor="middle" class="val-amber" font-size="12">1.8 A (→)</text>

  <!-- 底部 10Ω 與 節點 d -->
  <path d="M 525 343 L 525 440 L 825 440" class="wire"/>
  <circle cx="525" cy="440" r="4" fill="#38bdf8"/>
  <text x="525" y="460" text-anchor="middle" class="val-cyan" font-size="12">節點 d (Vd)</text>
  <rect x="670" y="430" width="45" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="692" y="445" text-anchor="middle" class="val-amber" font-size="12">10 Ω</text>

  <!-- 右側 60Ω -->
  <path d="M 825 210 L 825 440" class="wire"/>
  <rect x="815" y="335" width="20" height="45" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="845" y="362" class="val-amber" font-size="12">60 Ω</text>

  <circle cx="825" cy="210" r="5" fill="#f43f5e"/>
  <text x="840" y="215" class="val-rose" font-size="13">a (Va = Vth)</text>
  <circle cx="825" cy="440" r="5" fill="#38bdf8"/>
  <text x="840" y="445" class="val-cyan" font-size="13">b (0 V)</text>

  <rect x="495" y="465" width="380" height="35" fill="#0f172a" stroke="#38bdf8" rx="6"/>
  <text x="685" y="488" text-anchor="middle" class="val-cyan" font-size="13">Vth = Va = 270/7 V ≈ 38.57 V</text>
</svg>'''

# ----------------- 2. 104 年 第 5 題 -----------------
svg_104_q5 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 540" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="box-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="0.95"/><stop offset="100%" stop-color="#0f172a" stop-opacity="0.95"/>
    </linearGradient>
    <marker id="arr-c" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8"/>
    </marker>
    <marker id="arr-r" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#f43f5e"/>
    </marker>
  </defs>
  <style>
    .title { font-family: -apple-system, sans-serif; font-weight: 800; fill: #f8fafc; }
    .subtitle { font-family: -apple-system, sans-serif; font-size: 13px; fill: #94a3b8; }
    .val-c { font-family: monospace; font-size: 13px; font-weight: bold; fill: #38bdf8; }
    .val-a { font-family: monospace; font-size: 13px; font-weight: bold; fill: #f59e0b; }
    .val-r { font-family: monospace; font-size: 13px; font-weight: bold; fill: #f43f5e; }
    .val-e { font-family: monospace; font-size: 13px; font-weight: bold; fill: #10b981; }
    .wire { stroke: #94a3b8; stroke-width: 2.2; fill: none; stroke-linecap: round; }
    .box { stroke: #334155; stroke-width: 1.5; rx: 12; fill: url(#box-bg); }
  </style>

  <rect width="920" height="540" rx="16" fill="url(#bg)"/>
  <text x="460" y="38" text-anchor="middle" class="title" font-size="20">104 年 電路學 第五題：含相依源雙埠網絡 g 參數兩次測試分析圖</text>
  <text x="460" y="60" text-anchor="middle" class="subtitle">定義：I1 = g11·V1 + g12·I2,  V2 = g21·V1 + g22·I2 (受控電壓源 100 I2)</text>

  <!-- 左圖：測試條件 1 (I2 = 0 埠 2 開路) -->
  <rect x="25" y="80" width="420" height="435" class="box"/>
  <text x="45" y="110" class="title" font-size="16" fill="#38bdf8">【測試 1】令 I2 = 0 (埠 2 開路)</text>
  <text x="45" y="130" font-family="sans-serif" font-size="12" fill="#94a3b8">I2 = 0 ⇒ 100 I2 = 0V (中間短路接地) ⇒ g21 = 0, g11 = 1/(20+j10)</text>

  <!-- 埠 1 測試線路 -->
  <path d="M 60 210 L 230 210" class="wire"/>
  <rect x="90" y="200" width="40" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="110" y="215" text-anchor="middle" class="val-a" font-size="11">20Ω</text>
  <rect x="145" y="200" width="45" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="167" y="215" text-anchor="middle" class="val-a" font-size="11">j10Ω</text>

  <!-- 中間接地相依源 (變 0V 短路) -->
  <path d="M 230 210 L 230 430" class="wire" stroke="#38bdf8" stroke-width="2.5"/>
  <circle cx="230" cy="210" r="4" fill="#38bdf8"/>
  <text x="230" y="200" text-anchor="middle" class="val-c" font-size="12">Vmid = 0 V</text>
  <polygon points="230,290 250,315 230,340 210,315" fill="#1e293b" stroke="#38bdf8" stroke-width="1.8"/>
  <text x="230" y="320" text-anchor="middle" class="val-c" font-size="11">0 V</text>

  <!-- 右側 500Ω 與 -j50Ω (無激勵，V2 = 0) -->
  <path d="M 230 210 L 380 210" class="wire"/>
  <rect x="270" y="200" width="45" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="292" y="215" text-anchor="middle" class="val-a" font-size="11">500Ω</text>
  <path d="M 380 210 L 380 430" class="wire"/>
  <rect x="365" y="295" width="30" height="40" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="380" y="320" text-anchor="middle" class="val-a" font-size="11">-j50Ω</text>

  <path d="M 60 430 L 380 430" class="wire"/>
  <circle cx="60" cy="210" r="4" fill="#38bdf8"/><circle cx="60" cy="430" r="4" fill="#38bdf8"/>
  <text x="45" y="215" class="val-c">V1</text>
  <circle cx="380" cy="210" r="4" fill="#f43f5e"/><circle cx="380" cy="430" r="4" fill="#f43f5e"/>
  <text x="395" y="215" class="val-r">V2=0</text>

  <rect x="45" y="465" width="380" height="35" fill="#0f172a" stroke="#38bdf8" rx="6"/>
  <text x="235" y="488" text-anchor="middle" class="val-c" font-size="13">g11 = 0.04 - j0.02 S ,  g21 = 0</text>

  <!-- 右圖：測試條件 2 (V1 = 0 埠 1 短路) -->
  <rect x="475" y="80" width="420" height="435" class="box"/>
  <text x="495" y="110" class="title" font-size="16" fill="#f59e0b">【測試 2】令 V1 = 0 (埠 1 短路)</text>
  <text x="495" y="130" font-family="sans-serif" font-size="12" fill="#94a3b8">埠 2 外加 I2 ⇒ Vmid = 100 I2 ⇒ I1 = -100I2 / (20+j10)</text>

  <!-- 埠 1 短路 -->
  <line x1="510" y1="210" x2="510" y2="430" class="wire" stroke="#38bdf8" stroke-width="2.5"/>
  <text x="500" y="325" text-anchor="middle" class="val-c" transform="rotate(-90 500 325)">V1 短路 (0 V)</text>

  <path d="M 510 210 L 680 210" class="wire"/>
  <rect x="540" y="200" width="40" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="560" y="215" text-anchor="middle" class="val-a" font-size="11">20Ω</text>
  <rect x="595" y="200" width="45" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="617" y="215" text-anchor="middle" class="val-a" font-size="11">j10Ω</text>

  <!-- 相依源 Vmid = 100 I2 -->
  <path d="M 680 210 L 680 430" class="wire"/>
  <polygon points="680,285 705,315 680,345 655,315" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
  <text x="680" y="318" text-anchor="middle" class="val-a" font-size="11">100 I2</text>
  <circle cx="680" cy="210" r="4" fill="#f59e0b"/>
  <text x="680" y="198" text-anchor="middle" class="val-a" font-size="11">Vmid = 100 I2</text>

  <!-- 埠 2 注入 I2 -->
  <path d="M 680 210 L 830 210" class="wire"/>
  <rect x="720" y="200" width="45" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="742" y="215" text-anchor="middle" class="val-a" font-size="11">500Ω</text>
  <path d="M 830 210 L 830 430" class="wire"/>
  <rect x="815" y="295" width="30" height="40" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="830" y="320" text-anchor="middle" class="val-a" font-size="11">-j50Ω</text>

  <path d="M 510 430 L 830 430" class="wire"/>
  <!-- I2 箭頭 -->
  <line x1="860" y1="210" x2="835" y2="210" stroke="#f43f5e" stroke-width="2.5" marker-end="url(#arr-r)"/>
  <text x="870" y="200" class="val-r" font-size="13">I2 (流入)</text>

  <rect x="495" y="465" width="380" height="35" fill="#0f172a" stroke="#10b981" rx="6"/>
  <text x="685" y="488" text-anchor="middle" class="val-e" font-size="12">g12 = -4 + j2 ,  g22 = 600(1-j10)/101 ≈ 5.94-j59.41 Ω</text>
</svg>'''

# ----------------- 3. 106 年 第 3 題 (GIC) -----------------
svg_106_q3 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 540" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="box-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="0.95"/><stop offset="100%" stop-color="#0f172a" stop-opacity="0.95"/>
    </linearGradient>
  </defs>
  <style>
    .title { font-family: -apple-system, sans-serif; font-weight: 800; fill: #f8fafc; }
    .subtitle { font-family: -apple-system, sans-serif; font-size: 13px; fill: #94a3b8; }
    .val-c { font-family: monospace; font-size: 14px; font-weight: bold; fill: #38bdf8; }
    .val-a { font-family: monospace; font-size: 14px; font-weight: bold; fill: #f59e0b; }
    .val-r { font-family: monospace; font-size: 14px; font-weight: bold; fill: #f43f5e; }
    .val-e { font-family: monospace; font-size: 14px; font-weight: bold; fill: #10b981; }
    .wire { stroke: #94a3b8; stroke-width: 2.2; fill: none; stroke-linecap: round; }
    .box { stroke: #334155; stroke-width: 1.5; rx: 12; fill: url(#box-bg); }
  </style>

  <rect width="920" height="540" rx="16" fill="url(#bg)"/>
  <text x="460" y="38" text-anchor="middle" class="title" font-size="20">106 年 電路學 第三題：Antoniou 通用阻抗轉換器 (GIC) 5 個節點標定圖</text>
  <text x="460" y="60" text-anchor="middle" class="subtitle">虛短路關係：V1 = V3 = V5 = Vin ； 總輸入阻抗推導：Zin = (Z1 · Z3 · Z5) / (Z2 · Z4)</text>

  <rect x="30" y="80" width="860" height="435" class="box"/>

  <!-- 輸入測試電流源 Is -->
  <circle cx="80" cy="330" r="18" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <line x1="80" y1="342" x2="80" y2="318" stroke="#38bdf8" stroke-width="2.5"/>
  <text x="50" y="335" class="val-c">Is</text>
  <line x1="80" y1="348" x2="80" y2="450" class="wire"/>
  <line x1="60" y1="450" x2="100" y2="450" class="wire"/>

  <!-- 主幹階梯阻抗線 (Z1, Z2, Z3, Z4, Z5) -->
  <path d="M 80 312 L 80 250 L 170 250" class="wire"/>
  <circle cx="120" cy="250" r="5" fill="#38bdf8"/>
  <text x="120" y="235" text-anchor="middle" class="val-c">節點 1 (V1)</text>

  <!-- Z1 -->
  <rect x="170" y="240" width="45" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="192" y="255" text-anchor="middle" class="val-a">Z1</text>
  <path d="M 215 250 L 305 250" class="wire"/>
  <circle cx="260" cy="250" r="5" fill="#f43f5e"/>
  <text x="260" y="235" text-anchor="middle" class="val-r">節點 2 (V2)</text>

  <!-- Z2 -->
  <rect x="305" y="240" width="45" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="327" y="255" text-anchor="middle" class="val-a">Z2</text>
  <path d="M 350 250 L 440 250" class="wire"/>
  <circle cx="395" cy="250" r="5" fill="#38bdf8"/>
  <text x="395" y="235" text-anchor="middle" class="val-c">節點 3 (V3)</text>

  <!-- Z3 -->
  <rect x="440" y="240" width="45" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="462" y="255" text-anchor="middle" class="val-a">Z3</text>
  <path d="M 485 250 L 575 250" class="wire"/>
  <circle cx="530" cy="250" r="5" fill="#f43f5e"/>
  <text x="530" y="235" text-anchor="middle" class="val-r">節點 4 (V4)</text>

  <!-- Z4 -->
  <rect x="575" y="240" width="45" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="597" y="255" text-anchor="middle" class="val-a">Z4</text>
  <path d="M 620 250 L 710 250" class="wire"/>
  <circle cx="665" cy="250" r="5" fill="#38bdf8"/>
  <text x="665" y="235" text-anchor="middle" class="val-c">節點 5 (V5)</text>

  <!-- Z5 接地 -->
  <path d="M 710 250 L 710 320" class="wire"/>
  <rect x="698" y="320" width="24" height="45" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="735" y="348" class="val-a">Z5</text>
  <path d="M 710 365 L 710 420" class="wire"/>
  <line x1="695" y1="420" x2="725" y2="420" class="wire"/>

  <!-- 上方 Op-Amp 1 (輸出接 V4) -->
  <polygon points="220,130 300,165 220,200" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="235" y="155" fill="#38bdf8" font-size="14" font-weight="bold">+</text>
  <text x="235" y="185" fill="#f43f5e" font-size="16" font-weight="bold">−</text>
  <!-- 非反相(+)接 V1 -->
  <path d="M 120 250 L 120 150 L 220 150" class="wire"/>
  <!-- 反相(-)接 V3 -->
  <path d="M 395 250 L 395 180 L 220 180" class="wire"/>
  <!-- 輸出接 V4 -->
  <path d="M 300 165 L 530 165 L 530 250" class="wire" stroke="#f43f5e"/>

  <!-- 下方 Op-Amp 2 (輸出接 V2) -->
  <polygon points="480,330 560,365 480,400" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="495" y="355" fill="#f43f5e" font-size="16" font-weight="bold">−</text>
  <text x="495" y="385" fill="#38bdf8" font-size="14" font-weight="bold">+</text>
  <!-- 反相(-)接 V3 -->
  <path d="M 395 250 L 395 350 L 480 350" class="wire"/>
  <!-- 非反相(+)接 V5 -->
  <path d="M 665 250 L 665 380 L 480 380" class="wire"/>
  <!-- 輸出接 V2 -->
  <path d="M 560 365 L 260 365 L 260 250" class="wire" stroke="#f43f5e"/>

  <!-- 結論橫幅 -->
  <rect x="50" y="455" width="820" height="42" fill="#0f172a" stroke="#10b981" rx="8"/>
  <text x="460" y="482" text-anchor="middle" class="val-e" font-size="14">虛短路 ⇒ V1 = V3 = V5 ； 輸出阻抗 ⇒ Zin = (Z1 · Z3 · Z5) / (Z2 · Z4)</text>
</svg>'''

# ----------------- 4. 106 年 第 4 題 (對稱/反對稱) -----------------
svg_106_q4 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 540" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="box-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="0.95"/><stop offset="100%" stop-color="#0f172a" stop-opacity="0.95"/>
    </linearGradient>
    <marker id="arr-r" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#f43f5e"/>
    </marker>
  </defs>
  <style>
    .title { font-family: -apple-system, sans-serif; font-weight: 800; fill: #f8fafc; }
    .subtitle { font-family: -apple-system, sans-serif; font-size: 13px; fill: #94a3b8; }
    .val-c { font-family: monospace; font-size: 13px; font-weight: bold; fill: #38bdf8; }
    .val-a { font-family: monospace; font-size: 13px; font-weight: bold; fill: #f59e0b; }
    .val-r { font-family: monospace; font-size: 13px; font-weight: bold; fill: #f43f5e; }
    .val-e { font-family: monospace; font-size: 13px; font-weight: bold; fill: #10b981; }
    .wire { stroke: #94a3b8; stroke-width: 2.2; fill: none; stroke-linecap: round; }
    .box { stroke: #334155; stroke-width: 1.5; rx: 12; fill: url(#box-bg); }
  </style>

  <rect width="920" height="540" rx="16" fill="url(#bg)"/>
  <text x="460" y="38" text-anchor="middle" class="title" font-size="20">106 年 電路學 第四題：對稱模式 (Even) 與 反對稱模式 (Odd) 半電路分解圖</text>
  <text x="460" y="60" text-anchor="middle" class="subtitle">分解原則：VL=30V, VR=60V ⇒ Even Mode (45V, 45V) + Odd Mode (-15V, +15V)</text>

  <!-- 左圖：偶模式 (Even Mode 45V) -->
  <rect x="25" y="80" width="420" height="435" class="box"/>
  <text x="45" y="110" class="title" font-size="16" fill="#38bdf8">【偶模式】Ve = 45V (對稱軸開路)</text>
  <text x="45" y="130" font-family="sans-serif" font-size="12" fill="#94a3b8">對稱線上無橫向電流 ⇒ 2Ω 與 3Ω 支路均等效開路 ⇒ Io,e = 0 A</text>

  <!-- 45V 右電源 -->
  <circle cx="370" cy="290" r="18" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="370" y="295" text-anchor="middle" class="val-c">45V</text>
  <text x="370" y="265" text-anchor="middle" class="val-c">+</text>
  <text x="370" y="325" text-anchor="middle" class="val-c">−</text>

  <!-- 頂部與底部 1Ω -->
  <path d="M 370 272 L 370 200 L 220 200" class="wire"/>
  <rect x="270" y="190" width="40" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="290" y="205" text-anchor="middle" class="val-a">1 Ω</text>
  <!-- 電流 Io,e 標記 -->
  <text x="330" y="188" class="val-c">Io,e = 0 A</text>

  <path d="M 370 308 L 370 380 L 220 380" class="wire"/>
  <rect x="270" y="370" width="40" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="290" y="385" text-anchor="middle" class="val-a">1 Ω</text>

  <!-- 對稱中軸開路 (懸空標記) -->
  <circle cx="220" cy="200" r="4" fill="#64748b"/>
  <line x1="220" y1="200" x2="160" y2="200" stroke="#64748b" stroke-dasharray="3,3" stroke-width="2"/>
  <text x="175" y="190" fill="#64748b" font-size="11">開路(2Ω/2)</text>

  <circle cx="220" cy="380" r="4" fill="#64748b"/>
  <line x1="220" y1="380" x2="160" y2="380" stroke="#64748b" stroke-dasharray="3,3" stroke-width="2"/>
  <text x="175" y="398" fill="#64748b" font-size="11">開路(2Ω/2)</text>

  <rect x="45" y="465" width="380" height="35" fill="#0f172a" stroke="#38bdf8" rx="6"/>
  <text x="235" y="488" text-anchor="middle" class="val-c" font-size="13">偶模式輸出電流： Io,e = 0 A</text>


  <!-- 右圖：奇模式 (Odd Mode +15V) -->
  <rect x="475" y="80" width="420" height="435" class="box"/>
  <text x="495" y="110" class="title" font-size="16" fill="#f43f5e">【奇模式】Vo = 15V (對稱軸虛接地)</text>
  <text x="495" y="130" font-family="sans-serif" font-size="12" fill="#94a3b8">對稱線上電位為 0V ⇒ 2Ω 半支路 1Ω 接地, 3Ω 半支路 1.5Ω 接地</text>

  <!-- 15V 右電源 -->
  <circle cx="820" cy="290" r="18" fill="#1e293b" stroke="#f43f5e" stroke-width="2"/>
  <text x="820" y="295" text-anchor="middle" class="val-r">15V</text>
  <text x="820" y="265" text-anchor="middle" class="val-r">+</text>
  <text x="820" y="325" text-anchor="middle" class="val-r">−</text>

  <!-- 頂部與底部 1Ω -->
  <path d="M 820 272 L 820 200 L 670 200" class="wire"/>
  <rect x="720" y="190" width="40" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="740" y="205" text-anchor="middle" class="val-a">1 Ω</text>
  <!-- 電流 Io,o 標記 -->
  <line x1="800" y1="188" x2="770" y2="188" stroke="#f43f5e" stroke-width="2" marker-end="url(#arr-r)"/>
  <text x="785" y="178" class="val-r" font-size="11">Io,o</text>

  <path d="M 820 308 L 820 380 L 670 380" class="wire"/>
  <rect x="720" y="370" width="40" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="740" y="385" text-anchor="middle" class="val-a">1 Ω</text>

  <!-- 節點 B 處 1Ω || 1.5Ω 接地 -->
  <circle cx="670" cy="200" r="4" fill="#f59e0b"/>
  <text x="680" y="195" class="val-a" font-size="12">節點 B</text>
  <path d="M 670 200 L 670 270" class="wire"/>
  <rect x="655" y="220" width="30" height="35" fill="#334155" stroke="#10b981" rx="3"/>
  <text x="670" y="242" text-anchor="middle" class="val-e" font-size="11">0.6Ω</text>
  <line x1="655" y1="270" x2="685" y2="270" class="wire"/>
  <text x="700" y="242" class="val-e" font-size="10">(1 || 1.5)</text>

  <!-- 節點 D 處 1Ω || 1.5Ω 接地 -->
  <circle cx="670" cy="380" r="4" fill="#f59e0b"/>
  <text x="680" y="395" class="val-a" font-size="12">節點 D</text>
  <path d="M 670 380 L 670 310" class="wire"/>
  <rect x="655" y="325" width="30" height="35" fill="#334155" stroke="#10b981" rx="3"/>
  <text x="670" y="347" text-anchor="middle" class="val-e" font-size="11">0.6Ω</text>
  <line x1="655" y1="310" x2="685" y2="310" class="wire"/>

  <rect x="495" y="465" width="380" height="35" fill="#0f172a" stroke="#10b981" rx="6"/>
  <text x="685" y="488" text-anchor="middle" class="val-e" font-size="13">Io = Io,e + Io,o = 0 + 15/(1+0.6+0.6+1) = 75/16 A ≈ 4.69 A</text>
</svg>'''

# ----------------- 5. 107 年 第 1 題 (相依電流源) -----------------
svg_107_q1 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 540" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="box-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="0.95"/><stop offset="100%" stop-color="#0f172a" stop-opacity="0.95"/>
    </linearGradient>
    <marker id="arr-a" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#f59e0b"/>
    </marker>
    <marker id="arr-r" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#f43f5e"/>
    </marker>
  </defs>
  <style>
    .title { font-family: -apple-system, sans-serif; font-weight: 800; fill: #f8fafc; }
    .subtitle { font-family: -apple-system, sans-serif; font-size: 13px; fill: #94a3b8; }
    .val-c { font-family: monospace; font-size: 13px; font-weight: bold; fill: #38bdf8; }
    .val-a { font-family: monospace; font-size: 13px; font-weight: bold; fill: #f59e0b; }
    .val-r { font-family: monospace; font-size: 13px; font-weight: bold; fill: #f43f5e; }
    .val-e { font-family: monospace; font-size: 13px; font-weight: bold; fill: #10b981; }
    .wire { stroke: #94a3b8; stroke-width: 2.2; fill: none; stroke-linecap: round; }
    .box { stroke: #334155; stroke-width: 1.5; rx: 12; fill: url(#box-bg); }
  </style>

  <rect width="920" height="540" rx="16" fill="url(#bg)"/>
  <text x="460" y="38" text-anchor="middle" class="title" font-size="20">107 年 電路學 第一題：含流控相依電流源 (15 iφ) 節點分析與 4Ω 功率標定圖</text>
  <text x="460" y="60" text-anchor="middle" class="subtitle">控制變數：iφ = V1 / 20 (向下) ； 相依電流源：15 iφ = 0.75 V1 (向上注入節點 2)</text>

  <rect x="30" y="80" width="860" height="435" class="box"/>

  <!-- 50V 電源 -->
  <circle cx="120" cy="300" r="22" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="120" y="305" text-anchor="middle" class="val-c">50V</text>
  <text x="120" y="272" text-anchor="middle" class="val-c">+</text>
  <text x="120" y="338" text-anchor="middle" class="val-c">−</text>

  <!-- 頂部 1Ω 跨接線 -->
  <path d="M 120 278 L 120 170 L 760 170 L 760 300" class="wire"/>
  <rect x="420" y="160" width="50" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="445" y="175" text-anchor="middle" class="val-a">1 Ω</text>

  <!-- 中間水平支路 (5Ω 與 4Ω) -->
  <path d="M 120 278 L 120 300 L 460 300" class="wire"/>
  <rect x="230" y="290" width="50" height="20" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="255" y="305" text-anchor="middle" class="val-a">5 Ω</text>

  <!-- 節點 1 (V1) -->
  <circle cx="460" cy="300" r="6" fill="#38bdf8"/>
  <text x="460" y="280" text-anchor="middle" class="val-c" font-size="14">節點 1 (V1 = 200/3 V)</text>

  <!-- 20Ω 垂直支路 (iφ 向下) -->
  <path d="M 460 300 L 460 450" class="wire"/>
  <rect x="448" y="345" width="24" height="45" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="485" y="372" class="val-a">20 Ω</text>
  <!-- iφ 箭頭 -->
  <line x1="435" y1="350" x2="435" y2="385" stroke="#f59e0b" stroke-width="2" marker-end="url(#arr-a)"/>
  <text x="425" y="372" text-anchor="end" class="val-a">iφ</text>

  <!-- 4Ω 待求功率電阻 -->
  <path d="M 460 300 L 760 300" class="wire"/>
  <rect x="580" y="290" width="50" height="20" fill="#334155" stroke="#f43f5e" stroke-width="2" rx="3"/>
  <text x="605" y="305" text-anchor="middle" class="val-r" font-weight="bold">4 Ω</text>
  <!-- 電流 I_4Ω 箭頭 -->
  <line x1="640" y1="275" x2="570" y2="275" stroke="#f43f5e" stroke-width="2" marker-end="url(#arr-r)"/>
  <text x="605" y="265" text-anchor="middle" class="val-r">I_4Ω = -20/3 A (←)</text>

  <!-- 節點 2 (V2) -->
  <circle cx="760" cy="300" r="6" fill="#f43f5e"/>
  <text x="760" y="280" text-anchor="middle" class="val-r" font-size="14">節點 2 (V2 = 280/3 V)</text>

  <!-- 15 iφ 相依電流源 (向上注入節點 2) -->
  <path d="M 760 300 L 760 450" class="wire"/>
  <polygon points="760,350 785,380 760,410 735,380" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
  <line x1="760" y1="395" x2="760" y2="365" stroke="#f59e0b" stroke-width="2" marker-end="url(#arr-a)"/>
  <text x="800" y="385" class="val-a">15 iφ (↑)</text>

  <!-- 底部接地橫線 -->
  <path d="M 120 322 L 120 450 L 820 450" class="wire"/>
  <circle cx="120" cy="450" r="4" fill="#38bdf8"/>
  <circle cx="460" cy="450" r="4" fill="#38bdf8"/>
  <circle cx="760" cy="450" r="4" fill="#38bdf8"/>
  <text x="460" y="475" text-anchor="middle" class="val-c">參考接地（0 V）</text>

  <!-- 計算結果橫幅 -->
  <rect x="50" y="460" width="820" height="42" fill="#0f172a" stroke="#10b981" rx="8"/>
  <text x="460" y="487" text-anchor="middle" class="val-e" font-size="14">I_4Ω = (V1 - V2) / 4 = -20/3 A  ⇒  P_4Ω = |I|^2 · R = (20/3)^2 · 4 = 1600/9 W ≈ 177.78 W</text>
</svg>'''

files = [
    ("104年_電路學_第1題_戴維寧等效標定圖.svg", svg_104_q1),
    ("104年_電路學_第5題_雙埠g參數測試分析圖.svg", svg_104_q5),
    ("106年_電路學_第3題_GIC通用阻抗轉換器節點標定圖.svg", svg_106_q3),
    ("106年_電路學_第4題_對稱與反對稱半電路分析圖.svg", svg_106_q4),
    ("107年_電路學_第1題_相依電流源節點分析標定圖.svg", svg_107_q1),
]

for filename, content in files:
    filepath = os.path.join(target_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Generated: {filename}")
