"""EE-108-04-1 fig 1: 480/120 V, 5 kVA two-winding transformer reconnected as a 600 V -> 480 V
step-down autotransformer (120 V series winding aiding the 480 V common winding)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from auto_parts import stepdown

stepdown(
    'EE-108-04-1-connection.svg',
    v_in=[("v", "V"), ("vsub", "in"), ("n", " = 600 V")],
    v_se=[("v", "V"), ("vsub", "se"), ("n", " = 120 V")],
    v_c=[("v", "V"), ("vsub", "c"), ("n", " = 480 V")],
    v_out=([("v", "V"), ("vsub", "load")], [("n", "= 480 V")]),
    i_in=[("v", "I"), ("vsub", "in")],
    i_out=[("v", "I"), ("vsub", "out")],
    i_c=[("v", "I"), ("vsub", "c")],
    note1=[("t", "兩繞組打點端同在上方（加極性串接）："), ("n", "480 + 120 = 600 V")],
    note2=[("t", "電源跨兩繞組，負載跨 480 V 公共繞組（降壓）")],
)
