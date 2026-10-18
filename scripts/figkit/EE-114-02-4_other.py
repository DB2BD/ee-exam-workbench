"""EE-114-02-4: the two other protection methods (part 3): series inductor L_s limits di_T/dt at
turn-on; an MOV (or TVS) across T clamps the overvoltage.  i_T is the thyristor (loop) current.
Reuses the drawing helpers of EE-114-02-4_snubber.py."""
import importlib.util, pathlib, sys
_spec = importlib.util.spec_from_file_location("snub", pathlib.Path(__file__).with_name("EE-114-02-4_snubber.py"))
_m = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)
globals().update({k: v for k, v in vars(_m).items() if not k.startswith("__")})

W, H = 640, 380
# ---- figure 2: series L_s (di/dt) and MOV across T (overvoltage) ----
XA, XK, XL = 300, 440, 580
s = header(W, H)
s += skeleton(XA, XK, XL, line(180, YT, 200, YT) + coil(200, YT, 270, YT, turns=4) + line(270, YT, XA, YT))
YM = YT - 70
s += line(XA, YT, XA, YM) + varistor(XA, XK, YM) + line(XK, YM, XK, YT)
s += red_arrow(470, YT - 12, 520, YT - 12)
s += end_group()
t = common_text(XA, XK, XL)
t += text(235, YT - 18, [("v", "L"), ("vsub", "s")], anchor="middle")
t += ctext(495, YT - 22, [("v", "i"), ("vsub", "T")], anchor="middle")
t += text((XA + XK) / 2, YM - 22, [("t", "MOV／TVS")], anchor="middle")
t += text(20, 350, [("v", "L"), ("vsub", "s"), ("t", " 串聯：限制導通瞬間 "), ("v", "d"), ("v", "i"), ("vsub", "T"), ("n", "/"), ("v", "d"), ("v", "t"),
                    ("t", "；MOV 並接 "), ("v", "T"), ("t", "：箝位 "), ("v", "V"), ("vsub", "T"), ("t", " 的突波過電壓")])
s += t + footer()
write('EE-114-02-4-other.svg', s)
