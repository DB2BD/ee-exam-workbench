"""EE-112-04-4 fig 1: per-phase current phasors at start, V_phi (a-phase, line-to-neutral) as 0 deg reference.
I_m (motor, 330 A at -59.34 deg) + I_C (capacitor-bank line current, +90 deg) = I_L (200 A at -32.70 deg, still lagging).
Head-to-tail: I_C drawn from the tip of I_m; the active component 168.30 A is unchanged."""
import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import ttext

IP, IQ, IQn = 168.30, 283.857, 108.051
k = 0.85; ox, oy = 70, 60
W, H = 600, 340
mx, my = ox + k * IP, oy + k * IQ          # tip of I_m
cx, cy = mx, oy + k * IQn                  # tip of I_C = tip of I_L
s = header(W, H)
s += arrow(ox, oy, 470, oy, color=BLUE)
s += arrow(ox, oy, mx, my, color=RED)
s += arrow(mx, my, cx, cy, color=RED)
s += arrow(ox, oy, cx, cy, color=RED)
s += f'<path d="M{mx:.1f} {oy} L{mx:.1f} {cy:.1f}" stroke-dasharray="4 3" stroke-width="1"/>\n'
a1, a2 = math.radians(59.34), math.radians(32.70)
s += f'<path d="M{ox+110} {oy} A110 110 0 0 1 {ox+110*math.cos(a1):.1f} {oy+110*math.sin(a1):.1f}"/>\n'
s += f'<path d="M{ox+58} {oy} A58 58 0 0 1 {ox+58*math.cos(a2):.1f} {oy+58*math.sin(a2):.1f}"/>\n'
s += dot(ox, oy)
s += end_group()
s += text(ox - 8, oy + 5, [("v", "O")], anchor="end")
s += ttext(470, oy - 12, [("v", "V"), ("vsub", "ϕ"), ("n", "（0°）")], anchor="end", color=BLUE)
s += text((ox + mx) / 2, oy - 10, [("v", "I"), ("vsub", "P"), ("n", " = 168.30 A")], anchor="middle")
s += text(ox + 44, oy + 118, [("v", "φ"), ("vsub", "st"), ("n", " = 59.34°")], anchor="end")
s += text(ox + 66, oy + 24, [("v", "φ"), ("n", "′")])
s += ttext(mx - 70, my - 6, [("v", "I"), ("vsub", "m"), ("n", " = 330∠−59.34° A")], anchor="end", color=RED)
s += ttext(mx + 14, (my + cy) / 2 + 4, [("v", "I"), ("vsub", "C"), ("n", " = 175.806∠90° A")], color=RED)
s += ttext(mx + 14, cy - 8, [("v", "I"), ("vsub", "L"), ("n", " = 200∠−32.70° A")], color=RED)
s += text(mx + 14, (my + cy) / 2 + 28, [("t", "（電容組線電流，超前 "), ("v", "V"), ("vsub", "ϕ"), ("n", " 90°"), ("t", "）")])
s += text(300, 326, [("v", "I"), ("vsub", "L"), ("n", " = "), ("v", "I"), ("vsub", "m"), ("n", " + "), ("v", "I"), ("vsub", "C"), ("t", "：無功分量 "), ("v", "I"), ("vsub", "Q"), ("n", " = 283.857 A → "), ("v", "I"), ("vsub", "Q"), ("n", "′ = 108.051 A")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-112-04-4-phasor.svg'
out.write_text(s)
print(out.name, len(s))
