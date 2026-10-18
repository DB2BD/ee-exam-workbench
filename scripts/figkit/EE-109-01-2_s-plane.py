"""EE-109-01-2: s-plane pole locations (LHP shaded) and the impulse-response mode each location gives."""
import math, sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 700, 380
OX, OY = 220, 190                     # s-plane origin
s = header(W, H)
s += f'<rect x="30" y="40" width="{OX - 30}" height="300" fill="{FILL_BLUE}" stroke="none"/>\n'
s += arrow(30, OY, 400, OY) + arrow(OX, 340, OX, 30)


def cross(x, y, r=6):
    return f'<g stroke-width="2">' + line(x - r, y - r, x + r, y + r) + line(x - r, y + r, x + r, y - r) + '</g>\n'


poles = {1: [(120, 120), (120, 260)], 2: [(OX, 110), (OX, 270)], 3: [(320, OY)]}
for pts in poles.values():
    for x, y in pts:
        s += cross(x, y)
s += cross(80, OY) + cross(92, OY)                  # repeated real LHP pole (drawn as a double cross)

# right column: three mode sketches
PX0, PW, PH = 450, 220, 70
rows = [(70, "decay"), (190, "const"), (310, "grow")]
for y0, kind in rows:
    s += arrow(PX0, y0, PX0 + PW, y0) + line(PX0, y0 - PH / 2 - 4, PX0, y0 + PH / 2 + 4)
    pts = []
    for k in range(0, 201):
        t = k / 200
        w = 2 * math.pi * 4
        env = {"decay": math.exp(-3.2 * t), "const": 0.7, "grow": 0.12 * math.exp(1.8 * t)}[kind]
        pts.append((PX0 + t * (PW - 12), y0 - (PH / 2) * env * math.sin(w * t)))
    s += '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + '" stroke-width="1.5"/>\n'
s += end_group()

s += text(392, OY + 22, [("v", "σ")], anchor="middle")
s += text(OX + 10, 36, [("v", "jω")])
s += text(40, 62, [("t", "左半平面（穩定區）")])
s += text(120, 104, [("n", "①")], anchor="middle")
s += text(86, OY - 14, [("n", "①")], anchor="middle")
s += text(OX + 14, 106, [("n", "②")])
s += text(320, OY - 14, [("n", "③")], anchor="middle")
s += text(OX + 8, OY + 20, [("n", "0")])
s += text(30, 372, [("t", "× 極點（雙 × 表重根）；實係數系統的複數極點成共軛對")])
s += text(PX0, 26, [("n", "① Re "), ("v", "p"), ("n", " &lt; 0"), ("t", "：衰減")])
s += text(PX0, 146, [("n", "② "), ("t", "虛軸單重極點：等幅")])
s += text(PX0, 266, [("n", "③ Re "), ("v", "p"), ("n", " &gt; 0"), ("t", "：發散")])
s += text(PX0 + PW, 106, [("v", "t")], anchor="middle")
s += text(PX0 + PW, 226, [("v", "t")], anchor="middle")
s += text(PX0 + PW, 346, [("v", "t")], anchor="middle")
s += footer()
write('EE-109-01-2-s-plane.svg', s)
