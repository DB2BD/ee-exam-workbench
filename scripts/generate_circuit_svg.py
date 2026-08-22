#!/usr/bin/env python3

def generate_circuit_svg():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 540" width="100%" height="100%" style="background:#0f172a; font-family:'Segoe UI',Roboto,Helvetica,sans-serif; border-radius:12px; border:1px solid #334155;">
  <defs>
    <!-- Arrow Marker -->
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8"/>
    </marker>
    <marker id="arrow-gold" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#fbbf24"/>
    </marker>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#38bdf8" flood-opacity="0.3"/>
    </filter>
  </defs>

  <!-- Title & Banner -->
  <rect x="20" y="16" width="810" height="42" rx="8" fill="#1e293b" stroke="#475569" stroke-width="1"/>
  <text x="425" y="42" fill="#f8fafc" font-size="16" font-weight="bold" text-anchor="middle">⚡ 108年 電路學 第二題：全節點 (V1 ~ V4) 與超級節點標定圖</text>

  <!-- Supernode Background Region -->
  <rect x="110" y="210" width="510" height="190" rx="16" fill="rgba(56, 189, 248, 0.05)" stroke="#38bdf8" stroke-width="2" stroke-dasharray="6,6"/>
  <text x="130" y="235" fill="#38bdf8" font-size="13" font-weight="bold">🛡️ 超級節點 (Supernode: 節點 1 + 節點 2 + 節點 3)</text>

  <!-- Wires (Main Busbars) -->
  <!-- Top Wire (Node 4) -->
  <line x1="140" y1="120" x2="720" y2="120" stroke="#94a3b8" stroke-width="3"/>
  <line x1="140" y1="120" x2="140" y2="280" stroke="#94a3b8" stroke-width="3"/>

  <!-- Middle Wire between N1, N2, N3 -->
  <line x1="140" y1="280" x2="600" y2="280" stroke="#94a3b8" stroke-width="3"/>

  <!-- Bottom Wire (Ground) -->
  <line x1="140" y1="460" x2="720" y2="460" stroke="#64748b" stroke-width="4"/>

  <!-- Top 6A Current Source (on top wire) -->
  <circle cx="340" cy="120" r="26" fill="#1e293b" stroke="#f8fafc" stroke-width="2.5"/>
  <line x1="362" y1="120" x2="318" y2="120" stroke="#38bdf8" stroke-width="3" marker-end="url(#arrow)"/>
  <text x="340" y="85" fill="#f8fafc" font-size="15" font-weight="bold" text-anchor="middle">6 A</text>

  <!-- Left 1 Ohm Resistor (between N1 and Ground) -->
  <line x1="140" y1="280" x2="140" y2="340" stroke="#94a3b8" stroke-width="3"/>
  <rect x="122" y="340" width="36" height="60" rx="4" fill="#1e293b" stroke="#e2e8f0" stroke-width="2"/>
  <text x="140" y="375" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">1 Ω</text>
  <line x1="140" y1="400" x2="140" y2="460" stroke="#94a3b8" stroke-width="3"/>
  <!-- v1 polarity -->
  <text x="100" y="345" fill="#ef4444" font-size="14" font-weight="bold">+</text>
  <text x="96" y="375" fill="#fbbf24" font-size="14" font-weight="bold">v₁</text>
  <text x="100" y="405" fill="#ef4444" font-size="16" font-weight="bold">−</text>
  <!-- i1 current arrow at bottom -->
  <line x1="220" y1="440" x2="170" y2="440" stroke="#fbbf24" stroke-width="3" marker-end="url(#arrow-gold)"/>
  <text x="195" y="430" fill="#fbbf24" font-size="14" font-weight="bold" text-anchor="middle">i₁ (向左)</text>

  <!-- 6V Voltage Source (between N1 and N2) -->
  <circle cx="250" cy="280" r="26" fill="#1e293b" stroke="#f8fafc" stroke-width="2.5"/>
  <text x="236" y="285" fill="#ef4444" font-size="16" font-weight="bold">+</text>
  <text x="258" y="285" fill="#ef4444" font-size="18" font-weight="bold">−</text>
  <text x="250" y="244" fill="#f8fafc" font-size="15" font-weight="bold" text-anchor="middle">6 V</text>

  <!-- 4 Ohm Resistor (between N2 and Ground) -->
  <line x1="360" y1="280" x2="360" y2="340" stroke="#94a3b8" stroke-width="3"/>
  <rect x="342" y="340" width="36" height="60" rx="4" fill="#1e293b" stroke="#e2e8f0" stroke-width="2"/>
  <text x="360" y="375" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">4 Ω</text>
  <line x1="360" y1="400" x2="360" y2="460" stroke="#94a3b8" stroke-width="3"/>
  <!-- v polarity -->
  <text x="320" y="345" fill="#ef4444" font-size="14" font-weight="bold">+</text>
  <text x="320" y="375" fill="#38bdf8" font-size="15" font-weight="bold">v</text>
  <text x="320" y="405" fill="#ef4444" font-size="16" font-weight="bold">−</text>

  <!-- 4i1 Dependent Voltage Source (between N2 and N3) -->
  <!-- Diamond Shape -->
  <polygon points="480,256 504,280 480,304 456,280" fill="#1e293b" stroke="#f8fafc" stroke-width="2.5"/>
  <text x="466" y="285" fill="#ef4444" font-size="16" font-weight="bold">−</text>
  <text x="490" y="285" fill="#ef4444" font-size="15" font-weight="bold">+</text>
  <text x="480" y="244" fill="#f8fafc" font-size="15" font-weight="bold" text-anchor="middle">4i₁</text>

  <!-- Top 1 Ohm Resistor (between Node 4 and Node 3) -->
  <line x1="600" y1="120" x2="600" y2="165" stroke="#94a3b8" stroke-width="3"/>
  <rect x="582" y="165" width="36" height="60" rx="4" fill="#1e293b" stroke="#e2e8f0" stroke-width="2"/>
  <text x="600" y="200" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">1 Ω</text>
  <line x1="600" y1="225" x2="600" y2="280" stroke="#94a3b8" stroke-width="3"/>
  <!-- v2 polarity -->
  <text x="630" y="175" fill="#ef4444" font-size="14" font-weight="bold">+</text>
  <text x="630" y="200" fill="#a78bfa" font-size="14" font-weight="bold">v₂</text>
  <text x="630" y="225" fill="#ef4444" font-size="16" font-weight="bold">−</text>

  <!-- 1.5v2 Dependent Current Source (between Ground and Node 3) -->
  <line x1="600" y1="280" x2="600" y2="340" stroke="#94a3b8" stroke-width="3"/>
  <polygon points="600,346 624,370 600,394 576,370" fill="#1e293b" stroke="#f8fafc" stroke-width="2.5"/>
  <line x1="600" y1="384" x2="600" y2="356" stroke="#38bdf8" stroke-width="3" marker-end="url(#arrow)"/>
  <text x="655" y="375" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="start">1.5 v₂</text>
  <line x1="600" y1="394" x2="600" y2="460" stroke="#94a3b8" stroke-width="3"/>

  <!-- 2 Ohm Resistor (between Node 4 and Ground) -->
  <line x1="720" y1="120" x2="720" y2="250" stroke="#94a3b8" stroke-width="3"/>
  <rect x="702" y="250" width="36" height="60" rx="4" fill="#1e293b" stroke="#e2e8f0" stroke-width="2"/>
  <text x="720" y="285" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">2 Ω</text>
  <line x1="720" y1="310" x2="720" y2="460" stroke="#94a3b8" stroke-width="3"/>
  <text x="750" y="285" fill="#34d399" font-size="13" font-weight="bold">求 P₂ᵨ</text>

  <!-- ================= NODE BADGES ================= -->
  <!-- Node 1 Badge -->
  <circle cx="140" cy="280" r="7" fill="#38bdf8"/>
  <rect x="80" y="255" width="55" height="24" rx="4" fill="#0369a1" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="107" y="272" fill="#ffffff" font-size="12" font-weight="bold" text-anchor="middle">V₁</text>

  <!-- Node 2 Badge -->
  <circle cx="360" cy="280" r="7" fill="#38bdf8"/>
  <rect x="330" y="255" width="60" height="24" rx="4" fill="#0369a1" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="360" y="272" fill="#ffffff" font-size="12" font-weight="bold" text-anchor="middle">V₂ = v</text>

  <!-- Node 3 Badge -->
  <circle cx="600" cy="280" r="7" fill="#a855f7"/>
  <rect x="560" y="295" width="80" height="26" rx="4" fill="#6b21a8" stroke="#c084fc" stroke-width="1.5"/>
  <text x="600" y="313" fill="#ffffff" font-size="13" font-weight="bold" text-anchor="middle">📍 節點 V₃</text>

  <!-- Node 4 Badge -->
  <circle cx="600" cy="120" r="7" fill="#a855f7"/>
  <circle cx="720" cy="120" r="7" fill="#a855f7"/>
  <rect x="555" y="75" width="90" height="26" rx="4" fill="#6b21a8" stroke="#c084fc" stroke-width="1.5"/>
  <text x="600" y="93" fill="#ffffff" font-size="13" font-weight="bold" text-anchor="middle">📍 節點 V₄</text>

  <!-- Ground Reference Badge -->
  <rect x="360" y="475" width="130" height="24" rx="4" fill="#334155" stroke="#64748b" stroke-width="1"/>
  <text x="425" y="492" fill="#cbd5e1" font-size="12" font-weight="bold" text-anchor="middle">⏚ 參考接地 (0 V)</text>

</svg>
"""
    with open('/Users/a/技師考試/歷屆試題_104-114年/依考科分類/01_電路學/images/108年_電路學_第2題_節點分析標定圖.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print("✅ Successfully generated 108年_電路學_第2題_節點分析標定圖.svg")

if __name__ == '__main__':
    generate_circuit_svg()
