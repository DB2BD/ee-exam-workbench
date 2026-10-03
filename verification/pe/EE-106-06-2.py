"""EE-106-06-2: fault at F on the 220 V side of single-phase 3-wire transformer T2 (75 kVA, 380/220-110 V).

Givens (crop): 11.4 kV source 250 MVA; T1 1000 kVA 3-phase 3-wire 11.4 kV/380 V Z=1.2+j4.9 %;
feeder 60 mm2 x3, 30 m, 0.33+j0.144 ohm/km; T2 75 kVA 1-phase 380/220-110 V Z=1.2+j2.3 %;
F at T2 secondary (220 V marked between the two fault marks).  K = 1.25.

Reference-book branch (user-supplied book photos; not official): fault at 220 V line-line,
Z_f = 0.057 pu on the 75 kVA / 220 V base -> 5.98 kA, K = 1.25 -> 7.475 kA.  Z_f is a book value
that cannot be rebuilt from the stem; the script records the arithmetic and the discrepancy.
"""
import math
import numpy as np

# ---- stem-derived impedances referred to the 110 V half winding ----
k110 = (110.0 / 380.0) ** 2
z_sys = 1j * (11.4**2 / 250.0) * (0.38 / 11.4) ** 2 * k110
z_t1 = (0.012 + 0.049j) * (0.38**2 / 1.0) * k110
z_line = (0.33 + 0.144j) * 0.03 * k110
z_t2h = (0.012 + 0.023j) * (110.0**2 / 37.5e3)
assert abs(z_sys - 0.00004840j) < 1e-8
assert abs(z_t1 - (0.00014520 + 0.00059290j)) < 1e-8
assert abs(z_line - (0.000829571 + 0.000361994j)) < 1e-8
assert abs(z_t2h - (0.003872 + 0.00742133j)) < 1e-8

# original per-conductor model (left 110 V conductor to neutral)
z_one = z_sys + z_t1 + z_line + z_t2h
assert abs(110 / abs(z_one) / 1e3 - 11.318) / 11.318 < 5e-4
# complete 220 V line-line model, primary side referred as the note states
z_main = z_t2h + 2 * (z_sys + z_t1 + z_line)
i_ll = 110 / abs(z_main) / 1e3
xr = z_main.imag / z_main.real
assert abs(i_ll - 9.927) / 9.927 < 5e-4
assert abs(xr - 1.6195) / 1.6195 < 5e-4

def quarter_peak(i_sym_ka, kappa):
    return math.sqrt(2) * i_sym_ka * (1 + math.exp(-math.pi / (2 * kappa)))

def exact_peak(i_sym_ka, kappa):
    f = lambda u: math.cos(u) - math.exp(-u / kappa) + kappa * math.sin(u)
    lo, hi = 2.0, 3.0
    for _ in range(80):                  # bisection on the stationary-point equation
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(lo) * f(mid) > 0 else (lo, mid)
    u = (lo + hi) / 2
    d = math.exp(-u / kappa)
    return math.sqrt(2) * i_sym_ka * math.sqrt(1 + d * d - 2 * d * math.cos(u))

assert abs(quarter_peak(i_ll, xr) - 19.36) / 19.36 < 5e-4
assert abs(exact_peak(i_ll, xr) - 16.5404) / 16.5404 < 5e-4
kappa1 = z_one.imag / z_one.real
assert abs(exact_peak(110 / abs(z_one) / 1e3, kappa1) - 19.1841) / 19.1841 < 5e-4
assert abs(quarter_peak(110 / abs(z_one) / 1e3, kappa1) - 22.49) / 22.49 < 5e-4

# ---- reference-book main answer (book constants) ----
ZF_BOOK_PU = 0.057                      # book value, 75 kVA / 220 V base
I_BASE = 75e3 / 220.0                   # 340.9 A
K = 1.25
i_book = I_BASE / ZF_BOOK_PU / 1e3
assert abs(i_book - 5.98) / 5.98 < 1e-3                  # reference-book symmetrical
assert abs(K * i_book - 7.475) / 7.475 < 1e-3             # reference-book asymmetrical

# ---- discrepancy evidence: stem data on the same base ----
zb220 = 220.0**2 / 75e3
zf_stem_pu = 2 * z_main / zb220                           # 220 V full-winding frame
assert abs(abs(zf_stem_pu) - 0.0343) < 5e-4               # not 0.057
assert abs(I_BASE / abs(zf_stem_pu) / 1e3 - i_ll) < 1e-9
# strict loop model (every primary element doubled for the line-line path)
z_strict = z_t2h + 4 * (z_sys + z_t1 + z_line)
assert abs(110 / abs(z_strict) / 1e3 - 7.958) / 7.958 < 1e-3
print("PASS EE-106-06-2")
