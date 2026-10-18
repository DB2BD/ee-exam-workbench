import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def ctext(c, *a, **k): return text(*a, **k).replace('fill="#000"', f'fill="{c}"')
W, H = 720, 320
YT, YB = 90, 220
panels = [("1", "正序網路", "−", "6.9953", [("v", "j"), ("v", "X"), ("sub", "1"), ("n", " = "), ("v", "j"), ("n", "0.1")]),
          ("2", "負序網路", "", "0.9953", [("v", "j"), ("v", "X"), ("sub", "2"), ("n", "（未給）")]),
          ("0", "零序網路", "−", "3", [("v", "j"), ("v", "X"), ("sub", "0"), ("n", "（待求）")])]
s = header(W, H)
labels = ""
for k, (n, title, sign, val, zlab) in enumerate(panels):
    x0 = 10 + 240 * k
    xl, xc1, xc2, xf = x0 + 30, x0 + 70, x0 + 140, x0 + 195
    if n == "1":
        s += line(xl, YT, xl, 141) + ac_source(xl, 155) + line(xl, 169, xl, YB)
        labels += ctext(BLUE, xl + 20, 160, [("v", "E"), ("n", " = 1∠0°")])
    else:
        s += line(xl, YT, xl, YB)
    s += line(xl, YT, xc1, YT) + coil(xc1, YT, xc2, YT, turns=4) + line(xc2, YT, xf, YT)
    s += line(xl, YB, xf, YB)
    s += dot(xf, YT) + dot(xf, YB)
    s += arrow(xc2 + 6, YT, xf - 8, YT, color=RED)
    s += arrow(xf, YB - 6, xf, YT + 14, color=BLUE)
    labels += text((xc1 + xc2) / 2, YT + 30, zlab, anchor="middle")
    labels += ctext(RED, x0 + 150, YT - 22, [("v", "I"), ("vsub", "a"), ("sub", n), ("n", " = " + sign), ("v", "j"), ("n", val)], anchor="middle")
    labels += ctext(BLUE, xf + 8, 166, [("v", "V"), ("vsub", "a"), ("sub", n)])
    labels += text(xf + 6, YT - 4, [("v", "F")])
    labels += text(x0 + 112, YB + 30, [("t", title)], anchor="middle")
s += end_group() + labels
s += text(360, 296, [("t", "參考方向：序電流由網路流向故障點 "), ("v", "F"), ("t", "；序電壓為 "), ("v", "F"), ("t", " 對參考點（數值皆為 pu）")], anchor="middle")
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/05_電力系統/figures/EE-110-05-3-sequence.svg'), 'w').write(s)
print(len(s))
