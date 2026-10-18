"""EE-111-06-2 per-unit reactance divider at motor start (S_b = 5 MVA, start PF = 0).

E = 1∠0° — jX_s (0.01) — 69 kV bus — jX_T (0.05) — 3.3 kV bus — jX_M (0.2833) to the return line.
Values equal the note steps 1–2; I is the reference current from source to motor (value derived in step 3).
Voltage indicators are dashed (no conductor between bus and return line).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 680, 330; s = header(W, H); lab = ''
y, g, xs, x69, x2, xm = 90, 250, 70, 270, 470, 590
s += line(xs, g, xs, 184) + ac_source(xs, 170) + line(xs, 156, xs, y)
s += line(xs, y, 140, y) + coil(140, y, 220, y) + line(220, y, 320, y) + coil(320, y, 400, y) + line(400, y, xm, y)
s += line(xm, y, xm, 130) + coil(xm, 130, xm, 210) + line(xm, 210, xm, g)
s += line(xs, g, xm, g)
for x in (x69, x2):
    s += dot(x, y)
    # voltage indicator (not a wire): dashed blue, reference line -> bus node
    s += f'<path d="M{x} {g} L{x} {y + 12}" stroke="{BLUE}" stroke-width="1" stroke-dasharray="5 4"/>\n'
    s += arrow(x, y + 16, x, y + 4, BLUE)
s += arrow(96, y - 16, 136, y - 16, RED)
s += end_group()
lab += text(xs + 22, 166, [("v", "E")]) + text(xs + 22, 188, [("n", "1∠0°")])
lab += ctext(RED, 116, y - 26, [("v", "I")], anchor="middle")
lab += text(180, 64, [("v", "jX"), ("vsub", "s")], anchor="middle") + text(180, 122, [("v", "j"), ("n", "0.01")], anchor="middle")
lab += text(360, 64, [("v", "jX"), ("vsub", "T")], anchor="middle") + text(360, 122, [("v", "j"), ("n", "0.05")], anchor="middle")
lab += text(xm + 16, 166, [("v", "jX"), ("vsub", "M")]) + text(xm + 16, 188, [("v", "j"), ("n", "0.2833")])
lab += text(x69, 40, [("n", "69 kV"), ("t", " 母線")], anchor="middle")
lab += text(x2, 40, [("n", "3.3 kV"), ("t", " 母線（二次側）")], anchor="middle")
lab += ctext(BLUE, x69 + 10, 178, [("v", "V"), ("sub", "69")])
lab += ctext(BLUE, x2 + 10, 178, [("v", "V"), ("sub", "2")])
lab += text(W / 2, 290, [("v", "S"), ("vsub", "b"), ("n", " = 5 MVA"), ("t", "；電抗為標么值；"), ("v", "V"), ("sub", "69"), ("t", "、"), ("v", "V"), ("sub", "2"), ("t", " 為母線對回路線電壓")], anchor="middle")
lab += text(W / 2, 314, [("t", "啟動功因為 0：三個元件皆為純電抗，串聯成分壓器")], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-111-06-2-reactance.svg'
out.write_text(s); print(out.name, len(s))
