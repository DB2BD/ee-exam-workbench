"""Shared parts for small-signal / bias figures (subject 02): dependent current source, BJT symbol,
open terminal, voltage polarity labels.  Builds on power_parts (black line art, KaTeX font classes)."""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *  # noqa: F401,F403


def _unit(x1, y1, x2, y2):
    L = math.hypot(x2 - x1, y2 - y1)
    return L, (x2 - x1) / L, (y2 - y1) / L


def dep_isrc(x1, y1, x2, y2, h=17):
    """Dependent current source (diamond) between two terminals; inner arrow points (x1, y1) -> (x2, y2)."""
    L, ux, uy = _unit(x1, y1, x2, y2)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    s = line(x1, y1, cx - h * ux, cy - h * uy) + line(cx + h * ux, cy + h * uy, x2, y2)
    s += f'<path d="M{cx - h:.1f} {cy:.1f} L{cx:.1f} {cy - h:.1f} L{cx + h:.1f} {cy:.1f} L{cx:.1f} {cy + h:.1f} Z"/>\n'
    return s + arrow(cx - 9 * ux, cy - 9 * uy, cx + 9 * ux, cy + 9 * uy)


def isrc(x1, y1, x2, y2, r=16):
    """Independent current source (circle) between two terminals; inner arrow points (x1, y1) -> (x2, y2)."""
    L, ux, uy = _unit(x1, y1, x2, y2)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    s = line(x1, y1, cx - r * ux, cy - r * uy) + line(cx + r * ux, cy + r * uy, x2, y2)
    s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}"/>\n'
    return s + arrow(cx - 9 * ux, cy - 9 * uy, cx + 9 * ux, cy + 9 * uy)


def vsrc(x1, y1, x2, y2, r=16):
    """Independent voltage source (circle) between two terminals; + near (x1, y1), - near (x2, y2)."""
    L, ux, uy = _unit(x1, y1, x2, y2)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    s = line(x1, y1, cx - r * ux, cy - r * uy) + line(cx + r * ux, cy + r * uy, x2, y2)
    s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}"/>\n'
    px, py = cx - 7 * ux, cy - 7 * uy
    mx, my = cx + 7 * ux, cy + 7 * uy
    return s + line(px - 4, py, px + 4, py) + line(px, py - 4, px, py + 4) + line(mx - 4, my, mx + 4, my)


def terminal(x, y):
    return f'<circle cx="{x}" cy="{y}" r="3.5" fill="#fff"/>\n'


def npn(bx, by, lead=22):
    """Vertical NPN: base bar at x = bx centred on y = by; collector up-right, emitter down-right (arrow out).
    Returns (svg, (xc, yc), (xe, ye)) with the collector / emitter lead end points."""
    s = line(bx, by - 18, bx, by + 18) + f'<path d="M{bx:.1f} {by - 18:.1f} L{bx:.1f} {by + 18:.1f}" stroke-width="3"/>\n'
    xc, yc = bx + 24, by - 22
    xe, ye = bx + 24, by + 22
    s += line(bx, by - 7, xc, yc) + line(xc, yc, xc, yc - lead)
    s += line(bx, by + 7, xe, ye) + line(xe, ye, xe, ye + lead)
    # emitter arrow (solid head on the diagonal, pointing away from the base)
    ang = math.atan2(ye - (by + 7), xe - bx)
    hx, hy = bx + 0.8 * (xe - bx), by + 7 + 0.8 * (ye - by - 7)
    p1 = (hx - 8 * math.cos(ang) + 4 * math.sin(ang), hy - 8 * math.sin(ang) - 4 * math.cos(ang))
    p2 = (hx - 8 * math.cos(ang) - 4 * math.sin(ang), hy - 8 * math.sin(ang) + 4 * math.cos(ang))
    s += f'<path d="M{hx:.1f} {hy:.1f} L{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} Z" fill="#000"/>\n'
    return s, (xc, yc - lead), (xe, ye + lead)


def btext(x, y, parts, anchor="start"):
    """Blue label (voltages / emphasis)."""
    return ctext(x, y, parts, anchor=anchor, color=BLUE)


def polarity(x, ytop, ybot, parts, color=BLUE, anchor="start"):
    """+ near ytop, - near ybot, label centred between: a voltage drawn between two real nodes."""
    xm = x + 4 if anchor == "start" else x - 4
    return (ctext(x, ytop + 14, [("n", "+")], anchor="middle", color=color)
            + ctext(x, ybot - 4, [("n", "−")], anchor="middle", color=color)
            + ctext(xm + (6 if anchor == "start" else -6), (ytop + ybot) / 2 + 5, parts, anchor=anchor, color=color))
