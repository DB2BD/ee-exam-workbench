"""EE-107-04-1 fig 1: three single-phase 66 kVA, 6600/220 V transformers connected Y-Y between a
3-phase 4-wire 11.4 kV source and a 3-phase 380 V load.  Primary: H1 to A/B/C, H2 joined to the source
neutral N.  Secondary: X1 to a/b/c, X2 joined to the secondary neutral n.  Polarity dots on H1 and X1
(same side for all three units)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import terminal, ttext

W, H = 720, 470
X0, X1 = 70, 610                       # bus start / end
YS = {"A": 60, "B": 84, "C": 108, "N": 132}
YL = {"n": 300, "a": 324, "b": 348, "c": 372}
XC = (180, 350, 520)
YP, YS2 = 196, 236                    # primary / secondary coil rows
s = header(W, H)
# source buses end at their H1 drop (N at the last H2); load buses start at their X1 drop
for (n, y), xe in zip(YS.items(), (XC[0] - 50, XC[1] - 50, XC[2] - 50, XC[2] + 50)):
    s += line(X0, y, xe, y) + terminal(X0, y)
s += line(X0 + 40, YL["n"], XC[2] + 50, YL["n"])
for n, xc in zip("abc", XC):
    s += line(xc - 50, YL[n], X1, YL[n])
for k, (xc, ph, lp) in enumerate(zip(XC, "ABC", "abc")):
    xl, xr = xc - 50, xc + 50
    s += line(xl, YP, xc - 34, YP) + coil(xc - 34, YP, xc + 34, YP, turns=4, r=8.5).replace('rotate(0.00)', 'rotate(0.00) scale(1 -1)') + line(xc + 34, YP, xr, YP)
    s += line(xr, YS2, xc + 34, YS2) + coil(xc + 34, YS2, xc - 34, YS2, turns=4, r=8.5) + line(xc - 34, YS2, xl, YS2)
    s += line(xc - 40, 212, xc + 40, 212) + line(xc - 40, 218, xc + 40, 218)          # core
    s += line(xl, YP, xl, YS[ph])                                                        # H1 -> line (bus ends here)
    s += line(xr, YP, xr, YS["N"]) + (dot(xr, YS["N"]) if k < 2 else "")                   # H2 -> N (corner on T3)
    s += line(xl, YS2, xl, YL[lp])                                                      # X1 -> a/b/c (bus starts here)
    s += line(xr, YS2, xr, YL["n"]) + (dot(xr, YL["n"]) if k < 2 else "")                  # X2 -> n
    s += dot(xl + 10, YP - 12) + dot(xl + 10, YS2 + 12)                                 # polarity
# load: three-wire 380 V load on a, b, c; n left as the secondary neutral terminal
s += terminal(X0 + 40, YL["n"])
s += f'<rect x="{X1}" y="{YL["a"] - 16}" width="70" height="{YL["c"] - YL["a"] + 32}"/>\n'
s += end_group()
for n, y in YS.items():
    s += text(X0 - 12, y + 6, [("v", n)], anchor="end")
s += text(X0 + 28, YL["n"] + 6, [("v", "n")], anchor="end")
for n in "abc":
    s += text(X1 - 6, YL[n] - 6, [("v", n)], anchor="end")
s += text(X1 + 35, YL["b"] + 6, [("t", "負載")], anchor="middle")
s += text(X0 - 40, 32, [("t", "電源 三相四線 11.4 kV")])
for k, xc in enumerate(XC):
    s += text(xc, 268, [("v", "T"), ("sub", str(k + 1))], anchor="middle")
    s += text(xc - 56, YP + 6, [("v", "H"), ("sub", "1")], anchor="end")
    s += text(xc + 56, YP + 6, [("v", "H"), ("sub", "2")])
    s += text(xc - 56, YS2 + 6, [("v", "X"), ("sub", "1")], anchor="end")
    s += text(xc + 56, YS2 + 6, [("v", "X"), ("sub", "2")])
s += ttext(360, 410, [("t", "一次側 Y：每台繞組跨相電壓 "), ("n", "11 400/√3 = 6582 V ≈ 6600 V")], anchor="middle", color=BLUE)
s += ttext(360, 434, [("t", "二次側 Y：每台 220 V，線電壓 "), ("n", "220√3 = 381.05 V ≈ 380 V")], anchor="middle", color=BLUE)
s += text(360, 458, [("t", "● 為極性點：三台 "), ("v", "H"), ("sub", "1"), ("t", "、"), ("v", "X"), ("sub", "1"), ("t", " 同側；"), ("v", "H"), ("sub", "2"), ("t", " 接電源中性線 "), ("v", "N")], anchor="middle")
s += footer()
out = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures/EE-107-04-1-wiring.svg'
out.write_text(s)
print(out.name, len(s))
