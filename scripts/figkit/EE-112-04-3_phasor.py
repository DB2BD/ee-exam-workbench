"""EE-112-04-3 fig 2: phasors at PF 1.0 (a) and PF 0.8 leading (b); both E_A tips on Im = -80 V."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
kv, ki = 1.5, 1.6                      # px per volt, px per ampere
oy = 120
W, H = 720, 320
s = header(W, H)
yl = oy + kv * 80
s += f'<path d="M20 {yl} L{W-10} {yl}" stroke-dasharray="6 4" stroke-width="1"/>\n'   # constant-power locus
def panel(ox, I, E):
    P = lambda x, y, k: (ox + k * x, oy - k * y)
    vx, vy = P(120.09, 0, kv); e = P(*E, kv); i = P(*I, ki)
    out = f'<path d="M{ox-10} {oy} L{ox+300} {oy}" stroke-width="0.8"/>\n'
    out += arrow(ox, oy, vx, vy, color=BLUE) + arrow(vx, vy, *e, color=BLUE) + arrow(ox, oy, *e, color=BLUE)
    out += arrow(ox, oy, *i, color=RED) + dot(ox, oy)
    d = math.atan2(-E[1], E[0]); r = 64
    out += f'<path d="M{ox+r} {oy} A{r} {r} 0 0 1 {ox+r*math.cos(d):.1f} {oy+r*math.sin(d):.1f}"/>\n'
    return out, (vx, vy), e
pa, va, ea = panel(30, (50, 0), (120.09, -80))
pb, vb, eb = panel(380, (50, 37.5), (180.09, -80))
s += pa + pb
th = math.atan2(37.5, 50); r = 40
s += f'<path d="M{380+r} {oy} A{r} {r} 0 0 0 {380+r*math.cos(th):.1f} {oy-r*math.sin(th):.1f}"/>\n'
s += end_group()
for ox in (30, 380):
    s += text(ox - 6, oy - 8, [("v", "O")], anchor="end")
# panel a
s += ctext(BLUE, 150, oy - 10, [("v", "V"), ("vsub", "ϕ"), ("n", " = 120.09 V")], anchor="middle")
s += ctext(RED, 40, oy - 30, [("v", "I"), ("vsub", "A"), ("sub", "1"), ("n", " = 50∠0° A")])
s += text(30 + 74, oy + 22, [("v", "δ"), ("sub", "1")])
s += ctext(BLUE, va[0] + 8, oy + 56, [("n", "−"), ("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "A"), ("sub", "1")])
s += ctext(BLUE, va[0] + 8, oy + 76, [("n", "= −"), ("v", "j"), ("n", "80 V")])
s += ctext(BLUE, 160, yl + 26, [("v", "E"), ("vsub", "A"), ("sub", "1"), ("n", " = 144.30∠−33.67° V")], anchor="middle")
s += text(160, H - 14, [("t", "(a) PF 1.0（"), ("v", "I"), ("vsub", "f"), ("n", " = 2.7 A"), ("t", "）")], anchor="middle")
# panel b
s += ctext(BLUE, 500, oy - 10, [("v", "V"), ("vsub", "ϕ"), ("n", " = 120.09 V")], anchor="middle")
s += ctext(RED, 380 + 84, oy - 62, [("v", "I"), ("vsub", "A"), ("sub", "2"), ("n", " = 62.5∠36.87° A")])
s += text(380 + 46, oy - 8, [("v", "θ"), ("sub", "2")])
s += text(380 + 80, oy + 18, [("v", "δ"), ("sub", "2")])
s += ctext(BLUE, vb[0] + 56, oy + 46, [("n", "−"), ("v", "jX"), ("vsub", "s"), ("v", "I"), ("vsub", "A"), ("sub", "2")])
s += ctext(BLUE, vb[0] + 56, oy + 66, [("n", "= 60 − "), ("v", "j"), ("n", "80 V")])
s += ctext(BLUE, 540, yl + 26, [("v", "E"), ("vsub", "A"), ("sub", "2"), ("n", " = 197.06∠−23.95° V")], anchor="middle")
s += text(540, H - 14, [("t", "(b) PF 0.8 超前（機械負載不變）")], anchor="middle")
s += text(W / 2, 28, [("t", "虛線：定功率軌跡（"), ("v", "E"), ("vsub", "A"), ("t", " 虛部 = −80 V）；電壓、電流各自依比例")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-112-04-3-phasor.svg'), 'w').write(s)
print(len(s))
