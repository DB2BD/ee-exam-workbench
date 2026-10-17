"""EE-111-04-4 fig 3: linearised OCC through the operating point and the SCC line (field-current reading)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def dash(x1, y1, x2, y2): return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke-dasharray="4 3" stroke-width="1"/>\n'
W, H = 720, 330
s = header(W, H)
def axes(x0, y0, w, h):
    return arrow(x0, y0, x0 + w, y0) + arrow(x0, y0, x0, y0 - h)
# panel a: OCC, E (V/phase) vs I_f, 0..12000 V, 0..230 A
ax, ay, aw, ah = 100, 260, 260, 210
sx, sy = 240 / 230, 190 / 12000
P = lambda i, e: (ax + sx * i, ay - sy * e)
s += axes(ax, ay, aw, ah)
s += line(*P(0, 0), *P(225, 225 * 10710.171 / 200)).replace('/>', f' stroke="{BLUE}"/>')
op = P(200, 10710.171); rp = P(118.5948, 6350.853)
s += dot(*op) + dot(*rp)
s += dash(ax, op[1], *op) + dash(op[0], op[1], op[0], ay)
s += dash(ax, rp[1], *rp) + dash(rp[0], rp[1], rp[0], ay)
# panel b: SCC, I_a vs I_f, 0..1500 A
bx, by = 450, 260
tx, ty = 240 / 230, 190 / 1500
Q = lambda i, a: (bx + tx * i, by - ty * a)
s += axes(bx, by, aw, ah)
s += line(*Q(0, 0), *Q(1450 * 110.2637 / 1312.160, 1450)).replace('/>', f' stroke="{BLUE}"/>')
sp = Q(110.2637, 1312.160)
s += dot(*sp) + dash(bx, sp[1], *sp) + dash(sp[0], sp[1], sp[0], by)
s += end_group()
s += text(ax + aw, ay + 22, [("v", "I"), ("vsub", "f"), ("n", " (A)")], anchor="end")
s += text(ax + 6, ay - ah + 4, [("v", "E"), ("n", " (V/相)")])
s += text(ax - 6, op[1] + 5, [("n", "10 710.171")], anchor="end")
s += text(ax - 6, rp[1] + 5, [("n", "6350.853")], anchor="end")
s += text(op[0], ay + 22, [("n", "200")], anchor="middle")
s += text(rp[0], ay + 22, [("n", "118.5948")], anchor="middle")
s += text(op[0] - 6, op[1] + 22, [("t", "工作點")], anchor="end")
s += ctext(BLUE, P(125, 0)[0], P(0, 3600)[1], [("t", "線性化 OCC")])
s += ctext(BLUE, P(125, 0)[0], P(0, 3600)[1] + 20, [("v", "k"), ("n", " = 53.5509 V/A")])
s += text(ax + aw / 2, H - 12, [("t", "(a) OCC：額定電壓 "), ("v", "V"), ("vsub", "ϕ"), ("t", " 所需場電流")], anchor="middle")
s += text(bx + aw, by + 22, [("v", "I"), ("vsub", "f"), ("n", " (A)")], anchor="end")
s += text(bx + 6, by - ah + 4, [("v", "I"), ("vsub", "a"), ("n", " (A)")])
s += text(bx - 6, sp[1] + 5, [("n", "1312.160")], anchor="end")
s += text(sp[0], by + 22, [("n", "110.26")], anchor="middle")
s += ctext(BLUE, sp[0] + 10, sp[1] + 30, [("t", "SCC（過原點直線）")])
s += text(bx + aw / 2, H - 12, [("t", "(b) SCC：額定電流所需場電流")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/04_電機機械/figures/EE-111-04-4-occ-scc.svg'), 'w').write(s)
print(len(s))
