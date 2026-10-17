"""Shared parts for circuit-analysis figures (subject 01): sources, dependent sources, capacitor, switch.

Two-terminal parts are drawn along the segment between their terminals; polarity marks
(+ / -) stay upright in world coordinates, as in textbook drawings.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *  # noqa: F401,F403
from power_parts import cap, switch, dashed, ctext  # noqa: F401

OUT_DIR = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/01_電路學/figures'


def _unit(x1, y1, x2, y2):
    L = math.hypot(x2 - x1, y2 - y1)
    return L, (x2 - x1) / L, (y2 - y1) / L


def _plus(x, y, s=4):
    return line(x - s, y, x + s, y) + line(x, y - s, x, y + s)


def _minus(x, y, s=4):
    return line(x - s, y, x + s, y)


def vsrc(x1, y1, x2, y2, r=16):
    """Independent voltage source between two terminals; + near (x1, y1), - near (x2, y2)."""
    L, ux, uy = _unit(x1, y1, x2, y2)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    s = line(x1, y1, cx - r * ux, cy - r * uy) + line(cx + r * ux, cy + r * uy, x2, y2)
    s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}"/>\n'
    return s + _plus(cx - 7 * ux, cy - 7 * uy) + _minus(cx + 7 * ux, cy + 7 * uy)


def isrc(x1, y1, x2, y2, r=16):
    """Independent current source between two terminals; arrow inside points (x1, y1) -> (x2, y2)."""
    L, ux, uy = _unit(x1, y1, x2, y2)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    s = line(x1, y1, cx - r * ux, cy - r * uy) + line(cx + r * ux, cy + r * uy, x2, y2)
    s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}"/>\n'
    return s + arrow(cx - 9 * ux, cy - 9 * uy, cx + 9 * ux, cy + 9 * uy)


def dep_vsrc(x1, y1, x2, y2, h=17):
    """Dependent voltage source (diamond) between two terminals; + near (x1, y1), - near (x2, y2)."""
    L, ux, uy = _unit(x1, y1, x2, y2)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    s = line(x1, y1, cx - h * ux, cy - h * uy) + line(cx + h * ux, cy + h * uy, x2, y2)
    s += f'<path d="M{cx - h:.1f} {cy:.1f} L{cx:.1f} {cy - h:.1f} L{cx + h:.1f} {cy:.1f} L{cx:.1f} {cy + h:.1f} Z"/>\n'
    return s + _plus(cx - 7 * ux, cy - 7 * uy, 3.5) + _minus(cx + 7 * ux, cy + 7 * uy, 3.5)


def terminal(x, y):
    """Open terminal circle."""
    return f'<circle cx="{x}" cy="{y}" r="4" fill="#fff"/>\n'


def tint_arrow(x1, y1, x2, y2, color=RED):
    return f'<g stroke="{color}">' + arrow(x1, y1, x2, y2).replace('#000', color) + '</g>\n'


def mesh_arrow(cx, cy, r, a0=210, a1=-120, color=RED):
    """Clockwise circular mesh-current arrow (screen coordinates) from angle a0 to a1 (degrees, math sense)."""
    p = lambda a: (cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a)))
    (x0, y0), (x1, y1) = p(a0), p(a1)
    large = 1 if (a0 - a1) % 360 > 180 else 0
    s = f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}" stroke="{color}"/>\n'
    # head: tangent of a clockwise path at a1 points along (sin a, cos a) in screen coordinates
    tx, ty = math.sin(math.radians(a1)), math.cos(math.radians(a1))
    return s + tint_arrow(x1 - 2 * tx, y1 - 2 * ty, x1 + 0.5 * tx, y1 + 0.5 * ty, color)


def ttext(x, y, parts, anchor="start", color="#000"):
    return text(x, y, parts, anchor).replace('fill="#000"', f'fill="{color}"', 1)


def write(name, svg):
    out = OUT_DIR / name
    out.write_text(svg)
    print(out.name, len(svg))
