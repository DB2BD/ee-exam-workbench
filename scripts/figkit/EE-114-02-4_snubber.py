"""EE-114-02-4: RC snubber across the thyristor (part 2).

R_s - C_s in series, connected across T (anode A to cathode K); S closes at t = 0 with T blocking,
so the loop current i flows V_S -> S -> R_s -> C_s -> R_L.  V_T is + at A, - at K; V_L is + at the top of R_L.
The helpers (thyristor, varistor, skeleton, common_text) are reused by EE-114-02-4_other.py."""
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from electronics_parts import *

YT, YB = 150, 300


def thyristor(xa, xk, y):
    """Horizontal SCR, anode xa (left), cathode xk (right); gate lead from the cathode side, down-right."""
    m = (xa + xk) / 2
    s = diode(xa, y, xk, y)
    s += line(m + 10, y + 3, m + 24, y + 20) + line(m + 24, y + 20, m + 34, y + 20)
    return s


def varistor(x1, x2, y, h=12):
    """MOV: resistor box with a slanted bar (voltage-dependent resistor)."""
    m = (x1 + x2) / 2
    s = line(x1, y, m - 24, y) + line(m + 24, y, x2, y)
    s += f'<rect x="{m - 24:.1f}" y="{y - h / 2:.1f}" width="48" height="{h}"/>\n'
    s += line(m - 30, y + 14, m + 22, y - 14) + line(m + 22, y - 14, m + 32, y - 14)
    return s


def skeleton(xa, xk, xl, top_parts):
    """Source, closed switch, thyristor, load and return wire; top_parts draws what sits left of A."""
    s = vsrc(70, YT, 70, YB) + line(70, YT, 110, YT) + switch(110, YT, 180, YT, True)
    s += top_parts
    s += thyristor(xa, xk, YT) + dot(xa, YT) + dot(xk, YT)
    s += line(xk, YT, xl, YT) + resistor(xl, YT, xl, YB, zigs=6, lead=40)
    s += line(70, YB, xl, YB) + dot(xl, YB) + line(xl, YB, xl, YB + 8) + ground(xl, YB + 8)
    return s


def common_text(xa, xk, xl):
    m = (xa + xk) / 2
    t = [btext(48, (YT + YB) / 2 + 6, [("v", "V"), ("vsub", "S")], anchor="end"),
         text(145, YT - 16, [("v", "S")], anchor="middle"),
         text(m - 4, YT - 18, [("v", "T")], anchor="middle"),
         text(m + 30, YT + 42, [("v", "G")], anchor="middle"),
         text(xa - 6, YT + 20, [("v", "A")], anchor="end"),
         text(xk + 6, YT + 20, [("v", "K")]),
         btext(xa + 14, YT + 24, [("n", "+")], anchor="middle"),
         btext(xk - 14, YT + 24, [("n", "−")], anchor="middle"),
         btext(m - 26, YT + 30, [("v", "V"), ("vsub", "T")], anchor="middle"),
         text(xl - 14, (YT + YB) / 2 + 6, [("v", "R"), ("vsub", "L")], anchor="end"),
         polarity(xl + 18, YT, YB, [("v", "V"), ("vsub", "L")])]
    return ''.join(t)


if __name__ == "__main__":
    # ---- figure 1: RC snubber across T ----
    XA, XK, XL = 280, 420, 560
    W, H = 640, 380
    s = header(W, H)
    s += skeleton(XA, XK, XL, line(180, YT, XA, YT))
    YS = YT - 70
    s += line(XA, YT, XA, YS) + resistor(XA, YS, 350, YS, zigs=5, lead=12) + cap(350, YS, XK, YS) + line(XK, YS, XK, YT)
    s += red_arrow(205, YT - 12, 250, YT - 12)
    s += red_arrow(XA + 12, YS - 16, XA + 52, YS - 16)
    s += end_group()
    t = common_text(XA, XK, XL)
    t += ctext(228, YT - 18, [("v", "i")], anchor="middle")
    t += ctext(XA + 32, YS - 24, [("v", "i")], anchor="middle")
    t += text(315, YS + 30, [("v", "R"), ("vsub", "s")], anchor="middle")
    t += text(385, YS - 22, [("v", "C"), ("vsub", "s")], anchor="middle")
    t += text(20, 350, [("v", "S"), ("t", " 於 "), ("v", "t"), ("n", " = 0"), ("t", " 閉合；"), ("v", "T"), ("t", " 未觸發（阻斷），"),
                        ("v", "C"), ("vsub", "s"), ("t", " 初值為 0；"), ("v", "i"), ("t", " 經 "), ("v", "R"), ("vsub", "s"),
                        ("t", "、"), ("v", "C"), ("vsub", "s"), ("t", "、"), ("v", "R"), ("vsub", "L"), ("t", " 流通")])
    s += t + footer()
    write('EE-114-02-4-snubber.svg', s)

