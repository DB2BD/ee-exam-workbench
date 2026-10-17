"""Shared parts for power-electronics figures (subject 02): sources, diodes, switches, capacitors.

All parts take two terminal points and are drawn along the segment between them
(rotated as needed), black line art, so the per-figure scripts only place terminals.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *  # noqa: F401,F403

G_OPEN = '<g fill="none" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">\n'
OUT_DIR = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/02_電子學_含電力電子/figures'


def _frame(x1, y1, x2, y2):
    L = math.hypot(x2 - x1, y2 - y1)
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return L, f'transform="translate({x1:.1f} {y1:.1f}) rotate({ang:.2f})"'


def red_arrow(x1, y1, x2, y2, color=RED):
    return arrow(x1, y1, x2, y2, color=color)


def ctext(x, y, parts, anchor="start", color=RED):
    return text(x, y, parts, anchor).replace('fill="#000"', f'fill="{color}"', 1)


def dc_source(cx, cy, r=16, plus_up=True):
    """Voltage source: circle with + and - marks (+ on top unless plus_up is False)."""
    yp, ym = (cy - 7, cy + 7) if plus_up else (cy + 7, cy - 7)
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}"/>\n' + line(cx - 4, yp, cx + 4, yp) + line(cx, yp - 4, cx, yp + 4)
            + line(cx - 4, ym, cx + 4, ym))


def diode(xa, ya, xk, yk, size=10):
    """Diode from anode (xa, ya) to cathode (xk, yk): solid triangle pointing to the cathode + bar."""
    L, tr = _frame(xa, ya, xk, yk)
    m = L / 2; a = m - size; b = m + size
    d = (f'<g {tr}>' + line(0, 0, a, 0) + f'<path d="M{a:.1f} {-size} L{a:.1f} {size} L{b:.1f} 0 Z" fill="#000"/>\n'
         + line(b, -size, b, size) + line(b, 0, L, 0) + '</g>\n')
    return d


def cap(x1, y1, x2, y2, gap=10, w=28):
    """Capacitor between two points: two parallel plates centred on the segment."""
    L, tr = _frame(x1, y1, x2, y2)
    m = L / 2
    return (f'<g {tr}>' + line(0, 0, m - gap / 2, 0) + line(m - gap / 2, -w / 2, m - gap / 2, w / 2)
            + line(m + gap / 2, -w / 2, m + gap / 2, w / 2) + line(m + gap / 2, 0, L, 0) + '</g>\n')


def switch(x1, y1, x2, y2, closed):
    """SPST switch between two points with open terminal circles; open blade lifts to the left of travel."""
    L, tr = _frame(x1, y1, x2, y2)
    a, b = 16, L - 16
    s = line(0, 0, a - 3, 0) + line(b + 3, 0, L, 0)
    s += f'<circle cx="{a}" cy="0" r="3" fill="#fff"/>\n<circle cx="{b:.1f}" cy="0" r="3" fill="#fff"/>\n'
    s += line(a + 2, -3, b + 1, -3) if closed else line(a + 2, -2, b - 2, -22)
    return f'<g {tr}>' + s + '</g>\n'


def dashed(x1, y1, x2, y2, w=1):
    return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke-width="{w}" stroke-dasharray="4 3"/>\n'


def poly(pts, w=2.2, color=None):
    c = f' stroke="{color}"' if color else ''
    return '<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + f'" stroke-width="{w}"{c}/>\n'


def write(name, svg):
    out = OUT_DIR / name
    out.write_text(svg)
    print(out.name, len(svg))
