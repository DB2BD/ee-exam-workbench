"""Tiny helpers for textbook-style circuit SVGs (black line art, KaTeX font classes)."""
import math
FONT_V = "KaTeX_Math, 'Times New Roman', serif"
FONT_N = "KaTeX_Main, 'Times New Roman', serif"
FONT_T = "-apple-system, BlinkMacSystemFont, 'PingFang TC', 'Helvetica Neue', sans-serif"

def header(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'<rect width="{w}" height="{h}" fill="#fff"/>\n'
            '<g fill="none" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">\n')

def line(x1, y1, x2, y2):
    return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}"/>\n'

def coil(x1, y1, x2, y2, turns=4, r=6.5):
    """Inductor/reactance: fixed-size bumps centred between the two points, straight leads elsewhere."""
    L = math.hypot(x2 - x1, y2 - y1); ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    body = 2 * r * turns; lead = (L - body) / 2
    d = f'M0 0 L{lead:.1f} 0 '
    for k in range(turns):
        d += f'A{r:.1f} {r:.1f} 0 0 1 {lead + 2 * r * (k + 1):.1f} 0 '
    d += f'L{L:.1f} 0'
    return f'<path transform="translate({x1:.1f} {y1:.1f}) rotate({ang:.2f})" d="{d}"/>\n'

def resistor(x1, y1, x2, y2, zigs=6, lead=12, amp=6):
    L = math.hypot(x2 - x1, y2 - y1); ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    body = L - 2 * lead; step = body / zigs
    pts = [(0, 0), (lead, 0)]
    for k in range(zigs):
        pts.append((lead + step * (k + 0.5), -amp if k % 2 == 0 else amp))
    pts += [(lead + body, 0), (L, 0)]
    d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
    return f'<path transform="translate({x1:.1f} {y1:.1f}) rotate({ang:.2f})" d="{d}"/>\n'

def ac_source(cx, cy, r=14):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}"/>\n'
            f'<path d="M{cx - 7} {cy} C{cx - 4} {cy - 7} {cx - 1} {cy - 7} {cx} {cy} S{cx + 4} {cy + 7} {cx + 7} {cy}"/>\n')

def ground(x, y):
    return (line(x - 12, y, x + 12, y) + line(x - 8, y + 4, x + 8, y + 4) + line(x - 4, y + 8, x + 4, y + 8))

def busbar(x1, x2, y):
    return f'<path d="M{x1} {y} L{x2} {y}" stroke-width="5"/>\n'

def dot(x, y):
    return f'<circle cx="{x}" cy="{y}" r="2.6" fill="#000" stroke="none"/>\n'

RED = "#c0392b"; BLUE = "#1f5fa8"; FILL_RED = "#fde2e0"; FILL_BLUE = "#e3eefa"

def arrow(x1, y1, x2, y2, color="#000"):
    """Current arrow: shaft + solid triangle head at (x2, y2)."""
    ang = math.atan2(y2 - y1, x2 - x1); s = 8
    p1 = (x2 - s * math.cos(ang) + 4 * math.sin(ang), y2 - s * math.sin(ang) - 4 * math.cos(ang))
    p2 = (x2 - s * math.cos(ang) - 4 * math.sin(ang), y2 - s * math.sin(ang) + 4 * math.cos(ang))
    return (f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{color}"/>\n'
            f'<path d="M{x2:.1f} {y2:.1f} L{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} Z" fill="{color}" stroke="{color}"/>\n')

def end_group():
    return '</g>\n'

def text(x, y, parts, anchor="start", color="#000"):
    """parts: list of (kind, s) with kind in v (italic var), n (upright number/unit), t (Chinese text), sub (subscript upright), vsub (italic subscript)."""
    out = [f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="16" fill="{color}">']
    for kind, s in parts:
        if kind in ("sub", "vsub"):
            cls, fam = ("v", FONT_V) if kind == "vsub" else ("n", FONT_N)
            style = ' font-style="italic"' if kind == "vsub" else ''
            out.append(f'<tspan class="{cls} sub" font-family="{fam}"{style} font-size="12" baseline-shift="sub">{s}</tspan>')
        else:
            fam = {"v": FONT_V, "n": FONT_N, "t": FONT_T}[kind]
            style = ' font-style="italic"' if kind == "v" else ''
            out.append(f'<tspan class="{kind}" font-family="{fam}"{style}>{s}</tspan>')
    out.append('</text>\n')
    return ''.join(out)

def footer():
    return '</svg>\n'
