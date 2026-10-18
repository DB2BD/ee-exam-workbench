"""Shared drawing for single-phase step-down autotransformer figures (subject 04).

Layout: series winding on top, common winding below, both dotted at their upper ends (additive
series connection).  The source sits across both windings (left), the load across the common
winding (right, from the tap).  Reference directions: input current along the top line into the
series winding, output current from the tap to the load, common-winding current upward from the
common line to the tap (KCL at the tap: I_out = I_in + I_c)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from svgkit import *
from circuit_parts import terminal, ttext

OUT = pathlib.Path(__file__).resolve().parents[2] / '02_題解/技師題解/04_電機機械/figures'


def stepdown(name, v_in, v_se, v_c, v_out, i_in, i_out, i_c, note1, note2, terms=None):
    """v_* are label parts (v_out: two lines); i_* are label parts (red); terms: optional (H, X, N) names."""
    W, H = 700, 390
    XS, XW, XO = 200, 360, 560
    YT, YM, YB = 60, 160, 300
    s = header(W, H)
    s += line(XW, YT, XW, 76) + coil(XW, 76, XW, 144, turns=4, r=8.5) + line(XW, 144, XW, YM)
    s += line(XW, YM, XW, 178) + coil(XW, 178, XW, 282, turns=6, r=8.6) + line(XW, 282, XW, YB)
    # iron core, broken at the tap row so the tap lead to the load does not cross it
    s += line(XW + 26, 70, XW + 26, YM - 10) + line(XW + 32, 70, XW + 32, YM - 10)
    s += line(XW + 26, YM + 10, XW + 26, 290) + line(XW + 32, YM + 10, XW + 32, 290)
    s += dot(XW - 14, 80) + dot(XW - 14, 182)
    # source across both windings
    s += ac_source(XS, 180, r=22)
    s += line(XS, 158, XS, YT) + line(XS, YT, XW, YT)
    s += line(XS, 202, XS, YB) + line(XS, YB, XO, YB) + dot(XW, YB)
    # load across the common winding (from the tap)
    s += line(XW, YM, XO, YM) + dot(XW, YM)
    s += terminal(XO, YM) + terminal(XO, YB)
    s += line(XO, YM, XO + 40, YM) + resistor(XO + 40, YM, XO + 40, YB) + line(XO, YB, XO + 40, YB)
    # reference arrows
    s += arrow(245, YT - 14, 315, YT - 14, color=RED)
    s += arrow(462, YM - 14, 528, YM - 14, color=RED)
    s += arrow(XW - 40, 256, XW - 40, 208, color=RED)
    s += end_group()
    s += ttext(280, YT - 24, i_in, anchor="middle", color=RED)
    s += ttext(495, YM - 24, i_out, anchor="middle", color=RED)
    s += ttext(XW - 48, 238, i_c, anchor="end", color=RED)
    s += text(XW + 44, 96, [("t", "串聯繞組")])
    s += ttext(XW + 44, 118, v_se, color=BLUE)
    s += text(XW + 44, 224, [("t", "公共繞組")])
    s += ttext(XW + 44, 246, v_c, color=BLUE)
    s += text(XS - 30, 166, [("n", "+")], anchor="end") + text(XS - 30, 208, [("n", "−")], anchor="end")
    s += ttext(XS - 30, 188, v_in, anchor="end", color=BLUE)
    s += text(XO + 56, YM + 26, [("n", "+")]) + text(XO + 56, YB - 8, [("n", "−")])
    s += ttext(XO + 56, 212, v_out[0], color=BLUE)
    s += ttext(XO + 56, 234, v_out[1], color=BLUE)
    s += text(XO + 56, 258, [("t", "負載")])
    s += text(350, 346, note1, anchor="middle")
    s += text(350, 372, note2, anchor="middle")
    if terms:
        s += text(XW + 10, YT - 8, [("v", terms[0])])
        s += text(XO, YM - 12, [("v", terms[1])], anchor="middle")
        s += text(XO, YB + 22, [("v", terms[2])], anchor="middle")
    s += footer()
    out = OUT / name
    out.write_text(s)
    print(out.name, len(s))
