"""EE-110-04-2 fig 1: 220/160 V, 30 kVA two-winding transformer reconnected as a 380 V -> 220 V
step-down autotransformer (160 V series winding aiding the 220 V common winding)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from auto_parts import stepdown

stepdown(
    'EE-110-04-2-single-phase.svg',
    v_in=[("v", "V"), ("vsub", "HN"), ("n", " = 380 V")],
    v_se=[("v", "V"), ("vsub", "se"), ("n", " = 160 V")],
    v_c=[("v", "V"), ("vsub", "c"), ("n", " = 220 V")],
    v_out=([("v", "V"), ("vsub", "XN")], [("n", "= 220 V")]),
    i_in=[("v", "I"), ("vsub", "H")],
    i_out=[("v", "I"), ("vsub", "L")],
    i_c=[("v", "I"), ("vsub", "c")],
    note1=[("t", "兩繞組打點端同在上方（加極性串接）："), ("n", "220 + 160 = 380 V")],
    note2=[("t", "電源跨 "), ("v", "H"), ("t", "–"), ("v", "N"), ("t", "（兩繞組），負載跨 "), ("v", "X"), ("t", "–"), ("v", "N"), ("t", "（220 V 公共繞組）")],
    terms=("H", "X", "N"),
)
