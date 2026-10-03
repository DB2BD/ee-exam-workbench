"""EE-111-02-3 independent check: degenerated NMOS common-source stage (over-determined stem).

Givens (official crop): un*Cox = 200 uA/V^2, lambda = 0, VTH = 0.4 V, |Av| = 5,
IDS = 3.17 mA, IR1 = 0.167 mA, RS = 30 ohm, RD = 200 ohm, VDD = 1.8 V,
V(RS) = VOV.  The data over-determine gm, so both consistent subsets are solved:
  gain branch       : gm from |Av| = gm RD / (1 + gm RS)
  square-law branch : gm = 2 ID / VOV with VOV = ID RS
plus the minimum-correction candidate (keep |Av| = 5 and square law, free RS).
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


kn, VTH, Av, ID, IR1 = sp.Rational(200, 10**6), sp.Rational(2, 5), 5, sp.Rational(317, 10**5), sp.Rational(167, 10**6)
RS, RD, VDD = 30, 200, sp.Rational(9, 5)
gm = sp.symbols("gm", positive=True)

VOV = ID * RS
VG = VTH + 2 * VOV                       # VG = VGS + VS = (VTH + VOV) + VOV
R1, R2 = (VDD - VG) / IR1, VG / IR1      # gate draws no DC current
VDS = VDD - ID * RD - ID * RS
assert VDS > VOV                         # saturation holds

# gain branch
gm_gain = sp.solve(sp.Eq(gm * RD / (1 + gm * RS), Av), gm)[0]
wl_gain = gm_gain / (kn * VOV)           # gm = kn (W/L) VOV
# square-law branch: ID = kn/2 (W/L) VOV^2
WL = sp.symbols("WL", positive=True)
wl_sq = sp.solve(sp.Eq(ID, kn / 2 * WL * VOV**2), WL)[0]
gm_sq = sp.sqrt(2 * kn * wl_sq * ID)     # different route from 2ID/VOV
gain_sq = gm_sq * RD / (1 + gm_sq * RS)

# minimum correction: square law + |Av| = 5 + VOV = ID RS, RS unknown
Rs = sp.symbols("Rs", positive=True)
Rs_fix = sp.solve(sp.Eq((2 / Rs) * RD / (1 + (2 / Rs) * Rs), Av), Rs)[0]
gm_fix = 2 / Rs_fix
wl_fix = gm_fix / (kn * ID * Rs_fix)
VG_fix = VTH + 2 * ID * Rs_fix

# reference-book gm = 1 mS gives a gain far from 5
book_gain = sp.Rational(1, 1000) * RD / (1 + sp.Rational(1, 1000) * RS)

assert close(VOV, 0.0951) and close(VG, 0.5902)
assert close(R1, 7244.311) and close(R2, 3534.132)
assert close(gm_gain, 0.1) and close(wl_gain, 5257.624)
assert close(gm_sq, 0.0666667) and close(wl_sq, 3505.082) and close(gain_sq, 4.444444)
assert close(Rs_fix, 26.666667) and close(gm_fix, 0.075) and close(wl_fix, 4436.120)
assert close((VDD - VG_fix) / IR1, 7370.858) and close(VG_fix / IR1, 3407.585)
assert close(book_gain, 0.1942)
print(f"VOV={float(VOV)} VG={float(VG)} R1={float(R1):.3f} R2={float(R2):.3f}")
print(f"gain branch gm={float(gm_gain)} W/L={float(wl_gain):.3f}; square-law gm={float(gm_sq):.7f} "
      f"W/L={float(wl_sq):.3f} |Av|={float(gain_sq):.6f}; fix RS={float(Rs_fix):.6f} W/L={float(wl_fix):.3f}")
print("PASS EE-111-02-3")
