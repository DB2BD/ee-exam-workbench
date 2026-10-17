import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
import importlib; c = importlib.import_module("EE-113-05-2_common")
from svgkit import *
s = c.skeleton()
s += f'<path d="M{c.XG} {c.YT} L{c.XG} {c.YB}" stroke="{RED}" stroke-width="2.5"/>\n'   # bolted 3φ fault at G
s += dot(c.XG, c.YB)
s += arrow(192, c.YT + 18, 222, c.YT + 18, color=RED)          # Ig' toward G
s += arrow(285, c.YT + 18, 240, c.YT + 18, color=RED)          # Im' toward G (through line)
s += arrow(c.XG + 14, 180, c.XG + 14, 232, color=RED)          # If' down
s += end_group()
s += c.labels()
s += c.ctext(RED, 200, c.YT + 64, [("v", "I"), ("vsub", "g"), ("n", "′")], anchor="end")
s += c.ctext(RED, 270, c.YT + 64, [("v", "I"), ("vsub", "m"), ("n", "′")])
s += c.ctext(RED, c.XG + 24, 216, [("v", "I"), ("vsub", "f"), ("n", "′ = "), ("v", "I"), ("vsub", "g"), ("n", "′ + "), ("v", "I"), ("vsub", "m"), ("n", "′")])
s += c.text(340, 296, [("t", "故障瞬間（"), ("v", "E"), ("vsub", "g"), ("n", "′"), ("t", "、"), ("v", "E"), ("vsub", "m"), ("n", "′"), ("t", " 不變，發電機端 "), ("v", "V"), ("vsub", "G"), ("n", " = 0"), ("t", "）")], anchor="middle")
s += footer()
c.write(s, "fault")
