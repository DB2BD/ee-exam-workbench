"""EE-109-04-4 fig 1: t = 0, i_a = I, i_b = i_c = -I/2.
F_a = NI at 0 deg; F_b = NI/2 at 120-180 = -60 deg; F_c = NI/2 at 240-180 = 60 deg; F = 1.5NI at 0 deg."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
import importlib; c = importlib.import_module("EE-109-04-4_common")

comps = [(1.0, 0), (0.5, -60), (0.5, 60)]
fa = c.P(0.5, 0); fb = c.P(0.5, -60); fc = c.P(0.5, 60)
labels = [
    (fa[0], fa[1] + 24, [("n", "F"), ("vsub", "a"), ("n", " = "), ("v", "NI")], "middle"),
    (fb[0] + 8, fb[1] + 18, [("n", "F"), ("vsub", "b"), ("n", " = 0.5"), ("v", "NI"), ("n", "∠−60°")], "start"),
    (fc[0] + 6, fc[1] - 14, [("n", "F"), ("vsub", "c"), ("n", " = 0.5"), ("v", "NI"), ("n", "∠60°")], "start"),
]
r = c.P(1.5, 0)
res = (r[0], r[1] + 24, [("n", "F"), ("n", " = 1.5"), ("v", "NI"), ("n", "∠0°")], "middle")
note = [("v", "ω"), ("vsub", "e"), ("v", "t"), ("n", " = 0"), ("t", "：負電流的磁動勢畫在相軸反方向（"),
        ("n", "−"), ("v", "b"), ("t", "、"), ("n", "−"), ("v", "c"), ("t", "）；虛線為首尾相接")]
c.figure(comps, [0, 2, 1], 0, labels, res, note, 'EE-109-04-4-mmf-t0.svg')
