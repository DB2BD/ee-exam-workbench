"""EE-108-06-4: three-phase fault at F (480 V bus), symmetrical and asymmetrical current.

Givens (crop): 11.4 kV source short-circuit capacity 20 MVA; transformer 5 MVA 11,400/480 V
X=5.5 %; lumped motor 750 kVA X''d=25 %; K=1.25; V_b1=11.4 kV.
The stem prints S_b = 20 kVA; the source is 20 MVA, so S_b = 20 MVA is read.  The ampere
answer does not depend on the base, which is asserted below with both bases.
"""
import math

def fault(sb_kva):
    xs = sb_kva / 20e3
    xt = 0.055 * sb_kva / 5000.0
    xm = 0.25 * sb_kva / 750.0
    x_th = (xs + xt) * xm / (xs + xt + xm)
    ib = sb_kva * 1e3 / (math.sqrt(3) * 480.0)
    return xs, xt, xm, x_th, ib / x_th

xs, xt, xm, x_th, i_sym = fault(20e3)          # S_b = 20 MVA
assert (xs, round(xt, 5)) == (1.0, 0.22) and abs(xm - 6.666667) < 1e-6
assert abs(x_th - 1.031276) < 1e-6
assert abs(i_sym / 1e3 - 23.327) / 23.327 < 5e-4          # boxed (二)
assert abs(1.25 * i_sym / 1e3 - 29.158) / 29.158 < 5e-4   # boxed (三)
assert abs(fault(20.0)[4] - i_sym) / i_sym < 1e-12        # 20 kVA base gives the same amperes

# independent: physical ohms on the 480 V side
v = 480.0
z_s = v**2 / 20e6
z_t = 0.055 * v**2 / 5e6
z_m = 0.25 * v**2 / 750e3
i_check = (v / math.sqrt(3)) / (1 / (1 / (z_s + z_t) + 1 / z_m))
assert abs(i_check - i_sym) / i_sym < 1e-12
# KCL at F: branch currents add
assert abs((v / math.sqrt(3)) / (z_s + z_t) + (v / math.sqrt(3)) / z_m - i_sym) < 1e-6
print("PASS EE-108-06-4")
