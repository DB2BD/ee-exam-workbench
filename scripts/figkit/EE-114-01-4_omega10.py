"""EE-114-01-4: 10 rad/s phasor circuit (voltage source shorted, 8 ohm kept), I_s = 6∠0° A (cosine reference)."""
import importlib.util, pathlib
_p = pathlib.Path(__file__).with_name('EE-114-01-4_common.py')
_s = importlib.util.spec_from_file_location('c4', _p); c = importlib.util.module_from_spec(_s); _s.loader.exec_module(c)
from circuit_parts import *

s = c.frame(keep_vsrc=False, keep_isrc=True)
s += end_group()
s += text(c.XS - 10, 176, [("t", "電壓源短路")], anchor="end")
s += c.vo_label("10")
s += c.common_labels("j2 S", "−j0.1 S")
s += text(c.XI, c.YT - 14, [("v", "I"), ("vsub", "s"), ("n", " = 6∠0° A")], anchor="middle")
s = s.replace('<tspan class="v" font-family="KaTeX_Math, \'Times New Roman\', serif" font-style="italic">I</tspan>',
              '<tspan class="v" font-weight="bold" font-family="KaTeX_Math, \'Times New Roman\', serif" font-style="italic">I</tspan>')
s += text(20, 300, [("v", "ω"), ("n", " = 10 rad/s"), ("t", "（餘弦基準相量）；8 Ω 仍跨接輸出節點與地")])
s += footer()
write('EE-114-01-4-omega10.svg', s)
