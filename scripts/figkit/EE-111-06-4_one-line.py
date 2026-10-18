"""EE-111-06-4 one-line diagram (results): 3φ 220 V -> main breaker 175 AT / 225 AF (limit 194.20 A),
feeder 125 mm² (need 165.33 A, raised to 175 A by the book rule) -> four branches:
20 HP welder and 20 HP compressor 70 AT / 22 mm², 10 HP 40 AT / 8 mm², 8 HP 30 AT / 5.5 mm².
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
def breaker(x, y, h=24):
    return f'<rect x="{x - 10}" y="{y - h / 2}" width="20" height="{h}" fill="#fff"/>\n'
def motor(x, y, r=20):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff"/>\n'
W, H = 720, 500; s = header(W, H); lab = ''
xF, yS, yB = 360, 46, 210
s += busbar(280, 440, yS)
s += line(xF, yS, xF, yB) + breaker(xF, 92)
xs = (110, 270, 430, 590)
s += busbar(80, 640, yB)
for x in xs:
    s += line(x, yB, x, 390) + breaker(x, 250) + motor(x, 410)
s += end_group()
lab += text(450, yS + 5, [("n", "3φ 220 V")])
lab += text(xF + 20, 90, [("t", "主斷路器 "), ("n", "175 AT / 225 AF")])
lab += text(xF + 20, 112, [("n", "AT"), ("sub", "main"), ("n", " ≤ 194.20 A")])
lab += text(xF + 20, 150, [("t", "幹線 "), ("n", "125 mm²（220 A）")])
lab += text(xF + 20, 172, [("v", "I"), ("vsub", "w"), ("sub", ",main"), ("n", " ≥ 165.33 A → 175 A")])
rows = ((xs[0], "70 AT", "22 mm²", "20 HP 電焊機", "I", "20", "52.49 A", "65.61 A"),
        (xs[1], "70 AT", "22 mm²", "20 HP 壓縮機", "I", "20", "52.49 A", "65.61 A"),
        (xs[2], "40 AT", "8 mm²", "10 HP 冷氣機", "I", "10", "26.24 A", "32.80 A"),
        (xs[3], "30 AT", "5.5 mm²", "8 HP 車床", "I", "8", "20.99 A", "26.24 A"))
for x, at, mm, name, _, sub, i, iw in rows:
    lab += text(x + 16, 255, [("n", at)])
    lab += text(x + 16, 310, [("n", mm)])
    lab += text(x + 16, 332, [("v", "I"), ("vsub", "w"), ("sub", "," + sub), ("n", " = " + iw)])
    lab += text(x, 416, [("n", "M")], anchor="middle")
    lab += text(x, 456, [("t", name)], anchor="middle")
    lab += text(x, 480, [("v", "I"), ("sub", sub), ("n", " = " + i)], anchor="middle")
s += lab + footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/06_工業配電/figures/EE-111-06-4-one-line.svg'
out.write_text(s); print(out.name, len(s))
