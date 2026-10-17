import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *

RED = "#c0392b"
def red_arrow(x1, y1, x2, y2):
    return f'<g stroke="{RED}">' + arrow(x1, y1, x2, y2).replace('fill="#000"', f'fill="{RED}"') + '</g>\n'
def red_text(x, y, parts, anchor="start"):
    return text(x, y, parts, anchor).replace('fill="#000"', f'fill="{RED}"', 1)

G_OPEN = '<g fill="none" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">\n'

def dc_source(cx, cy, r=16):
    """Voltage source: circle with + (top) and - (bottom)."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}"/>\n' + line(cx - 4, cy - 7, cx + 4, cy - 7) + line(cx, cy - 11, cx, cy - 3)
            + line(cx - 4, cy + 7, cx + 4, cy + 7))

def cap_v(x, y1, y2, gap=10, w=28):
    """Vertical capacitor between (x,y1) and (x,y2): two parallel plates centred."""
    m = (y1 + y2) / 2
    return (line(x, y1, x, m - gap / 2) + line(x - w / 2, m - gap / 2, x + w / 2, m - gap / 2)
            + line(x - w / 2, m + gap / 2, x + w / 2, m + gap / 2) + line(x, m + gap / 2, x, y2))

def diode_left(x1, x2, y, size=11):
    """Horizontal diode, cathode at x1 (left), anode at x2 (right): solid triangle pointing left + bar."""
    m = (x1 + x2) / 2; a = m - size; b = m + size
    return (line(x1, y, a, y) + f'<path d="M{a} {y} L{b} {y - size} L{b} {y + size} Z" fill="#000"/>\n'
            + line(a, y - size, a, y + size) + line(b, y, x2, y))

def switch(x1, x2, y, closed):
    """SPST switch between x1 and x2 with open terminal circles."""
    a, b = x1 + 16, x2 - 16
    s = line(x1, y, a - 3, y) + line(b + 3, y, x2, y)
    s += f'<circle cx="{a}" cy="{y}" r="3" fill="#fff"/>\n<circle cx="{b}" cy="{y}" r="3" fill="#fff"/>\n'
    s += line(a + 2, y - 3, b + 1, y - 3) if closed else line(a + 2, y - 2, b - 2, y - 22)
    return s

def panel(ox, on):
    s = ''
    s += dc_source(ox + 50, 150) + line(ox + 50, 134, ox + 50, 70) + line(ox + 50, 166, ox + 50, 230)
    s += switch(ox + 50, ox + 130, 70, on)
    s += coil(ox + 130, 70, ox + 130, 230, turns=5)
    s += diode_left(ox + 130, ox + 245, 70)
    s += cap_v(ox + 245, 70, 230)
    s += line(ox + 245, 70, ox + 315, 70) + resistor(ox + 315, 70, ox + 315, 230, zigs=8, lead=40)
    s += line(ox + 50, 230, ox + 315, 230)
    for x, y in ((130, 70), (245, 70), (130, 230), (245, 230)):
        s += dot(ox + x, y)
    s += red_arrow(ox + 108, 118, ox + 108, 158)              # i_L
    if on:
        s += red_arrow(ox + 282, 112, ox + 282, 152)          # I_o
    else:
        s += red_arrow(ox + 212, 46, ox + 166, 46)            # i_D (anode -> cathode, leftward)
    s += end_group()
    t = []
    if on:
        t.append(text(ox + 10, 26, [("t", "(a) "), ("v", "Q"), ("t", " 導通："), ("n", "0 &lt; "), ("v", "t"), ("n", " &lt; "), ("v", "DT"), ("sub", "s")]))
    else:
        t.append(text(ox + 10, 26, [("t", "(b) "), ("v", "Q"), ("t", " 截止："), ("v", "DT"), ("sub", "s"), ("n", " &lt; "), ("v", "t"), ("n", " &lt; "), ("v", "T"), ("sub", "s")]))
    t.append(text(ox + 30, 156, [("v", "V"), ("sub", "s")], anchor="end"))
    t.append(text(ox + 90, 56 if on else 44, [("v", "Q")], anchor="middle"))
    t.append(red_text(ox + 101, 144, [("v", "i"), ("vsub", "L")], anchor="end"))
    t.append(text(ox + 146, 156, [("v", "L")]))
    t.append(text(ox + 144, 98, [("n", "+")]))
    t.append(text(ox + 144, 218, [("n", "−")]))
    t.append(text(ox + 188, 104, [("v", "D"), ("t", " 截止" if on else " 導通")], anchor="middle"))
    t.append(text(ox + 227, 160, [("v", "C")], anchor="end"))
    t.append(text(ox + 328, 156, [("v", "R")]))
    t.append(text(ox + 324, 92, [("n", "−")]))
    t.append(text(ox + 324, 222, [("n", "+")]))
    if on:
        t.append(red_text(ox + 288, 138, [("v", "I"), ("vsub", "o")]))
        t.append(text(ox + 10, 262, [("v", "v"), ("vsub", "L"), ("n", " = +"), ("v", "V"), ("sub", "s"), ("n", " = 24 V"), ("t", "（電感儲能）")]))
        t.append(text(ox + 10, 286, [("v", "C"), ("t", " 單獨供給負載："), ("v", "i"), ("vsub", "C"), ("n", " = −"), ("v", "I"), ("vsub", "o")]))
    else:
        t.append(red_text(ox + 218, 51, [("v", "i"), ("vsub", "D")]))
        t.append(text(ox + 10, 262, [("v", "v"), ("vsub", "L"), ("n", " = −"), ("v", "V"), ("vsub", "o"), ("n", " = −36 V"), ("t", "（電感釋能）")]))
        t.append(text(ox + 10, 286, [("v", "i"), ("vsub", "D"), ("n", " = "), ("v", "i"), ("vsub", "L"), ("t", "，"), ("v", "i"), ("vsub", "C"), ("n", " = "), ("v", "i"), ("vsub", "L"), ("n", " − "), ("v", "I"), ("vsub", "o")]))
    return s, ''.join(t)

W, H = 720, 300
s = header(W, H)
a, ta = panel(0, True)
b, tb = panel(360, False)
s += a + G_OPEN + b + ta + tb + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/02_電子學_含電力電子/figures/EE-112-02-3-on-off.svg'
out.write_text(s); print(len(s))
