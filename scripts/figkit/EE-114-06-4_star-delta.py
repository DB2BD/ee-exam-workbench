"""EE-114-06-4 same winding impedance Z_w in Y (starting) and Delta (running), part (一); symbols only.
Y: winding voltage V_L/sqrt3, line current I_{L,Y} = winding current I_{w,Y}.
Delta: winding voltage V_L, winding current I_{w,Delta}, line current I_{L,Delta} = sqrt3 I_{w,Delta}.
Current reference arrows: line currents into the motor terminals; I_{w,Delta} along winding a->b.
"""
import sys, math, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 700, 400; s = header(W, H); lab = ''
# ---- Y panel ----
nx, ny, R = 170, 220, 105
ang = {"a": -90, "b": 150, "c": 30}
term = {k: (nx + R * math.cos(math.radians(v)), ny + R * math.sin(math.radians(v))) for k, v in ang.items()}
for k, (x, y) in term.items():
    s += coil(x, y, nx, ny, turns=4, r=7) + dot(x, y)
s += dot(nx, ny)
ta = term["a"]
s += line(ta[0], ta[1], ta[0], ta[1] - 55) + arrow(ta[0] + 14, ta[1] - 50, ta[0] + 14, ta[1] - 18, RED)
for k in ("b", "c"):
    x, y = term[k]; dx = -50 if k == "b" else 50
    s += line(x, y, x + dx, y)
# ---- Delta panel ----
cx0, cy0, Rd = 520, 225, 110
v = {"a": (cx0, cy0 - Rd), "b": (cx0 - Rd * math.sqrt(3) / 2, cy0 + Rd / 2), "c": (cx0 + Rd * math.sqrt(3) / 2, cy0 + Rd / 2)}
for p, q in (("a", "b"), ("b", "c"), ("c", "a")):
    s += coil(*v[p], *v[q], turns=4, r=7)
for k, (x, y) in v.items():
    s += dot(x, y)
va = v["a"]
s += line(va[0], va[1], va[0], va[1] - 50) + arrow(va[0] + 14, va[1] - 46, va[0] + 14, va[1] - 14, RED)
s += line(*v["b"], v["b"][0] - 40, v["b"][1]) + line(*v["c"], v["c"][0] + 40, v["c"][1])
# winding current along a->b (outside the edge, parallel)
mx, my = (va[0] + v["b"][0]) / 2, (va[1] + v["b"][1]) / 2
ux, uy = (v["b"][0] - va[0]) / (2 * Rd * math.sqrt(3) / 2), (v["b"][1] - va[1]) / (2 * Rd * math.sqrt(3) / 2)
nxo, nyo = -uy * 22, ux * 22          # outward normal of edge a-b
s += arrow(mx + nxo - 18 * ux, my + nyo - 18 * uy, mx + nxo + 18 * ux, my + nyo + 18 * uy, RED)
s += end_group()
# labels Y
lab += text(nx, 380, [("t", "起動：Y 接")], anchor="middle")
lab += text(ta[0] - 8, ta[1] - 34, [("v", "a")], anchor="end")
lab += ctext(RED, ta[0] + 24, ta[1] - 28, [("v", "I"), ("vsub", "L,Y"), ("n", " = "), ("v", "I"), ("vsub", "w,Y")])
lab += text(nx + 14, ny - 52, [("v", "Z"), ("vsub", "w")])
lab += ctext(BLUE, nx - 16, ny - 66, [("v", "V"), ("vsub", "w,Y")], anchor="end")
lab += ctext(BLUE, nx - 16, ny - 44, [("n", "= "), ("v", "V"), ("vsub", "L"), ("n", "/√3")], anchor="end")
lab += text(nx + 4, ny + 26, [("v", "N")])
lab += text(term["b"][0] - 50, term["b"][1] + 22, [("v", "b")]) + text(term["c"][0] + 44, term["c"][1] + 22, [("v", "c")])
# labels Delta
lab += text(cx0, 380, [("t", "運轉：Δ 接")], anchor="middle")
lab += text(va[0] - 8, va[1] - 30, [("v", "a")], anchor="end")
lab += ctext(RED, va[0] + 24, va[1] - 24, [("v", "I"), ("vsub", "L,"), ("sub", "Δ"), ("n", " = √3 "), ("v", "I"), ("vsub", "w,"), ("sub", "Δ")])
lab += ctext(RED, mx + nxo - 14, my + nyo - 8, [("v", "I"), ("vsub", "w,"), ("sub", "Δ")], anchor="end")
lab += ctext(BLUE, cx0, cy0 + Rd / 2 + 30, [("v", "V"), ("vsub", "w,"), ("sub", "Δ"), ("n", " = "), ("v", "V"), ("vsub", "L")], anchor="middle")
lab += text(mx + 36, my + 16, [("v", "Z"), ("vsub", "w")])
lab += text(v["b"][0] - 40, v["b"][1] + 22, [("v", "b")]) + text(v["c"][0] + 34, v["c"][1] + 22, [("v", "c")])
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-114-06-4-star-delta.svg'
out.write_text(s); print(out.name, len(s))
