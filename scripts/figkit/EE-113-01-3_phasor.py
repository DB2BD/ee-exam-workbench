import sys, pathlib, math; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
RED, BLUE = "#c0392b", "#1f5fa8"
W, H = 620, 350
O = (230, 160); K = 115 / 110          # px per ampere (V_ab drawn at an arbitrary length)
def tip(mag, deg, k=K):
    return O[0] + mag * k * math.cos(math.radians(deg)), O[1] - mag * k * math.sin(math.radians(deg))
Iab, Ica, mIca = tip(110, -20), tip(110, 100), tip(110, -80)
Ia, Vab = tip(110 * math.sqrt(3), -50), tip(150, 25, 1)
def dashed(p, q, w=1.0, da="5 4"):
    return f'<path d="M{p[0]:.1f} {p[1]:.1f} L{q[0]:.1f} {q[1]:.1f}" stroke-width="{w}" stroke-dasharray="{da}"/>\n'
s = header(W, H)
s += dashed((60, O[1]), (540, O[1]), 0.8, "3 4") + dashed((O[0], 20), (O[0], 335), 0.8, "3 4")   # axes
s += dashed(Iab, Ia) + dashed(mIca, Ia)                                                         # parallelogram
s += arrow(*O, *Iab) + arrow(*O, *Ica) + arrow(*O, *mIca)
s += f'<g stroke="{BLUE}">' + arrow(*O, *Vab).replace('#000', BLUE) + '</g>\n'
s += f'<g stroke="{RED}" stroke-width="2.4">' + arrow(*O, *Ia).replace('#000', RED) + '</g>\n'
s += dot(*O)
s += end_group()
s += text(548, O[1] + 5, [("t", "實軸")])
s += text(round(Vab[0]) + 8, round(Vab[1]) + 2, [("v", "V"), ("vsub", "ab"), ("n", "∠25°")]).replace('#000', BLUE)
s += text(round(Iab[0]) + 10, round(Iab[1]) + 2, [("v", "I"), ("vsub", "ab"), ("n", " = 110∠−20°")])
s += text(round(Ica[0]) - 10, round(Ica[1]) + 4, [("v", "I"), ("vsub", "ca"), ("n", " = 110∠100°")], anchor="end")
s += text(O[0] - 8, round(mIca[1]) + 4, [("n", "−"), ("v", "I"), ("vsub", "ca"), ("n", " = 110∠−80°")], anchor="end")
s += text(round(Ia[0]) + 12, round(Ia[1]) + 6, [("v", "I"), ("vsub", "a"), ("n", " = "), ("v", "I"), ("vsub", "ab"),
          ("n", " − "), ("v", "I"), ("vsub", "ca"), ("n", " = 110√3∠−50°")]).replace('#000', RED)
s += footer()
open(pathlib.Path(__file__).resolve().parents[2].joinpath('02_題解/技師題解/01_電路學/figures/EE-113-01-3-phasor.svg'), 'w').write(s)
print(len(s))
