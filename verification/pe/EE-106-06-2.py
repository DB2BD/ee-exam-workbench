"""EE-106-06-2: fault at F on the 220 V side of single-phase 3-wire transformer T2 (75 kVA, 380/220-110 V).

Givens (crop): 11.4 kV source 250 MVA; T1 1000 kVA 3-phase 3-wire 11.4 kV/380 V Z=1.2+j4.9 %;
feeder 60 mm2 x3, 30 m, 0.33+j0.144 ohm/km; T2 75 kVA 1-phase 380/220-110 V Z=1.2+j2.3 %;
F on the 220 V side (two fault marks joined by a line marked 220 V -> line-to-line fault).

Main model: 220 V line-to-line fault, base 75 kVA / 220 V.  T2 full winding Z=0.012+j0.023 pu.
The 3-phase upstream (source, T1, feeder) feeds a single-phase load between two lines, so the
loop impedance is Z1+Z2 = 2 Z1.  K = 1.25 is NOT given in the stem (low-voltage convention).
Reference-book branch (user-supplied photos, not official): Zf = 0.057 pu -> 5.98 kA / 7.475 kA;
0.057 cannot be rebuilt from the stem, so it is recorded as a named constant only.
"""
import math

SB = 75e3
VB = 220.0
I_BASE = SB / VB                                  # 340.9 A
ZB220 = VB**2 / SB                                # 0.6453 ohm
K = 1.25                                          # assumed convention, not stem data

# ---- upstream per phase, per unit on 75 kVA ----
zb380 = 380.0**2 / SB
z_sys = 1j * SB / 250e6
z_t1 = (0.012 + 0.049j) * SB / 1000e3
z_line = (0.33 + 0.144j) * 0.03 / zb380           # one conductor
z_t2 = 0.012 + 0.023j                             # full winding
assert abs(z_sys - 0.0003j) < 1e-9
assert abs(z_t1 - (0.0009 + 0.003675j)) < 1e-9
assert abs(z_line - (0.005142 + 0.002244j)) < 1e-6

up = z_sys + z_t1 + z_line
zf = z_t2 + 2 * up                                # line-to-line loop: Z1 + Z2 = 2 Z1
assert abs(zf - (0.02408 + 0.03544j)) < 2e-5
assert abs(abs(zf) - 0.04285) / 0.04285 < 5e-4
i_sym = I_BASE / abs(zf) / 1e3
assert abs(i_sym - 7.956) / 7.956 < 5e-4                    # boxed symmetrical
assert abs(K * i_sym - 9.946) / 9.946 < 5e-4                # boxed asymmetrical

# ---- independent route: ohms on the 220 V side ----
a = (220.0 / 380.0) ** 2
zt2_ohm = (0.012 + 0.023j) * ZB220
up_ohm = ((0.0 + 1j * 11.4**2 / 250.0 * (0.38 / 11.4) ** 2)
          + (0.012 + 0.049j) * 0.38**2 / 1.0
          + (0.33 + 0.144j) * 0.03)               # on 380 V side, per conductor
z_ohm = zt2_ohm + 2 * up_ohm * a
assert abs(abs(z_ohm) - 0.02765) / 0.02765 < 5e-4
assert abs(VB / abs(z_ohm) / 1e3 - i_sym) < 1e-9

# ---- comparison models (labels as in the note) ----
# upstream NOT doubled (simple same-base series sum) -> 9.927 kA
z_single = z_t2 + up
assert abs(abs(z_single) - 0.0343) < 5e-4
assert abs(I_BASE / abs(z_single) / 1e3 - 9.927) / 9.927 < 5e-4
# same figure in the 110 V half-winding frame: Z_T2,half + 2(...)110
k110 = (110.0 / 380.0) ** 2
z_t2h = (0.012 + 0.023j) * 110.0**2 / 37.5e3
z_up110 = (1j * (11.4**2 / 250.0) * (0.38 / 11.4) ** 2 + (0.012 + 0.049j) * 0.38**2 + (0.33 + 0.144j) * 0.03) * k110
assert abs(110 / abs(z_t2h + 2 * z_up110) / 1e3 - 9.927) / 9.927 < 5e-4
# left 110 V conductor to neutral only -> 11.318 kA
assert abs(110 / abs(z_t2h + z_up110) / 1e3 - 11.318) / 11.318 < 5e-4
# reference book
ZF_BOOK_PU = 0.057
i_book = I_BASE / ZF_BOOK_PU / 1e3
assert abs(i_book - 5.98) / 5.98 < 1e-3
assert abs(K * i_book - 7.475) / 7.475 < 1e-3
assert ZF_BOOK_PU > abs(zf) > abs(z_single)                 # book value is larger than any stem-derived Zf
print("PASS EE-106-06-2")
