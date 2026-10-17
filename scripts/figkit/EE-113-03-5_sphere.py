import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from math_parts import *

W, H = 600, 380
cx, cy, r = 190, 200, 125
s = header(W, H)
s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{FILL_BLUE}"/>\n'
# equator: back half dashed, front half solid
s += f'<path d="M{cx - r} {cy} A{r} 32 0 0 1 {cx + r} {cy}" stroke-dasharray="5 4"/>\n'
s += f'<path d="M{cx - r} {cy} A{r} 32 0 0 0 {cx + r} {cy}"/>\n'
# radius R = 3
s += dot(cx, cy) + line(cx, cy, cx + r * math.cos(math.radians(35)), cy - r * math.sin(math.radians(35)))
# outward unit normals n on the surface
for a in (90, 160, 215, 330):
    x0, y0 = cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))
    s += arrow(x0, y0, x0 + 42 * math.cos(math.radians(a)), y0 - 42 * math.sin(math.radians(a)))
s += end_group()
xr, yr = cx + 0.55 * r * math.cos(math.radians(35)), cy - 0.55 * r * math.sin(math.radians(35))
s += text(xr - 6, yr - 8, [("v", "R"), ("n", " = 3")], anchor="end")
for a, dx, dy in ((90, 14, 4), (160, -12, -10), (215, -10, 22), (330, 12, 14)):
    x0, y0 = cx + (r + 42) * math.cos(math.radians(a)), cy - (r + 42) * math.sin(math.radians(a))
    s += text(x0 + dx, y0 + dy, [("v", "n")], anchor="middle")
s += ctext(cx, cy + 60, [("v", "V"), ("t", "：球體內部")], anchor="middle")
s += text(cx + r * 0.72 + 10, cy - r * 0.72 - 6, [("v", "S")])
# side notes
X = 360
s += mtext(X, 92, [("v", "S"), ("n", "： "), ("v", "x"), ("sup", "2"), ("n", " + "), ("v", "y"), ("sup", "2"), ("n", " + "), ("v", "z"), ("sup", "2"), ("n", " = 9")])
s += text(X, 122, [("t", "封閉曲面，"), ("v", "n"), ("t", " 取向外")])
s += mtext(X, 166, [("v", "V"), ("n", "： "), ("v", "x"), ("sup", "2"), ("n", " + "), ("v", "y"), ("sup", "2"), ("n", " + "), ("v", "z"), ("sup", "2"), ("n", " ≤ 9")], color=BLUE)
s += ctext(X, 196, [("t", "半徑 "), ("v", "R"), ("n", " = 3"), ("t", " 的實心球")])
s += text(X, 240, [("n", "∇ · "), ("v", "F"), ("n", " = 9"), ("t", "（常數）")])
s += text(X, 270, [("n", "⇒ "), ("t", "通量 = "), ("n", "9 × "), ("t", "體積")])
s += footer()
write('EE-113-03-5-sphere.svg', s)
