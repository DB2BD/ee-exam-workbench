"""EE-109-04-4 fig 2: w_e t = 60 deg, i_a = i_b = I/2, i_c = -I.
F_a = NI/2 at 0 deg; F_b = NI/2 at 120 deg; F_c = NI at 240-180 = 60 deg; F = 1.5NI at 60 deg."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
import importlib; c = importlib.import_module("EE-109-04-4_common")

comps = [(0.5, 0), (0.5, 120), (1.0, 60)]
fa = c.P(0.5, 0); fb = c.P(0.5, 120); fc = c.P(1.0, 60)
labels = [
    (fa[0], fa[1] + 24, [("n", "F"), ("vsub", "a"), ("n", " = 0.5"), ("v", "NI")], "middle"),
    (fb[0] - 12, fb[1] + 14, [("n", "F"), ("vsub", "b"), ("n", " = 0.5"), ("v", "NI"), ("n", "∠120°")], "end"),
    (fc[0] - 14, fc[1] + 4, [("n", "F"), ("vsub", "c"), ("n", " = "), ("v", "NI"), ("n", "∠60°")], "end"),
]
r = c.P(1.5, 60)
res = (r[0] + 14, r[1] + 2, [("n", "F"), ("n", " = 1.5"), ("v", "NI"), ("n", "∠60°")], "start")
note = [("v", "ω"), ("vsub", "e"), ("v", "t"), ("n", " = 60°"), ("t", "："), ("v", "i"), ("vsub", "c"), ("n", " = −"), ("v", "I"),
        ("t", "，"), ("n", "F"), ("vsub", "c"), ("t", " 指向 "), ("n", "−"), ("v", "c"), ("t", " 方向（60°）；虛線為首尾相接")]
c.figure(comps, [0, 2, 1], 60, labels, res, note, 'EE-109-04-4-mmf-60.svg')
