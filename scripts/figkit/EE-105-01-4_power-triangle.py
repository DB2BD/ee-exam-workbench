"""EE-105-01-4: power triangle before (0.78 lag) and after (0.94 lead) adding the wye capacitor bank."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from circuit_parts import *

W, H = 600, 440
k = 12.0                      # px per MW / Mvar
x0, base = 90, 250
P, Q, Qn = 18.72, 15.019, -6.794
xe = x0 + P * k; yq = base - Q * k; yn = base - Qn * k
s = header(W, H)
s += line(x0, base, xe, base)
s += line(xe, base, xe, yq) + line(x0, base, xe, yq)
s += f'<path d="M{x0} {base} L{xe:.1f} {yn:.1f} L{xe:.1f} {base}" stroke="{BLUE}" stroke-dasharray="6 4"/>\n'
s += f'<g stroke="{BLUE}">' + arrow(xe + 26, yq, xe + 26, yn).replace('#000', BLUE) + '</g>\n'
s += dot(xe, yq) + dot(xe, yn) + dot(x0, base)
s += end_group()
s += text((x0 + xe) / 2 + 20, base - 10, [("v", "P"), ("n", " = 18.72 MW")], anchor="middle")
s += text(xe - 10, yq + 4, [("v", "Q"), ("n", " = 15.019 Mvar")], anchor="end")
s += ttext(xe, yn + 28, [("v", "Q"), ("sub", "new"), ("n", " = −6.794 Mvar")], anchor="middle", color=BLUE)
s += ttext(xe + 36, (yq + yn) / 2 + 6, [("v", "Q"), ("vsub", "C"), ("n", " = 21.813 Mvar")], color=BLUE)
s += text(x0 + 46, base - 12, [("v", "φ")]) + ttext(x0 + 62, base + 17, [("v", "θ")], color=BLUE)
s += text(300, 400, [("t", "黑：原負載 "), ("n", "cos "), ("v", "φ"), ("n", " = 0.78"), ("t", "（落後，"), ("v", "Q"), ("n", " > 0"), ("t", "）")], anchor="middle")
s += text(300, 424, [("t", "藍虛線：加 Y 接電容後 "), ("n", "cos "), ("v", "θ"), ("n", " = 0.94"), ("t", "（領先，"), ("v", "Q"), ("n", " &lt; 0"), ("t", "）")], anchor="middle")
s += footer()
write('EE-105-01-4-power-triangle.svg', s)
