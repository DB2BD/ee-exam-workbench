import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
import importlib; c = importlib.import_module("EE-113-05-2_common")
from svgkit import *
s = c.skeleton()
s += arrow(250, c.YT + 18, 285, c.YT + 18, color=RED)
s += end_group()
s += c.labels()
s += c.ctext(RED, 268, c.YT + 64, [("v", "I"), ("n", " = 0.75∠36.87°")], anchor="middle")
s += c.ctext(BLUE, c.XM, 200, [("v", "V"), ("vsub", "m"), ("n", " = 20/24 = 0.83∠0°")], anchor="middle")
s += f'<g fill="none" stroke="{BLUE}" stroke-width="1" stroke-dasharray="4 4"><path d="M{c.XM} {c.YT + 6} L{c.XM} 182"/></g>\n'
s += c.text(340, 296, [("t", "故障前（以電動機端電壓為參考，"), ("v", "I"), ("t", " 由發電機流向電動機）")], anchor="middle")
s += footer()
c.write(s, "prefault")
