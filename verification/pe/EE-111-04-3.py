"""EE-111-04-3: 20 kW 200 V 1800 rpm DC generator, long-shunt cumulative compound.

Ra = 0.1, Rfw = 150, Rsr = 0.04 ohm; magnetization table at 1800 rpm; Nf = 1200 t/pole.
"""
import numpy as np

If_tab = np.array([0.0, 0.125, 0.25, 0.5, 0.625, 0.75, 0.875, 1.0, 1.25, 1.48])
Ea_tab = np.array([5, 33.5, 67, 134, 160, 175, 190, 200, 214, 222])
E = lambda x: np.interp(x, If_tab, Ea_tab)
Finv = lambda e: np.interp(e, Ea_tab, If_tab)
Ra, Rsr, Rfw, Nf = 0.1, 0.04, 150.0, 1200

# (1) Rfc = 0, no load: Ia = If, Ea = 150 If + 0.14 If; bisection on segment
lo, hi = 1.0, 1.48
for _ in range(80):
    mid = (lo + hi) / 2
    if E(mid) - (Rfw + Ra + Rsr) * mid > 0:
        lo = mid
    else:
        hi = mid
If1 = lo
V1 = Rfw * If1
assert abs(V1 - 221.73) / 221.73 <= 0.005
assert abs(V1 - 222) / 222 <= 0.005          # table-level answer ~222 V

# (2) full load: IL = 100 A, Ea = 200 + 0.14 (100 + Ish); Ish in (0, 4/3]
IL = 20e3 / 200
for Ish in (1e-9, 1.0, 200 / 150):
    Ifeq = Finv(200 + (Ra + Rsr) * (IL + Ish))
    assert 1.25 <= Ifeq <= 1.2554
Ifeq2 = Finv(200 + (Ra + Rsr) * (IL + 1.0))
assert abs(Ifeq2 - 1.25) / 1.25 <= 0.005

# (3) flat compound: solve Rfc, Ns simultaneously (no-load and full-load Vt = 200)
def residual(Ns):
    # no-load: Ish = Ia; Ea = 200 + 0.14 Ish; Ifeq = Ish (1 + Ns/Nf)
    lo, hi = 0.9, 1.05
    for _ in range(80):
        mid = (lo + hi) / 2
        if E(mid * (1 + Ns / Nf)) - (200 + (Ra + Rsr) * mid) > 0:
            hi = mid
        else:
            lo = mid
    Ish = lo
    Ia = IL + Ish
    return Ish + Ns * Ia / Nf - Finv(200 + (Ra + Rsr) * Ia), Ish
lo, hi = 0.0, 10.0
for _ in range(80):
    mid = (lo + hi) / 2
    if residual(mid)[0] < 0:
        lo = mid
    else:
        hi = mid
Ns_exact, Ish = lo, residual(lo)[1]
Ns_first_order = Nf * (Ifeq2 - 1.0) / 101
assert abs(Ns_first_order - 3.02) / 3.02 <= 0.005
assert abs(Ns_exact - 3.0) / 3.0 <= 0.01
assert round(Ns_first_order) == 3 and round(Ns_exact) == 3
print(f"V0max={V1:.3f} If={If1:.5f} Ifeq={Ifeq2:.5f} Ns1={Ns_first_order:.3f} Ns_exact={Ns_exact:.3f} Ish={Ish:.4f}")
print("PASS EE-111-04-3")
