"""EE-111-06-1 (chart-dependent): 100/5 CT excitation curve, relay pickup 8 A.

Stem givens: ratio 100/5, Z' = 0.082 ohm, relay operates at I' = 8 A,
error = Ie/(I'+Ie); (一) Z_B = 0.8 ohm, (二) Z_B = 3 ohm; primary fault 200 A.
The 100:5 E'-Ie curve was digitized from the embedded official chart image
(native JPX, stitched, 2x resampled, grid lines removed, log axes calibrated on
the decade lines).  The table below is that reading; it mirrors the note's
「條件與疑義」.
"""
import numpy as np

N = 100 / 5
Z_LEAK = 0.082
I_PICKUP = 8.0
I_FAULT_PRIMARY = 200.0

# ---- digitized 100:5 curve (Ie [A], E' [V]) ----
CURVE_100_5 = [
    (0.360, 6.42), (0.432, 8.54), (0.519, 10.62), (0.623, 12.50), (0.748, 14.33),
    (0.898, 16.55), (1.295, 18.10), (1.555, 18.74), (1.867, 19.34), (2.241, 19.56),
    (2.691, 19.56), (3.231, 19.72), (3.879, 20.03), (4.658, 20.18), (5.593, 20.34),
    (6.715, 20.50), (8.062, 20.74), (9.680, 20.90), (11.622, 21.07), (13.955, 21.15),
    (16.755, 21.40), (20.117, 21.65), (24.153, 21.82), (29.000, 21.90),
]
CHART_IE_MAX = 30.0          # curves end at Ie = 30 A
READ_TOL = 0.025             # +-3 px of 297 px/decade ~ +-2.4 % on either axis
IE_READ_ZB08 = 0.4           # value used in the boxed answer (chart reading, 2 s.f.)
lgI = np.log10([p[0] for p in CURVE_100_5]); lgE = np.log10([p[1] for p in CURVE_100_5])

def ie_from_e(e, scale=1.0):
    return 10 ** np.interp(np.log10(e / scale), lgE, lgI)

def e_from_ie(ie, scale=1.0):
    return scale * 10 ** np.interp(np.log10(ie), lgI, lgE)

# ---- (一) Z_B = 0.8: relay-pickup method ----
E1 = I_PICKUP * (Z_LEAK + 0.8)
assert abs(E1 - 7.056) < 1e-9
ie1 = ie_from_e(E1)
ie1_band = (ie_from_e(E1, 1 + READ_TOL) * (1 - READ_TOL), ie_from_e(E1, 1 - READ_TOL) * (1 + READ_TOL))
assert 0.35 < ie1_band[0] < ie1 < ie1_band[1] < 0.43, (ie1, ie1_band)
assert abs(ie1 - IE_READ_ZB08) / IE_READ_ZB08 < 0.06          # chart read 0.38 -> 0.4 A
err1 = IE_READ_ZB08 / (I_PICKUP + IE_READ_ZB08)
ip1 = N * (I_PICKUP + IE_READ_ZB08)
assert abs(err1 * 100 - 4.76) / 4.76 < 0.005                    # boxed 4.76 %
assert abs(ip1 - 168) < 1e-9 and ip1 <= I_FAULT_PRIMARY         # boxed 168 A -> detects 200 A

# ---- (二) Z_B = 3: E' beyond the curve end ----
E2 = I_PICKUP * (Z_LEAK + 3.0)
assert abs(E2 - 24.656) < 1e-9
assert E2 > CURVE_100_5[-1][1] * (1 + READ_TOL)                 # 24.66 V > ~22 V at Ie = 30 A
ie2_min = CHART_IE_MAX
err2_min = ie2_min / (I_PICKUP + ie2_min)
ip2_min = N * (I_PICKUP + ie2_min)
assert abs(err2_min * 100 - 78.95) / 78.95 < 0.005               # boxed >= 78.9 %
assert abs(ip2_min - 760) < 1e-9 and ip2_min > I_FAULT_PRIMARY   # boxed >= 760 A -> cannot detect

# ---- check by the other route: fixed 200 A fault, intersect load line with curve ----
I2 = I_FAULT_PRIMARY / N
def intersect(zb, scale=1.0):
    lo, hi = 0.36, 29.0
    f = lambda ie: (Z_LEAK + zb) * (I2 - ie) - e_from_ie(ie, scale)
    for _ in range(200):
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    return mid
for zb, lo_ok, hi_ok, detect in ((0.8, 0.40, 0.46, True), (3.0, 3.2, 3.8, False)):
    vals = [intersect(zb, s) for s in (1 - READ_TOL, 1.0, 1 + READ_TOL)]
    assert all(lo_ok < v < hi_ok for v in vals), (zb, vals)
    assert all(((I2 - v) >= I_PICKUP) == detect for v in vals)
    print(f"Z_B={zb}: Ie={vals[1]:.3f} A (band {min(vals):.2f}-{max(vals):.2f}), I'={I2-vals[1]:.2f} A")
assert I2 - 2.0 == I_PICKUP    # threshold Ie <= 2.0 A for a 200 A fault
print(f"pickup route: Ie(7.056 V)={ie1:.3f} A band {ie1_band[0]:.3f}-{ie1_band[1]:.3f}")
print("PASS EE-111-06-1")
