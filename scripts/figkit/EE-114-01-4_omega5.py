"""EE-114-01-4: 5 rad/s phasor circuit (current source opened), V_s = 75∠0° V (sine reference)."""
import importlib.util, pathlib
_p = pathlib.Path(__file__).with_name('EE-114-01-4_common.py')
_s = importlib.util.spec_from_file_location('c4', _p); c = importlib.util.module_from_spec(_s); _s.loader.exec_module(c)
from circuit_parts import *

s = c.frame(keep_vsrc=True, keep_isrc=False)
s += end_group()
s += ttext(c.XS - 26, 176, [("v", "V"), ("vsub", "s"), ("n", " = 75∠0° V")], anchor="end", color=BLUE)
s = s.replace('<tspan class="v" font-family', '<tspan class="v" font-weight="bold" font-family', 1)
s += c.vo_label("5")
s += c.common_labels("j1 S", "−j0.2 S")
s += text(c.XI - 20, 176, [("t", "（電流源開路）")])
s += text(20, 300, [("v", "ω"), ("n", " = 5 rad/s"), ("t", "（正弦基準相量）")])
s += footer()
write('EE-114-01-4-omega5.svg', s)
