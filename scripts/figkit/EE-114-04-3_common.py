import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
def into(x, y, c=RED, r=9):
    d = r * 0.7
    return (f'<circle cx="{x}" cy="{y}" r="{r}" stroke="{c}"/>\n'
            f'<path d="M{x-d:.1f} {y-d:.1f} L{x+d:.1f} {y+d:.1f} M{x-d:.1f} {y+d:.1f} L{x+d:.1f} {y-d:.1f}" stroke="{c}"/>\n')
def outof(x, y, c=RED, r=9):
    return f'<circle cx="{x}" cy="{y}" r="{r}" stroke="{c}"/>\n<circle cx="{x}" cy="{y}" r="2.6" fill="{c}" stroke="none"/>\n'
def flux_plane(title, angles, ccw, out_name):
    """X-Y plane with flux vectors of length phi_m at the given angles (t1,t3,t5,t7)."""
    W, H = 560, 420; cx, cy, R = 250, 215, 130
    s = header(W, H)
    s += arrow(cx - 175, cy, cx + 175, cy) + arrow(cx, cy + 175, cx, cy - 180)
    s += f'<circle cx="{cx}" cy="{cy}" r="{R}" stroke-dasharray="5 4" stroke-width="1"/>\n'
    for a in angles:
        r = math.radians(a)
        s += arrow(cx, cy, cx + R * math.cos(r), cy - R * math.sin(r), color=BLUE)
    # rotation sense arc at radius 60, from 60 deg to 120 deg
    rr = 62; a1, a2 = (60, 115) if ccw else (120, 65)
    p1 = (cx + rr * math.cos(math.radians(a1)), cy - rr * math.sin(math.radians(a1)))
    p2 = (cx + rr * math.cos(math.radians(a2)), cy - rr * math.sin(math.radians(a2)))
    sweep = 0 if ccw else 1
    s += f'<path d="M{p1[0]:.1f} {p1[1]:.1f} A{rr} {rr} 0 0 {sweep} {p2[0]:.1f} {p2[1]:.1f}" stroke-width="1.2"/>\n'
    t = math.radians(a2 + (8 if ccw else -8))
    s += arrow(p2[0] + 0.1 * (p2[0] - cx - rr * math.cos(t)), p2[1], p2[0], p2[1]).split('\n')[1] + '\n' if False else ''
    # small solid head at p2 tangent to the arc
    tang = math.radians(a2 + (90 if ccw else -90))
    hx, hy = math.cos(tang), -math.sin(tang)
    s += arrow(p2[0] - 6 * hx, p2[1] - 6 * hy, p2[0] + 2 * hx, p2[1] + 2 * hy)
    s += dot(cx, cy)
    s += end_group()
    s += text(cx + 178, cy + 20, [("n", "+X")], anchor="end")
    s += text(cx + 10, cy - 166, [("n", "+Y")])
    s += text(cx - 8, cy + 20, [("v", "O")], anchor="end")
    for k, a in zip((1, 3, 5, 7), angles):
        r = math.radians(a)
        x, y = cx + (R + 22) * math.cos(r), cy - (R + 22) * math.sin(r) + 6
        anc = "start" if math.cos(r) > 0 else "end"
        s += ctext(BLUE, x, y, [("v", "t"), ("sub", str(k)), ("n", f"：{a}°")], anchor=anc)
    s += text(cx + 150, cy + 150, [("t", "箭頭長 = "), ("v", "ϕ"), ("vsub", "m")])
    s += text(cx + 150, cy + 172, [("t", "（虛線圓半徑）")])
    lab = "逆時針" if ccw else "順時針"
    s += text(cx + 4, cy - 70, [("t", lab)], anchor="middle")
    s += text(20, 28, title)
    s += footer()
    open(pathlib.Path(__file__).resolve().parents[2].joinpath(f'02_題解/技師題解/04_電機機械/figures/{out_name}'), 'w').write(s)
    print(len(s))
