"""EE-105-02-4: rms spectra of v(t) and i(t); only the same-frequency pair (fundamental) carries real power."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from power_parts import *

W, H = 720, 330
X = {0: 165, 1: 320, 3: 470}          # columns: dc, fundamental, 3rd harmonic
YV, YI = 125, 275                      # baselines of the voltage and current rows
s = header(W, H)
# shaded column: the only frequency present in both v and i with V != 0
s = s.replace(G_OPEN, f'<rect x="{X[1] - 50}" y="22" width="100" height="262" fill="{FILL_BLUE}" stroke="none"/>\n' + G_OPEN, 1)
for y in (YV, YI):
    s += arrow(100, y, 540, y) + arrow(100, y + 6, 100, y - 100)
bar = lambda x, y, h, c: f'<path d="M{x} {y} L{x} {y - h:.1f}" stroke="{c}" stroke-width="7" stroke-linecap="butt"/>\n'
s += bar(X[1], YV, 70.71, BLUE)                    # V_1 = 70.71 V (1 px / V)
s += bar(X[0], YI, 7 * 8, RED)                     # I_dc = 7 A (8 px / A)
s += bar(X[1], YI, 8.485 * 8, RED)                 # I_1 = 8.485 A
s += bar(X[3], YI, 3.536 * 8, RED)                 # I_3 = 3.536 A
s += end_group()
s += text(92, 40, [("t", "電壓 rms")], anchor="end")
s += text(92, 190, [("t", "電流 rms")], anchor="end")
s += ctext(X[1], YV - 78, [("v", "V"), ("sub", "1"), ("n", " = 70.71 V")], anchor="middle", color=BLUE)
s += text(X[0], YV - 8, [("v", "V"), ("sub", "0"), ("n", " = 0")], anchor="middle")
s += text(X[3], YV - 8, [("v", "V"), ("sub", "3"), ("n", " = 0")], anchor="middle")
s += ctext(X[0], YI - 64, [("v", "I"), ("sub", "dc"), ("n", " = 7 A")], anchor="middle")
s += ctext(X[1], YI - 76, [("v", "I"), ("sub", "1"), ("n", " = 8.485 A ∠30°")], anchor="middle")
s += ctext(X[3], YI - 36, [("v", "I"), ("sub", "3"), ("n", " = 3.536 A ∠60°")], anchor="middle")
s += text(X[0], YI + 22, [("t", "直流")], anchor="middle")
s += text(X[1], YI + 22, [("t", "基波 "), ("v", "ω")], anchor="middle")
s += text(X[3], YI + 22, [("t", "三次 3"), ("v", "ω")], anchor="middle")
s += text(556, 60, [("v", "P"), ("sub", "0"), ("n", " = "), ("v", "V"), ("sub", "0"), ("v", "I"), ("sub", "dc"), ("n", " = 0")])
s += text(556, 100, [("v", "P"), ("sub", "1"), ("n", " = "), ("v", "V"), ("sub", "1"), ("v", "I"), ("sub", "1"), ("n", " cos 30°")])
s += text(580, 124, [("n", "= 519.62 W")])
s += text(556, 164, [("v", "P"), ("sub", "3"), ("n", " = "), ("v", "V"), ("sub", "3"), ("v", "I"), ("sub", "3"), ("n", " cos"), ("v", "ϕ"), ("sub", "3"), ("n", " = 0")])
s += text(556, 214, [("t", "只有同頻率的"), ("v", "V")])
s += text(556, 236, [("t", "與"), ("v", "I"), ("t", "配對產生實功")])
s += footer()
write('EE-105-02-4-spectrum.svg', s)
