#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Generator for Electronics (and Power Electronics) Equivalent Circuit SVGs
for all 11 years (104-114).
Generates vector graphics, embeds into Markdown files, and compiles the bundle.
"""

import os
import re
import subprocess

target_dir = "/Users/a/技師考試/歷屆試題_104-114年/依考科分類/02_電子學_含電力電子/images"
md_dir = "/Users/a/技師考試/歷屆試題_104-114年/📝 個人題解與錯題本/02_電子學_含電力電子"
os.makedirs(target_dir, exist_ok=True)

COMMON_DEFS = '''
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b0f19"/><stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="box-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="0.95"/><stop offset="100%" stop-color="#0f172a" stop-opacity="0.95"/>
    </linearGradient>
    <linearGradient id="accent-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0369a1" stop-opacity="0.25"/><stop offset="100%" stop-color="#0f172a" stop-opacity="0.6"/>
    </linearGradient>
    <marker id="arr-cyan" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8"/>
    </marker>
    <marker id="arr-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#f59e0b"/>
    </marker>
    <marker id="arr-rose" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#f43f5e"/>
    </marker>
    <marker id="arr-emerald" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981"/>
    </marker>
  </defs>
  <style>
    .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-weight: 800; fill: #f8fafc; }
    .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; fill: #94a3b8; }
    .label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; fill: #cbd5e1; }
    .val-cyan { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-size: 13px; font-weight: bold; fill: #38bdf8; }
    .val-amber { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-size: 13px; font-weight: bold; fill: #f59e0b; }
    .val-rose { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-size: 13px; font-weight: bold; fill: #f43f5e; }
    .val-emerald { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-size: 13px; font-weight: bold; fill: #10b981; }
    .val-purple { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-size: 13px; font-weight: bold; fill: #c084fc; }
    .wire { stroke: #94a3b8; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; fill: none; }
    .wire-active { stroke: #38bdf8; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; fill: none; }
    .wire-dash { stroke: #64748b; stroke-width: 1.8; stroke-dasharray: 4,4; fill: none; }
    .box { stroke: #334155; stroke-width: 1.5; rx: 12; fill: url(#box-bg); }
    .ground { stroke: #94a3b8; stroke-width: 2; stroke-linecap: round; }
  </style>
'''

# 113 Q1: 理想二極體電路狀態分析等效電路
svg_113_q1 = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 560" width="100%" height="100%">
{COMMON_DEFS}
  <rect width="950" height="560" rx="16" fill="url(#bg)"/>
  <text x="475" y="38" text-anchor="middle" class="title" font-size="20">113 年 電子學 第一題：理想二極體電路狀態分析與輸出電壓等效分析圖</text>
  <text x="475" y="60" text-anchor="middle" class="subtitle">狀態判定：D1 承受逆偏 (OFF, 開路)、D2 順偏導通 (ON, 短路) ⇒ Vo = 4 V</text>

  <!-- 左圖：假設一 (D1 ON, D2 ON) 矛盾判定 -->
  <rect x="25" y="80" width="435" height="450" class="box"/>
  <text x="45" y="110" class="title" font-size="16" fill="#f43f5e">【假設一】D1 導通 (ON), D2 導通 (ON) ⇒ 產生矛盾</text>
  <text x="45" y="130" class="subtitle">若 D1, D2 皆短路 ⇒ 節點電壓迫使 D1 電流反向流動 (iD1 &lt; 0 矛盾)</text>

  <circle cx="70" cy="220" r="16" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="70" y="225" text-anchor="middle" class="val-cyan">10V</text>
  <path d="M 70 204 L 70 170 L 130 170" class="wire"/>
  <rect x="130" y="158" width="45" height="24" fill="#334155" stroke="#38bdf8" rx="3"/>
  <text x="152" y="174" text-anchor="middle" class="val-cyan">R1=2k</text>

  <path d="M 175 170 L 250 170" class="wire"/>
  <circle cx="250" cy="170" r="5" fill="#f43f5e"/>
  <text x="250" y="150" text-anchor="middle" class="val-rose">Vx</text>

  <!-- D1 導通線路 (紅色叉標示矛盾) -->
  <path d="M 250 170 L 320 170" class="wire" stroke="#f43f5e"/>
  <line x1="320" y1="170" x2="380" y2="170" stroke="#f43f5e" stroke-width="3"/>
  <text x="350" y="155" text-anchor="middle" class="val-rose">D1 短路</text>
  <circle cx="380" cy="170" r="16" fill="#1e293b" stroke="#f43f5e" stroke-width="2"/>
  <text x="380" y="175" text-anchor="middle" class="val-rose">6V</text>

  <rect x="45" y="400" width="395" height="110" fill="#0f172a" stroke="#f43f5e" rx="8"/>
  <text x="60" y="430" class="val-rose" font-size="13">● 計算得 iD1 = (Vx - 6V)/R = -1.2 mA &lt; 0</text>
  <text x="60" y="460" class="label">二極體僅具單向導電性，無法逆向導通</text>
  <text x="60" y="490" class="val-rose" font-size="13">❌ 判定：D1 必處於截止狀態 (OFF)</text>

  <!-- 右圖：正確狀態 (D1 OFF, D2 ON) -->
  <rect x="490" y="80" width="435" height="450" class="box"/>
  <text x="510" y="110" class="title" font-size="16" fill="#10b981">【正確等效】D1 截止 (OFF 開路), D2 導通 (ON 短路)</text>
  <text x="510" y="130" class="subtitle">D1 開路無電流，由 10V 電源與 R1, R2 分壓求得 Vo = 4 V</text>

  <!-- 10V 電源 -->
  <circle cx="530" cy="220" r="16" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="530" y="225" text-anchor="middle" class="val-cyan">10V</text>
  <path d="M 530 204 L 530 170 L 590 170" class="wire-active"/>
  
  <!-- R1 = 3kΩ -->
  <rect x="590" y="158" width="50" height="24" fill="#334155" stroke="#38bdf8" rx="3"/>
  <text x="615" y="174" text-anchor="middle" class="val-cyan">R1=3kΩ</text>

  <!-- 節點 Vo -->
  <path d="M 640 170 L 720 170" class="wire-active"/>
  <circle cx="720" cy="170" r="6" fill="#10b981"/>
  <text x="720" y="145" text-anchor="middle" class="val-emerald" font-size="15">Vo</text>

  <!-- D1 截止開路 (上方虛線) -->
  <path d="M 720 170 L 720 120 L 760 120" class="wire-dash"/>
  <circle cx="760" cy="120" r="4" fill="#64748b"/>
  <circle cx="800" cy="120" r="4" fill="#64748b"/>
  <text x="780" y="105" text-anchor="middle" class="label" font-size="11">D1 (開路 OFF)</text>
  <path d="M 800 120 L 840 120" class="wire-dash"/>
  <circle cx="855" cy="120" r="14" fill="#1e293b" stroke="#64748b"/>
  <text x="855" y="124" text-anchor="middle" class="label" font-size="10">6V</text>

  <!-- D2 導通短路 (實線連接 R2) -->
  <path d="M 720 170 L 720 220" class="wire-active"/>
  <polygon points="710,220 730,220 720,240" fill="#10b981" stroke="#10b981"/>
  <line x1="710" y1="240" x2="730" y2="240" stroke="#10b981" stroke-width="3"/>
  <text x="750" y="235" class="val-emerald" font-size="11">D2 (ON)</text>
  <path d="M 720 240 L 720 280" class="wire-active"/>

  <!-- R2 = 2kΩ -->
  <rect x="708" y="280" width="24" height="45" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="745" y="305" class="val-amber">R2=2kΩ</text>
  <path d="M 720 325 L 720 370 L 530 370 L 530 236" class="wire-active"/>
  <line x1="620" y1="370" x2="640" y2="370" class="ground"/>

  <!-- 結論框 -->
  <rect x="510" y="400" width="395" height="110" fill="#0f172a" stroke="#10b981" rx="8"/>
  <text x="525" y="430" class="val-emerald" font-size="14">✅ (一) D1 截止 (OFF)、D2 導通 (ON)</text>
  <text x="525" y="460" class="val-cyan" font-size="14">✅ (二) 輸出電壓分壓公式：</text>
  <text x="525" y="490" class="val-amber" font-size="15">Vo = 10V × [R2 / (R1 + R2)] = 10 × (2/5) = 4.0 V</text>
</svg>'''

# 112 Q3: 降升壓 Buck-Boost 轉換器操作狀態等效電路
svg_112_q3 = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 560" width="100%" height="100%">
{COMMON_DEFS}
  <rect width="950" height="560" rx="16" fill="url(#bg)"/>
  <text x="475" y="38" text-anchor="middle" class="title" font-size="20">112 年 電子學 第三題：降升壓型 (Buck-Boost) 轉換器二操作狀態等效電路與設計分析圖</text>
  <text x="475" y="60" text-anchor="middle" class="subtitle">極性反轉：Vo/Vs = -D/(1-D)，CCM 操作條件，電感與電容極小值設計</text>

  <!-- 左圖：狀態 1 S ON, D OFF -->
  <rect x="25" y="80" width="435" height="340" class="box"/>
  <text x="45" y="110" class="title" font-size="15" fill="#38bdf8">【狀態一】開關 S 導通 (0 ≤ t ≤ DTs)</text>
  <text x="45" y="130" class="subtitle">電源 Vs 直接跨於電感 L 兩端儲能，vL = +Vs，二極體 D 逆偏截止</text>

  <!-- Vs -->
  <circle cx="65" cy="220" r="16" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="65" y="225" text-anchor="middle" class="val-cyan">Vs</text>
  <path d="M 65 204 L 65 170 L 120 170" class="wire-active"/>
  <circle cx="120" cy="170" r="4" fill="#38bdf8"/>
  <line x1="120" y1="170" x2="170" y2="170" stroke="#38bdf8" stroke-width="3"/>
  <circle cx="170" cy="170" r="4" fill="#38bdf8"/>
  <text x="145" y="155" text-anchor="middle" class="val-cyan">S (ON)</text>

  <!-- 電感 L (向下接地) -->
  <path d="M 170 170 L 220 170 L 220 200" class="wire-active"/>
  <path d="M 220 200 A 7 7 0 0 1 220 214 A 7 7 0 0 1 220 228 A 7 7 0 0 1 220 242 A 7 7 0 0 1 220 256" class="wire-active" fill="none"/>
  <text x="240" y="230" class="val-amber">L</text>
  <path d="M 220 256 L 220 290 L 65 290 L 65 236" class="wire-active"/>
  <line x1="140" y1="290" x2="160" y2="290" class="ground"/>

  <!-- 右側負載由電容 C 獨立供電 -->
  <path d="M 330 200 L 330 290" class="wire-active"/>
  <line x1="318" y1="220" x2="342" y2="220" stroke="#10b981" stroke-width="3"/>
  <line x1="318" y1="228" x2="342" y2="228" stroke="#10b981" stroke-width="3"/>
  <text x="310" y="225" class="val-emerald">C</text>

  <path d="M 330 200 L 400 200 L 400 225" class="wire-active"/>
  <rect x="388" y="225" width="24" height="40" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="420" y="248" class="val-amber">R</text>
  <path d="M 400 265 L 400 290 L 330 290" class="wire-active"/>
  <text x="400" y="185" text-anchor="middle" class="val-rose">- Vo (負電壓)</text>

  <!-- 右圖：狀態 2 S OFF, D ON -->
  <rect x="490" y="80" width="435" height="340" class="box"/>
  <text x="510" y="110" class="title" font-size="15" fill="#f59e0b">【狀態二】開關 S 截止 (DTs ≤ t ≤ Ts)</text>
  <text x="510" y="130" class="subtitle">電感 L 釋能，反向經順偏二極體 D 對 C 與 R 供電，vL = -Vo</text>

  <!-- 電感 L -->
  <path d="M 580 200 A 7 7 0 0 1 580 214 A 7 7 0 0 1 580 228 A 7 7 0 0 1 580 242 A 7 7 0 0 1 580 256" class="wire-active" fill="none"/>
  <text x="555" y="230" class="val-amber">L</text>
  <path d="M 580 256 L 580 290" class="wire-active"/>
  <path d="M 580 200 L 580 170 L 660 170" class="wire-active"/>

  <!-- 二極體 D (朝右順偏導通) -->
  <polygon points="660,162 660,178 676,170" fill="#10b981" stroke="#10b981"/>
  <line x1="676" y1="162" x2="676" y2="178" stroke="#10b981" stroke-width="3"/>
  <text x="668" y="150" text-anchor="middle" class="val-emerald">D (ON)</text>

  <!-- 負載 C || R -->
  <path d="M 676 170 L 760 170 L 760 205" class="wire-active"/>
  <line x1="748" y1="205" x2="772" y2="205" stroke="#10b981" stroke-width="3"/>
  <line x1="748" y1="213" x2="772" y2="213" stroke="#10b981" stroke-width="3"/>
  <path d="M 760 213 L 760 290" class="wire-active"/>
  <text x="740" y="210" class="val-emerald">C</text>

  <path d="M 760 170 L 840 170 L 840 200" class="wire-active"/>
  <rect x="828" y="200" width="24" height="40" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="860" y="225" class="val-amber">R</text>
  <path d="M 840 240 L 840 290 L 580 290" class="wire-active"/>
  <line x1="710" y1="290" x2="730" y2="290" class="ground"/>

  <!-- 下方結論卡片 -->
  <rect x="25" y="435" width="280" height="105" class="box"/>
  <text x="40" y="460" class="val-cyan" font-size="13">1. 電壓轉換比 Vo/Vs</text>
  <text x="40" y="485" class="val-cyan">|Vo| = [D / (1 - D)] · Vs</text>
  <text x="40" y="515" class="val-emerald" font-size="14">輸出極性永遠與輸入相反</text>

  <rect x="330" y="435" width="285" height="105" class="box"/>
  <text x="345" y="460" class="val-amber" font-size="13">2. 臨界電感 Lmin</text>
  <text x="345" y="485" class="label">維持 CCM 導通條件：</text>
  <text x="345" y="515" class="val-amber" font-size="14">Lmin = (1 - D)² · R / (2 fs)</text>

  <rect x="635" y="435" width="290" height="105" class="box"/>
  <text x="650" y="460" class="val-rose" font-size="13">3. 濾波電容 Cmin</text>
  <text x="650" y="485" class="label">漣波比限制 ΔVo/Vo：</text>
  <text x="650" y="515" class="val-rose" font-size="14">Cmin = D / (R · fs · (ΔVo/Vo))</text>
</svg>'''

# 110 Q1: BJT 集極回授偏壓小訊號等效電路
svg_110_q1 = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 560" width="100%" height="100%">
{COMMON_DEFS}
  <rect width="950" height="560" rx="16" fill="url(#bg)"/>
  <text x="475" y="38" text-anchor="middle" class="title" font-size="20">110 年 電子學 第一題：BJT 集極回授偏壓電路與小訊號等效分析圖</text>
  <text x="475" y="60" text-anchor="middle" class="subtitle">負回授自穩定機制：溫升使 IC 增加 ⇒ VC 下降 ⇒ IB = (VC - VBE)/RB 下降 ⇒ 抑制 IC 漂移</text>

  <rect x="30" y="80" width="890" height="340" class="box"/>

  <!-- 信號源 vsig, Rsig -->
  <circle cx="80" cy="220" r="16" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="80" y="225" text-anchor="middle" class="val-cyan">vsig</text>
  <path d="M 80 236 L 80 290" class="wire"/>
  <line x1="70" y1="290" x2="90" y2="290" class="ground"/>

  <path d="M 96 220 L 150 220" class="wire"/>
  <rect x="150" y="208" width="45" height="24" fill="#334155" stroke="#38bdf8" rx="3"/>
  <text x="172" y="224" text-anchor="middle" class="val-cyan">Rsig</text>

  <!-- 基極 B 與 rπ -->
  <path d="M 195 220 L 260 220" class="wire"/>
  <circle cx="260" cy="220" r="5" fill="#38bdf8"/>
  <text x="260" y="200" text-anchor="middle" class="val-cyan">B (基極)</text>

  <path d="M 260 220 L 260 250" class="wire"/>
  <rect x="248" y="250" width="24" height="40" fill="#334155" stroke="#38bdf8" rx="3"/>
  <text x="220" y="275" class="val-cyan">rπ</text>
  <path d="M 260 290 L 260 310" class="wire"/>
  <line x1="250" y1="310" x2="270" y2="310" class="ground"/>

  <!-- 集極回授電阻 RB 跨接 B 與 C 兩端 -->
  <path d="M 260 220 L 260 140 L 580 140 L 580 220" class="wire" stroke="#f43f5e" stroke-width="2.2"/>
  <rect x="390" y="128" width="60" height="24" fill="#334155" stroke="#f43f5e" rx="3"/>
  <text x="420" y="144" text-anchor="middle" class="val-rose">RB (回授電阻)</text>

  <!-- 集極受控源 gm vbe -->
  <path d="M 580 220 L 580 250" class="wire"/>
  <circle cx="580" cy="270" r="16" fill="#1e293b" stroke="#f59e0b" stroke-width="1.8"/>
  <line x1="580" y1="282" x2="580" y2="258" stroke="#f59e0b" stroke-width="2" marker-end="url(#arr-amber)"/>
  <path d="M 580 286 L 580 310" class="wire"/>
  <line x1="570" y1="310" x2="590" y2="310" class="ground"/>
  <text x="510" y="275" class="val-amber">gm·vbe</text>

  <!-- 集極 C 與 RC 負載 -->
  <circle cx="580" cy="220" r="5" fill="#f59e0b"/>
  <text x="580" y="200" text-anchor="middle" class="val-amber">C (集極)</text>

  <path d="M 580 220 L 720 220 L 720 250" class="wire"/>
  <rect x="708" y="250" width="24" height="40" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="745" y="275" class="val-amber">RC</text>
  <path d="M 720 290 L 720 310" class="wire"/>
  <line x1="710" y1="310" x2="730" y2="310" class="ground"/>

  <!-- 輸出 vo -->
  <path d="M 720 220 L 820 220" class="wire"/>
  <circle cx="820" cy="220" r="5" fill="#10b981"/>
  <text x="820" y="200" text-anchor="middle" class="val-emerald" font-size="14">vo</text>

  <!-- 結論卡片 -->
  <rect x="30" y="435" width="280" height="105" class="box"/>
  <text x="45" y="460" class="val-cyan" font-size="13">1. 直流工作點 IC</text>
  <text x="45" y="485" class="val-cyan">IB = (VCC - VBE) / [RB + (β+1)RC]</text>
  <text x="45" y="515" class="val-emerald" font-size="14">IC = β · IB</text>

  <rect x="335" y="435" width="280" height="105" class="box"/>
  <text x="350" y="460" class="val-rose" font-size="13">2. 負回授穩定機制</text>
  <text x="350" y="485" class="label">T↑ ⇒ IC↑ ⇒ VC↓ ⇒ IB↓</text>
  <text x="350" y="515" class="val-rose" font-size="14">自動下拉抑制溫漂</text>

  <rect x="640" y="435" width="280" height="105" class="box"/>
  <text x="655" y="460" class="val-amber" font-size="13">3. 交流電壓增益 Av</text>
  <text x="655" y="485" class="label">米勒定理等效分拆 RB：</text>
  <text x="655" y="515" class="val-amber" font-size="14">Av ≈ -gm · (RC || RB)</text>
</svg>'''

# 109 Q2: 昇壓型 Boost 轉換器二操作狀態等效電路
svg_109_q2 = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 560" width="100%" height="100%">
{COMMON_DEFS}
  <rect width="950" height="560" rx="16" fill="url(#bg)"/>
  <text x="475" y="38" text-anchor="middle" class="title" font-size="20">109 年 電子學 第二題：昇壓型 (Boost) 轉換器二操作狀態等效電路分析圖</text>
  <text x="475" y="60" text-anchor="middle" class="subtitle">昇壓規律：Vo/Vs = 1/(1-D) > 1，臨界電感 Lmin = D(1-D)² R / (2 fs)</text>

  <!-- 左圖：狀態 1 S ON, D OFF -->
  <rect x="25" y="80" width="435" height="340" class="box"/>
  <text x="45" y="110" class="title" font-size="15" fill="#38bdf8">【狀態一】開關 S 閉合導通 (0 ≤ t ≤ DTs)</text>
  <text x="45" y="130" class="subtitle">電源 Vs 直接對電感 L 充電，vL = Vs > 0，iL 自 ILmin 升至 ILmax</text>

  <!-- Vs -->
  <circle cx="65" cy="220" r="16" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="65" y="225" text-anchor="middle" class="val-cyan">Vs</text>
  <path d="M 65 204 L 65 170 L 110 170" class="wire-active"/>

  <!-- 電感 L -->
  <path d="M 110 170 A 7 7 0 0 1 124 170 A 7 7 0 0 1 138 170 A 7 7 0 0 1 152 170 A 7 7 0 0 1 166 170" class="wire-active" fill="none"/>
  <text x="138" y="150" text-anchor="middle" class="val-amber">L</text>

  <!-- 開關 S (ON 短路接地) -->
  <path d="M 166 170 L 220 170 L 220 200" class="wire-active"/>
  <circle cx="220" cy="200" r="4" fill="#38bdf8"/>
  <line x1="220" y1="200" x2="220" y2="250" stroke="#38bdf8" stroke-width="3"/>
  <circle cx="220" cy="250" r="4" fill="#38bdf8"/>
  <text x="245" y="225" class="val-cyan">S (ON)</text>
  <path d="M 220 250 L 220 290 L 65 290 L 65 236" class="wire-active"/>
  <line x1="140" y1="290" x2="160" y2="290" class="ground"/>

  <!-- 右側負載由電容 C 獨立供電 -->
  <path d="M 330 200 L 330 290" class="wire-active"/>
  <line x1="318" y1="220" x2="342" y2="220" stroke="#10b981" stroke-width="3"/>
  <line x1="318" y1="228" x2="342" y2="228" stroke="#10b981" stroke-width="3"/>
  <text x="310" y="225" class="val-emerald">C</text>

  <path d="M 330 200 L 400 200 L 400 225" class="wire-active"/>
  <rect x="388" y="225" width="24" height="40" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="420" y="248" class="val-amber">R</text>
  <path d="M 400 265 L 400 290 L 330 290" class="wire-active"/>

  <!-- 右圖：狀態 2 S OFF, D ON -->
  <rect x="490" y="80" width="435" height="340" class="box"/>
  <text x="510" y="110" class="title" font-size="15" fill="#f59e0b">【狀態二】開關 S 斷開截止 (DTs ≤ t ≤ Ts)</text>
  <text x="510" y="130" class="subtitle">電源 Vs 與電感釋能疊加供電，vL = Vs - Vo &lt; 0，二極體 D 導通</text>

  <!-- Vs + L 疊加 -->
  <circle cx="530" cy="220" r="16" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="530" y="225" text-anchor="middle" class="val-cyan">Vs</text>
  <path d="M 530 204 L 530 170 L 570 170" class="wire-active"/>
  <path d="M 570 170 A 7 7 0 0 1 584 170 A 7 7 0 0 1 598 170 A 7 7 0 0 1 612 170 A 7 7 0 0 1 626 170" class="wire-active" fill="none"/>
  <text x="598" y="150" text-anchor="middle" class="val-amber">L</text>

  <!-- 二極體 D 順偏導通 -->
  <path d="M 626 170 L 670 170" class="wire-active"/>
  <polygon points="670,162 670,178 686,170" fill="#10b981" stroke="#10b981"/>
  <line x1="686" y1="162" x2="686" y2="178" stroke="#10b981" stroke-width="3"/>
  <text x="678" y="150" text-anchor="middle" class="val-emerald">D (ON)</text>

  <!-- 負載 C || R -->
  <path d="M 686 170 L 760 170 L 760 205" class="wire-active"/>
  <line x1="748" y1="205" x2="772" y2="205" stroke="#10b981" stroke-width="3"/>
  <line x1="748" y1="213" x2="772" y2="213" stroke="#10b981" stroke-width="3"/>
  <path d="M 760 213 L 760 290" class="wire-active"/>
  <text x="740" y="210" class="val-emerald">C</text>

  <path d="M 760 170 L 840 170 L 840 200" class="wire-active"/>
  <rect x="828" y="200" width="24" height="40" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="860" y="225" class="val-amber">R</text>
  <path d="M 840 240 L 840 290 L 530 290 L 530 236" class="wire-active"/>
  <line x1="710" y1="290" x2="730" y2="290" class="ground"/>

  <!-- 下方結論卡片 -->
  <rect x="25" y="435" width="280" height="105" class="box"/>
  <text x="40" y="460" class="val-cyan" font-size="13">1. 電壓轉換比 Vo/Vs</text>
  <text x="40" y="485" class="val-cyan">Vo = Vs / (1 - D)</text>
  <text x="40" y="515" class="val-emerald" font-size="14">輸出電壓必定高於輸入電壓</text>

  <rect x="330" y="435" width="285" height="105" class="box"/>
  <text x="345" y="460" class="val-amber" font-size="13">2. 臨界電感 Lmin</text>
  <text x="345" y="485" class="label">維持連續導通 CCM：</text>
  <text x="345" y="515" class="val-amber" font-size="14">Lmin = D(1 - D)² · R / (2 fs)</text>

  <rect x="635" y="435" width="290" height="105" class="box"/>
  <text x="650" y="460" class="val-rose" font-size="13">3. 電壓漣波比 ΔVo/Vo</text>
  <text x="650" y="485" class="label">電容放電電荷量：</text>
  <text x="650" y="515" class="val-rose" font-size="14">ΔVo/Vo = D / (R · C · fs)</text>
</svg>'''

# 108 Q4: GIC 主動濾波器等效電路
svg_108_q4 = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 560" width="100%" height="100%">
{COMMON_DEFS}
  <rect width="950" height="560" rx="16" fill="url(#bg)"/>
  <text x="475" y="38" text-anchor="middle" class="title" font-size="20">108 年 電子學 第四題：雙運算放大器 GIC 通用阻抗轉換器等效電感電路圖</text>
  <text x="475" y="60" text-anchor="middle" class="subtitle">Antoniou 電感模擬：Zin(s) = (Z1·Z3·Z5) / (Z2·Z4) ⇒ 當 Z4 = 1/sC4 時，Zin(s) = s·Leq (無磁芯高品質電感)</text>

  <rect x="30" y="80" width="890" height="340" class="box"/>

  <!-- 輸入節點 1 與 Zin -->
  <circle cx="80" cy="180" r="5" fill="#38bdf8"/>
  <text x="80" y="160" text-anchor="middle" class="val-cyan" font-size="14">節點 1 (輸入端)</text>
  <line x1="80" y1="180" x2="130" y2="180" stroke="#38bdf8" stroke-width="2" marker-end="url(#arr-cyan)"/>
  <text x="105" y="205" text-anchor="middle" class="val-cyan">Zin(s)</text>

  <!-- GIC 五阻抗鏈 -->
  <!-- Z1 = R1 -->
  <path d="M 130 180 L 180 180" class="wire"/>
  <rect x="180" y="168" width="50" height="24" fill="#334155" stroke="#38bdf8" rx="3"/>
  <text x="205" y="184" text-anchor="middle" class="val-cyan">Z1 = R1</text>

  <!-- 節點 2 -->
  <path d="M 230 180 L 280 180" class="wire"/>
  <circle cx="280" cy="180" r="4" fill="#f59e0b"/>

  <!-- Z2 = R2 -->
  <rect x="280" y="168" width="50" height="24" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="305" y="184" text-anchor="middle" class="val-amber">Z2 = R2</text>

  <!-- 節點 3 -->
  <path d="M 330 180 L 380 180" class="wire"/>
  <circle cx="380" cy="180" r="4" fill="#f59e0b"/>

  <!-- Z3 = R3 -->
  <rect x="380" y="168" width="50" height="24" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="405" y="184" text-anchor="middle" class="val-amber">Z3 = R3</text>

  <!-- 節點 4 與 Z4 = 1/sC4 -->
  <path d="M 430 180 L 480 180" class="wire"/>
  <circle cx="480" cy="180" r="4" fill="#10b981"/>
  <line x1="495" y1="168" x2="495" y2="192" stroke="#10b981" stroke-width="3"/>
  <line x1="503" y1="168" x2="503" y2="192" stroke="#10b981" stroke-width="3"/>
  <text x="499" y="155" text-anchor="middle" class="val-emerald">Z4=1/sC4</text>

  <!-- 節點 5 與 Z5 = R5 (接地) -->
  <path d="M 503 180 L 560 180" class="wire"/>
  <circle cx="560" cy="180" r="4" fill="#c084fc"/>
  <rect x="560" y="168" width="50" height="24" fill="#334155" stroke="#c084fc" rx="3"/>
  <text x="585" y="184" text-anchor="middle" class="val-purple">Z5 = R5</text>
  <path d="M 610 180 L 650 180" class="wire"/>
  <line x1="650" y1="170" x2="650" y2="190" class="ground"/>

  <!-- 等效電感標註方塊 -->
  <rect x="680" y="140" width="220" height="150" fill="#1e293b" stroke="#38bdf8" stroke-width="2" rx="8"/>
  <text x="790" y="175" text-anchor="middle" class="val-cyan" font-size="16">等效模擬電感 Leq</text>
  <text x="790" y="210" text-anchor="middle" class="val-emerald" font-size="14">Leq = (C4·R1·R3·R5) / R2</text>
  <text x="790" y="245" text-anchor="middle" class="label" font-size="12">取代笨重、耗能之實體電感</text>
  <text x="790" y="270" text-anchor="middle" class="val-amber" font-size="12">構成高 Q 階主動帶通濾波器</text>

  <!-- 下方結論卡片 -->
  <rect x="30" y="435" width="280" height="105" class="box"/>
  <text x="45" y="460" class="val-cyan" font-size="13">1. GIC 阻抗轉換通式</text>
  <text x="45" y="485" class="val-cyan">Zin(s) = (Z1·Z3·Z5) / (Z2·Z4)</text>
  <text x="45" y="515" class="val-emerald" font-size="14">雙 OP 虛短路與負回授推導</text>

  <rect x="335" y="435" width="280" height="105" class="box"/>
  <text x="350" y="460" class="val-amber" font-size="13">2. 濾波器類型與階數</text>
  <text x="350" y="485" class="label">並聯 RLC 諧振回路：</text>
  <text x="350" y="515" class="val-amber" font-size="14">二階帶通濾波器 (2nd BPF)</text>

  <rect x="640" y="435" width="280" height="105" class="box"/>
  <text x="655" y="460" class="val-rose" font-size="13">3. 中心頻率與品質因數</text>
  <text x="655" y="485" class="label">ω0 = 1 / √(Leq·C)</text>
  <text x="655" y="515" class="val-rose" font-size="14">Q = R · √(C / Leq)</text>
</svg>'''

# 107 Q2: NMOS 混合 pi 小訊號等效模型
svg_107_q2 = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 560" width="100%" height="100%">
{COMMON_DEFS}
  <rect width="950" height="560" rx="16" fill="url(#bg)"/>
  <text x="475" y="38" text-anchor="middle" class="title" font-size="20">107 年 電子學 第二題：NMOS 混合 π (Hybrid-π) 小訊號等效模型與雙偏壓參數分析圖</text>
  <text x="475" y="60" text-anchor="middle" class="subtitle">轉導 gm = 2ID/(VGS - Vt) = √(2 kn' (W/L) ID)，輸出電阻 ro = (VA + VDS) / ID = 1 / (λ·ID)</text>

  <rect x="30" y="80" width="890" height="340" class="box"/>

  <!-- 閘極 G -->
  <circle cx="100" cy="180" r="5" fill="#38bdf8"/>
  <text x="100" y="160" text-anchor="middle" class="val-cyan" font-size="14">G (閘極)</text>
  <path d="M 100 180 L 220 180" class="wire"/>
  <circle cx="220" cy="180" r="4" fill="#38bdf8"/>
  <text x="180" y="170" class="val-cyan">vgs (+)</text>

  <!-- 源極 S (地) -->
  <circle cx="100" cy="300" r="5" fill="#38bdf8"/>
  <text x="100" y="325" text-anchor="middle" class="val-cyan" font-size="14">S (源極)</text>
  <path d="M 100 300 L 220 300" class="wire"/>
  <circle cx="220" cy="300" r="4" fill="#38bdf8"/>
  <text x="180" y="290" class="val-cyan">vgs (−)</text>
  <line x1="220" y1="300" x2="220" y2="330" class="wire"/>
  <line x1="210" y1="330" x2="230" y2="330" class="ground"/>

  <!-- 閘源開路虛線 -->
  <line x1="220" y1="180" x2="220" y2="300" class="wire-dash"/>
  <text x="250" y="245" class="label" font-size="11">Rin = ∞ (絕緣閘極)</text>

  <!-- 汲極受控源 gm vgs -->
  <path d="M 520 180 L 520 215" class="wire"/>
  <circle cx="520" cy="240" r="18" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
  <line x1="520" y1="225" x2="520" y2="255" stroke="#f59e0b" stroke-width="2" marker-end="url(#arr-amber)"/>
  <path d="M 520 258 L 520 300 L 220 300" class="wire"/>
  <text x="440" y="245" class="val-amber" font-size="13">id = gm·vgs</text>

  <!-- 通道長度調變輸出電阻 ro -->
  <path d="M 520 180 L 660 180 L 660 215" class="wire"/>
  <rect x="648" y="215" width="24" height="50" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="685" y="245" class="val-amber">ro = (VA + VDS)/ID</text>
  <path d="M 660 265 L 660 300 L 520 300" class="wire"/>

  <!-- 汲極 D -->
  <circle cx="800" cy="180" r="5" fill="#f59e0b"/>
  <text x="800" y="160" text-anchor="middle" class="val-amber" font-size="14">D (汲極)</text>
  <path d="M 660 180 L 800 180" class="wire"/>

  <!-- 結論卡片 -->
  <rect x="30" y="435" width="280" height="105" class="box"/>
  <text x="45" y="460" class="val-cyan" font-size="13">1. 偏壓一 (ID1, VGS1, VDS1)</text>
  <text x="45" y="485" class="val-cyan">gm1 = 2ID1 / (VGS1 - Vt)</text>
  <text x="45" y="515" class="val-emerald" font-size="14">ro1 = (VA + VDS1) / ID1</text>

  <rect x="335" y="435" width="280" height="105" class="box"/>
  <text x="350" y="460" class="val-amber" font-size="13">2. 偏壓二 (ID2, VGS2, VDS2)</text>
  <text x="350" y="485" class="val-amber">gm2 = 2ID2 / (VGS2 - Vt)</text>
  <text x="350" y="515" class="val-emerald" font-size="14">ro2 = (VA + VDS2) / ID2</text>

  <rect x="640" y="435" width="280" height="105" class="box"/>
  <text x="655" y="460" class="val-rose" font-size="13">3. 本質電壓增益 A0</text>
  <text x="655" y="485" class="label">單級共源極極限增益：</text>
  <text x="655" y="515" class="val-rose" font-size="14">A0 = gm · ro = 2VA / VOV</text>
</svg>'''

# 106 Q3: BJT 共射極放大器米勒等效高頻電路
svg_106_q3 = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 560" width="100%" height="100%">
{COMMON_DEFS}
  <rect width="950" height="560" rx="16" fill="url(#bg)"/>
  <text x="475" y="38" text-anchor="middle" class="title" font-size="20">106 年 電子學 第三題：BJT 共射極放大器米勒等效 (Miller Effect) 高頻小訊號模型圖</text>
  <text x="475" y="60" text-anchor="middle" class="subtitle">米勒拆解：跨接電容 Cμ 拆為輸入端 CM1 = Cμ·(1 - K) 與輸出端 CM2 = Cμ·(1 - 1/K)，其中中頻增益 K = -gm·(RC||RL)</text>

  <rect x="30" y="80" width="890" height="340" class="box"/>

  <!-- 輸入信號源 vsig, Rsig -->
  <circle cx="70" cy="220" r="16" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="70" y="225" text-anchor="middle" class="val-cyan">vsig</text>
  <path d="M 70 236 L 70 290" class="wire"/>
  <line x1="60" y1="290" x2="80" y2="290" class="ground"/>

  <path d="M 86 220 L 130 220" class="wire"/>
  <rect x="130" y="208" width="45" height="24" fill="#334155" stroke="#38bdf8" rx="3"/>
  <text x="152" y="224" text-anchor="middle" class="val-cyan">Rsig</text>

  <!-- 基極節點 B -->
  <path d="M 175 220 L 230 220" class="wire"/>
  <circle cx="230" cy="220" r="5" fill="#38bdf8"/>
  <text x="230" y="200" text-anchor="middle" class="val-cyan" font-size="14">B (基極)</text>

  <!-- rπ 電阻 -->
  <path d="M 230 220 L 230 250" class="wire"/>
  <rect x="218" y="250" width="24" height="35" fill="#334155" stroke="#38bdf8" rx="3"/>
  <text x="190" y="270" class="val-cyan">rπ</text>
  <path d="M 230 285 L 230 310" class="wire"/>
  <line x1="220" y1="310" x2="240" y2="310" class="ground"/>

  <!-- Cπ 電容 -->
  <path d="M 230 220 L 300 220 L 300 250" class="wire"/>
  <line x1="288" y1="250" x2="312" y2="250" stroke="#38bdf8" stroke-width="3"/>
  <line x1="288" y1="258" x2="312" y2="258" stroke="#38bdf8" stroke-width="3"/>
  <path d="M 300 258 L 300 310" class="wire"/>
  <line x1="290" y1="310" x2="310" y2="310" class="ground"/>
  <text x="330" y="260" class="val-cyan">Cπ</text>

  <!-- 米勒輸入電容 CM1 = Cμ·(1 + gm R'L) (紅框重點) -->
  <path d="M 300 220 L 390 220 L 390 250" class="wire" stroke="#f43f5e"/>
  <line x1="378" y1="250" x2="402" y2="250" stroke="#f43f5e" stroke-width="3"/>
  <line x1="378" y1="258" x2="402" y2="258" stroke="#f43f5e" stroke-width="3"/>
  <path d="M 390 258 L 390 310" class="wire" stroke="#f43f5e"/>
  <line x1="380" y1="310" x2="400" y2="310" class="ground"/>
  <text x="445" y="255" class="val-rose" font-size="11">CM1 = Cμ(1+|K|)</text>
  <text x="445" y="272" class="val-rose" font-size="10">(米勒放大百倍)</text>

  <!-- 集極受控源 gm vbe -->
  <path d="M 580 220 L 580 250" class="wire"/>
  <circle cx="580" cy="270" r="16" fill="#1e293b" stroke="#f59e0b" stroke-width="1.8"/>
  <line x1="580" y1="282" x2="580" y2="258" stroke="#f59e0b" stroke-width="2" marker-end="url(#arr-amber)"/>
  <path d="M 580 286 L 580 310" class="wire"/>
  <line x1="570" y1="310" x2="590" y2="310" class="ground"/>
  <text x="510" y="275" class="val-amber">gm·vbe</text>

  <!-- 集極節點 C -->
  <circle cx="580" cy="220" r="5" fill="#f59e0b"/>
  <text x="580" y="200" text-anchor="middle" class="val-amber" font-size="14">C (集極)</text>

  <!-- 米勒輸出電容 CM2 ≈ Cμ -->
  <path d="M 580 220 L 660 220 L 660 250" class="wire" stroke="#f43f5e"/>
  <line x1="648" y1="250" x2="672" y2="250" stroke="#f43f5e" stroke-width="3"/>
  <line x1="648" y1="258" x2="672" y2="258" stroke="#f43f5e" stroke-width="3"/>
  <path d="M 660 258 L 660 310" class="wire" stroke="#f43f5e"/>
  <line x1="650" y1="310" x2="670" y2="310" class="ground"/>
  <text x="705" y="260" class="val-rose" font-size="11">CM2 ≈ Cμ</text>

  <!-- 負載電阻 R'L = RC || RL -->
  <path d="M 660 220 L 760 220 L 760 250" class="wire"/>
  <rect x="748" y="250" width="24" height="40" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="780" y="275" class="val-amber">R'L</text>
  <path d="M 760 290 L 760 310" class="wire"/>
  <line x1="750" y1="310" x2="770" y2="310" class="ground"/>

  <!-- 輸出 vo -->
  <path d="M 760 220 L 850 220" class="wire"/>
  <circle cx="850" cy="220" r="5" fill="#10b981"/>
  <text x="850" y="200" text-anchor="middle" class="val-emerald" font-size="14">vo</text>

  <!-- 結論卡片 -->
  <rect x="30" y="435" width="280" height="105" class="box"/>
  <text x="45" y="460" class="val-rose" font-size="13">1. 米勒效應 (Miller Effect)</text>
  <text x="45" y="485" class="val-rose">CM1 = Cμ · (1 + gm·R'L)</text>
  <text x="45" y="515" class="val-rose" font-size="14">輸入端等效電容急遽膨脹</text>

  <rect x="335" y="435" width="280" height="105" class="box"/>
  <text x="350" y="460" class="val-cyan" font-size="13">2. 主極點頻率 fH</text>
  <text x="350" y="485" class="label">輸入迴路時間常數主導：</text>
  <text x="350" y="515" class="val-cyan" font-size="14">fH ≈ 1 / [2π (Rsig||rπ)(Cπ + CM1)]</text>

  <rect x="640" y="435" width="280" height="105" class="box"/>
  <text x="655" y="460" class="val-emerald" font-size="13">3. 增益-頻寬積 (GBW)</text>
  <text x="655" y="485" class="label">共基極/疊接電路消除米勒效應</text>
  <text x="655" y="515" class="val-emerald" font-size="14">高頻頻寬可大幅拓展數十倍</text>
</svg>'''

# 105 Q2: 實體反相運算放大器等效電路模型
svg_105_q2 = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 560" width="100%" height="100%">
{COMMON_DEFS}
  <rect width="950" height="560" rx="16" fill="url(#bg)"/>
  <text x="475" y="38" text-anchor="middle" class="title" font-size="20">105 年 電子學 第二題：非理想實體運算放大器 (有限增益 A 與有限阻抗) 等效模型圖</text>
  <text x="475" y="60" text-anchor="middle" class="subtitle">精確閉迴路增益：G = - (R2/R1) / [1 + (1 + R2/R1)/A]，增益誤差 Gain Error = -(1 + R2/R1) / [A + 1 + R2/R1]</text>

  <rect x="30" y="80" width="890" height="340" class="box"/>

  <!-- 輸入信號源 vi 與 R1 -->
  <circle cx="80" cy="220" r="16" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="80" y="225" text-anchor="middle" class="val-cyan">vi</text>
  <path d="M 80 236 L 80 290" class="wire"/>
  <line x1="70" y1="290" x2="90" y2="290" class="ground"/>

  <path d="M 96 220 L 150 220" class="wire"/>
  <rect x="150" y="208" width="50" height="24" fill="#334155" stroke="#38bdf8" rx="3"/>
  <text x="175" y="224" text-anchor="middle" class="val-cyan">R1</text>

  <!-- 反相輸入端 v- -->
  <path d="M 200 220 L 260 220" class="wire"/>
  <circle cx="260" cy="220" r="5" fill="#f43f5e"/>
  <text x="260" y="200" text-anchor="middle" class="val-rose">v−</text>

  <!-- 回授電阻 R2 跨接至輸出 vo -->
  <path d="M 260 220 L 260 140 L 760 140 L 760 220" class="wire" stroke="#f59e0b" stroke-width="2.2"/>
  <rect x="480" y="128" width="60" height="24" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="510" y="144" text-anchor="middle" class="val-amber">R2 (回授電阻)</text>

  <!-- 內部差模輸入阻抗 Rid -->
  <path d="M 260 220 L 330 220 L 330 240" class="wire"/>
  <rect x="318" y="240" width="24" height="40" fill="#334155" stroke="#38bdf8" rx="3"/>
  <text x="360" y="265" class="val-cyan">Rid</text>
  <path d="M 330 280 L 330 310" class="wire"/>
  <line x1="320" y1="310" x2="340" y2="310" class="ground"/>
  <text x="330" y="325" text-anchor="middle" class="label">v+ = 0V (接地)</text>

  <!-- 內部開迴路受控源 A·vd -->
  <path d="M 520 220 L 520 250" class="wire"/>
  <circle cx="520" cy="270" r="16" fill="#1e293b" stroke="#38bdf8" stroke-width="1.8"/>
  <text x="520" y="262" text-anchor="middle" class="val-cyan" font-size="11">+</text>
  <text x="520" y="284" text-anchor="middle" class="val-cyan" font-size="11">−</text>
  <path d="M 520 286 L 520 310" class="wire"/>
  <line x1="510" y1="310" x2="530" y2="310" class="ground"/>
  <text x="440" y="275" class="val-cyan">A·(v+ - v−) = -A·v−</text>

  <!-- 內部輸出阻抗 Ro -->
  <path d="M 520 220 L 600 220" class="wire"/>
  <rect x="600" y="208" width="45" height="24" fill="#334155" stroke="#f59e0b" rx="3"/>
  <text x="622" y="224" text-anchor="middle" class="val-amber">Ro</text>
  <path d="M 645 220 L 760 220" class="wire"/>

  <!-- 輸出節點 vo -->
  <circle cx="760" cy="220" r="6" fill="#10b981"/>
  <text x="760" y="200" text-anchor="middle" class="val-emerald" font-size="14">vo</text>
  <path d="M 760 220 L 850 220" class="wire"/>
  <circle cx="850" cy="220" r="5" fill="#10b981"/>

  <!-- 結論卡片 -->
  <rect x="30" y="435" width="280" height="105" class="box"/>
  <text x="45" y="460" class="val-cyan" font-size="13">1. 理想 vs 實體增益</text>
  <text x="45" y="485" class="val-cyan">理想增益 Gideal = -R2 / R1</text>
  <text x="45" y="515" class="val-emerald" font-size="14">G = Gideal / [1 + (1/Aβ)]</text>

  <rect x="335" y="435" width="280" height="105" class="box"/>
  <text x="350" y="460" class="val-amber" font-size="13">2. 迴路增益 T = A·β</text>
  <text x="350" y="485" class="label">回授因素 β = R1 / (R1 + R2)</text>
  <text x="350" y="515" class="val-amber" font-size="14">T = A · R1 / (R1 + R2)</text>

  <rect x="640" y="435" width="280" height="105" class="box"/>
  <text x="655" y="460" class="val-rose" font-size="13">3. 相對增益誤差</text>
  <text x="655" y="485" class="label">誤差百分比 ε：</text>
  <text x="655" y="515" class="val-rose" font-size="14">ε ≈ - 1 / (A · β) = - (1 + R2/R1) / A</text>
</svg>'''

new_svg_files = [
    ("113年_電子學_第1題_理想二極體電路狀態分析等效電路圖.svg", svg_113_q1),
    ("112年_電子學_第3題_降升壓BuckBoost轉換器操作狀態等效電路圖.svg", svg_112_q3),
    ("110年_電子學_第1題_BJT集極回授偏壓小訊號等效電路圖.svg", svg_110_q1),
    ("109年_電子學_第2題_昇壓型Boost轉換器二操作狀態等效電路圖.svg", svg_109_q2),
    ("108年_電子學_第4題_GIC通用阻抗轉換器主動濾波器等效電路圖.svg", svg_108_q4),
    ("107年_電子學_第2題_NMOS混合pi小訊號等效模型圖.svg", svg_107_q2),
    ("106年_電子學_第3題_BJT共射極放大器米勒等效高頻電路圖.svg", svg_106_q3),
    ("105年_電子學_第2題_實體反相運算放大器等效電路模型圖.svg", svg_105_q2),
]

for filename, content in new_svg_files:
    filepath = os.path.join(target_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Generated new SVG: {filename}")

# ------------------------------------------------------------------------------
# Embedding into Markdown Files
# ------------------------------------------------------------------------------

EMBED_MAPPINGS = {
    "114年_電子學_全卷完整詳細題解.md": [
        (r"(## 一、BJT 差動放大器.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[114年_電子學_第1題_BJT差動放大器三種輸入模式等效電路分析圖.svg|850]]\n*圖：114年第一題 BJT 差動放大器差模與共模小訊號半電路等效拓撲圖*\n\n"),
        (r"(## 二、高頻放大器.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[114年_電子學_第2題_高頻放大器開路時間常數法等效電路圖.svg|850]]\n*圖：114年第二題 高頻放大器小訊號等效電路與開路時間常數 (OCTC) 模型圖*\n\n"),
        (r"(## 三、開關切換電力電子.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[114年_電子學_第3題_開關切換電感充放電二狀態等效電路圖.svg|850]]\n*圖：114年第三題 開關切換電感充放電二操作狀態等效電路圖*\n\n"),
        (r"(#### 🔹 \(2\) 閘流體保護電路設計與元件功能說明\n)", r"\1\n![[114年_電子學_第4題_閘流體完整防護電路拓撲圖.svg|850]]\n*圖：114年第四題 閘流體 (SCR) 四重全方位保護電路拓撲等效圖*\n\n"),
    ],
    "113年_電子學_全卷完整詳細題解.md": [
        (r"(## 一、理想二極體.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[113年_電子學_第1題_理想二極體電路狀態分析等效電路圖.svg|850]]\n*圖：113年第一題 理想二極體電路操作狀態等效分析圖*\n\n"),
        (r"(#### 步驟 1：繪製小訊號 T 模型等效電路.*?\n)", r"\1\n![[113年_電子學_第2題_共基極BJT放大器小訊號T模型等效電路圖.svg|850]]\n*圖：113年第二題 共基極 BJT 放大器小訊號 T 模型完整等效電路圖*\n\n"),
        (r"(#### 步驟 1：繪製二操作狀態等效電路.*?\n)", r"\1\n![[113年_電子學_第3題_降壓型Buck轉換器二操作狀態等效電路圖.svg|850]]\n*圖：113年第三題 降壓型 (Buck) 轉換器 BCM 二操作狀態等效電路圖*\n\n"),
    ],
    "112年_電子學_全卷完整詳細題解.md": [
        (r"(## 一、共基極（CB）放大器高頻.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[112年_電子學_第1題_共基極CB高頻小訊號等效電路圖.svg|850]]\n*圖：112年第一題 共基極高頻小訊號等效電路與截止頻率分析圖*\n\n"),
        (r"(## 三、電力電子降升壓.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[112年_電子學_第3題_降升壓BuckBoost轉換器操作狀態等效電路圖.svg|850]]\n*圖：112年第三題 降升壓型 (Buck-Boost) 轉換器二操作狀態等效電路圖*\n\n"),
    ],
    "111年_電子學_全卷完整詳細題解.md": [
        (r"(## 三、MOSFET 源極退化放大器.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[111年_電子學_第3題_MOSFET源極退化放大器小訊號等效電路圖.svg|850]]\n*圖：111年第三題 MOSFET 源極退化放大器小訊號等效電路分析圖*\n\n"),
        (r"(## 四、電流-電流負回授放大器.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[111年_電子學_第4題_電流電流負回授放大器A電路與beta網路等效圖.svg|850]]\n*圖：111年第四題 電流-電流負回授放大器 A 電路與 β 網路等效拆解圖*\n\n"),
    ],
    "110年_電子學_全卷完整詳細題解.md": [
        (r"(## 一、BJT 集極回授偏壓電路.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[110年_電子學_第1題_BJT集極回授偏壓小訊號等效電路圖.svg|850]]\n*圖：110年第一題 BJT 集極回授偏壓小訊號等效電路分析圖*\n\n"),
    ],
    "109年_電子學_全卷完整詳細題解.md": [
        (r"(## 二、昇壓型（Boost）轉換器.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[109年_電子學_第2題_昇壓型Boost轉換器二操作狀態等效電路圖.svg|850]]\n*圖：109年第二題 昇壓型 (Boost) 轉換器二操作狀態等效電路分析圖*\n\n"),
    ],
    "108年_電子學_全卷完整詳細題解.md": [
        (r"(## 三、MOSFET 串聯-串聯負回授放大器.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[108年_電子學_第3題_MOSFET串聯串聯負回授放大器等效電路圖.svg|850]]\n*圖：108年第三題 MOSFET 串聯-串聯負回授放大器等效電路分析圖*\n\n"),
        (r"(## 四、GIC 主動濾波器.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[108年_電子學_第4題_GIC通用阻抗轉換器主動濾波器等效電路圖.svg|850]]\n*圖：108年第四題 雙運算放大器 GIC 通用阻抗轉換器等效電路圖*\n\n"),
    ],
    "107年_電子學_全卷完整詳細題解.md": [
        (r"(## 二、NMOS 小訊號轉導.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[107年_電子學_第2題_NMOS混合pi小訊號等效模型圖.svg|850]]\n*圖：107年第二題 NMOS 混合 π 小訊號等效模型圖*\n\n"),
    ],
    "106年_電子學_全卷完整詳細題解.md": [
        (r"(## 三、BJT 共射極放大器直流工作點、米勒電容.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[106年_電子學_第3題_BJT共射極放大器米勒等效高頻電路圖.svg|850]]\n*圖：106年第三題 BJT 共射極放大器米勒等效高頻小訊號模型圖*\n\n"),
    ],
    "105年_電子學_全卷完整詳細題解.md": [
        (r"(## 二、有限增益反相運算放大器.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[105年_電子學_第2題_實體反相運算放大器等效電路模型圖.svg|850]]\n*圖：105年第二題 非理想實體運算放大器等效模型圖*\n\n"),
    ],
    "104年_電子學_全卷完整詳細題解.md": [
        (r"(## 一、PMOS 共源極放大器.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[104年_電子學_第1題_PMOS共源極高頻小訊號等效電路圖.svg|850]]\n*圖：104年第一題 PMOS 共源極高頻小訊號等效電路與轉移函數圖*\n\n"),
        (r"(## 二、共基極（CB）放大器直流電壓.*?\n### ✏️ 步驟式詳細數學推導\n)", r"\1\n![[104年_電子學_第2題_共基極放大器小訊號T模型等效電路圖.svg|850]]\n*圖：104年第二題 共基極放大器小訊號 T 模型等效電路圖*\n\n"),
    ],
}

for md_file, replacements in EMBED_MAPPINGS.items():
    md_path = os.path.join(md_dir, md_file)
    if not os.path.exists(md_path):
        print(f"⚠️ File not found: {md_path}")
        continue
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    modified = content
    for pattern, repl in replacements:
        # Check if already embedded
        svg_name_match = re.search(r'!\[\[(.*?\.svg)', repl)
        if svg_name_match and svg_name_match.group(1) in modified:
            continue
        # Remove mermaid blocks if replacing
        modified = re.sub(pattern, repl, modified, count=1, flags=re.DOTALL)

    if modified != content:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(modified)
        print(f"✨ Successfully updated Markdown: {md_file}")
    else:
        print(f"ℹ️ Already up-to-date: {md_file}")

# ------------------------------------------------------------------------------
# Re-compile Bundle
# ------------------------------------------------------------------------------
print("\n📦 Compiling dashboard database & solutions bundle...")
res = subprocess.run(["python3", "scripts/compile_dashboard_database.py"], cwd="/Users/a/技師考試/歷屆試題_104-114年", capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("Error:", res.stderr)

print("\n🎉 ALL DONE! All Electronics equivalent circuits vector SVGs generated and integrated seamlessly!")
